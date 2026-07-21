"""
retriever.py
------------
Thin, well-documented wrapper around the ChromaDB-backed LangChain retriever.
Kept separate from chain.py so retrieval strategy (top_k, filtering, future
hybrid/BM25 blending, etc.) can evolve independently of prompt/generation
logic.
"""

from typing import List, Optional

from langchain_core.documents import Document

from config import RETRIEVER_TOP_K
from src.utils.logger import get_logger
from src.vectorstore.chroma_store import get_chroma_store

logger = get_logger(__name__)


def retrieve_relevant_clauses(
    claim_description: str,
    policy_id: Optional[str] = None,
    top_k: int = RETRIEVER_TOP_K,
) -> List[Document]:
    """
    Perform semantic retrieval over stored policy chunks for a given claim.

    Args:
        claim_description: free-text claim description from the user.
        policy_id: optional filter to scope retrieval to a single ingested policy.
        top_k: number of chunks to retrieve.

    Returns:
        List of LangChain Document objects (page_content + metadata), ordered
        by relevance (most relevant first).
    """
    store = get_chroma_store()
    retriever = store.as_retriever(top_k=top_k, policy_id=policy_id)

    logger.info(
        "Retrieving top-%d clause(s) for claim (policy_id=%s): %.80s...",
        top_k,
        policy_id or "ANY",
        claim_description,
    )
    results = retriever.invoke(claim_description)
    logger.info("Retrieved %d chunk(s).", len(results))
    return results


def format_context_for_prompt(documents: List[Document]) -> str:
    """
    Serialize retrieved chunks into a citation-friendly text block that gets
    injected into the LLM prompt as POLICY CONTEXT.
    """
    if not documents:
        return "(No relevant policy excerpts were retrieved.)"

    blocks = []
    for doc in documents:
        meta = doc.metadata or {}
        chunk_id = meta.get("chunk_id", "unknown")
        source = meta.get("source", "unknown")
        page = meta.get("page_number", "?")
        section = meta.get("section_title", "")
        header = f"[chunk_id: {chunk_id}] (source: {source}, page: {page}" + (
            f", section: {section})" if section else ")"
        )
        blocks.append(f"{header}\n{doc.page_content}")

    return "\n\n---\n\n".join(blocks)
