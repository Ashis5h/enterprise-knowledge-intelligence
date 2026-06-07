"""
LLM-as-judge for RAGAS-style evaluation metrics.
Uses Ollama (or falls back to heuristics if unavailable).
"""
from __future__ import annotations

import re

import httpx

from app.core.config import settings

_TIMEOUT = 60.0


async def score_faithfulness(question: str, answer: str, context: str) -> float:
    """
    Score 0.0–1.0: is every claim in the answer supported by the context?
    """
    prompt = (
        "You are an evaluation judge. Given a question, an answer, and a context, "
        "score how faithful the answer is to the context on a scale of 0 to 10.\n"
        "A score of 10 means every claim in the answer is directly supported by the context.\n"
        "A score of 0 means the answer contains facts not found in the context.\n"
        "Reply with a single integer between 0 and 10. Nothing else.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        f"Context: {context[:1500]}\n"
        "Score:"
    )
    raw = await _call_ollama(prompt)
    return _parse_score(raw, fallback=_heuristic_faithfulness(answer, context))


async def score_answer_relevancy(question: str, answer: str) -> float:
    """
    Score 0.0–1.0: how well does the answer address the question?
    """
    prompt = (
        "You are an evaluation judge. Score how relevant the answer is to the question "
        "on a scale of 0 to 10.\n"
        "A score of 10 means the answer directly and completely addresses the question.\n"
        "A score of 0 means the answer is off-topic or empty.\n"
        "Reply with a single integer between 0 and 10. Nothing else.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        "Score:"
    )
    raw = await _call_ollama(prompt)
    return _parse_score(raw, fallback=_heuristic_relevancy(question, answer))


async def score_context_recall(question: str, context: str, expected_terms: list[str]) -> float:
    """
    Score 0.0–1.0: does the retrieved context contain the information needed to answer?
    """
    prompt = (
        "You are an evaluation judge. Given a question and retrieved context, "
        "score whether the context contains enough information to answer the question "
        "on a scale of 0 to 10.\n"
        "A score of 10 means the context fully contains the answer.\n"
        "A score of 0 means the context is irrelevant.\n"
        "Reply with a single integer between 0 and 10. Nothing else.\n\n"
        f"Question: {question}\n"
        f"Context: {context[:1500]}\n"
        "Score:"
    )
    raw = await _call_ollama(prompt)
    fallback = sum(1 for t in expected_terms if t.lower() in context.lower()) / max(len(expected_terms), 1)
    return _parse_score(raw, fallback=fallback)


async def _call_ollama(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "").strip()
    except httpx.HTTPError:
        return ""


def _parse_score(raw: str, fallback: float) -> float:
    match = re.search(r"\b(\d+)\b", raw)
    if match:
        value = int(match.group(1))
        return round(min(max(value, 0), 10) / 10, 2)
    return round(fallback, 2)


def _heuristic_faithfulness(answer: str, context: str) -> float:
    answer_terms = set(re.findall(r"[a-zA-Z0-9]+", answer.lower()))
    context_terms = set(re.findall(r"[a-zA-Z0-9]+", context.lower()))
    if not answer_terms:
        return 0.0
    overlap = answer_terms & context_terms
    return len(overlap) / len(answer_terms)


def _heuristic_relevancy(question: str, answer: str) -> float:
    q_terms = set(re.findall(r"[a-zA-Z0-9]+", question.lower()))
    a_terms = set(re.findall(r"[a-zA-Z0-9]+", answer.lower()))
    if not q_terms:
        return 0.0
    return len(q_terms & a_terms) / len(q_terms)
