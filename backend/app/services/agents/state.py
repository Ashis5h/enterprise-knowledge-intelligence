from typing import TypedDict

from app.schemas.chat import SourceCitation


class AgentState(TypedDict, total=False):
    question: str
    mode: str
    context: str
    answer: str
    sources: list[SourceCitation]
    validation_status: str
    validation_notes: list[str]

