"""
app.py
------
ClaimWise AI - Streamlit MVP frontend.

Deliberately basic UI (forms + tabs, no custom styling) per project
requirements -- the focus is on demonstrating the GenAI/RAG functionality,
not visual polish.
"""

import streamlit as st

from config import OPENAI_API_KEY, SAMPLE_CLAIMS_DIR, SAMPLE_POLICIES_DIR, UPLOAD_DIR
from src.bonus.multi_agent import run_multi_agent_analysis
from src.bonus.similar_claims import seed_historical_claims
from src.ingestion.pipeline import ingest_policy_document
from src.utils.logger import get_logger
from src.utils.pii_mask import mask_pii
from config import ENABLE_PII_MASKING
from src.vectorstore.chroma_store import get_chroma_store

logger = get_logger(__name__)

st.set_page_config(page_title="ClaimWise AI", layout="wide")

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "ingested_policies" not in st.session_state:
    st.session_state.ingested_policies = {}  # policy_id -> summary dict
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("ClaimWise AI - Insurance Claims Copilot")
st.caption(
    "GenAI + RAG demo. Not legal advice. All outputs require human adjuster review."
)

if not OPENAI_API_KEY:
    st.warning(
        "OPENAI_API_KEY is not set. Add it to your `.env` file (see `.env.example`) "
        "before running ingestion or claim assessment.",
        icon="⚠️",
    )

tab_ingest, tab_claim, tab_library, tab_about = st.tabs(
    ["1. Upload Policy", "2. Assess a Claim", "Policy Library", "About / Guardrails"]
)

