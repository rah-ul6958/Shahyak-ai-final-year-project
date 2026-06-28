"""
SAHAYAK-AI State Schemas

Defines Pydantic models and LangGraph TypedState for the agent pipeline.
"""

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class TriageResult(BaseModel):
    """Result from the Triage Agent - hazard classification and extraction."""

    hazard_type: Literal[
        "FIRE",
        "FLOOD",
        "EARTHQUAKE",
        "MEDICAL",
        "CHEMICAL",
        "CYCLONE",
        "UNKNOWN",
    ] = Field(
        description="Classified hazard type from the emergency query"
    )

    location_string: str = Field(
        description="State and district extracted from query"
    )

    severity_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        description="Assessed severity level of the emergency"
    )

    semantic_query: str = Field(
        description="Precise retrieval query for Librarian Agent"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score of the triage classification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hazard_type": "FLOOD",
                "location_string": "Uttarakhand, Chamoli",
                "severity_level": "HIGH",
                "semantic_query": "flood evacuation protocol Uttarakhand",
                "confidence": 0.92,
            }
        }


class RetrievedChunk(BaseModel):
    """A retrieved document chunk from the RAG pipeline."""

    content: str = Field(
        description="Text content of the retrieved chunk"
    )

    source: str = Field(
        description="Source document and page number (e.g., 'NDMA_Flood_Protocol_2019.pdf, p.14')"
    )

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance score from reranker"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "1. Move to higher ground immediately...",
                "source": "NDMA_Flood_Protocol_2019.pdf, p.14",
                "relevance_score": 0.95,
            }
        }


class SafetyOutput(BaseModel):
    """Output from the Safety Agent with generated instructions and guardrails."""

    instructions: List[str] = Field(
        description="Numbered, imperative disaster response instructions"
    )

    redline_triggered: bool = Field(
        description="Whether any redline rule was triggered and overridden"
    )

    redline_override_applied: bool = Field(
        description="Whether a safe override was applied instead of dangerous instruction"
    )

    reflection_passed: bool = Field(
        description="Whether self-reflection check passed"
    )

    sources: List[str] = Field(
        description="List of source documents used for instructions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "instructions": [
                    "1. Move to higher ground immediately.",
                    "2. Do not attempt to cross flooded roads.",
                ],
                "redline_triggered": False,
                "redline_override_applied": False,
                "reflection_passed": True,
                "sources": ["NDMA_Flood_Protocol_2019.pdf, p.14"],
            }
        }


class LocationData(BaseModel):
    """Geographic location data."""

    lat: float = Field(
        ge=-90.0,
        le=90.0,
        description="Latitude"
    )

    lon: float = Field(
        ge=-180.0,
        le=180.0,
        description="Longitude"
    )


class POIInfo(BaseModel):
    """Point of Interest information."""

    name: str = Field(description="Name of the POI")

    poi_type: str = Field(
        description="Type: hospital, police_station, shelter, relief_centre"
    )

    distance_km: float = Field(description="Distance from user in kilometers")

    lat: float = Field(description="Latitude of POI")

    lon: float = Field(description="Longitude of POI")

    contact: Optional[str] = Field(
        default=None,
        description="Contact information"
    )


class RouteInfo(BaseModel):
    """Route information from OSRM."""

    summary: str = Field(
        description="Human-readable route summary"
    )

    duration_seconds: float = Field(
        description="Total duration in seconds"
    )

    distance_km: float = Field(
        description="Total distance in kilometers"
    )

    steps: List[Dict[str, Any]] = Field(
        description="Turn-by-turn directions"
    )


class SAHAYAKState(MessagesState):
    """
    LangGraph TypedState for SAHAYAK-AI pipeline.

    Manages state across the 3-agent pipeline: Triage -> Librarian -> Safety
    """

    # Raw input
    raw_query: str = Field(
        default="",
        description="Original user query (text or transcribed from voice)"
    )

    # Triage Agent output
    triage: Optional[TriageResult] = Field(
        default=None,
        description="Triage classification result"
    )

    # Librarian Agent output
    retrieved_chunks: List[RetrievedChunk] = Field(
        default_factory=list,
        description="Retrieved document chunks from RAG"
    )

    # Safety Agent output
    safety_output: Optional[SafetyOutput] = Field(
        default=None,
        description="Safety-checked instructions"
    )

    # Geospatial
    route_info: Optional[RouteInfo] = Field(
        default=None,
        description="Route information to nearest POI"
    )

    nearest_poi: Optional[POIInfo] = Field(
        default=None,
        description="Nearest point of interest"
    )

    # Error handling
    error: Optional[str] = Field(
        default=None,
        description="Error message if any pipeline step fails"
    )

    retry_count: int = Field(
        default=0,
        description="Number of retries for current agent"
    )

    # Metadata
    ttfi_ms: Optional[float] = Field(
        default=None,
        description="Time to first instruction in milliseconds"
    )

    user_location: Optional[LocationData] = Field(
        default=None,
        description="User's geographic location"
    )


class QueryRequest(BaseModel):
    """Request schema for /query endpoint."""

    query: str = Field(
        min_length=1,
        max_length=2000,
        description="Emergency query text"
    )

    location: Optional[LocationData] = Field(
        default=None,
        description="User's current location"
    )


class QueryResponse(BaseModel):
    """Response schema for /query endpoint."""

    triage: TriageResult = Field(description="Triage classification result")

    instructions: List[str] = Field(
        description="Safety-checked instructions"
    )

    sources: List[str] = Field(
        description="Source documents used"
    )

    redline_triggered: bool = Field(
        description="Whether redline rule was triggered"
    )

    reflection_passed: bool = Field(
        description="Whether self-reflection check passed"
    )

    nearest_shelter: Optional[POIInfo] = Field(
        default=None,
        description="Nearest shelter information"
    )

    route_summary: Optional[str] = Field(
        default=None,
        description="Route summary to nearest POI"
    )

    ttfi_ms: float = Field(
        description="Time to first instruction in milliseconds"
    )


class HealthResponse(BaseModel):
    """Response schema for /health endpoint."""

    status: str = Field(description="Overall health status")

    model_loaded: bool = Field(
        description="Whether Ollama model is loaded"
    )

    chroma_ready: bool = Field(
        description="Whether ChromaDB is ready"
    )

    osrm_reachable: bool = Field(
        description="Whether OSRM service is reachable"
    )

    hardware_profile: str = Field(
        description="Current hardware profile"
    )

    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional health details"
    )


class POIRequest(BaseModel):
    """Request schema for /poi endpoint."""

    lat: float = Field(
        ge=-90.0,
        le=90.0,
        description="Latitude"
    )

    lon: float = Field(
        ge=-180.0,
        le=180.0,
        description="Longitude"
    )

    poi_type: str = Field(
        description="POI type: hospital, shelter, police_station, relief_centre"
    )

    radius_km: float = Field(
        default=10.0,
        gt=0,
        le=100,
        description="Search radius in kilometers"
    )


class RouteRequest(BaseModel):
    """Request schema for /route endpoint."""

    from_lat: float = Field(
        ge=-90.0,
        le=90.0,
        description="Origin latitude"
    )

    from_lon: float = Field(
        ge=-180.0,
        le=180.0,
        description="Origin longitude"
    )

    poi_type: str = Field(
        description="Destination POI type"
    )