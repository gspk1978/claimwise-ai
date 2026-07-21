"""
chain.py
--------
The heart of the RAG pipeline. Builds and runs a LangChain LCEL chain that:

    claim_description -> retrieve chunks -> format context -> prompt -> LLM
        -> JSON parse -> deterministic guardrails -> final structured result

Uses LangChain's ChatOpenAI + JsonOutputParser + RunnableLambda/Runnable
composition, i.e. proper LangChain chain/retriever usage rather than raw
API calls.
"""

import json
from typing import Any, Dict, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from config import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY, RETRIEVER_TOP_K
from src.guardrails.guardrails import (
    build_insufficient_context_response,
    check_context_sufficiency,
    enforce_output_guardrails,
)
from src.prompts.templates import CLAIM_ASSESSMENT_JSON_SCHEMA, CLAIM_ASSESSMENT_PROMPT
from src.rag.retriever import format_context_for_prompt, retrieve_relevant_clauses
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENAI_API_KEY,
    )


def _build_generation_chain():
    """LCEL chain: prompt -> LLM -> JSON parser."""
    llm = _get_llm()
    parser = JsonOutputParser()
    return CLAIM_ASSESSMENT_PROMPT | llm | parser


def assess_claim(
    claim_description: str,
    policy_id: Optional[str] = None,
    top_k: int = RETRIEVER_TOP_K,
) -> Dict[str, Any]:
    """
    Run the full RAG pipeline for a claim description and return a
    guardrail-checked, structured assessment dict ready for the UI.

    This is the main entry point used by the Streamlit app.
    """
    if not claim_description or not claim_description.strip():
        raise ValueError("claim_description must not be empty")

    # 1. RETRIEVE ------------------------------------------------------
    retrieved_docs = retrieve_relevant_clauses(
        claim_description=claim_description, policy_id=policy_id, top_k=top_k
    )

    # 2. GUARDRAIL: context sufficiency check ---------------------------
    if not check_context_sufficiency(retrieved_docs):
        response = build_insufficient_context_response()
        response["retrieved_chunks"] = []
        return response

    context_text = format_context_for_prompt(retrieved_docs)

    # 3. GENERATE (grounded strictly in retrieved context) --------------
    chain = _build_generation_chain()
    try:
        raw_result = chain.invoke(
            {
                "context": context_text,
                "claim_description": claim_description,
                "schema": CLAIM_ASSESSMENT_JSON_SCHEMA,
            }
        )
    except Exception as exc:
        logger.error("LLM generation/parsing failed: %s", exc)
        raise RuntimeError(
            "The AI model failed to produce a valid structured assessment. "
            "Please retry, or escalate this claim to a human adjuster."
        ) from exc

    if isinstance(raw_result, str):
        # Defensive: some parser/model combos may still return a string.
        raw_result = json.loads(raw_result)

    # 4. GUARDRAIL: deterministic post-processing ------------------------
    final_result = enforce_output_guardrails(raw_result)

    # 5. Attach raw retrieved chunks so the UI can show citations/sources.
    final_result["retrieved_chunks"] = [
        {
            "chunk_id": doc.metadata.get("chunk_id"),
            "source": doc.metadata.get("source"),
            "page_number": doc.metadata.get("page_number"),
            "section_title": doc.metadata.get("section_title"),
            "text": doc.page_content,
        }
        for doc in retrieved_docs
    ]

    logger.info(
        "Claim assessment complete. confidence=%s, clauses=%d, exclusions=%d",
        final_result.get("confidence_score"),
        len(final_result.get("relevant_clauses", [])),
        len(final_result.get("exclusions", [])),
    )
    return final_result
