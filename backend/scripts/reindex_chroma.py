"""Re-index all documents tracked in PostgreSQL into the active vector store.

Useful when switching VECTOR_DB_PROVIDER (e.g. pinecone -> chroma) so that
previously uploaded documents become searchable again under the new store.

Run inside the backend container:
    docker compose exec backend python scripts/reindex_chroma.py
"""

from pathlib import Path

from app.services.rag.document_registry import list_document_records
from app.services.rag.ingestion import _load_document, _split_documents
from app.services.rag.vector_store import get_vector_store


def main() -> None:
    rows = list_document_records()

    if not rows:
        print("No document records found.")
        return

    vector_store = get_vector_store()
    total_chunks = 0
    skipped = 0

    for row in rows:
        path = Path(row.source_path)
        if not path.exists():
            print(f"SKIP (file missing): {row.filename} -> {path}")
            skipped += 1
            continue

        try:
            documents = _load_document(path)
        except Exception as exc:
            print(f"SKIP (load failed): {row.filename} -> {exc}")
            skipped += 1
            continue

        chunks = _split_documents(documents)
        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "document_name": row.filename,
                    "chunk_id": f"{path.stem}-{index}",
                    "source": str(path),
                    "department": row.department,
                    "document_type": row.document_type,
                    "access_level": row.access_level,
                }
            )

        if chunks:
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)
            print(f"OK: {row.filename} -> {len(chunks)} chunks")

    print(f"\nDone. Re-indexed {len(rows) - skipped} documents, {total_chunks} chunks total.")
    if skipped:
        print(f"Skipped {skipped} documents (missing files or load errors).")


if __name__ == "__main__":
    main()
