"""
guardrails.py
-------------
Runtime (post-hoc) guardrails that sit on top of prompt-level instructions.
Prompting alone is not reliable enough for a claims-adjacent product, so we
add deterministic checks here:

1. Context sufficiency check -- refuse to produce a confident assessment if
   retrieval returned too little/irrelevant context (prevents hallucination
   when the uploaded policy simply doesn't cover the topic).
2. Confidence floor -- if the LLM's self-reported confidence is below a
   threshold, we force the recommendation to lean on human review.
3. Disclaimer enforcement -- guarantees the "not legal advice / human
   review required" language is always present, even if the model forgets.
4. Citation presence check -- flags assessments that cite no chunk_ids as
   low-trust output.
"""

from typing import Any, Dict, List

from config import LOW_CONTEXT_CHAR_THRESHOLD, MIN_CONFIDENCE_FOR_ASSESSMENT
from src.utils.logger import get_logger

logger = get_logger(__name__)

MANDATORY_DISCLAIMER = (
    "This is an AI-generated preliminary analysis, not legal or financial advice. "
    "A licensed claims adjuster must review this claim before any final decision."
)

INSUFFICIENT_CONTEXT_MESSAGE = (
    "The uploaded policy document(s) do not appear to contain enough relevant "
    "information to assess this claim. Please upload the applicable policy or "
    "escalate directly to a human claims adjuster."
)


def check_context_sufficiency(retrieved_chunks: List[Any]) -> bool:
    """Return True if retrieved context is substantial enough to reason over."""
    total_chars = sum(len(getattr(c, "page_content", "")) for c in retrieved_chunks)
    sufficient = len(retrieved_chunks) > 0 and total_chars >= LOW_CONTEXT_CHAR_THRESHOLD
    if not sufficient:
        logger.warning(
            "Context sufficiency check FAILED (chunks=%d, chars=%d, threshold=%d).",
            len(retrieved_chunks),
            total_chars,
            LOW_CONTEXT_CHAR_THRESHOLD,
        )
    return sufficient


def enforce_output_guardrails(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply deterministic post-processing guardrails to a parsed LLM assessment.
    Mutates and returns the result dict with guarantees applied.
    """
    # 1. Always enforce the disclaimer text, regardless of what the model produced.
    result["disclaimer"] = MANDATORY_DISCLAIMER

    # 2. Clamp / validate confidence score.
    try:
        confidence = float(result.get("confidence_score", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    result["confidence_score"] = round(confidence, 2)

    # 3. Confidence floor -> nudge recommendation toward human review.
    if confidence < MIN_CONFIDENCE_FOR_ASSESSMENT:
        result["low_confidence_warning"] = (
            f"Confidence score ({confidence:.2f}) is below the trust threshold "
            f"({MIN_CONFIDENCE_FOR_ASSESSMENT}). Treat this assessment as indicative "
            "only and prioritize human review."
        )
        logger.warning("Low-confidence assessment produced: score=%.2f", confidence)

    # 4. Citation presence check.
    relevant_clauses = result.get("relevant_clauses") or []
    exclusions = result.get("exclusions") or []
    if not relevant_clauses and not exclusions:
        result.setdefault("low_confidence_warning", "")
        result["low_confidence_warning"] += (
            " No specific policy clauses were cited; this assessment may be "
            "unreliable and requires manual verification."
        )
        logger.warning("Assessment produced with zero cited clauses/exclusions.")

    # 5. Always guarantee 'human review' language appears in the summary.
    summary = result.get("recommendation_summary", "") or ""
    if "human" not in summary.lower() and "adjuster" not in summary.lower():
        summary = summary.rstrip(". ") + ". A licensed human adjuster should review this claim before any final decision."
        result["recommendation_summary"] = summary

    return result


def build_insufficient_context_response() -> Dict[str, Any]:
    """Standard structured response returned when guardrails block generation."""
    return {
        "coverage_assessment": "Indeterminate -- insufficient retrieved context.",
        "relevant_clauses": [],
        "exclusions": [],
        "missing_documents": ["Applicable policy document covering this claim type."],
        "confidence_score": 0.0,
        "recommendation_summary": INSUFFICIENT_CONTEXT_MESSAGE,
        "disclaimer": MANDATORY_DISCLAIMER,
        "low_confidence_warning": INSUFFICIENT_CONTEXT_MESSAGE,
    }
