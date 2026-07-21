"""
pipeline.py
-----------
Orchestrates the full ingestion pipeline for a single policy document:

    PDF/TXT file -> parse pages -> chunk -> embed -> persist in ChromaDB

This is kept separate from the RAG (query-time) pipeline so ingestion and
retrieval can be reasoned about, tested, and scaled independently.
"""

import uuid
from pathlib import Path
from typing import Union

from src.ingestion.chunker import chunk_pages
from src.ingestion.pdf_loader import load_pdf, load_text_file
from src.utils.logger import get_logger
from src.vectorstore.chroma_store import get_chroma_store

logger = get_logger(__name__)


def ingest_policy_document(file_path: Union[str, Path], policy_name: str = None) -> dict:
    """
    Run the full ingestion pipeline for one policy file.

    Args:
        file_path: path to a .pdf or .txt policy document.
        policy_name: human-readable name; defaults to the filename stem.

    Returns:
        dict summary: {policy_id, policy_name, num_pages, num_chunks}
    """
    file_path = Path(file_path)
    policy_name = policy_name or file_path.stem
    policy_id = f"{policy_name}-{uuid.uuid4().hex[:8]}"

    logger.info("Starting ingestion for '%s' (policy_id=%s)", policy_name, policy_id)

    if file_path.suffix.lower() == ".pdf":
        pages = load_pdf(file_path)
    elif file_path.suffix.lower() == ".txt":
        pages = load_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}. Use .pdf or .txt")

    if not pages:
        raise ValueError(
            f"No extractable text found in '{file_path.name}'. "
            "The file may be empty, corrupted, or a scanned image without OCR."
        )

    chunks = chunk_pages(pages, policy_name=policy_name)

    store = get_chroma_store()
    num_stored = store.add_chunks(chunks, policy_id=policy_id)

    summary = {
        "policy_id": policy_id,
        "policy_name": policy_name,
        "source_file": file_path.name,
        "num_pages": len(pages),
        "num_chunks": num_stored,
    }
    logger.info("Ingestion complete: %s", summary)
    return summary
