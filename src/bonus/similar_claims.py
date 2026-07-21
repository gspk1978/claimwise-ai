"""
similar_claims.py
------------------
BONUS FEATURE: Similar historical claims retrieval.

Maintains a small, separate ChromaDB collection of historical (sample)
claims so a new claim can be semantically compared against past cases --
a common real-world adjuster workflow ("has something like this come up
before, and how was it resolved?").
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_PERSIST_DIR, SAMPLE_CLAIMS_DIR
from src.embeddings.embedding_service import get_embedding_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

_HISTORICAL_COLLECTION = "claimwise_historical_claims"


@lru_cache(maxsize=1)
def _get_historical_store() -> Chroma:
    embeddings = get_embedding_service().get_langchain_embeddings()
    return Chroma(
        collection_name=_HISTORICAL_COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )


def seed_historical_claims(json_path: Path = None) -> int:
    """
    Load sample historical claims from JSON and index them (idempotent --
    skips if the collection is already populated). Returns number indexed.
    """
    store = _get_historical_store()
    try:
        existing = store._collection.count()
    except Exception:
        existing = 0

    if existing > 0:
        logger.info("Historical claims collection already seeded (%d records).", existing)
        return existing

    json_path = json_path or (SAMPLE_CLAIMS_DIR / "sample_claims.json")
    if not json_path.exists():
        logger.warning("No sample_claims.json found at %s; skipping seeding.", json_path)
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        claims = json.load(f)

    documents = []
    ids = []
    for claim in claims:
        documents.append(
            Document(
                page_content=claim["description"],
                metadata={
                    "claim_id": claim["claim_id"],
                    "claim_type": claim.get("claim_type", ""),
                    "outcome": claim.get("outcome", ""),
                    "resolution_notes": claim.get("resolution_notes", ""),
                },
            )
        )
        ids.append(claim["claim_id"])

    store.add_documents(documents=documents, ids=ids)
    logger.info("Seeded %d historical claim(s) into vector store.", len(documents))
    return len(documents)


def find_similar_claims(claim_description: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Return the top_k most semantically similar historical claims with outcomes."""
    store = _get_historical_store()
    try:
        results = store.similarity_search_with_score(claim_description, k=top_k)
    except Exception as exc:
        logger.error("Similar claims search failed: %s", exc)
        return []

    similar = []
    for doc, score in results:
        similar.append(
            {
                "claim_id": doc.metadata.get("claim_id"),
                "claim_type": doc.metadata.get("claim_type"),
                "description": doc.page_content,
                "outcome": doc.metadata.get("outcome"),
                "resolution_notes": doc.metadata.get("resolution_notes"),
                "similarity_distance": round(float(score), 4),
            }
        )
    return similar
