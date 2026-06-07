import json
import re
from pathlib import Path

from langchain_core.documents import Document

LOCAL_INDEX_PATH = Path("data/local_vector_index.json")


def add_local_documents(documents: list[Document]) -> None:
    records = _read_records()
    for document in documents:
        content_key = _content_key(document.page_content)
        records = [
            record
            for record in records
            if _content_key(record["page_content"]) != content_key
        ]
        records.append(
            {
                "page_content": document.page_content,
                "metadata": document.metadata,
            }
        )

    LOCAL_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_INDEX_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def search_local_documents(question: str, k: int = 4) -> list[tuple[Document, float]]:
    question_terms = _tokenize(question)
    scored: list[tuple[Document, float]] = []
    seen_content: set[str] = set()

    for record in reversed(_read_records()):
        content = record["page_content"]
        content_key = _content_key(content)
        if content_key in seen_content:
            continue

        seen_content.add(content_key)
        content_terms = _tokenize(content)
        overlap = question_terms.intersection(content_terms)
        if not overlap:
            continue

        score = len(overlap) / max(len(question_terms), 1)
        scored.append((Document(page_content=content, metadata=record["metadata"]), score))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


def _read_records() -> list[dict]:
    if not LOCAL_INDEX_PATH.exists():
        return []

    return json.loads(LOCAL_INDEX_PATH.read_text(encoding="utf-8"))


def _tokenize(text: str) -> set[str]:
    stop_words = {
        "the",
        "and",
        "are",
        "how",
        "many",
        "allowed",
        "with",
        "from",
        "what",
        "when",
        "must",
        "should",
    }
    return {
        _normalize_token(token)
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 2 and token not in stop_words
    }


def _content_key(text: str) -> str:
    return "".join(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def _normalize_token(token: str) -> str:
    if token.startswith("acknowledg"):
        return "acknowledge"
    if token.startswith("submit"):
        return "submit"
    if token.startswith("report"):
        return "report"
    if token.startswith("incident"):
        return "incident"
    return token.rstrip("s")
