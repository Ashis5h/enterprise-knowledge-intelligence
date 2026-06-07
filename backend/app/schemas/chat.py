from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    document_name: str
    chunk_id: str
    page_number: int | None = None
    confidence: float = 0.0
    excerpt: str = ""
    department: str = "General"
    document_type: str = "Policy"
    access_level: str = "internal"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    conversation_id: str | None = None
    mode: str = "qa"


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = Field(default_factory=list)
    validation_status: str = "not_evaluated"
    validation_notes: list[str] = Field(default_factory=list)
