"""
SAHAYAK-AI API Routes

FastAPI endpoints for the disaster response platform.
"""

import time
from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse

from agents.state import (
    QueryRequest,
    QueryResponse,
    LocationData,
)
from agents.graph import sahayak_graph
from voice.whisper_asr import get_whisper_asr
from geo.routing import get_router

logger = structlog.get_logger(__name__)

# Create API router
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest) -> QueryResponse:
    """
    Process emergency query through 3-agent pipeline.

    Args:
        request: Query request with text and optional location

    Returns:
        QueryResponse with instructions and metadata
    """
    start_time = time.time()
    logger.info(
        "query_endpoint_called",
        query_length=len(request.query),
        has_location=bool(request.location),
    )

    try:
        # Prepare initial state
        initial_state = {
            "raw_query": request.query,
            "user_location": request.location,
            "triage": None,
            "retrieved_chunks": [],
            "safety_output": None,
            "error": None,
            "retry_count": 0,
            "ttfi_ms": None,
            "messages": [],
        }

        # Run the graph
        final_state = await sahayak_graph.ainvoke(initial_state)

        # Extract results
        triage = final_state.get("triage")
        safety_output = final_state.get("safety_output")
        error = final_state.get("error")

        if error or not triage or not safety_output:
            logger.error("query_failed", error=error)
            raise HTTPException(
                status_code=500,
                detail=f"Query processing failed: {error or 'Unknown error'}",
            )

        # Get nearest POI if location is available
        nearest_poi = None
        route_summary = None

        if request.location:
            try:
                router_instance = get_router()
                route_result = await router_instance.find_nearest_with_route(
                    lat=request.location.lat,
                    lon=request.location.lon,
                    poi_type="shelter",
                )

                if route_result.get("route"):
                    nearest_poi = route_result.get("nearest_poi")
                    route_info = route_result.get("route")
                    route_summary = route_info.summary if route_info else None

            except Exception as e:
                logger.warning("route_calculation_failed", error=str(e))

        # Build response
        ttfi_ms = (time.time() - start_time) * 1000

        response = QueryResponse(
            triage=triage,
            instructions=safety_output.instructions,
            sources=[chunk.source for chunk in final_state.get("retrieved_chunks", [])],
            redline_triggered=safety_output.redline_triggered,
            reflection_passed=safety_output.reflection_passed,
            nearest_shelter=nearest_poi,
            route_summary=route_summary,
            ttfi_ms=ttfi_ms,
        )

        logger.info(
            "query_completed",
            hazard_type=triage.hazard_type,
            instructions_count=len(safety_output.instructions),
            ttfi_ms=ttfi_ms,
        )

        return response

    except Exception as e:
        logger.error("query_endpoint_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}",
        )


@router.post("/voice", response_model=QueryResponse)
async def voice_endpoint(
    audio_file: UploadFile = File(...),
    location: Optional[LocationData] = None,
) -> QueryResponse:
    """
    Transcribe voice input and process as query.

    Args:
        audio_file: Audio file upload
        location: Optional user location

    Returns:
        QueryResponse with instructions
    """
    logger.info(
        "voice_endpoint_called",
        filename=audio_file.filename,
        content_type=audio_file.content_type,
    )

    try:
        # Save temporary audio file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name
            content = await audio_file.read()
            tmp.write(content)

        try:
            # Transcribe audio
            whisper = get_whisper_asr()
            query_text = whisper.transcribe(tmp_path)

            logger.info("audio_transcribed", query_length=len(query_text))

            # Process as regular query
            request = QueryRequest(query=query_text, location=location)
            return await query_endpoint(request)

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        logger.error("voice_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Voice processing failed: {str(e)}",
        )


@router.get("/poi", response_model=Dict[str, Any])
async def poi_endpoint(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    poi_type: str = Query("shelter", description="POI type"),
    radius_km: float = Query(50.0, gt=0, le=100, description="Search radius in km"),
) -> Dict[str, Any]:
    """
    Query Points of Interest by location and type.

    Args:
        lat: User latitude
        lon: User longitude
        poi_type: Type of POI (shelter, hospital, etc.)
        radius_km: Search radius in kilometers

    Returns:
        Dict with nearest POI
    """
    logger.info(
        "poi_endpoint_called",
        location=(lat, lon),
        poi_type=poi_type,
        radius_km=radius_km,
    )

    try:
        from geo.poi_db import get_poi_db

        poi_db = get_poi_db()

        # Find nearest POI
        pois = poi_db.find_nearest(
            lat=lat,
            lon=lon,
            poi_type=poi_type,
            limit=1,
        )

        if not pois:
            return {"poi": None, "route": None, "error": f"No {poi_type} found nearby"}

        nearest = pois[0]

        # Try to get route from OSRM (optional)
        route_info = None
        try:
            from geo.osrm_client import get_osrm_client

            osrm = get_osrm_client()
            osrm_response = await osrm.get_route(
                origin_lat=lat,
                origin_lon=lon,
                dest_lat=nearest["lat"],
                dest_lon=nearest["lon"],
            )
            route_info = osrm.parse_route_response(osrm_response)
        except Exception as e:
            logger.debug("osrm_unavailable", error=str(e))

        return {
            "poi": nearest,
            "route": route_info,
        }

    except Exception as e:
        logger.error("poi_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"POI query failed: {str(e)}",
        )


@router.get("/route", response_model=Dict[str, Any])
async def route_endpoint(
    from_lat: float = Query(..., ge=-90, le=90, description="Origin latitude"),
    from_lon: float = Query(..., ge=-180, le=180, description="Origin longitude"),
    poi_type: str = Query("shelter", description="Destination POI type"),
) -> Dict[str, Any]:
    """
    Get route from origin to nearest POI.

    Args:
        from_lat: Origin latitude
        from_lon: Origin longitude
        poi_type: Type of POI to route to

    Returns:
        Dict with route information
    """
    logger.info(
        "route_endpoint_called",
        origin=(from_lat, from_lon),
        poi_type=poi_type,
    )

    try:
        router_instance = get_router()
        result = await router_instance.find_nearest_with_route(
            lat=from_lat,
            lon=from_lon,
            poi_type=poi_type,
        )

        if result.get("error"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error"),
            )

        return {
            "poi": result.get("nearest_poi"),
            "route": result.get("route"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("route_endpoint_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Route calculation failed: {str(e)}",
        )
