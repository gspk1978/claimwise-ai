"""
multi_agent.py
---------------
BONUS FEATURE: Multi-agent architecture.

A lightweight "coordinator" pattern (no heavyweight agent framework needed
for an MVP): three specialized agents each own one concern, and a
coordinator function runs them and merges results. This demonstrates the
multi-agent concept -- decomposition of a task into specialist roles --
without adding unnecessary complexity to a demo project.

Agents:
    1. CoverageAgent      -> RAG-grounded coverage assessment (src.rag.chain)
    2. FraudRiskAgent      -> heuristic fraud-risk triage (src.bonus.fraud_scoring)
    3. HistoricalCaseAgent -> similar past claims lookup (src.bonus.similar_claims)
"""

from typing import Any, Dict, Optional

from src.bonus.fraud_scoring import score_fraud_risk
from src.bonus.similar_claims import find_similar_claims
from src.rag.chain import assess_claim
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_multi_agent_analysis(
    claim_description: str,
    policy_id: Optional[str] = None,
    include_fraud_check: bool = True,
    include_similar_claims: bool = True,
) -> Dict[str, Any]:
    """
    Coordinator: runs the specialist agents relevant to a claim and merges
    their outputs into a single response consumed by the Streamlit UI.
    """
    logger.info("Multi-agent coordinator starting for claim.")

    # Agent 1: Coverage assessment (core, always runs)
    coverage_result = assess_claim(claim_description=claim_description, policy_id=policy_id)

    result: Dict[str, Any] = {"coverage_assessment_agent": coverage_result}

    # Agent 2: Fraud risk triage
    if include_fraud_check:
        try:
            result["fraud_risk_agent"] = score_fraud_risk(claim_description)
        except Exception as exc:
            logger.error("Fraud risk agent failed: %s", exc)
            result["fraud_risk_agent"] = {"error": str(exc)}

    # Agent 3: Historical similar-claims lookup
    if include_similar_claims:
        try:
            result["historical_case_agent"] = find_similar_claims(claim_description)
        except Exception as exc:
            logger.error("Historical case agent failed: %s", exc)
            result["historical_case_agent"] = []

    logger.info("Multi-agent coordinator finished.")
    return result
