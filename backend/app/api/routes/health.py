from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    result: dict = {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "embedding_model": settings.embedding_model,
        "vector_db_provider": settings.vector_db_provider,
        "llm_provider": settings.llm_provider,
        "db": _db_status(),
    }

    if settings.vector_db_provider.lower() == "pinecone":
        result["pinecone"] = _pinecone_status()

    return result


def _db_status() -> dict:
    try:
        from sqlalchemy import text
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "connected"}
    except Exception as exc:
        return {"status": "unavailable", "detail": str(exc)}


def _pinecone_status() -> dict:
    if not settings.pinecone_api_key:
        return {"status": "not_configured", "detail": "PINECONE_API_KEY is not set"}

    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=settings.pinecone_api_key)
        if not pc.has_index(settings.pinecone_index_name):
            return {
                "status": "index_missing",
                "index": settings.pinecone_index_name,
                "detail": "Set PINECONE_CREATE_INDEX=true to create it on startup",
            }

        stats = pc.Index(settings.pinecone_index_name).describe_index_stats()
        total_vectors = _get_attr(stats, "total_vector_count", 0)
        namespaces = _get_attr(stats, "namespaces", {})
        return {
            "status": "connected",
            "index": settings.pinecone_index_name,
            "namespace": settings.pinecone_namespace,
            "total_vectors": total_vectors,
            "namespaces": list(namespaces.keys()) if isinstance(namespaces, dict) else [],
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def _get_attr(obj, key: str, default):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
