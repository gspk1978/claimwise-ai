"""
chroma_store.py
----------------
Wrapper around a persistent ChromaDB collection used to store policy chunk
embeddings and retrieve them via similarity search. Uses LangChain's Chroma
integration so it plugs directly into LangChain retrievers/chains.
"""

from functools import lru_cache
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.embeddings.embedding_service import get_embedding_service
from src.ingestion.chunker import PolicyChunk
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaStore:
    """Manages a single persistent Chroma collection for policy chunks."""

    def __init__(
        self,
        collection_name: str = CHROMA_COLLECTION_NAME,
        persist_directory: str = CHROMA_PERSIST_DIR,
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._embedding_service = get_embedding_service()
        self._store = Chroma(
            collection_name=collection_name,
            embedding_function=self._embedding_service.get_langchain_embeddings(),
            persist_directory=persist_directory,
        )

    def add_chunks(self, chunks: List[PolicyChunk], policy_id: str) -> int:
        """
        Embed and persist a list of PolicyChunk objects, tagging each with
        a policy_id so retrieval can optionally be scoped to one policy.
        """
        if not chunks:
            logger.warning("add_chunks called with an empty chunk list; nothing to store.")
            return 0

        documents = [
            Document(
                page_content=chunk.text,
                metadata={
                    "source": chunk.source,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "chunk_id": chunk.chunk_id,
                    "policy_id": policy_id,
                },
            )
            for chunk in chunks
        ]
        ids = [chunk.chunk_id for chunk in chunks]

        self._store.add_documents(documents=documents, ids=ids)
        logger.info(
            "Stored %d chunk(s) for policy_id='%s' in collection '%s'.",
            len(documents),
            policy_id,
            self.collection_name,
        )
        return len(documents)

    def as_retriever(self, top_k: int, policy_id: Optional[str] = None):
        """Return a LangChain retriever, optionally filtered to one policy_id."""
        search_kwargs = {"k": top_k}
        if policy_id:
            search_kwargs["filter"] = {"policy_id": policy_id}
        return self._store.as_retriever(search_kwargs=search_kwargs)

    def similarity_search_with_score(self, query: str, k: int = 5, policy_id: Optional[str] = None):
        filter_dict = {"policy_id": policy_id} if policy_id else None
        return self._store.similarity_search_with_score(query, k=k, filter=filter_dict)

    def list_policy_ids(self) -> List[str]:
        """Return the distinct policy_id values currently stored (for the UI dropdown)."""
        try:
            raw = self._store.get(include=["metadatas"])
            ids = {m.get("policy_id") for m in raw.get("metadatas", []) if m.get("policy_id")}
            return sorted(ids)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to list policy ids: %s", exc)
            return []

    def count(self) -> int:
        try:
            return self._store._collection.count()
        except Exception:  # pragma: no cover
            return 0


@lru_cache(maxsize=1)
def get_chroma_store() -> ChromaStore:
    """Singleton accessor for the Chroma store."""
    return ChromaStore()
