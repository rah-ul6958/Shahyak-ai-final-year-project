"""
SAHAYAK-AI RAG Embedder

FastEmbed-based embedding generation for offline vector search.
"""

from typing import List, Optional

import structlog
from fastembed import TextEmbedding

from config import settings

logger = structlog.get_logger(__name__)

# Model identifier for BAAI/bge-small-en-v1.5
EMBED_MODEL = "BAAI/bge-small-en-v1.5"


class Embedder:
    """
    FastEmbed-based text embedder with local caching.
    """

    def __init__(
        self,
        model_name: str = EMBED_MODEL,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the embedder.

        Args:
            model_name: Model identifier for FastEmbed
            cache_dir: Local cache directory for models
        """
        self.model_name = model_name
        self.cache_dir = str(cache_dir) if cache_dir else None
        self._model: Optional[TextEmbedding] = None

    @property
    def model(self) -> TextEmbedding:
        """Lazy-load the embedding model."""
        if self._model is None:
            logger.info("loading_embedder_model", model=self.model_name)
            self._model = TextEmbedding(
                model_name=self.model_name,
                cache_dir=self.cache_dir,
            )
            logger.info("embedder_model_loaded")
        return self._model

    def embed(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of text strings to embed
            batch_size: Batch size for embedding (defaults to model default)

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        embeddings = list(self.model.embed(texts, batch_size=batch_size))
        return embeddings

    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        return self.embed([text])[0]


# Global embedder instance
_embedder: Optional[Embedder] = None


def get_embedder() -> Embedder:
    """
    Get global embedder instance.

    Returns:
        Embedder instance
    """
    global _embedder
    if _embedder is None:
        _embedder = Embedder(
            cache_dir=str(settings.embed_cache_dir),
        )
    return _embedder


def embed_documents(documents: List[str]) -> List[List[float]]:
    """
    Convenience function to embed multiple documents.

    Args:
        documents: List of document texts

    Returns:
        List of embedding vectors
    """
    embedder = get_embedder()
    return embedder.embed(documents)


def embed_query(query: str) -> List[float]:
    """
    Convenience function to embed a single query.

    Args:
        query: Query text

    Returns:
        Embedding vector
    """
    embedder = get_embedder()
    return embedder.embed_single(query)