"""
SAHAYAK-AI Safety Agent

Agent 3: Generates safe instructions with hard guardrails and self-reflection.
"""

import json
import time
from typing import Any, Dict, List

import structlog
from pydantic import ValidationError

from agents.state import SAHAYAKState, RetrievedChunk, SafetyOutput
from safety.redline_rules import check_redlines, RedlineResult
from config import settings

logger = structlog.get_logger(__name__)

# System prompt for instruction generation
SAFETY_SYSTEM_PROMPT = """You are a disaster response instruction generator.
Using ONLY the provided protocol documents, generate numbered imperative instructions.

Context from protocol documents:
{context}

Generate numbered instructions (1., 2., 3., etc.) that:
- Are imperative and actionable
- Use only information from the provided context
- Are clear and brief
- Do NOT add information not present in the context
- Do NOT suggest actions that could cause harm

Respond ONLY with JSON format:
{{
  "instructions": ["1. <instruction>", "2. <instruction>", ...]
}}

Do not add any explanation or preamble. JSON only."""


# System prompt for self-reflection
REFLECTION_SYSTEM_PROMPT = """You are a safety reviewer for disaster response instructions.
Review the following instructions and determine if they are safe and accurate.

Instructions to review:
{instructions}

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


def parse_instructions_response(response_text: str) -> List[str]:
    """
    Parse LLM response to extract instructions.

    Args:
        response_text: Raw text response from LLM

    Returns:
        List of instruction strings

    Raises:
        ValueError: If JSON cannot be parsed
    """
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
        instructions = data.get("instructions", [])
        # Ensure each instruction is numbered
        numbered = []
        for i, inst in enumerate(instructions, 1):
            # Remove existing numbering if present
            inst = inst.strip()
            if inst and not inst[0].isdigit():
                inst = f"{i}. {inst}"
            numbered.append(inst)
        return numbered
    except json.JSONDecodeError as e:
        # Try to find JSON array in the text
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            data = json.loads(json_str)
            return data.get("instructions", [])
        raise ValueError(f"Cannot parse instructions: {e}") from e


def parse_reflection_response(response_text: str) -> Dict[str, Any]:
    """
    Parse self-reflection response.

    Args:
        response_text: Raw text response from LLM

    Returns:
        Dict with safe boolean and reason

    Raises:
        ValueError: If JSON cannot be parsed
    """
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
        return {
            "safe": data.get("safe", True),
            "reason": data.get("reason", ""),
        }
    except json.JSONDecodeError as e:
        # Default to safe if cannot parse
        logger.warning("reflection_parse_error", error=str(e))
        return {"safe": True, "reason": "Could not verify, assuming safe"}


async def safety_node(state: SAHAYAKState) -> Dict[str, Any]:
    """
    Safety Agent node for LangGraph pipeline.

    Steps:
    1. Generate instructions using retrieved chunks as context
    2. Run deterministic redline check
    3. Run self-reflection LLM pass

    Args:
        state: Current pipeline state with retrieved chunks

    Returns:
        Dict with updated state containing safety output
    """
    start_time = time.time()

    triage = state.get("triage")
    retrieved_chunks = state.get("retrieved_chunks", [])

    if not triage or not retrieved_chunks:
        logger.warning(
            "safety_agent_no_input",
            has_triage=bool(triage),
            chunks_count=len(retrieved_chunks),
        )
        return {
            "safety_output": None,
            "error": "No triage result or retrieved chunks",
        }

    hazard_type = triage.get("hazard_type", "UNKNOWN") if isinstance(triage, dict) else triage.hazard_type
    location_string = triage.get("location_string", "") if isinstance(triage, dict) else triage.location_string

    logger.info(
        "safety_agent_started",
        hazard_type=hazard_type,
        chunks_count=len(retrieved_chunks),
    )

    try:
        from llm.ollama_client import get_ollama_client

        client = get_ollama_client()

        # Step 1: Build context from retrieved chunks
        context_parts = []
        sources = set()
        for chunk in retrieved_chunks:
            context_parts.append(f"[Source: {chunk.source}]\n{chunk.content}")
            sources.add(chunk.source)

        context = "\n\n".join(context_parts)

        # Step 2: Generate instructions
        generation_prompt = SAFETY_SYSTEM_PROMPT.format(context=context)

        messages = [
            {"role": "system", "content": generation_prompt},
            {
                "role": "user",
                "content": f"Generate instructions for {hazard_type} emergency in {location_string}",
            },
        ]

        response = client.chat(
            model=settings.ollama_model,
            messages=messages,
            format="json",
            options={
                "temperature": 0.2,
                "top_p": 0.9,
            },
        )

        response_text = response["message"]["content"]
        instructions = parse_instructions_response(response_text)

        # Step 3: Redline check (deterministic)
        redline_result = check_redlines(instructions, hazard_type)

        if redline_result.triggered:
            logger.warning(
                "safety_agent_redline_triggered",
                triggered_rules=redline_result.matched_rules,
                original_instructions=instructions,
            )
            instructions = redline_result.safe_instructions

        # Step 4: Self-reflection check
        reflection_prompt = REFLECTION_SYSTEM_PROMPT.format(
            instructions="\n".join(f"- {i}" for i in instructions),
            context=context,
        )

        reflection_messages = [
            {"role": "system", "content": reflection_prompt},
            {"role": "user", "content": "Review these instructions for safety"},
        ]

        reflection_response = client.chat(
            model=settings.ollama_model,
            messages=reflection_messages,
            format="json",
            options={
                "temperature": 0.1,
                "top_p": 0.9,
            },
        )

        reflection_result = parse_reflection_response(
            reflection_response["message"]["content"]
        )

        if not reflection_result["safe"]:
            logger.warning(
                "safety_agent_reflection_failed",
                reason=reflection_result["reason"],
            )

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "safety_agent_completed",
            instructions_count=len(instructions),
            redline_triggered=redline_result.triggered,
            reflection_passed=reflection_result["safe"],
            duration_ms=duration_ms,
        )

        safety_output = SafetyOutput(
            instructions=instructions,
            redline_triggered=redline_result.triggered,
            redline_override_applied=bool(redline_result.triggered),
            reflection_passed=reflection_result["safe"],
            sources=list(sources),
        )

        return {
            "safety_output": safety_output,
            "error": None,
        }

    except ValidationError as e:
        logger.error("safety_agent_validation_error", error=str(e))
        return {
            "safety_output": None,
            "error": f"Validation error: {str(e)}",
        }

    except Exception as e:
        logger.error("safety_agent_error", error=str(e))
        return {
            "safety_output": None,
            "error": f"Safety generation failed: {str(e)}",
        }