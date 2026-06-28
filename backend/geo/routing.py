"""
SAHAYAK-AI Routing Module

Combines POI database search with OSRM routing for navigation.
"""

from typing import Any, Dict, List, Optional

import structlog

from agents.state import POIInfo, RouteInfo
from geo.poi_db import get_poi_db
from geo.osrm_client import get_osrm_client
from config import settings

logger = structlog.get_logger(__name__)


class Router:
    """
    Router combining POI search and OSRM routing.
    """

    def __init__(self):
        """Initialize router with POI database and OSRM client."""
        self.poi_db = get_poi_db()
        self.osrm_client = get_osrm_client()

    async def find_nearest_with_route(
        self,
        lat: float,
        lon: float,
        poi_type: str = "shelter",
    ) -> Dict[str, Any]:
        """
        Find nearest POI and get route to it.

        Args:
            lat: User latitude
            lon: User longitude
            poi_type: Type of POI to find (shelter, hospital, etc.)

        Returns:
            Dict with nearest POI and route info
        """
        logger.info(
            "finding_nearest_with_route",
            lat=lat,
            lon=lon,
            poi_type=poi_type,
        )

        # Find nearest POI
        pois = self.poi_db.find_nearest(
            lat=lat,
            lon=lon,
            poi_type=poi_type,
            limit=1,
        )

        if not pois:
            logger.warning("no_poi_found", poi_type=poi_type)
            return {
                "nearest_poi": None,
                "route": None,
                "error": f"No {poi_type} found nearby",
            }

        nearest = pois[0]

        # Get route to POI
        try:
            osrm_response = await self.osrm_client.get_route(
                origin_lat=lat,
                origin_lon=lon,
                dest_lat=nearest["lat"],
                dest_lon=nearest["lon"],
            )

            route_info = self.osrm_client.parse_route_response(osrm_response)

            # Get first instruction as summary
            summary = "Start your journey"
            if route_info["steps"]:
                summary = route_info["steps"][0]["instruction"]
                if len(route_info["steps"]) > 1:
                    summary += f" then continue for {route_info['distance_km']} km"

            return {
                "nearest_poi": POIInfo(
                    name=nearest["name"],
                    poi_type=nearest["type"],
                    distance_km=nearest["distance_km"],
                    lat=nearest["lat"],
                    lon=nearest["lon"],
                    contact=nearest.get("contact"),
                ),
                "route": RouteInfo(
                    summary=summary,
                    duration_seconds=route_info["duration_seconds"],
                    distance_km=route_info["distance_km"],
                    steps=route_info["steps"],
                ),
                "error": None,
            }

        except Exception as e:
            logger.error("route_error", error=str(e))
            return {
                "nearest_poi": POIInfo(
                    name=nearest["name"],
                    poi_type=nearest["type"],
                    distance_km=nearest["distance_km"],
                    lat=nearest["lat"],
                    lon=nearest["lon"],
                    contact=nearest.get("contact"),
                ),
                "route": None,
                "error": f"Route calculation failed: {str(e)}",
            }

    async def get_route_to_poi(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float,
    ) -> Dict[str, Any]:
        """
        Get route from origin to destination.

        Args:
            from_lat: Origin latitude
            from_lon: Origin longitude
            to_lat: Destination latitude
            to_lon: Destination longitude

        Returns:
            Dict with route info
        """
        try:
            osrm_response = await self.osrm_client.get_route(
                origin_lat=from_lat,
                origin_lon=from_lon,
                dest_lat=to_lat,
                dest_lon=to_lon,
            )

            route_info = self.osrm_client.parse_route_response(osrm_response)

            summary = "Start your journey"
            if route_info["steps"]:
                summary = route_info["steps"][0]["instruction"]
                if len(route_info["steps"]) > 1:
                    summary += f" then continue for {route_info['distance_km']} km"

            return {
                "route": RouteInfo(
                    summary=summary,
                    duration_seconds=route_info["duration_seconds"],
                    distance_km=route_info["distance_km"],
                    steps=route_info["steps"],
                ),
                "error": None,
            }

        except Exception as e:
            logger.error("route_error", error=str(e))
            return {
                "route": None,
                "error": f"Route calculation failed: {str(e)}",
            }


# Global router instance
_router: Optional[Router] = None


def get_router() -> Router:
    """
    Get global router instance.

    Returns:
        Router instance
    """
    global _router
    if _router is None:
        _router = Router()
    return _router