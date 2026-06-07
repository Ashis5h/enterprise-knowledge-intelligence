"""
Migrate local vector index to Pinecone.

Reads data/local_vector_index.json, embeds every chunk with the configured
sentence-transformer, and upserts batches into Pinecone.

Usage:
    # From the backend directory with .env present:
    python ../scripts/migrate_to_pinecone.py [--dry-run] [--batch-size 100]

Requirements:
    PINECONE_API_KEY must be set in .env or environment.
    VECTOR_DB_PROVIDER does NOT need to be changed — this script targets Pinecone directly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: allow running from the repo root or the backend directory.
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

LOCAL_INDEX_PATH = REPO_ROOT / "data" / "local_vector_index.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate local index to Pinecone")
    parser.add_argument("--dry-run", action="store_true", help="Skip Pinecone upsert — just report counts")
    parser.add_argument("--batch-size", type=int, default=100, help="Vectors per upsert batch (default 100)")
    parser.add_argument("--namespace", type=str, default="", help="Override Pinecone namespace")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load settings after path is on sys.path
    from app.core.config import settings  # noqa: E402

    if not settings.pinecone_api_key:
        print("ERROR: PINECONE_API_KEY is not configured. Set it in .env and retry.")
        sys.exit(1)

    namespace = args.namespace or settings.pinecone_namespace
    print(f"Source:    {LOCAL_INDEX_PATH}")
    print(f"Index:     {settings.pinecone_index_name}")
    print(f"Namespace: {namespace}")
    print(f"Dry run:   {args.dry_run}")

    if not LOCAL_INDEX_PATH.exists():
        print("ERROR: local_vector_index.json not found. Nothing to migrate.")
        sys.exit(1)

    records: list[dict] = json.loads(LOCAL_INDEX_PATH.read_text(encoding="utf-8"))
    print(f"Chunks to migrate: {len(records)}")

    if args.dry_run:
        print("Dry run — no data sent to Pinecone.")
        return

    # Import here so missing deps fail with a clear message
    try:
        from pinecone import Pinecone, ServerlessSpec
    except ImportError:
        print("ERROR: pinecone package not installed. Run: pip install pinecone")
        sys.exit(1)

    from app.services.rag.embeddings import get_embedding_model

    print("Loading embedding model...")
    # Force real embeddings regardless of local settings
    import os
    os.environ["VECTOR_DB_PROVIDER"] = "pinecone"  # tricks get_embedding_model into using real model

    embedding_model = get_embedding_model()

    pc = Pinecone(api_key=settings.pinecone_api_key)

    if not pc.has_index(settings.pinecone_index_name):
        print(f"Creating index '{settings.pinecone_index_name}'...")
        from pinecone import ServerlessSpec
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
            deletion_protection="disabled",
        )
        print("Index created.")

    index = pc.Index(settings.pinecone_index_name)

    # Process in batches
    total_upserted = 0
    batch_size = args.batch_size
    for batch_start in range(0, len(records), batch_size):
        batch = records[batch_start : batch_start + batch_size]
        texts = [r["page_content"] for r in batch]
        embeddings = embedding_model.embed_documents(texts)

        vectors = []
        for idx, (record, embedding) in enumerate(zip(batch, embeddings)):
            metadata = dict(record.get("metadata", {}))
            chunk_id = metadata.get("chunk_id") or f"chunk-{batch_start + idx}"
            metadata["page_content"] = record["page_content"]
            # Filter to scalar types Pinecone accepts
            metadata = {
                k: v for k, v in metadata.items()
                if isinstance(v, (str, int, float, bool)) or v is None
            }
            vectors.append({"id": str(chunk_id), "values": embedding, "metadata": metadata})

        index.upsert(vectors=vectors, namespace=namespace)
        total_upserted += len(vectors)
        print(f"  Upserted {total_upserted}/{len(records)} vectors...")

    stats = index.describe_index_stats()
    total_in_index = getattr(stats, "total_vector_count", None) or stats.get("total_vector_count", "?")
    print(f"\nMigration complete. {total_upserted} vectors upserted.")
    print(f"Total vectors in index '{settings.pinecone_index_name}': {total_in_index}")


if __name__ == "__main__":
    main()
