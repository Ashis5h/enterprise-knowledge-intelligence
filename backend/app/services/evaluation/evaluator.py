import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import EvaluationCase, EvaluationRun
from app.db.session import SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agents.graph import run_agent_workflow
from app.services.evaluation.llm_judge import (
    score_answer_relevancy,
    score_context_recall,
    score_faithfulness,
)

EVALUATION_RESULTS_PATH = Path("data/evaluation_results.json")

BENCHMARK_CASES = [
    {
        "id": "leave_casual",
        "question": "How many casual leaves are allowed?",
        "expected_terms": ["12", "casual", "leaves"],
        "expected_source": "sample_leave_policy.txt",
    },
    {
        "id": "security_incident_reporting",
        "question": "When should security incidents be reported?",
        "expected_terms": ["30", "minutes", "discovery"],
        "expected_source": "security_guidelines.txt",
    },
    {
        "id": "project_status_due",
        "question": "When are project status reports due?",
        "expected_terms": ["Friday", "5:00", "PM"],
        "expected_source": "project_documentation.txt",
    },
    {
        "id": "onboarding_training",
        "question": "When must onboarding training be completed?",
        "expected_terms": ["15", "days", "joining"],
        "expected_source": "employee_handbook.txt",
    },
    {
        "id": "priority_one_acknowledgement",
        "question": "What is the acknowledgement time for Priority 1 incidents?",
        "expected_terms": ["15", "minutes", "IT Operations Manager"],
        "expected_source": "it_support_sop.txt",
    },
]


async def run_evaluation() -> dict:
    case_results = []

    for benchmark in BENCHMARK_CASES:
        response = await run_agent_workflow(
            ChatRequest(question=benchmark["question"], mode="qa")
        )
        scored = await _score_case(benchmark, response)
        case_results.append(scored)

    summary = _aggregate(case_results)
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": summary,
        "cases": case_results,
    }

    EVALUATION_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVALUATION_RESULTS_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _try_save_run_to_db(result)
    return result


def latest_evaluation() -> dict:
    db_result = _try_load_latest_run_from_db()
    if db_result:
        return db_result

    if not EVALUATION_RESULTS_PATH.exists():
        return {
            "generated_at": None,
            "summary": {
                "total_cases": 0,
                "faithfulness": 0.0,
                "context_precision": 0.0,
                "answer_relevancy": 0.0,
                "context_recall": 0.0,
                "hallucination_rate": 0.0,
            },
            "cases": [],
        }

    return json.loads(EVALUATION_RESULTS_PATH.read_text(encoding="utf-8"))


def _try_save_run_to_db(result: dict) -> None:
    try:
        with SessionLocal() as session:
            summary = result["summary"]
            run = EvaluationRun(
                generated_at=datetime.fromisoformat(result["generated_at"]).replace(tzinfo=None),
                total_cases=summary["total_cases"],
                faithfulness=summary["faithfulness"],
                context_precision=summary["context_precision"],
                answer_relevancy=summary["answer_relevancy"],
                context_recall=summary["context_recall"],
                hallucination_rate=summary["hallucination_rate"],
            )
            session.add(run)
            session.flush()  # get run.id before adding cases
            for case in result["cases"]:
                session.add(
                    EvaluationCase(
                        run_id=run.id,
                        case_id=case["id"],
                        question=case["question"],
                        answer=case["answer"],
                        expected_source=case["expected_source"],
                        top_source=case.get("top_source"),
                        faithfulness=case["faithfulness"],
                        context_precision=case["context_precision"],
                        answer_relevancy=case["answer_relevancy"],
                        context_recall=case["context_recall"],
                        passed=int(case["passed"]),
                    )
                )
            session.commit()
    except (SQLAlchemyError, ValueError):
        return


def _try_load_latest_run_from_db() -> dict | None:
    try:
        with SessionLocal() as session:
            run = session.execute(
                select(EvaluationRun).order_by(EvaluationRun.generated_at.desc())
            ).scalars().first()
            if run is None:
                return None
            cases = session.execute(
                select(EvaluationCase).where(EvaluationCase.run_id == run.id)
            ).scalars().all()
            return {
                "generated_at": run.generated_at.replace(tzinfo=UTC).isoformat(),
                "summary": {
                    "total_cases": run.total_cases,
                    "faithfulness": run.faithfulness,
                    "context_precision": run.context_precision,
                    "answer_relevancy": run.answer_relevancy,
                    "context_recall": run.context_recall,
                    "hallucination_rate": run.hallucination_rate,
                },
                "cases": [
                    {
                        "id": c.case_id,
                        "question": c.question,
                        "answer": c.answer,
                        "expected_source": c.expected_source,
                        "top_source": c.top_source,
                        "faithfulness": c.faithfulness,
                        "context_precision": c.context_precision,
                        "answer_relevancy": c.answer_relevancy,
                        "context_recall": c.context_recall,
                        "passed": bool(c.passed),
                    }
                    for c in cases
                ],
            }
    except SQLAlchemyError:
        return None


async def _score_case(benchmark: dict, response: ChatResponse) -> dict:
    expected_terms = benchmark["expected_terms"]
    expected_source = benchmark["expected_source"]
    sources = response.sources
    context = "\n\n".join(s.excerpt for s in sources if s.excerpt)

    source_hits = sum(1 for source in sources if source.document_name == expected_source)
    top_source_match = bool(sources and sources[0].document_name == expected_source)
    context_precision = 1.0 if top_source_match else 0.5 if source_hits else 0.0

    # LLM-as-judge scores (fall back to heuristics if Ollama unavailable)
    faithfulness = await score_faithfulness(benchmark["question"], response.answer, context)
    answer_relevancy = await score_answer_relevancy(benchmark["question"], response.answer)
    context_recall = await score_context_recall(benchmark["question"], context, expected_terms)

    passed = faithfulness >= 0.7 and answer_relevancy >= 0.7 and context_recall >= 0.7

    return {
        "id": benchmark["id"],
        "question": benchmark["question"],
        "answer": response.answer,
        "expected_source": expected_source,
        "top_source": sources[0].document_name if sources else None,
        "faithfulness": faithfulness,
        "context_precision": round(context_precision, 2),
        "answer_relevancy": answer_relevancy,
        "context_recall": context_recall,
        "passed": passed,
    }


def _aggregate(case_results: list[dict]) -> dict:
    total = len(case_results)
    if total == 0:
        return {
            "total_cases": 0,
            "faithfulness": 0.0,
            "context_precision": 0.0,
            "answer_relevancy": 0.0,
            "context_recall": 0.0,
            "hallucination_rate": 0.0,
        }

    return {
        "total_cases": total,
        "faithfulness": _average(case_results, "faithfulness"),
        "context_precision": _average(case_results, "context_precision"),
        "answer_relevancy": _average(case_results, "answer_relevancy"),
        "context_recall": _average(case_results, "context_recall"),
        "hallucination_rate": round(
            1 - (sum(1 for result in case_results if result["passed"]) / total),
            2,
        ),
    }


def _average(case_results: list[dict], key: str) -> float:
    return round(sum(result[key] for result in case_results) / len(case_results), 2)
