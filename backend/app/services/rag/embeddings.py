import hashlib
import math
import re
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from app.core.config import settings


class LocalHashEmbeddings(Embeddings):
    """Offline deterministic embeddings for local demos and tests."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]


@lru_cache
def get_embedding_model() -> Embeddings:
    # When Pinecone is selected but no real embedding model is explicitly configured,
    # fall back to a real sentence-transformer so vectors are semantically meaningful.
    if (
        settings.vector_db_provider.lower() == "pinecone"
        and settings.embedding_model == "local-hash"
    ):
        return HuggingFaceEmbeddings(model_name=settings.pinecone_embedding_model)

    if settings.embedding_model == "local-hash":
        return LocalHashEmbeddings()

    return HuggingFaceEmbeddings(model_name=settings.embedding_model)
