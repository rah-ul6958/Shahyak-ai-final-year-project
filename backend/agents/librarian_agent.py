"""
SAHAYAK-AI Librarian Agent

Agent 2: Retrieves verified NDMA/SDMA protocol chunks from offline vector DB.
"""

import time
from typing import Any, Dict, List

import structlog

from agents.state import SAHAYAKState, RetrievedChunk, TriageResult
from config import settings

logger = structlog.get_logger(__name__)


async def librarian_node(state: SAHAYAKState) -> Dict[str, Any]:
    """
    Librarian Agent node for LangGraph pipeline.

    Implements three-stage hybrid retrieval:
    1. Lexical pre-filter using metadata
    2. Dense semantic search using FastEmbed
    3. Cross-encoder reranking

    Args:
        state: Current pipeline state with triage result

    Returns:
        Dict with updated state containing retrieved chunks
    """
    start_time = time.time()

    triage = state.get("triage")

    if not triage:
        logger.warning("librarian_agent_no_triage")
        return {
            "retrieved_chunks": [],
            "error": "No triage result available",
        }

    hazard_type = triage.get("hazard_type", "UNKNOWN") if isinstance(triage, dict) else triage.hazard_type
    semantic_query = triage.get("semantic_query", "") if isinstance(triage, dict) else triage.semantic_query
    location_string = triage.get("location_string", "") if isinstance(triage, dict) else triage.location_string

    logger.info(
        "librarian_agent_started",
        hazard_type=hazard_type,
        semantic_query=semantic_query,
        location=location_string,
    )

    try:
        from rag.retriever import HybridRetriever

        # Extract state from location string (e.g., "Uttarakhand, Chamoli")
        location_parts = location_string.split(",")
        state_name = location_parts[0].strip() if location_parts else "unknown"

        # Initialize retriever
        retriever = HybridRetriever()

        # Perform hybrid retrieval
        chunks = await retriever.retrieve(
            query=semantic_query,
            hazard_type=hazard_type,
            state=state_name,
            top_k=5,
        )

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "librarian_agent_completed",
            chunks_retrieved=len(chunks),
            hazard_type=hazard_type,
            duration_ms=duration_ms,
        )

        return {
            "retrieved_chunks": chunks,
            "error": None,
        }

    except Exception as e:
        logger.error("librarian_agent_error", error=str(e))
        return {
            "retrieved_chunks": [],
            "error": f"Retrieval failed: {str(e)}",
        }