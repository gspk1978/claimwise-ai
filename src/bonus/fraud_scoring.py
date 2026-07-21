"""
fraud_scoring.py
-----------------
BONUS FEATURE: Fraud risk scoring.

Produces a heuristic, text-pattern-based fraud risk signal for a claim
description. This is explicitly framed as a screening aid for human
investigators -- never a fraud determination -- consistent with the app's
guardrail philosophy.
"""

from typing import Any, Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from config import LLM_MODEL, OPENAI_API_KEY
from src.prompts.templates import FRAUD_SCORING_PROMPT, FRAUD_SCORING_SCHEMA
from src.utils.logger import get_logger

logger = get_logger(__name__)


def score_fraud_risk(claim_description: str) -> Dict[str, Any]:
    """Run the fraud-risk triage chain over a claim description."""
    if not claim_description or not claim_description.strip():
        raise ValueError("claim_description must not be empty")

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0.0, api_key=OPENAI_API_KEY)
    parser = JsonOutputParser()
    chain = FRAUD_SCORING_PROMPT | llm | parser

    try:
        result = chain.invoke(
            {"claim_description": claim_description, "schema": FRAUD_SCORING_SCHEMA}
        )
    except Exception as exc:
        logger.error("Fraud scoring failed: %s", exc)
        return {
            "fraud_risk_score": 0.0,
            "risk_level": "unknown",
            "red_flags": [],
            "rationale": "Fraud scoring could not be completed due to a system error.",
            "disclaimer": (
                "This is a heuristic AI screening signal only, not a fraud determination. "
                "Requires human investigator review."
            ),
        }

    # Clamp score defensively
    try:
        score = max(0.0, min(1.0, float(result.get("fraud_risk_score", 0.0))))
    except (TypeError, ValueError):
        score = 0.0
    result["fraud_risk_score"] = round(score, 2)

    logger.info("Fraud risk score computed: %.2f (%s)", score, result.get("risk_level"))
    return result
