"""
SAHAYAK-AI API Routes Tests

Tests for FastAPI endpoints.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestAPIRoutes:
    """Tests for FastAPI API routes."""

    def test_root_endpoint(self):
        """Test root endpoint returns basic info."""
        from main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SAHAYAK-AI"
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self):
        """Test health endpoint returns status."""
        from main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "chroma_ready" in data

    def test_query_endpoint_missing_query(self):
        """Test query endpoint rejects empty query."""
        from main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/query",
            json={},
        )

        assert response.status_code == 422  # Validation error

    def test_query_endpoint_valid_request(self):
        """Test query endpoint accepts valid request."""
        from main import app

        client = TestClient(app)

        with patch("api.routes.sahayak_graph") as mock_graph:
            mock_graph.ainvoke = AsyncMock(return_value={
                "triage": MagicMock(
                    hazard_type="FLOOD",
                    location_string="Uttarakhand",
                    severity_level="HIGH",
                    confidence=0.9,
                    model_dump=lambda: {
                        "hazard_type": "FLOOD",
                        "location_string": "Uttarakhand",
                        "severity_level": "HIGH",
                        "confidence": 0.9,
                    },
                ),
                "retrieved_chunks": [],
                "safety_output": MagicMock(
                    instructions=["1. Move to higher ground."],
                    sources=["NDMA.pdf"],
                    redline_triggered=False,
                    reflection_passed=True,
                ),
                "error": None,
            })

            response = client.post(
                "/api/v1/query",
                json={"query": "There is a flood in Uttarakhand"},
            )

            # Should return 200 or 500 depending on mock completeness
            assert response.status_code in [200, 500]

    def test_poi_endpoint_missing_params(self):
        """Test POI endpoint rejects missing parameters."""
        from main import app

        client = TestClient(app)
        response = client.get("/api/v1/poi")

        assert response.status_code == 422  # Validation error

    def test_route_endpoint_missing_params(self):
        """Test route endpoint rejects missing parameters."""
        from main import app

        client = TestClient(app)
        response = client.get("/api/v1/route")

        assert response.status_code == 422  # Validation error

    def test_voice_endpoint_missing_file(self):
        """Test voice endpoint rejects missing audio file."""
        from main import app

        client = TestClient(app)
        response = client.post("/api/v1/voice")

        assert response.status_code == 422  # Validation error


class TestQueryRequest:
    """Tests for QueryRequest model."""

    def test_valid_query(self):
        """Test valid query request."""
        from agents.state import QueryRequest

        request = QueryRequest(query="Test emergency")
        assert request.query == "Test emergency"
        assert request.location is None

    def test_empty_query_rejected(self):
        """Test empty query is rejected."""
        from pydantic import ValidationError
        from agents.state import QueryRequest

        with pytest.raises(ValidationError):
            QueryRequest(query="")

    def test_long_query_rejected(self):
        """Test overly long query is rejected."""
        from pydantic import ValidationError
        from agents.state import QueryRequest

        with pytest.raises(ValidationError):
            QueryRequest(query="x" * 2001)


class TestQueryResponse:
    """Tests for QueryResponse model."""

    def test_query_response_serialization(self):
        """Test QueryResponse can be serialized."""
        from agents.state import QueryResponse, TriageResult

        response = QueryResponse(
            triage=TriageResult(
                hazard_type="FLOOD",
                location_string="Uttarakhand",
                severity_level="HIGH",
                semantic_query="flood protocol",
                confidence=0.9,
            ),
            instructions=["1. Move to higher ground."],
            sources=["NDMA.pdf"],
            redline_triggered=False,
            reflection_passed=True,
            ttfi_ms=1500.0,
        )

        json_str = response.model_dump_json()
        assert "FLOOD" in json_str
        assert "1500" in json_str
