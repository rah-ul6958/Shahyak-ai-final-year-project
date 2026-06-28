"""
SAHAYAK-AI Triage Agent Tests

Tests for hazard classification and context extraction.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestTriageAgent:
    """Tests for the Triage Agent."""

    def test_parse_valid_json_response(self):
        """Test parsing valid JSON response from LLM."""
        from agents.triage_agent import parse_triage_response

        response = json.dumps({
            "hazard_type": "FLOOD",
            "location_string": "Uttarakhand, Chamoli",
            "severity_level": "HIGH",
            "semantic_query": "flood evacuation protocol",
            "confidence": 0.9,
        })

        result = parse_triage_response(response)

        assert result is not None
        assert result["hazard_type"] == "FLOOD"
        assert result["location_string"] == "Uttarakhand, Chamoli"
        assert result["severity_level"] == "HIGH"
        assert result["confidence"] == 0.9

    def test_parse_json_in_markdown_block(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        from agents.triage_agent import parse_triage_response

        response = """```json
{
    "hazard_type": "FIRE",
    "location_string": "Mumbai, Maharashtra",
    "severity_level": "CRITICAL",
    "semantic_query": "fire evacuation protocol",
    "confidence": 0.85
}
```"""

        result = parse_triage_response(response)

        assert result is not None
        assert result["hazard_type"] == "FIRE"
        assert result["severity_level"] == "CRITICAL"

    def test_parse_invalid_json_returns_none(self):
        """Test that invalid JSON returns None."""
        from agents.triage_agent import parse_triage_response

        response = "This is not valid JSON at all"
        result = parse_triage_response(response)

        assert result is None

    def test_hazard_type_validation(self):
        """Test that invalid hazard types are rejected."""
        from pydantic import ValidationError
        from agents.state import TriageResult

        with pytest.raises(ValidationError):
            TriageResult(
                hazard_type="INVALID",
                location_string="Test",
                severity_level="HIGH",
                semantic_query="test",
                confidence=0.9,
            )

    def test_severity_level_validation(self):
        """Test that invalid severity levels are rejected."""
        from pydantic import ValidationError
        from agents.state import TriageResult

        with pytest.raises(ValidationError):
            TriageResult(
                hazard_type="FLOOD",
                location_string="Test",
                severity_level="EXTREME",
                semantic_query="test",
                confidence=0.9,
            )

    def test_confidence_range_validation(self):
        """Test that confidence must be between 0 and 1."""
        from pydantic import ValidationError
        from agents.state import TriageResult

        # Valid confidence
        result = TriageResult(
            hazard_type="FLOOD",
            location_string="Test",
            severity_level="HIGH",
            semantic_query="test",
            confidence=0.5,
        )
        assert result.confidence == 0.5

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            TriageResult(
                hazard_type="FLOOD",
                location_string="Test",
                severity_level="HIGH",
                semantic_query="test",
                confidence=1.5,
            )

        # Invalid confidence (too low)
        with pytest.raises(ValidationError):
            TriageResult(
                hazard_type="FLOOD",
                location_string="Test",
                severity_level="HIGH",
                semantic_query="test",
                confidence=-0.1,
            )

    @pytest.mark.asyncio
    async def test_triage_node_success(self, mock_ollama_client):
        """Test successful triage node execution."""
        from agents.triage_agent import triage_node

        state = {
            "raw_query": "There is a flood in Chamoli district",
            "triage": None,
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        result = await triage_node(state)

        assert result.get("triage") is not None
        assert result.get("error") is None
        assert result["triage"].hazard_type == "FLOOD"

    @pytest.mark.asyncio
    async def test_triage_node_with_malformed_response(self):
        """Test triage node handles malformed LLM response."""
        from agents.triage_agent import triage_node

        with patch("llm.ollama_client.get_ollama_client") as mock:
            client = MagicMock()
            client.chat.return_value = {
                "message": {"content": "Invalid JSON response"}
            }
            mock.return_value = client

            state = {
                "raw_query": "Test query",
                "triage": None,
                "error": None,
                "retry_count": 0,
                "messages": [],
            }

            result = await triage_node(state)

            # Should set error or increment retry count
            assert result.get("error") is not None or result.get("retry_count", 0) > 0

    def test_triage_result_serialization(self, sample_triage_result):
        """Test TriageResult can be serialized to JSON."""
        from agents.state import TriageResult

        triage = TriageResult(**sample_triage_result)
        json_str = triage.model_dump_json()

        assert json_str is not None
        assert "FLOOD" in json_str
