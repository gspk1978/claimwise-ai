"""
embedding_service.py
---------------------
Reusable embedding service. Wraps LangChain's OpenAIEmbeddings so the rest
of the app never talks to the OpenAI SDK directly. Centralizing this makes
it trivial to swap embedding providers/models later (e.g. local
sentence-transformers) without touching ingestion or RAG code.
"""

from functools import lru_cache
from typing import List

from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_MODEL, OPENAI_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Thin, cached wrapper around the embedding model used across the app."""

    def __init__(self, model: str = EMBEDDING_MODEL, api_key: str = OPENAI_API_KEY):
        if not api_key:
            logger.warning(
                "OPENAI_API_KEY is not set. Embedding calls will fail until it is configured."
            )
        self._model_name = model
        self._embeddings = OpenAIEmbeddings(model=model, api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model_name

    def get_langchain_embeddings(self) -> OpenAIEmbeddings:
        """Return the underlying LangChain embeddings object (for use by ChromaDB)."""
        return self._embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.info("Embedding %d document chunk(s) with model '%s'.", len(texts), self._model_name)
        return self._embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Singleton accessor so we don't re-instantiate the client repeatedly."""
    return EmbeddingService()
