"""
SAHAYAK-AI Triage Agent

Agent 1: Classifies hazard type and extracts structured context from emergency queries.
"""

import json
import time
from typing import Any, Dict

import structlog
from pydantic import ValidationError

from agents.state import SAHAYAKState, TriageResult
from config import settings

logger = structlog.get_logger(__name__)

# System prompt for Triage Agent
TRIAGE_SYSTEM_PROMPT = """You are an emergency triage classifier for disaster response.
Your task is to analyze the user's emergency query and extract structured information.

Extract the following fields and respond ONLY in valid JSON format:
{{
  "hazard_type": "FIRE|FLOOD|EARTHQUAKE|MEDICAL|CHEMICAL|CYCLONE|UNKNOWN",
  "location_string": "<state, district if mentioned, else 'unspecified'>",
  "severity_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "semantic_query": "<precise retrieval query for protocol database>",
  "confidence": <0.0-1.0>
}}

Rules:
- Analyze keywords and context to determine hazard_type
- location_string should include state and district if mentioned
- severity_level: CRITICAL = immediate danger to life, HIGH = significant threat, MEDIUM = moderate threat, LOW = minor incident
- semantic_query should be a concise phrase for searching disaster protocols
- confidence reflects your certainty (0.0-1.0)
- Do NOT add any explanation or preamble. JSON only."""


def parse_triage_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response to extract TriageResult.

    Args:
        response_text: Raw text response from LLM

    Returns:
        Dict containing parsed triage data

    Raises:
        ValueError: If JSON cannot be parsed
    """
    # Try to find JSON in response
    text = response_text.strip()

    # Handle potential markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3]

    text = text.strip()

    # Parse JSON
    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                pass
        logger.warning("triage_parse_failed", error=str(e))
        return None


async def triage_node(state: SAHAYAKState) -> Dict[str, Any]:
    """
    Triage Agent node for LangGraph pipeline.

    Args:
        state: Current pipeline state containing raw_query

    Returns:
        Dict with updated state
    """
    start_time = time.time()
    raw_query = state.get("raw_query", "")

    logger.info(
        "triage_agent_started",
        query_length=len(raw_query),
        retry_count=state.get("retry_count", 0),
    )

    try:
        from llm.ollama_client import get_ollama_client

        client = get_ollama_client()

        # Build messages for the LLM
        messages = [
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": raw_query},
        ]

        # Call Ollama
        response = client.chat(
            model=settings.ollama_model,
            messages=messages,
            format="json",
            options={
                "temperature": 0.1,  # Low temperature for structured output
                "top_p": 0.9,
            },
        )

        response_text = response["message"]["content"]

        # Parse the response
        triage_data = parse_triage_response(response_text)

        # Validate with Pydantic
        triage_result = TriageResult(
            hazard_type=triage_data.get("hazard_type", "UNKNOWN"),
            location_string=triage_data.get("location_string", "unspecified"),
            severity_level=triage_data.get("severity_level", "MEDIUM"),
            semantic_query=triage_data.get(
                "semantic_query",
                raw_query,
            ),
            confidence=triage_data.get("confidence", 0.5),
        )

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "triage_agent_completed",
            hazard_type=triage_result.hazard_type,
            severity=triage_result.severity_level,
            location=triage_result.location_string,
            confidence=triage_result.confidence,
            duration_ms=duration_ms,
        )

        return {
            "triage": triage_result,
            "error": None,
        }

    except ValidationError as e:
        logger.error("triage_agent_validation_error", error=str(e))
        return {
            "triage": None,
            "error": f"Validation error: {str(e)}",
            "retry_count": state.get("retry_count", 0) + 1,
        }

    except Exception as e:
        logger.error("triage_agent_error", error=str(e))
        return {
            "triage": None,
            "error": f"Triage failed: {str(e)}",
            "retry_count": state.get("retry_count", 0) + 1,
        }