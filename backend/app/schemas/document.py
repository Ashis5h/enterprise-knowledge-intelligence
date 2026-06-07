from pydantic import BaseModel


class DocumentRecord(BaseModel):
    id: str
    filename: str
    chunks_created: int
    status: str
    uploaded_at: str
    source_path: str
    department: str = "General"
    document_type: str = "Policy"
    access_level: str = "internal"


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    chunks_created: int
    status: str
    department: str
    document_type: str
    access_level: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecord]
