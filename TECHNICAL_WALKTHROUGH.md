# ClaimWise AI — Technical Notes (Code Flow)

Quick notes on how each use case is implemented — file by file, with input
and output at each step. For the "why", see `BUSINESS_OVERVIEW.md`. For
setup, see `README.md`.

---

## 1. Policy Ingestion & Knowledge Base Creation

Triggered from `app.py` (Upload Policy tab) → `ingest_policy_document()`
in `src/ingestion/pipeline.py`.

- **`pdf_loader.py` → `load_pdf()`**
  In: PDF file path. Out: list of `RawPage` (text + page number + filename),
  using `pypdf`.
- **`chunker.py` → `chunk_pages()`**
  In: `RawPage` list. Regex first splits pages on section headers
  ("Section 4: Exclusions" etc.), then `RecursiveCharacterTextSplitter`
  breaks up anything still too big. Out: list of `PolicyChunk`, each with a
  `chunk_id`, source, page, section title.
- **`embedding_service.py`**
  Wraps `OpenAIEmbeddings` — not called directly, passed into Chroma as the
  embedding function.
- **`chroma_store.py` → `add_chunks()`**
  In: `PolicyChunk` list + a generated `policy_id`. Converts to LangChain
  `Document`s, embeds + persists them in ChromaDB (`data/chroma_db/`).

`pipeline.py` returns a summary dict (policy_id, num_chunks, etc.) that
`app.py` shows as a success message and stores in session state.

---

## 2. Coverage Assessment for a Submitted Claim

Triggered from `app.py` (Assess Claim tab) → `run_multi_agent_analysis()`
→ `assess_claim()` in `src/rag/chain.py`.

- **`retriever.py` → `retrieve_relevant_clauses()`**
  In: claim text + optional policy_id filter. Out: top-k similar
  `Document` chunks from Chroma (default k=5).
- **`guardrails.py` → `check_context_sufficiency()`**
  In: retrieved chunks. Out: bool — if False, pipeline stops and returns a
  canned "insufficient context" response instead of calling the LLM.
- **`retriever.py` → `format_context_for_prompt()`**
  In: retrieved chunks. Out: text block with each chunk labeled by
  chunk_id/source/page — this is what the LLM actually sees.
- **`templates.py` + `chain.py`**
  Prompt (`CLAIM_ASSESSMENT_PROMPT`) + formatted context + claim text →
  `ChatOpenAI` → `JsonOutputParser`. Out: raw JSON dict matching
  `CLAIM_ASSESSMENT_JSON_SCHEMA`.
- **`guardrails.py` → `enforce_output_guardrails()`**
  In: raw JSON. Out: same dict with disclaimer/confidence/warnings applied
  (details in section 5).

`chain.py` attaches the raw retrieved chunks to the result before
returning, so `app.py` has both the LLM's answer and the source text to
display.

---

## 3. Exclusion Identification

No separate retrieval step — rides on the same call as #2.

- `templates.py`'s JSON schema has an `exclusions` array (chunk_id,
  excerpt, applies: yes/no/unclear, reasoning).
- Because retrieval in #2 pulls whatever's semantically closest to the
  whole claim text, exclusion clauses (e.g. "unlicensed driver exclusion")
  get retrieved automatically when relevant — they're just chunks like any
  other, kept intact as their own section by `chunker.py`.
- `app.py` renders `exclusions` in its own column, separate from
  `relevant_clauses`.

---

## 4. Missing Documentation Detection

Also rides on the same call as #2 — just another field in the schema.

- `templates.py` schema includes `missing_documents` (plain string list).
  Prompt tells the model to compare the claim description against what the
  retrieved policy text requires (policies include a "Required
  Documentation" section — see `scripts/generate_sample_policies.py`).
- Fallback: if guardrails block generation entirely (#5), `missing_documents`
  still gets a generic placeholder so the field is never empty.
- Rendered as a bullet list in `app.py`.

---

## 5. Confidence-Scored, Human-Review-First Output

Mostly `src/guardrails/guardrails.py`, called from `chain.py` after the
LLM step.

- Prompt-level: `templates.py`'s `SYSTEM_GUARDRAILS` asks for hedged
  language and human-review mentions (soft guardrail, not guaranteed).
- `check_context_sufficiency()` — runs before the LLM call; blocks
  generation if retrieval is too thin.
- `enforce_output_guardrails()` — runs after the LLM call:
  - Overwrites `disclaimer` with fixed text regardless of model output.
  - Clamps `confidence_score` to [0.0, 1.0].
  - Below `MIN_CONFIDENCE_FOR_ASSESSMENT` → adds `low_confidence_warning`.
  - No cited clauses/exclusions → appends a warning about that too.
  - No "human"/"adjuster" mention in the summary → appends one.

In: raw LLM JSON. Out: same dict, guaranteed to carry a disclaimer and
(where warranted) explicit low-confidence flags. `app.py` shows
`confidence_score` as a metric and `low_confidence_warning` as a warning
box above the assessment.

---

## 6. Similar Historical Claims Lookup (Bonus)

`src/bonus/similar_claims.py`, called via `multi_agent.py`.

- Separate Chroma collection (`claimwise_historical_claims`), kept apart
  from policy chunks.
- `seed_historical_claims()` — in: nothing (reads
  `data/sample_claims/sample_claims.json`); out: indexes claims once,
  skips if already seeded (checked via collection count).
- `find_similar_claims()` — in: new claim text, top_k=3; out: similar past
  claims with outcome + resolution_notes + similarity distance.
- `multi_agent.py` merges this under `historical_case_agent` in the final
  response; `app.py` renders each as an expandable card.

---

## 7. Auditable Citations

Threaded through the whole pipeline rather than a standalone feature.

- `chunker.py` assigns each chunk a `chunk_id`
  (`policy_name::pPAGE::cINDEX`) at ingestion time, along with source,
  page, section.
- `chroma_store.py` stores those fields as metadata and uses `chunk_id` as
  the literal Chroma document ID.
- `retriever.py::format_context_for_prompt()` prints chunk_id/source/page
  as a visible header above each chunk's text in the prompt, so the model
  can reference the right ID.
- `templates.py` requires `chunk_id` on every entry in `relevant_clauses`
  and `exclusions`.
- `chain.py` attaches the full, unedited retrieved chunk text (not the
  model's paraphrase) to the result as `retrieved_chunks`.
- `app.py` shows these in an expandable "raw retrieved chunks" section so
  you can check the AI's claim against the actual source text.

---

## Quick File Reference

| Use case | Primary file(s) |
|---|---|
| Policy Ingestion & Knowledge Base Creation | `src/ingestion/pdf_loader.py`, `src/ingestion/chunker.py`, `src/embeddings/embedding_service.py`, `src/vectorstore/chroma_store.py`, `src/ingestion/pipeline.py` |
| Coverage Assessment | `src/rag/retriever.py`, `src/rag/chain.py`, `src/prompts/templates.py` |
| Exclusion Identification | `src/prompts/templates.py` (schema), `src/rag/chain.py` (same call as coverage) |
| Missing Documentation Detection | `src/prompts/templates.py` (schema), `src/guardrails/guardrails.py` (fallback case) |
| Confidence-Scored, Human-Review-First Output | `src/guardrails/guardrails.py`, `src/rag/chain.py` |
| Similar Historical Claims Lookup | `src/bonus/similar_claims.py`, `src/bonus/multi_agent.py` |
| Auditable Citations | `src/ingestion/chunker.py`, `src/vectorstore/chroma_store.py`, `src/rag/retriever.py`, `src/prompts/templates.py`, `src/rag/chain.py` |
