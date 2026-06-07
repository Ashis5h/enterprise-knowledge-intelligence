from functools import lru_cache

from langchain_community.vectorstores import Chroma

from app.core.config import settings
from app.services.rag.embeddings import get_embedding_model
from app.services.rag.pinecone_store import PineconeVectorStore


@lru_cache
def get_vector_store() -> Chroma | PineconeVectorStore:
    if settings.vector_db_provider.lower() == "pinecone":
        return PineconeVectorStore()

    return Chroma(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=get_embedding_model(),
        collection_name="enterprise_documents",
    )
