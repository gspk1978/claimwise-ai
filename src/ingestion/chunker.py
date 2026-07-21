"""
chunker.py
----------
Intelligent chunking for insurance policy documents.

Strategy:
1. Try to detect natural clause/section boundaries (e.g. "Section 4:",
   "4.1 Exclusions", "ARTICLE III") using regex, so a clause is rarely
   split mid-thought.
2. Any section still too large is further split using LangChain's
   RecursiveCharacterTextSplitter, which respects paragraph/sentence
   boundaries as much as possible.
3. Every resulting chunk keeps metadata: source file, page number,
   detected section title, and a chunk_id used for citations.
"""

import re
from dataclasses import dataclass, field
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE
from src.ingestion.pdf_loader import RawPage
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Matches common policy section headers, e.g.:
#   "Section 4: Exclusions", "4.1 Covered Perils", "ARTICLE III - CLAIMS"
_SECTION_HEADER_RE = re.compile(
    r"(?im)^\s*(?:(?:section|article|clause)\s+[\dIVXLC]+[:.\-]?.*|"
    r"\d{1,2}(?:\.\d{1,2})?\s+[A-Z][A-Za-z /&\-]{3,60}\s*$)"
)


@dataclass
class PolicyChunk:
    text: str
    source: str
    page_number: int
    section_title: str = ""
    chunk_id: str = field(default="")


def _detect_sections(page_text: str) -> List[tuple]:
    """Split page text into (section_title, section_body) tuples using header regex."""
    matches = list(_SECTION_HEADER_RE.finditer(page_text))
    if not matches:
        return [("", page_text)]

    sections = []
    for i, match in enumerate(matches):
        title = match.group().strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
        body = page_text[start:end].strip()
        if body:
            sections.append((title, body))

    # Capture any preamble text before the first detected header
    if matches[0].start() > 0:
        preamble = page_text[: matches[0].start()].strip()
        if preamble:
            sections.insert(0, ("", preamble))

    return sections


def chunk_pages(pages: List[RawPage], policy_name: str) -> List[PolicyChunk]:
    """
    Convert raw pages into citation-ready PolicyChunk objects.

    Args:
        pages: output of pdf_loader.load_pdf / load_text_file
        policy_name: logical name of the policy document (used in chunk_id)

    Returns:
        List of PolicyChunk with overlapping, section-aware text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: List[PolicyChunk] = []
    running_index = 0

    for page in pages:
        sections = _detect_sections(page.text)

        for section_title, section_body in sections:
            if len(section_body) <= CHUNK_SIZE:
                sub_texts = [section_body]
            else:
                sub_texts = splitter.split_text(section_body)

            for sub_text in sub_texts:
                sub_text = sub_text.strip()
                if not sub_text:
                    continue
                running_index += 1
                chunk_id = f"{policy_name}::p{page.page_number}::c{running_index}"
                chunks.append(
                    PolicyChunk(
                        text=sub_text,
                        source=page.source,
                        page_number=page.page_number,
                        section_title=section_title,
                        chunk_id=chunk_id,
                    )
                )

    logger.info(
        "Chunked '%s' into %d chunk(s) across %d page(s).",
        policy_name,
        len(chunks),
        len(pages),
    )
    return chunks
