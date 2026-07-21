"""
config.py
---------
Central configuration for ClaimWise AI.
All tunable parameters live here so the rest of the codebase never
hardcodes magic strings/numbers. Values are pulled from environment
variables (see .env.example) with sane defaults for local demos.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from a local .env file if present
load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_POLICIES_DIR = DATA_DIR / "sample_policies"
SAMPLE_CLAIMS_DIR = DATA_DIR / "sample_claims"
CHROMA_PERSIST_DIR = str(DATA_DIR / "chroma_db")
UPLOAD_DIR = DATA_DIR / "uploaded_policies"
LOG_DIR = BASE_DIR / "logs"

for _dir in (DATA_DIR, SAMPLE_POLICIES_DIR, SAMPLE_CLAIMS_DIR, UPLOAD_DIR, LOG_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# OpenAI / LLM configuration
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

# ---------------------------------------------------------------------------
# Chunking configuration
# ---------------------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ---------------------------------------------------------------------------
# Retrieval configuration
# ---------------------------------------------------------------------------
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "5"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "claimwise_policies")

# ---------------------------------------------------------------------------
# LangSmith observability (optional, bonus feature)
# ---------------------------------------------------------------------------
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "claimwise-ai")

if LANGCHAIN_TRACING_V2.lower() == "true" and LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

# ---------------------------------------------------------------------------
# Guardrail / confidence thresholds
# ---------------------------------------------------------------------------
MIN_CONFIDENCE_FOR_ASSESSMENT = float(os.getenv("MIN_CONFIDENCE_FOR_ASSESSMENT", "0.35"))
LOW_CONTEXT_CHAR_THRESHOLD = int(os.getenv("LOW_CONTEXT_CHAR_THRESHOLD", "200"))

# ---------------------------------------------------------------------------
# PII masking toggle (bonus feature)
# ---------------------------------------------------------------------------
ENABLE_PII_MASKING = os.getenv("ENABLE_PII_MASKING", "true").lower() == "true"
