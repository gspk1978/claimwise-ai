"""
pii_mask.py
-----------
Lightweight, regex-based PII masking (bonus feature).

This is intentionally dependency-free (no spaCy/presidio) to keep the MVP
easy to run locally. It redacts common PII patterns from claim text before
it is logged or sent to the LLM, and can be toggled off via config.

NOTE: This is a *best-effort* demo-grade masker, not a production PII
compliance solution.
"""

import re
from typing import Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)

_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "POLICY_NUMBER": re.compile(r"\b(?:POL|POLICY)[-#]?\s?\d{4,10}\b", re.IGNORECASE),
}


def mask_pii(text: str) -> Tuple[str, int]:
    """
    Mask common PII patterns in the given text.

    Returns:
        (masked_text, number_of_redactions)
    """
    if not text:
        return text, 0

    masked = text
    total_redactions = 0

    for label, pattern in _PATTERNS.items():
        masked, count = pattern.subn(f"[REDACTED_{label}]", masked)
        total_redactions += count

    if total_redactions:
        logger.info("PII masking redacted %d item(s) from input text.", total_redactions)

    return masked, total_redactions
