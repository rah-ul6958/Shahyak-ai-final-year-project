"""
SAHAYAK-AI Reranker

Cross-encoder reranking for improved retrieval accuracy.
"""

from typing import List, Tuple, Optional

import structlog
from sentence_transformers import CrossEncoder

from config import settings

logger = structlog.get_logger(__name__)

# Cross-encoder model
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """
    Cross-encoder reranker for re-ranking retrieved documents.
    """

    def __init__(
        self,
        model_name: str = RERANK_MODEL,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the reranker.

        Args:
            model_name: Model identifier for cross-encoder
            cache_dir: Local cache directory for models
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        """Lazy-load the cross-encoder model."""
        if self._model is None:
            logger.info("loading_reranker_model", model=self.model_name)
            self._model = CrossEncoder(
                self.model_name,
                max_length=512,
                cache_dir=self.cache_dir,
            )
            logger.info("reranker_model_loaded")
        return self._model

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
    ) -> List[Tuple[int, float]]:
        """
        Re-rank documents using cross-encoder scores.

        Args:
            query: Query string
            documents: List of document texts
            top_k: Number of top results to return

        Returns:
            List of (index, score) tuples sorted by score descending
        """
        if not documents:
            return []

        # Create query-document pairs
        pairs = [[query, doc] for doc in documents]

        # Get cross-encoder scores
        scores = self.model.predict(pairs)

        # Combine with document indices and sort
        results = list(enumerate(scores))
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]


# Global reranker instance
_reranker: Optional[Reranker] = None


def get_reranker() -> Reranker:
    """
    Get global reranker instance.

    Returns:
        Reranker instance
    """
    global _reranker
    if _reranker is None:
        _reranker = Reranker(
            cache_dir=str(settings.reranker_cache_dir),
        )
    return _reranker


def rerank_documents(
    query: str,
    documents: List[str],
    top_k: int = 5,
) -> List[Tuple[int, float]]:
    """
    Convenience function to rerank documents.

    Args:
        query: Query string
        documents: List of document texts
        top_k: Number of top results to return

    Returns:
        List of (index, score) tuples
    """
    reranker = get_reranker()
    return reranker.rerank(query, documents, top_k)