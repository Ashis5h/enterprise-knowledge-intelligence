from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile
from uuid import uuid4

from fastapi import UploadFile
from langchain_core.documents import Document

from app.core.config import settings
from app.schemas.document import DocumentUploadResponse
from app.services.rag.document_registry import add_document_record

UPLOAD_DIR = Path("data/uploads")


async def ingest_upload(
    file: UploadFile,
    department: str = "General",
    document_type: str = "Policy",
    access_level: str = "internal",
) -> DocumentUploadResponse:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    document_id = str(uuid4())
    destination = UPLOAD_DIR / f"{document_id}-{file.filename}"
    destination.write_bytes(await file.read())

    documents = _load_document(destination)
    chunks = _split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "document_name": file.filename,
                "chunk_id": f"{destination.stem}-{index}",
                "source": str(destination),
                "department": department,
                "document_type": document_type,
                "access_level": access_level,
            }
        )

    if chunks and settings.vector_db_provider.lower() == "pinecone":
        from app.services.rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
    elif chunks and settings.embedding_model == "local-hash":
        from app.services.rag.local_index import add_local_documents

        add_local_documents(chunks)
    elif chunks:
        from app.services.rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        vector_store.add_documents(chunks)

    filename = file.filename or destination.name
    add_document_record(
        document_id=document_id,
        filename=filename,
        chunks_created=len(chunks),
        status="indexed",
        source_path=str(destination),
        department=department,
        document_type=document_type,
        access_level=access_level,
    )

    return DocumentUploadResponse(
        id=document_id,
        filename=filename,
        chunks_created=len(chunks),
        status="indexed",
        department=department,
        document_type=document_type,
        access_level=access_level,
    )


def _load_document(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        return [Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path)})]
    if suffix == ".docx":
        return _load_docx(path)
    if suffix == ".pdf":
        return _load_pdf(path)

    raise ValueError(f"Unsupported document type: {suffix}")


def _load_pdf(path: Path) -> list[Document]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    documents = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": str(path), "page": page_index},
                )
            )

    return documents


def _load_docx(path: Path) -> list[Document]:
    with ZipFile(path) as docx:
        xml = docx.read("word/document.xml")

    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []

    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        if text.strip():
            paragraphs.append(text.strip())

    return [
        Document(
            page_content="\n".join(paragraphs),
            metadata={"source": str(path)},
        )
    ]


def _split_documents(
    documents: list[Document],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> list[Document]:
    chunks: list[Document] = []
    step = max(1, chunk_size - chunk_overlap)

    for document in documents:
        text = " ".join(document.page_content.split())
        if not text:
            continue

        for start in range(0, len(text), step):
            chunk_text = text[start : start + chunk_size]
            if chunk_text:
                chunks.append(Document(page_content=chunk_text, metadata=dict(document.metadata)))

    return chunks
