"""
SAHAYAK-AI LangGraph State Machine

Defines the 3-agent pipeline graph with conditional edges.
"""

from typing import Optional

import structlog
from langgraph.graph import StateGraph, START, END

from agents.state import SAHAYAKState
from agents.triage_agent import triage_node
from agents.librarian_agent import librarian_node
from agents.safety_agent import safety_node

logger = structlog.get_logger(__name__)


def route_after_triage(state: SAHAYAKState) -> str:
    """
    Route after Triage Agent execution.

    Args:
        state: Current pipeline state

    Returns:
        str: Next node to route to
    """
    # Check for errors
    if state.get("error"):
        if state.get("retry_count", 0) < 2:
            logger.info(
                "routing_after_triage_retry",
                retry_count=state.get("retry_count", 0),
            )
            return "triage"
        logger.warning("routing_after_triage_error_max_retries")
        return END

    triage = state.get("triage")
    if not triage:
        logger.warning("routing_after_triage_no_result")
        if state.get("retry_count", 0) < 2:
            return "triage"
        return END

    hazard_type = triage.get("hazard_type", "UNKNOWN") if isinstance(triage, dict) else triage.hazard_type

    # Route to Librarian for unknown hazard types after retries
    if hazard_type == "UNKNOWN":
        if state.get("retry_count", 0) < 2:
            logger.info(
                "routing_after_triage_unknown_hazard",
                retry_count=state.get("retry_count", 0),
            )
            return "triage"
        return END

    severity = triage.get("severity_level", "UNKNOWN") if isinstance(triage, dict) else triage.severity_level
    logger.info(
        "routing_after_triage_success",
        hazard_type=hazard_type,
        severity=severity,
    )
    return "librarian"


def route_after_safety(state: SAHAYAKState) -> str:
    """
    Route after Safety Agent execution.

    Args:
        state: Current pipeline state

    Returns:
        str: Next node to route to
    """
    # Check for errors
    if state.get("error"):
        logger.warning("routing_after_safety_error")
        return END

    safety_output = state.get("safety_output")
    if not safety_output:
        logger.warning("routing_after_safety_no_result")
        return END

    # Check if self-reflection failed
    if not safety_output.reflection_passed:
        retry_count = state.get("retry_count", 0)
        if retry_count < 2:
            logger.info(
                "routing_after_safety_reflection_failed",
                retry_count=retry_count,
            )
            return "librarian"
        logger.warning("routing_after_safety_max_retries")
        return END

    logger.info(
        "routing_after_safety_success",
        instructions_count=len(safety_output.instructions),
        redline_triggered=safety_output.redline_triggered,
    )
    return END


def build_graph() -> StateGraph:
    """
    Build the SAHAYAK-AI StateGraph.

    Returns:
        StateGraph: Compiled LangGraph StateGraph
    """
    graph_builder = StateGraph(SAHAYAKState)

    # Add nodes
    graph_builder.add_node("triage", triage_node)
    graph_builder.add_node("librarian", librarian_node)
    graph_builder.add_node("safety", safety_node)

    # Add start edge
    graph_builder.add_edge(START, "triage")

    # Add conditional edges from triage
    graph_builder.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "librarian": "librarian",
            "triage": "triage",
            END: END,
        },
    )

    # Add edge from librarian to safety
    graph_builder.add_edge("librarian", "safety")

    # Add conditional edges from safety
    graph_builder.add_conditional_edges(
        "safety",
        route_after_safety,
        {
            "librarian": "librarian",
            END: END,
        },
    )

    return graph_builder


# Build and compile the graph
sahayak_graph = build_graph().compile()

logger.info("sahayak_graph_compiled", nodes=["triage", "librarian", "safety"])