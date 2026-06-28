"""
SAHAYAK-AI Self-Reflection

LLM-based self-reflection pass to verify instruction safety.
"""

from typing import Any, Dict, List

import structlog

logger = structlog.get_logger(__name__)

# This module is integrated into safety_agent.py
# This file provides utility functions for reflection checks


def build_reflection_prompt(
    instructions: List[str],
    context: str,
) -> str:
    """
    Build self-reflection prompt.

    Args:
        instructions: Generated instructions
        context: Retrieved protocol context

    Returns:
        Formatted prompt string
    """
    instructions_text = "\n".join(f"- {i}" for i in instructions)

    return f"""You are a safety reviewer for disaster response instructions.
Review the following instructions and determine if they are safe and accurate.

Instructions to review:
{instructions_text}

Context from protocol documents:
{context}

Check for:
(a) Unsafe instructions that could cause harm
(b) Instructions contradicting the retrieved protocol
(c) Hallucinated advice not present in the context

Respond ONLY with JSON format:
{{
  "safe": true/false,
  "reason": "<if unsafe, explain why and what specifically is wrong>"
}}

Do not add any explanation beyond the JSON."""


def parse_reflection_result(response_text: str) -> Dict[str, Any]:
    """
    Parse reflection response.

    Args:
        response_text: LLM response text

    Returns:
        Parsed result with safe bool and reason
    """
    import json
    import re

    # Try to extract JSON from response
    text = response_text.strip()

    # Handle markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3]

    text = text.strip()

    try:
        data = json.loads(text)
        return {
            "safe": data.get("safe", True),
            "reason": data.get("reason", ""),
        }
    except json.JSONDecodeError:
        # Try to find JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "safe": data.get("safe", True),
                    "reason": data.get("reason", ""),
                }
            except json.JSONDecodeError:
                pass

        # Default to safe if cannot parse
        logger.warning("reflection_parse_failed", response=response_text[:200])
        return {
            "safe": True,
            "reason": "Could not verify - assuming safe",
        }