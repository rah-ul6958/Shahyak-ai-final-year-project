"""
SAHAYAK-AI Safety Agent Tests

Tests for instruction generation, redline checking, and self-reflection.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestSafetyAgent:
    """Tests for the Safety Agent."""

    def test_parse_instructions_response_valid(self):
        """Test parsing valid instructions JSON response."""
        from agents.safety_agent import parse_instructions_response

        response = json.dumps({
            "instructions": [
                "1. Move to higher ground immediately.",
                "2. Do not cross flooded roads.",
            ]
        })

        result = parse_instructions_response(response)

        assert len(result) == 2
        assert "Move to higher ground" in result[0]

    def test_parse_instructions_response_with_markdown(self):
        """Test parsing instructions from markdown code block."""
        from agents.safety_agent import parse_instructions_response

        response = """```json
{
    "instructions": [
        "1. Evacuate the building immediately.",
        "2. Use emergency exits only."
    ]
}
```"""

        result = parse_instructions_response(response)

        assert len(result) == 2

    def test_parse_reflection_response_safe(self):
        """Test parsing safe reflection response."""
        from agents.safety_agent import parse_reflection_response

        response = json.dumps({
            "safe": True,
            "reason": ""
        })

        result = parse_reflection_response(response)

        assert result["safe"] is True

    def test_parse_reflection_response_unsafe(self):
        """Test parsing unsafe reflection response."""
        from agents.safety_agent import parse_reflection_response

        response = json.dumps({
            "safe": False,
            "reason": "Instructions contain potentially dangerous advice"
        })

        result = parse_reflection_response(response)

        assert result["safe"] is False
        assert "dangerous" in result["reason"]

    def test_parse_reflection_response_invalid_json(self):
        """Test parsing invalid JSON defaults to safe."""
        from agents.safety_agent import parse_reflection_response

        result = parse_reflection_response("Not valid JSON")

        assert result["safe"] is True  # Default to safe

    @pytest.mark.asyncio
    async def test_safety_node_success(self, mock_ollama_client):
        """Test successful safety node execution."""
        from agents.safety_agent import safety_node

        state = {
            "triage": {
                "hazard_type": "FLOOD",
                "location_string": "Uttarakhand, Chamoli",
                "severity_level": "HIGH",
                "semantic_query": "flood evacuation",
                "confidence": 0.9,
            },
            "retrieved_chunks": [
                MagicMock(
                    content="Move to higher ground during floods",
                    source="NDMA_Flood.pdf, p.1",
                    relevance_score=0.95,
                )
            ],
            "safety_output": None,
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        # Mock both chat calls (generation + reflection)
        mock_ollama_client.chat.side_effect = [
            {"message": {"content": json.dumps({"instructions": ["1. Move to higher ground."]})}},
            {"message": {"content": json.dumps({"safe": True, "reason": ""})}},
        ]

        result = await safety_node(state)

        assert result.get("safety_output") is not None
        assert result["safety_output"].reflection_passed is True
        assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_safety_node_with_no_chunks(self):
        """Test safety node handles missing retrieved chunks."""
        from agents.safety_agent import safety_node

        state = {
            "triage": {
                "hazard_type": "FLOOD",
                "location_string": "Test",
                "severity_level": "HIGH",
                "semantic_query": "test",
                "confidence": 0.9,
            },
            "retrieved_chunks": [],
            "safety_output": None,
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        result = await safety_node(state)

        assert result.get("error") is not None

    def test_safety_output_validation(self, sample_safety_output):
        """Test SafetyOutput model validation."""
        from agents.state import SafetyOutput

        output = SafetyOutput(**sample_safety_output)

        assert output.redline_triggered is False
        assert output.reflection_passed is True
        assert len(output.instructions) == 3
        assert len(output.sources) == 1

    @pytest.mark.asyncio
    async def test_safety_node_redline_triggered(self, mock_ollama_client):
        """Test safety node triggers redline for dangerous instructions."""
        from agents.safety_agent import safety_node

        state = {
            "triage": {
                "hazard_type": "FIRE",
                "location_string": "Mumbai",
                "severity_level": "HIGH",
                "semantic_query": "fire safety",
                "confidence": 0.9,
            },
            "retrieved_chunks": [
                MagicMock(
                    content="Use water on electrical fires",
                    source="Fire_Safety.pdf, p.5",
                    relevance_score=0.9,
                )
            ],
            "safety_output": None,
            "error": None,
            "retry_count": 0,
            "messages": [],
        }

        # Mock responses with dangerous instruction
        mock_ollama_client.chat.side_effect = [
            {"message": {"content": json.dumps({"instructions": ["1. Use water on electrical fires."]})}},
            {"message": {"content": json.dumps({"safe": True, "reason": ""})}},
        ]

        result = await safety_node(state)

        # Redline should have been triggered and instruction modified
        assert result.get("safety_output") is not None
        assert result["safety_output"].redline_triggered is True
