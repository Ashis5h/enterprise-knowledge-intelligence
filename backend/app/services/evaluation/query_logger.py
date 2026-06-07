import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import QueryLog
from app.db.session import SessionLocal
from app.schemas.chat import ChatRequest, ChatResponse

QUERY_LOG_PATH = Path("data/query_log.json")


def log_query(request: ChatRequest, response: ChatResponse) -> None:
    created_at = datetime.now(UTC)
    average_confidence = _average_confidence(response)
    records = _read_records()
    records.append(
        {
            "question": request.question,
            "mode": request.mode,
            "answer": response.answer,
            "validation_status": response.validation_status,
            "source_count": len(response.sources),
            "average_confidence": average_confidence,
            "created_at": created_at.isoformat(),
        }
    )
    QUERY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUERY_LOG_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    _try_log_query_to_db(request, response, average_confidence, created_at)


def analytics_summary() -> dict[str, float | int]:
    records = _try_read_records_from_db() or _read_records()
    total = len(records)
    if total == 0:
        return {
            "queries_processed": 0,
            "faithfulness": 0.0,
            "context_precision": 0.0,
            "answer_relevancy": 0.0,
            "hallucination_rate": 0.0,
        }

    grounded = sum(1 for record in records if record["validation_status"] == "grounded")
    average_confidence = sum(record["average_confidence"] for record in records) / total
    hallucination_risk = 1 - (grounded / total)

    return {
        "queries_processed": total,
        "faithfulness": round(grounded / total, 2),
        "context_precision": round(average_confidence, 2),
        "answer_relevancy": round(grounded / total, 2),
        "hallucination_rate": round(hallucination_risk, 2),
    }


def _average_confidence(response: ChatResponse) -> float:
    if not response.sources:
        return 0.0

    return sum(source.confidence for source in response.sources) / len(response.sources)


def _read_records() -> list[dict]:
    if not QUERY_LOG_PATH.exists():
        return []

    return json.loads(QUERY_LOG_PATH.read_text(encoding="utf-8"))


def _try_log_query_to_db(
    request: ChatRequest,
    response: ChatResponse,
    average_confidence: float,
    created_at: datetime,
) -> None:
    try:
        with SessionLocal() as session:
            session.add(
                QueryLog(
                    question=request.question,
                    mode=request.mode,
                    answer=response.answer,
                    validation_status=response.validation_status,
                    source_count=len(response.sources),
                    average_confidence=average_confidence,
                    created_at=created_at.replace(tzinfo=None),
                )
            )
            session.commit()
    except SQLAlchemyError:
        return


def _try_read_records_from_db() -> list[dict]:
    try:
        with SessionLocal() as session:
            rows = session.execute(
                select(QueryLog).order_by(QueryLog.created_at.asc())
            ).scalars()
            return [
                {
                    "question": row.question,
                    "mode": row.mode,
                    "answer": row.answer,
                    "validation_status": row.validation_status,
                    "source_count": row.source_count,
                    "average_confidence": row.average_confidence,
                    "created_at": row.created_at.replace(tzinfo=UTC).isoformat(),
                }
                for row in rows
            ]
    except SQLAlchemyError:
        return []
