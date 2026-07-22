# ClaimWise AI — Business Overview & Use Cases

## 1. Business Background

Insurance claims processing is one of the most document-heavy, time-sensitive
workflows in the insurance industry. Every claim requires an adjuster to
cross-reference a claim description against a policy document that is often
20–100+ pages long, written in dense legal/technical language, and organized
inconsistently across insurers and product lines (auto, home, health, etc.).

Industry research consistently points to the same operational pain points:

- **Time-consuming manual review.** Adjusters spend a significant share of
  their day reading policy documents line-by-line to determine whether a
  clause applies, whether an exclusion is triggered, and what documentation
  is still missing — work that scales linearly with claim volume.
- **Inconsistent first-pass triage.** Two adjusters reviewing the same claim
  can reach different preliminary conclusions depending on experience level,
  fatigue, or how familiar they are with a specific policy's wording.
- **Slow claim cycle times hurt customer satisfaction.** Policyholders
  routinely cite claim resolution speed and transparency as top drivers of
  satisfaction (or complaint volume) with an insurer.
- **Fraud leakage.** Industry estimates put fraudulent or exaggerated claims
  at a meaningful percentage of total claims paid annually, but manual
  fraud screening is inconsistent unless flagged by an experienced
  investigator.
- **Growing claim complexity.** Multi-peril policies, endorsements, and
  regional regulatory riders make it harder for any single adjuster to hold
  an entire policy's nuances in their head.

These pain points create a clear opening for a **generative AI copilot** —
not to replace adjuster judgment or issue binding decisions, but to
**accelerate the first-pass read of a policy against a claim**, surface the
exact clauses that matter, and flag what's missing — while keeping a human
firmly in the loop for every final decision.

---

## 2. Problem Statement

> **How cab we help claims adjusters go from "claim submitted" to "informed
> first-pass understanding of coverage" in minutes instead of hours — without
> introducing hallucinated or unsupported coverage conclusions?**

Any AI system operating in this space carries real risk if it:
- Invents policy terms that don't exist in the actual document,
- Presents a probabilistic language-model output as a definitive legal or
  financial decision, or
- Omits the exclusions/limitations that would have changed the outcome.

ClaimWise AI is aimed around **grounding and restraint** as first-class
requirements, not afterthoughts — every conclusion must be traceable to a
specific passage in the uploaded policy, and every output is explicitly
framed as a preliminary, human-reviewable analysis.

---

## 3. Who This Is For (Primary Personas)

| Persona | How they'd use ClaimWise AI |
|---|---|
| **Claims Adjuster** | Uploads the relevant policy, pastes in the claim description, and gets a first-pass coverage read with cited clauses/exclusions before doing their own full review — cutting down initial research time. |
| **Claims Team Lead / QA Reviewer** | Uses the confidence score and cited clauses as a consistency check across adjusters handling similar claim types. |
| **Special Investigations Unit (SIU) Analyst** | Uses the fraud risk screening and similar-historical-claims features as an early triage signal on which claims to prioritize for deeper investigation. |
| **New/Junior Adjuster** | Uses the tool as a guided way to learn how to navigate a new or unfamiliar policy document quickly. |
| **Product/Engineering teams evaluating GenAI for claims** | Uses this MVP as a reference architecture for what a grounded, guardrailed RAG system in a regulated-adjacent domain can look like. |

---

## 4. Use Cases Handled

### 4.1 Policy Ingestion & Knowledge Base Creation
- Upload any insurance policy PDF (auto, home, health, or other lines) and
  have it automatically parsed, split into meaningful clause-level chunks,
  embedded, and stored for retrieval — turning a static PDF into a
  queryable knowledge base in seconds.
- Supports maintaining multiple policies in the same session and scoping a
  claim's search to one specific policy or searching across all ingested
  policies.

### 4.2 Coverage Assessment for a Submitted Claim
- Adjuster enters a free-text claim description (e.g., "hail damage to my
  car's hood and roof while parked in my driveway").
- The system retrieves the most semantically relevant clauses from the
  policy — not just keyword matches, but conceptually related language
  (e.g., a claim about "hail dents" correctly surfaces a "Comprehensive
  Coverage" clause that never uses the word "hail damage" etc).
- Produces a structured, cited assessment: does this appear covered,
  partially covered, or likely excluded — and why, in the policy's own
  language.

### 4.3 Exclusion Identification
- Explicitly surfaces exclusion clauses that may apply to the claim (e.g.,
  unlicensed-driver exclusions, flood exclusions, cosmetic-procedure
  exclusions) so an adjuster doesn't have to manually search the entire
  document for disqualifying language.

### 4.4 Missing Documentation Detection
- Flags what documentation the policy requires to fully process the claim
  type described (e.g., police report for theft, contractor estimate for
  structural damage) — helping front-load document requests to the
  policyholder instead of a multi-round back-and-forth.

### 4.5 Confidence-Scored, Human-Review-First Output
- Every assessment carries a confidence score reflecting how well the
  retrieved policy text actually supports the conclusion.
- Low-confidence or low-context situations are explicitly flagged, and the
  system will refuse to produce a confident-sounding answer if the
  uploaded policy simply doesn't contain relevant text — reducing the risk
  of an adjuster over-trusting a thin or unsupported answer.
- Every output — regardless of confidence — carries a mandatory reminder
  that a licensed human adjuster must make the final call.

### 4.6 Similar Historical Claims Lookup
- Semantically searches a bank of past claims and their resolutions to
  show an adjuster "here's how a similar claim was handled before and what
  the outcome was" — useful for consistency and precedent-awareness.

### 4.7 Auditable Citations
- Every clause and exclusion referenced in an assessment links back to the
  exact retrieved passage (with source document, page number, and section)
  so an adjuster — or a compliance reviewer — can verify the AI's
  reasoning against the source text in seconds rather than re-reading the
  whole policy.