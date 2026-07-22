# ClaimWise AI — Insurance Claims Copilot (MVP)

A Retrieval-Augmented Generation (RAG) demo application that helps a claims
adjuster quickly understand how an insurance policy applies to a submitted
claim — grounded strictly in the policy's own text, with explicit
guardrails against hallucination and unauthorized "final decisions."

Built to showcase a near-real GenAI/RAG architecture: **PyPDF → LangChain chunking → OpenAI embeddings → ChromaDB → LangChain
RAG chain → guardrails → structured JSON → Streamlit UI.**

> ⚠️ **Please note that this is a demo/portfolio project, not a certified claims system.**

## Additional Documentation

- [Business Overview](./BUSINESS_OVERVIEW.md) — business background, problem statement, and use cases
- [Technical Walkthrough](./TECHNICAL_WALKTHROUGH.md) — code-level flow for each use case

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [Setup Instructions](#setup-instructions)
5. [Using the App](#using-the-app)
6. [Guardrails](#guardrails)
7. [Bonus Features](#bonus-features)
8. [Testing](#testing)
9. [Design Notes / Interview Talking Points](#design-notes--interview-talking-points)

---

## Features

**Core (functional requirements):**
- Upload insurance policy PDFs (or plain text) via a Streamlit UI
- Intelligent, section-aware document chunking (detects "Section 4:
  Exclusions"-style headers before falling back to recursive splitting)
- Embedding generation via OpenAI (`text-embedding-3-small` by default)
- Persistent storage in ChromaDB, scoped per ingested policy
- Free-text claim description input
- Semantic retrieval (RAG) of the most relevant policy clauses
- LLM-generated structured output:
  - Coverage assessment
  - Relevant clauses (with citations)
  - Exclusions (with applicability reasoning)
  - Missing documents
  - Confidence score
  - Recommendation summary
- Every clause/exclusion is tagged with a `chunk_id` you can expand to see
  the exact retrieved source text (citation/grounding transparency)
- Guardrails: no final legal advice, mandatory human-review language,
  context-sufficiency gating, confidence-floor gating
- Modular architecture with separated ingestion / RAG / prompt / guardrail
  layers and centralized logging
- Bundled sample policies (auto + homeowners) and sample historical claims

**Additional Features added to showcase AI capabilities :**
- Fraud risk scoring (heuristic, LLM-based text pattern screening)
- Similar historical claims retrieval (its own Chroma collection)
- Simple multi-agent coordinator pattern (coverage / fraud / historical
  agents run and merged by a coordinator)
- LangSmith observability (opt-in via `.env`)
- Basic PII masking of claim text before processing/logging

---

## Architecture

```
                    ┌─────────────────────────┐
                    │   Streamlit UI (app.py) │
                    └───────────┬─────────────┘
                                │
         ┌──────────────────────┼───────────────────────┐
         │                                                │
 ┌───────▼────────┐                              ┌────────▼─────────┐
 │ INGESTION       │                              │ RAG / QUERY TIME  │
 │ pipeline        │                              │ pipeline           │
 │                 │                              │                   │
 │ pdf_loader.py   │                              │ retriever.py      │
 │   (PyPDF)       │                              │  (Chroma semantic │
 │        │        │                              │   search)          │
 │ chunker.py      │                              │        │           │
 │   (section-aware│                              │ chain.py           │
 │    + recursive) │                              │  (LangChain LCEL:  │
 │        │        │                              │   prompt→LLM→JSON) │
 │ embedding_       │                              │        │           │
 │ service.py      │                              │ guardrails.py      │
 │   (OpenAI embed)│                              │  (grounding checks,│
 │        │        │                              │   confidence floor)│
 │ chroma_store.py │◄─────────shared store────────►│                   │
 └─────────────────┘                              └───────────────────┘

 Bonus agents (src/bonus/): fraud_scoring.py, similar_claims.py,
 multi_agent.py (coordinator) — orchestrated from app.py
```

**Why this split?** Ingestion (write-path) and RAG (read-path) are
independent concerns with different scaling/testing needs — a common
production pattern. Prompts are isolated in `src/prompts/templates.py` so
they can be reviewed/tuned without touching orchestration code. Guardrails
are deterministic Python checks layered *on top of* prompt instructions,
because prompting alone is not reliable enough to trust for a claims-
adjacent product.

---

## Folder Structure

```
claimwise-ai/
├── app.py                        # Streamlit frontend (entry point)
├── config.py                     # Central configuration (env-driven)
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   ├── sample_policies/          # Bundled sample policy PDFs
│   ├── sample_claims/            # sample_claims.json (test data)
│   ├── uploaded_policies/        # User-uploaded PDFs land here
│   └── chroma_db/                # Persistent ChromaDB storage
├── scripts/
│   └── generate_sample_policies.py   # Regenerates the sample PDFs
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py         # PyPDF-based text extraction
│   │   ├── chunker.py            # Section-aware chunking
│   │   └── pipeline.py           # load -> chunk -> embed -> store
│   ├── embeddings/
│   │   └── embedding_service.py  # Reusable OpenAI embedding wrapper
│   ├── vectorstore/
│   │   └── chroma_store.py       # ChromaDB wrapper (LangChain Chroma)
│   ├── rag/
│   │   ├── retriever.py          # Semantic retrieval + context formatting
│   │   └── chain.py              # LCEL chain: retrieve->prompt->LLM->JSON
│   ├── prompts/
│   │   └── templates.py          # All prompt templates + JSON schemas
│   ├── guardrails/
│   │   └── guardrails.py         # Deterministic grounding/safety checks
│   ├── bonus/
│   │   ├── fraud_scoring.py      # Fraud risk triage agent
│   │   ├── similar_claims.py     # Historical claims similarity search
│   │   └── multi_agent.py        # Coordinator merging all agents
│   └── utils/
│       ├── logger.py             # Centralized logging
│       └── pii_mask.py           # Regex-based PII redaction
└── tests/
    └── test_ingestion.py         # No-API-key-required sanity tests
```

---

## Setup Instructions

- Please note that instructions use the Python i.e. 'py' as the main interpreter. This means the commands involving 'pip' or 'streamlit' etc are run with the 'py' as the interpreter. This was followed as this is the commonly recommended pattern in official Python docs specifically to avoid the interpreter-mismatch problem

### 1. Prerequisites
- Python 3.11 or 3.12
- An OpenAI API key ([platform.openai.com](https://platform.openai.com))

### 2. Clone / unzip the project and enter the folder
```bash
cd claimwise-ai
```

### 3. Create a virtual environment (recommended)
```bash
py -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
py -m pip install -r requirements.txt
```

### 5. Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and set your `OPENAI_API_KEY`. All other values have sensible
defaults for a local demo.

### 6. (Optional) Regenerate the bundled sample policy PDFs
Sample PDFs are already included under `data/sample_policies/`, but you can
regenerate them any time:
```bash
py scripts/generate_sample_policies.py
```

### 7. Run the app
```bash
streamlit run app.py
OR
py -m streamlit run app.py
```
Then open the URL Streamlit prints (typically `http://localhost:8501`).

---

## Using the App

1. **Tab "1. Upload Policy"** — upload your own policy PDF, or click
   **Ingest Sample** to load one of the bundled sample policies
   (`auto_policy_sample.pdf`, `home_policy_sample.pdf`).
2. **Tab "2. Assess a Claim"** — pick which ingested policy to search
   against (or search across all), type a claim description (or copy one
   from the sample claims in the Policy Library tab), and click
   **Assess Claim**.
3. Review the structured output: coverage assessment, cited clauses,
   exclusions, missing documents, confidence score, and recommendation —
   plus optional fraud-risk screening and similar historical claims.
4. **Tab "Policy Library"** — This tab contains what is currently indexed in ChromaDB and can
   browse bundled sample claims for quick testing.
5. **Tab "About / Guardrails"** — explains the safety mechanisms in this context, i.e. what kind of claim assessment is relavant or not.

### Try these sample claims (from `data/sample_claims/sample_claims.json`)
- *"My car was parked in my driveway during a hailstorm... hood, roof, and
  trunk have multiple dents..."* → should retrieve the Comprehensive /
  hail coverage clause from the auto policy.
- *"My teenage son borrowed my car without permission... does not have a
  driver's license..."* → should surface the unlicensed-driver exclusion.
- *"Heavy rainfall caused a nearby river to overflow, flooding our
  basement..."* → should surface the flood exclusion from the homeowners
  policy.

---

## Guardrails

| Guardrail | Where implemented | What it does |
|---|---|---|
| Grounding-only instructions | `src/prompts/templates.py` (system prompt) | Tells the LLM to use *only* retrieved context, never outside knowledge |
| Context sufficiency check | `src/guardrails/guardrails.py::check_context_sufficiency` | Blocks generation entirely if retrieval returns too little relevant text, returning a safe "insufficient context" response instead |
| Confidence floor | `src/guardrails/guardrails.py::enforce_output_guardrails` | Below `MIN_CONFIDENCE_FOR_ASSESSMENT`, adds an explicit low-confidence warning pushing toward human review |
| Citation presence check | same | Flags assessments with zero cited clauses/exclusions as low-trust |
| Mandatory disclaimer | same | Always injects "not legal advice / human review required" text, regardless of what the LLM produced |
| No final decisions | Prompt + guardrails | Prompt instructs hedged language ("appears to be covered based on retrieved excerpts") rather than definitive rulings |
| PII masking | `src/utils/pii_mask.py` | Regex-redacts emails, phone numbers, SSNs, card numbers, policy numbers from claim text before logging/processing (toggle via `ENABLE_PII_MASKING`) |

---

## Additional Features

- **Fraud risk scoring** (`src/bonus/fraud_scoring.py`): a separate LLM
  call scores textual red-flag patterns (vague timelines, high-value items
  with no documentation, etc.) — explicitly framed as a *screening signal
  for human investigators*, never a fraud accusation.
- **Similar historical claims** (`src/bonus/similar_claims.py`): a second,
  dedicated ChromaDB collection indexes `data/sample_claims/sample_claims.json`
  so a new claim can be semantically compared against past claims and their
  outcomes.
- **Multi-agent architecture** (`src/bonus/multi_agent.py`): a lightweight
  coordinator pattern runs the Coverage, Fraud Risk, and Historical Case
  agents and merges their structured outputs — demonstrating task
  decomposition into specialist roles without unnecessary framework
  overhead for an MVP.
- **LangSmith observability**: set `LANGCHAIN_TRACING_V2=true` and
  `LANGCHAIN_API_KEY` in `.env` to get full trace visibility into every
  chain/LLM call in the [LangSmith UI](https://smith.langchain.com).
- **PII masking**: see Guardrails table above.

---

## Testing

Ingestion (PDF parsing + chunking) can be tested **without an OpenAI API
key**:
```bash
python tests/test_ingestion.py
# or
pytest tests/ -v
```

Full end-to-end testing (embeddings, retrieval, LLM generation) requires a
valid `OPENAI_API_KEY` in `.env` and is best exercised through the
Streamlit UI using the bundled sample policies and sample claims.

---
