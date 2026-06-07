from app.core.config import settings
from app.schemas.chat import SourceCitation
from app.services.rag.document_registry import list_document_records


def retrieve_context(question: str, k: int = 4) -> tuple[str, list[SourceCitation]]:
    try:
        if (
            settings.embedding_model == "local-hash"
            and settings.vector_db_provider.lower() != "pinecone"
        ):
            from app.services.rag.local_index import search_local_documents

            results = search_local_documents(question, k=k)
        else:
            from app.services.rag.vector_store import get_vector_store

            vector_store = get_vector_store()
            results = vector_store.similarity_search_with_relevance_scores(question, k=k)
    except Exception:
        return "", []

    context_blocks: list[str] = []
    citations: list[SourceCitation] = []
    seen_contents: set[str] = set()
    records_by_filename = {record.filename: record for record in list_document_records()}

    for document, score in results:
        metadata = document.metadata
        document_name = metadata.get("document_name", "unknown")
        registry_record = records_by_filename.get(document_name)
        content_key = " ".join(document.page_content.lower().split())
        if content_key in seen_contents:
            continue

        seen_contents.add(content_key)
        context_blocks.append(document.page_content)
        citations.append(
            SourceCitation(
                document_name=document_name,
                chunk_id=metadata.get("chunk_id", "unknown"),
                page_number=metadata.get("page"),
                confidence=max(0.0, min(1.0, float(score))),
                excerpt=document.page_content[:900],
                department=(
                    registry_record.department
                    if registry_record
                    else metadata.get("department", "General")
                ),
                document_type=(
                    registry_record.document_type
                    if registry_record
                    else metadata.get("document_type", "Policy")
                ),
                access_level=(
                    registry_record.access_level
                    if registry_record
                    else metadata.get("access_level", "internal")
                ),
            )
        )

    return "\n\n".join(context_blocks), citations
