from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.document import DocumentListResponse, DocumentUploadResponse
from app.services.rag.document_registry import list_document_records
from app.services.rag.ingestion import ingest_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form("General"),
    document_type: str = Form("Policy"),
    access_level: str = Form("internal"),
) -> DocumentUploadResponse:
    try:
        return await ingest_upload(
            file=file,
            department=department,
            document_type=document_type,
            access_level=access_level,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    return DocumentListResponse(documents=list_document_records())
