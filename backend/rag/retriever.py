"""
SAHAYAK-AI Hybrid Retriever

Combines lexical (metadata) filtering with semantic search and reranking.
"""

from typing import Any, Dict, List, Optional

import structlog

from agents.state import RetrievedChunk
from rag.embedder import get_embedder, embed_query
from rag.vector_store import get_chroma_client, get_or_create_collection, query_collection
from rag.reranker import get_reranker, rerank_documents
from config import settings

logger = structlog.get_logger(__name__)


class HybridRetriever:
    """
    Hybrid retriever combining:
    1. Lexical pre-filter using metadata
    2. Dense semantic search using FastEmbed
    3. Cross-encoder reranking
    """

    def __init__(self):
        """Initialize the hybrid retriever."""
        self._chroma_client = None
        self._collection = None
        self._embedder = None
        self._reranker = None

    @property
    def chroma_client(self):
        """Lazy-load ChromaDB client."""
        if self._chroma_client is None:
            self._chroma_client = get_chroma_client()
        return self._chroma_client

    @property
    def collection(self):
        """Lazy-load ChromaDB collection."""
        if self._collection is None:
            self._collection = get_or_create_collection(self.chroma_client)
        return self._collection

    @property
    def embedder(self):
        """Lazy-load embedder."""
        if self._embedder is None:
            self._embedder = get_embedder()
        return self._embedder

    @property
    def reranker(self):
        """Lazy-load reranker."""
        if self._reranker is None:
            self._reranker = get_reranker()
        return self._reranker

    def _build_where_filter(
        self,
        hazard_type: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build metadata filter for ChromaDB.

        Args:
            hazard_type: Hazard type filter
            state: State name filter

        Returns:
            Dict for ChromaDB where clause
        """
        filters = {}

        if hazard_type and hazard_type != "UNKNOWN":
            filters["hazard_type"] = hazard_type

        if state:
            filters["state"] = {"$eq": state}

        return filters

    async def retrieve(
        self,
        query: str,
        hazard_type: Optional[str] = None,
        state: Optional[str] = None,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:
        """
        Perform hybrid retrieval.

        Args:
            query: Semantic query for retrieval
            hazard_type: Hazard type for metadata filter
            state: State name for metadata filter
            top_k: Number of final results to return

        Returns:
            List of RetrievedChunk objects
        """
        logger.info(
            "retrieval_started",
            query=query,
            hazard_type=hazard_type,
            state=state,
            top_k=top_k,
        )

        # Stage 1: Generate query embedding
        query_embedding = embed_query(query)

        # Stage 2: Lexical pre-filter
        where_filter = self._build_where_filter(hazard_type, state)

        # Stage 3: Semantic search (get more results for reranking)
        search_results = query_collection(
            self.collection,
            query_embeddings=[query_embedding],
            n_results=min(top_k * 2, 10),  # Get more for reranking
            where=where_filter if where_filter else None,
        )

        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]
        distances = search_results.get("distances", [[]])[0]

        if not documents:
            logger.warning(
                "retrieval_no_results",
                query=query,
                hazard_type=hazard_type,
            )
            return []

        # Stage 4: Cross-encoder reranking
        reranked_indices = rerank_documents(
            query=query,
            documents=documents,
            top_k=top_k,
        )

        # Build results
        results = []
        for idx, score in reranked_indices:
            if idx < len(documents):
                # Convert distance to relevance score (1 - distance)
                relevance = 1.0 - distances[idx] if idx < len(distances) else score

                chunk = RetrievedChunk(
                    content=documents[idx],
                    source=metadatas[idx].get("source", "unknown")
                    if metadatas[idx]
                    else "unknown",
                    relevance_score=float(relevance),
                )
                results.append(chunk)

        logger.info(
            "retrieval_completed",
            results_count=len(results),
            query=query,
        )

        return results


# Global retriever instance
_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """
    Get global retriever instance.

    Returns:
        HybridRetriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever