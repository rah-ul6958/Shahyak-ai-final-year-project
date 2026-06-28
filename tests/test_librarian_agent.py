"""
SAHAYAK-AI Librarian Agent Tests

Tests for hybrid retrieval and reranking pipeline.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestLibrarianAgent:
    """Tests for the Librarian Agent."""

    @pytest.mark.asyncio
    async def test_librarian_node_success(self, mock_chroma_client):
        """Test successful librarian node execution."""
        from agents.librarian_agent import librarian_node

        state = {
            "triage": {
                "hazard_type": "FLOOD",
                "location_string": "Uttarakhand, Chamoli",
                "severity_level": "HIGH",
                "semantic_query": "flood evacuation protocol",
                "confidence": 0.9,
            },
            "retrieved_chunks": [],
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        with patch("rag.retriever.HybridRetriever") as mock:
            retriever = MagicMock()
            mock.return_value = retriever
            retriever.retrieve = AsyncMock(return_value=[
                MagicMock(
                    content="Flood protocol text",
                    source="NDMA_Flood.pdf, p.1",
                    relevance_score=0.95,
                )
            ])

            result = await librarian_node(state)

            assert result.get("retrieved_chunks") is not None
            assert len(result["retrieved_chunks"]) > 0
            assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_librarian_node_with_no_triage(self):
        """Test librarian node handles missing triage result."""
        from agents.librarian_agent import librarian_node

        state = {
            "triage": None,
            "retrieved_chunks": [],
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        result = await librarian_node(state)

        assert result.get("error") is not None

    def test_hybrid_retriever_initialization(self):
        """Test HybridRetriever can be initialized."""
        from rag.retriever import HybridRetriever

        retriever = HybridRetriever()
        assert retriever._chroma_client is None
        assert retriever._collection is None

    def test_build_where_filter(self):
        """Test metadata filter construction."""
        from rag.retriever import HybridRetriever

        retriever = HybridRetriever()

        # Test with hazard type
        filter1 = retriever._build_where_filter(hazard_type="FLOOD")
        assert "hazard_type" in filter1
        assert filter1["hazard_type"] == "FLOOD"

        # Test with state
        filter2 = retriever._build_where_filter(state="Uttarakhand")
        assert "state" in filter2

        # Test with both
        filter3 = retriever._build_where_filter(hazard_type="FIRE", state="Maharashtra")
        assert "hazard_type" in filter3
        assert "state" in filter3

        # Test with UNKNOWN hazard type (should not filter)
        filter4 = retriever._build_where_filter(hazard_type="UNKNOWN")
        assert "hazard_type" not in filter4

    def test_embedder_initialization(self):
        """Test embedder can be initialized."""
        from rag.embedder import Embedder

        embedder = Embedder(model_name="BAAI/bge-small-en-v1.5")
        assert embedder.model_name == "BAAI/bge-small-en-v1.5"
        assert embedder._model is None  # Lazy loaded

    def test_reranker_initialization(self):
        """Test reranker can be initialized."""
        from rag.reranker import Reranker

        reranker = Reranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
        assert reranker.model_name == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert reranker._model is None  # Lazy loaded

    def test_vector_store_client_creation(self):
        """Test ChromaDB client creation."""
        from rag.vector_store import get_chroma_client

        client = get_chroma_client()
        assert client is not None

    def test_retrieved_chunk_validation(self, sample_retrieved_chunks):
        """Test RetrievedChunk model validation."""
        from agents.state import RetrievedChunk

        for chunk_data in sample_retrieved_chunks:
            chunk = RetrievedChunk(**chunk_data)
            assert chunk.content is not None
            assert chunk.source is not None
            assert 0 <= chunk.relevance_score <= 1
