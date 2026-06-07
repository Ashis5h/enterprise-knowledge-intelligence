from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from app.core.config import settings
from app.services.rag.embeddings import get_embedding_model


class PineconeVectorStore:
    def __init__(self) -> None:
        if not settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is required when VECTOR_DB_PROVIDER=pinecone")

        from pinecone import Pinecone, ServerlessSpec

        self._embedding_model = get_embedding_model()
        self._pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index_name = settings.pinecone_index_name
        self._namespace = settings.pinecone_namespace

        if settings.pinecone_create_index and not self._pc.has_index(self._index_name):
            self._pc.create_index(
                name=self._index_name,
                dimension=settings.pinecone_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.pinecone_cloud,
                    region=settings.pinecone_region,
                ),
                deletion_protection="disabled",
            )

        self._index = self._pc.Index(self._index_name)

    def add_documents(self, documents: list[Document]) -> None:
        if not documents:
            return

        vectors = []
        embeddings = self._embedding_model.embed_documents(
            [document.page_content for document in documents]
        )
        for document, embedding in zip(documents, embeddings, strict=True):
            chunk_id = str(document.metadata.get("chunk_id"))
            metadata = _prepare_metadata(document)
            vectors.append(
                {
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": metadata,
                }
            )

        for start in range(0, len(vectors), 100):
            self._index.upsert(
                vectors=vectors[start : start + 100],
                namespace=self._namespace,
            )

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = 4,
    ) -> list[tuple[Document, float]]:
        query_vector = self._embedding_model.embed_query(query)
        result = self._index.query(
            vector=query_vector,
            top_k=k,
            include_metadata=True,
            namespace=self._namespace,
        )

        matches = _get_matches(result)
        documents: list[tuple[Document, float]] = []
        for match in matches:
            metadata = dict(_get_value(match, "metadata", {}) or {})
            page_content = str(metadata.pop("page_content", ""))
            score = float(_get_value(match, "score", 0.0) or 0.0)
            if page_content:
                documents.append((Document(page_content=page_content, metadata=metadata), score))

        return documents


def _prepare_metadata(document: Document) -> dict[str, Any]:
    metadata = dict(document.metadata)
    metadata["page_content"] = document.page_content
    return {
        key: value
        for key, value in metadata.items()
        if isinstance(value, str | int | float | bool) or value is None
    }


def _get_matches(result: Any) -> list[Any]:
    if isinstance(result, dict):
        return list(result.get("matches", []))

    return list(getattr(result, "matches", []))


def _get_value(item: Any, key: str, default: Any) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)
