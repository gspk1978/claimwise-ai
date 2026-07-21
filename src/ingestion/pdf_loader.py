"""
pdf_loader.py
-------------
Handles parsing of insurance policy PDFs into raw page-level text using
PyPDF (pypdf). Keeps per-page metadata (source filename, page number) so
downstream chunks can carry citation information.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

from pypdf import PdfReader

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RawPage:
    """A single page of extracted text plus provenance metadata."""

    text: str
    page_number: int  # 1-indexed
    source: str  # filename


def load_pdf(file_path: Union[str, Path]) -> List[RawPage]:
    """
    Extract text from every page of a PDF file.

    Args:
        file_path: path to a .pdf file on disk.

    Returns:
        List of RawPage objects (one per page with non-empty text).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    logger.info("Loading PDF: %s", file_path.name)
    reader = PdfReader(str(file_path))

    pages: List[RawPage] = []
    for idx, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to extract page %d of %s: %s", idx, file_path.name, exc)
            text = ""

        text = text.strip()
        if text:
            pages.append(RawPage(text=text, page_number=idx, source=file_path.name))

    logger.info("Extracted %d non-empty page(s) from %s", len(pages), file_path.name)
    if not pages:
        logger.warning(
            "No extractable text found in %s. It may be a scanned/image-only PDF.",
            file_path.name,
        )
    return pages


def load_text_file(file_path: Union[str, Path]) -> List[RawPage]:
    """
    Load a plain-text policy file (.txt) as a single 'page'.
    Useful for sample data authored as text rather than PDF.
    """
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [RawPage(text=text, page_number=1, source=file_path.name)]
