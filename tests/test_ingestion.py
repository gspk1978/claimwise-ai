"""
test_ingestion.py
------------------
Lightweight sanity tests for the ingestion pipeline that do NOT require an
OpenAI API key (PDF parsing + chunking only -- no embeddings). Run with:

    pytest tests/test_ingestion.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.chunker import chunk_pages
from src.ingestion.pdf_loader import load_pdf

SAMPLE_POLICY = Path(__file__).resolve().parent.parent / "data" / "sample_policies" / "auto_policy_sample.pdf"


def test_load_pdf_extracts_pages():
    pages = load_pdf(SAMPLE_POLICY)
    assert len(pages) > 0
    assert all(p.text for p in pages)
    assert pages[0].source == "auto_policy_sample.pdf"


def test_chunker_produces_chunks_with_metadata():
    pages = load_pdf(SAMPLE_POLICY)
    chunks = chunk_pages(pages, policy_name="auto_policy_sample")

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.chunk_id
        assert chunk.text
        assert chunk.page_number >= 1


def test_chunker_detects_known_sections():
    pages = load_pdf(SAMPLE_POLICY)
    chunks = chunk_pages(pages, policy_name="auto_policy_sample")
    section_titles = {c.section_title for c in chunks if c.section_title}

    assert any("Exclusions" in title for title in section_titles)


if __name__ == "__main__":
    test_load_pdf_extracts_pages()
    test_chunker_produces_chunks_with_metadata()
    test_chunker_detects_known_sections()
    print("All ingestion tests passed.")