# ---------------------------------------------------------------------------
# TAB 1: Upload & Ingest Policy PDFs
# ---------------------------------------------------------------------------
with tab_ingest:
    st.header("Upload Insurance Policy")
    st.write(
        "Upload a policy PDF (or use a bundled sample below) to parse, chunk, "
        "embed, and store it in the vector database for retrieval."
    )

    with st.form("upload_form", clear_on_submit=False):
        uploaded_file = st.file_uploader("Policy PDF", type=["pdf", "txt"])
        policy_name_input = st.text_input(
            "Policy name (optional)", placeholder="e.g. Auto Policy - Comprehensive"
        )
        submitted = st.form_submit_button("Ingest Policy")

    if submitted:
        if not uploaded_file:
            st.error("Please choose a PDF or TXT file first.")
        else:
            save_path = UPLOAD_DIR / uploaded_file.name
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Parsing, chunking, embedding, and storing..."):
                try:
                    summary = ingest_policy_document(
                        save_path, policy_name=policy_name_input or None
                    )
                    st.session_state.ingested_policies[summary["policy_id"]] = summary
                    st.success(
                        f"Ingested '{summary['policy_name']}' -> "
                        f"{summary['num_chunks']} chunks from {summary['num_pages']} page(s)."
                    )
                except Exception as exc:
                    logger.error("Ingestion failed: %s", exc)
                    st.error(f"Ingestion failed: {exc}")

    st.divider()
    st.subheader("Or use a bundled sample policy")
    sample_files = sorted(SAMPLE_POLICIES_DIR.glob("*.pdf"))
    if not sample_files:
        st.info("No sample policies found in data/sample_policies.")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            chosen_sample = st.selectbox(
                "Sample policy", [f.name for f in sample_files], key="sample_policy_select"
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("Ingest Sample"):
                sample_path = SAMPLE_POLICIES_DIR / chosen_sample
                with st.spinner(f"Ingesting {chosen_sample}..."):
                    try:
                        summary = ingest_policy_document(sample_path)
                        st.session_state.ingested_policies[summary["policy_id"]] = summary
                        st.success(
                            f"Ingested '{summary['policy_name']}' -> "
                            f"{summary['num_chunks']} chunks."
                        )
                    except Exception as exc:
                        logger.error("Sample ingestion failed: %s", exc)
                        st.error(f"Ingestion failed: {exc}")

# ---------------------------------------------------------------------------
# TAB 2: Submit a claim and get an assessment
# ---------------------------------------------------------------------------
with tab_claim:
    st.header("Submit a Claim for Assessment")

    store = get_chroma_store()
    all_policy_ids = store.list_policy_ids()

    if not all_policy_ids:
        st.info("No policies ingested yet. Go to 'Upload Policy' tab first.")
    else:
        policy_options = ["(search across all ingested policies)"] + all_policy_ids
        selected_policy = st.selectbox("Scope retrieval to policy", policy_options)
        policy_filter = None if selected_policy == policy_options[0] else selected_policy

        with st.form("claim_form"):
            claim_text = st.text_area(
                "Claim description",
                height=180,
                placeholder=(
                    "e.g. My car was damaged in a hailstorm on June 12th while parked "
                    "in my driveway. There is significant dent damage to the hood and roof..."
                ),
            )
            col_a, col_b = st.columns(2)
            with col_a:
                run_fraud = st.checkbox("Run fraud risk screening (bonus)", value=True)
            with col_b:
                run_similar = st.checkbox("Find similar historical claims (bonus)", value=True)
            claim_submitted = st.form_submit_button("Assess Claim")

        if claim_submitted:
            if not claim_text.strip():
                st.error("Please enter a claim description.")
            else:
                display_text = claim_text
                if ENABLE_PII_MASKING:
                    masked_text, n_redacted = mask_pii(claim_text)
                    if n_redacted:
                        st.caption(f"🔒 PII masking redacted {n_redacted} item(s) before processing.")
                    display_text = masked_text

                seed_historical_claims()  # idempotent seeding of demo historical claims

                with st.spinner("Retrieving relevant clauses and generating assessment..."):
                    try:
                        result = run_multi_agent_analysis(
                            claim_description=claim_text,  # full text used for retrieval accuracy
                            policy_id=policy_filter,
                            include_fraud_check=run_fraud,
                            include_similar_claims=run_similar,
                        )
                        st.session_state.last_result = result
                    except Exception as exc:
                        logger.error("Claim assessment failed: %s", exc)
                        st.error(f"Assessment failed: {exc}")
                        st.session_state.last_result = None

    # ---------------- Render results ----------------
    if st.session_state.last_result:
        result = st.session_state.last_result
        coverage = result.get("coverage_assessment_agent", {})

        st.divider()
        st.subheader("Coverage Assessment")

        conf = coverage.get("confidence_score", 0.0)
        st.metric("Confidence Score", f"{conf:.2f}")
        if coverage.get("low_confidence_warning"):
            st.warning(coverage["low_confidence_warning"])

        st.write("**Assessment:**", coverage.get("coverage_assessment", "N/A"))
        st.write("**Recommendation Summary:**", coverage.get("recommendation_summary", "N/A"))
        st.info(coverage.get("disclaimer", ""))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Relevant Clauses**")
            clauses = coverage.get("relevant_clauses", [])
            if not clauses:
                st.write("None cited.")
            for c in clauses:
                with st.expander(f"[{c.get('chunk_id', 'unknown')}]"):
                    st.write(c.get("excerpt", ""))
                    st.caption(c.get("relevance", ""))
        with col2:
            st.markdown("**Exclusions**")
            exclusions = coverage.get("exclusions", [])
            if not exclusions:
                st.write("None cited.")
            for e in exclusions:
                with st.expander(f"[{e.get('chunk_id', 'unknown')}] applies: {e.get('applies', '?')}"):
                    st.write(e.get("excerpt", ""))
                    st.caption(e.get("reasoning", ""))

        st.markdown("**Missing Documents**")
        missing = coverage.get("missing_documents", [])
        if missing:
            for m in missing:
                st.write(f"- {m}")
        else:
            st.write("None identified.")

        with st.expander("Show raw retrieved chunks (citations / grounding source)"):
            for rc in coverage.get("retrieved_chunks", []):
                st.markdown(f"`{rc['chunk_id']}` — page {rc['page_number']} — {rc.get('section_title','')}")
                st.text(rc["text"])
                st.markdown("---")

        # Fraud risk
        if "fraud_risk_agent" in result:
            st.divider()
            st.subheader("Fraud Risk Screening (Bonus)")
            fraud = result["fraud_risk_agent"]
            if "error" in fraud:
                st.error(fraud["error"])
            else:
                st.write(f"**Risk Level:** {fraud.get('risk_level','unknown').upper()}  |  "
                         f"**Score:** {fraud.get('fraud_risk_score', 0.0)}")
                flags = fraud.get("red_flags", [])
                if flags:
                    for fl in flags:
                        st.write(f"- {fl}")
                else:
                    st.write("No notable red flags detected.")
                st.caption(fraud.get("rationale", ""))
                st.caption(fraud.get("disclaimer", ""))

        # Similar historical claims
        if "historical_case_agent" in result:
            st.divider()
            st.subheader("Similar Historical Claims (Bonus)")
            similar = result["historical_case_agent"]
            if not similar:
                st.write("No similar historical claims found.")
            for s in similar:
                with st.expander(f"{s['claim_id']} — {s.get('claim_type','')} (distance={s['similarity_distance']})"):
                    st.write(s["description"])
                    st.write(f"**Outcome:** {s.get('outcome','')}")
                    st.caption(s.get("resolution_notes", ""))

# ---------------------------------------------------------------------------
# TAB 3: Policy library / vector store status
# ---------------------------------------------------------------------------
with tab_library:
    st.header("Ingested Policy Library")
    store = get_chroma_store()
    policy_ids = store.list_policy_ids()
    st.write(f"Total chunks stored in vector DB: **{store.count()}**")
    if policy_ids:
        st.write("Ingested policy_ids:")
        for pid in policy_ids:
            st.write(f"- `{pid}`")
    else:
        st.info("No policies ingested yet.")

    st.divider()
    st.subheader("Sample claims available for testing")
    sample_claims_file = SAMPLE_CLAIMS_DIR / "sample_claims.json"
    if sample_claims_file.exists():
        import json

        with open(sample_claims_file) as f:
            claims = json.load(f)
        for c in claims:
            st.write(f"- **{c['claim_id']}** ({c.get('claim_type')}): {c['description'][:120]}...")
    else:
        st.info("No sample claims file found.")

# ---------------------------------------------------------------------------
# TAB 4: About / Guardrails explanation
# ---------------------------------------------------------------------------
with tab_about:
    st.header("About ClaimWise AI")
    st.markdown(
        """
ClaimWise AI is an MVP **Insurance Claims Copilot** built to demonstrate a
production-style Retrieval-Augmented Generation (RAG) architecture:

**Pipeline:** PDF upload → PyPDF text extraction → section-aware chunking →
OpenAI embeddings → ChromaDB vector store → semantic retrieval → LangChain
prompt/LLM chain → deterministic guardrails → structured JSON output.

### Guardrails in place
- **Grounding only:** the LLM is instructed to use *only* retrieved policy
  excerpts, never outside knowledge.
- **Context sufficiency check:** if retrieval returns too little relevant
  text, the app refuses to generate a confident assessment and asks for
  more documents instead.
- **Confidence floor:** low self-reported confidence triggers an explicit
  warning and pushes the recommendation toward human review.
- **No legal/final decisions:** every response carries a disclaimer and a
  human-adjuster-review recommendation.
- **Citations:** every clause/exclusion is tied back to a `chunk_id` you
  can expand to see the exact retrieved text.
- **PII masking (bonus):** common PII patterns are redacted before
  processing, when enabled.

This is a demo/interview project, not a certified claims-adjudication
system.
        """
    )
