import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import Document as DocumentModel
from app.db.session import SessionLocal
from app.schemas.document import DocumentRecord

REGISTRY_PATH = Path("data/document_registry.json")


def add_document_record(
    document_id: str,
    filename: str,
    chunks_created: int,
    status: str,
    source_path: str,
    department: str,
    document_type: str,
    access_level: str,
) -> DocumentRecord:
    records = list_document_records()
    record = DocumentRecord(
        id=document_id,
        filename=filename,
        chunks_created=chunks_created,
        status=status,
        uploaded_at=datetime.now(UTC).isoformat(),
        source_path=source_path,
        department=department,
        document_type=document_type,
        access_level=access_level,
    )

    updated = [existing for existing in records if existing.id != document_id]
    updated.append(record)
    _write_records(updated)
    _try_add_record_to_db(record)
    return record


def list_document_records() -> list[DocumentRecord]:
    db_records = _try_list_records_from_db()
    if db_records:
        return db_records

    if not REGISTRY_PATH.exists():
        return []

    raw_records = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = [DocumentRecord.model_validate(record) for record in raw_records]
    latest_by_filename: dict[str, DocumentRecord] = {}

    for record in sorted(records, key=lambda item: item.uploaded_at, reverse=True):
        latest_by_filename.setdefault(record.filename, record)

    return list(latest_by_filename.values())


def _write_records(records: list[DocumentRecord]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps([record.model_dump() for record in records], indent=2),
        encoding="utf-8",
    )


def _try_add_record_to_db(record: DocumentRecord) -> None:
    try:
        with SessionLocal() as session:
            existing = session.get(DocumentModel, record.id)
            if existing is None:
                session.add(
                    DocumentModel(
                        id=record.id,
                        filename=record.filename,
                        chunks_created=record.chunks_created,
                        status=record.status,
                        source_path=record.source_path,
                        department=record.department,
                        document_type=record.document_type,
                        access_level=record.access_level,
                        uploaded_at=datetime.fromisoformat(record.uploaded_at),
                    )
                )
            session.commit()
    except (SQLAlchemyError, ValueError):
        return


def _try_list_records_from_db() -> list[DocumentRecord]:
    try:
        with SessionLocal() as session:
            rows = session.execute(
                select(DocumentModel).order_by(DocumentModel.uploaded_at.desc())
            ).scalars()
            latest_by_filename: dict[str, DocumentRecord] = {}
            for row in rows:
                latest_by_filename.setdefault(
                    row.filename,
                    DocumentRecord(
                        id=row.id,
                        filename=row.filename,
                        chunks_created=row.chunks_created,
                        status=row.status,
                        uploaded_at=row.uploaded_at.replace(tzinfo=UTC).isoformat(),
                        source_path=row.source_path,
                        department=row.department,
                        document_type=row.document_type,
                        access_level=row.access_level,
                    ),
                )
            return list(latest_by_filename.values())
    except SQLAlchemyError:
        return []
