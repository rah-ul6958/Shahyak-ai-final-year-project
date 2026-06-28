"""
SAHAYAK-AI OSRM Client

HTTP client for OSRM routing service (local Docker container).
"""

from typing import Any, Dict, List, Optional

import httpx
import structlog

from config import settings

logger = structlog.get_logger(__name__)


class OSRMClient:
    """
    OSRM HTTP client for offline turn-by-turn routing.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize OSRM client.

        Args:
            base_url: OSRM service base URL
        """
        self.base_url = base_url or settings.osrm_host

    async def get_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        overview: str = "full",
        geometries: str = "geojson",
        steps: bool = True,
    ) -> Dict[str, Any]:
        """
        Get route between two points.

        Args:
            origin_lat: Origin latitude
            origin_lon: Origin longitude
            dest_lat: Destination latitude
            dest_lon: Destination longitude
            overview: Overview type (full, simplified, false)
            geometries: Geometry format (geojson, polyline)
            steps: Include turn-by-turn steps

        Returns:
            Route response from OSRM

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"

        params = {
            "overview": overview,
            "geometries": geometries,
            "steps": steps,
            "alternatives": "false",
        }

        logger.info(
            "osrm_route_request",
            url=url,
            origin=(origin_lat, origin_lon),
            dest=(dest_lat, dest_lon),
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        # Check for OSRM error code
        if data.get("code") != "Ok":
            error_msg = data.get("message", "Unknown OSRM error")
            logger.error("osrm_error", code=data.get("code"), message=error_msg)
            raise ValueError(f"OSRM error: {error_msg}")

        return data

    def parse_route_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OSRM route response into structured format.

        Args:
            response: Raw OSRM response

        Returns:
            Parsed route info
        """
        routes = response.get("routes", [])
        if not routes:
            return {
                "summary": "No route found",
                "duration_seconds": 0,
                "distance_km": 0,
                "steps": [],
            }

        route = routes[0]

        # Parse steps
        steps = []
        for i, leg in enumerate(route.get("legs", [])):
            for step in leg.get("steps", []):
                steps.append({
                    "instruction": self._get_step_instruction(step),
                    "distance_km": round(step.get("distance", 0) / 1000, 2),
                    "duration_min": round(step.get("duration", 0) / 60, 1),
                    "name": step.get("name", ""),
                    "maneuver": step.get("maneuver", {}).get("type", ""),
                })

        return {
            "summary": route.get("summary", ""),
            "duration_seconds": route.get("duration", 0),
            "distance_km": round(route.get("distance", 0) / 1000, 2),
            "steps": steps,
        }

    def _get_step_instruction(self, step: Dict[str, Any]) -> str:
        """
        Generate human-readable instruction from step.

        Args:
            step: OSRM step data

        Returns:
            Instruction string
        """
        maneuver = step.get("maneuver", {})
        maneuver_type = maneuver.get("type", "")
        maneuver_modifier = maneuver.get("modifier", "")
        street_name = step.get("name", "")
        distance = step.get("distance", 0)

        instruction = ""

        if maneuver_type == "depart":
            instruction = "Start"
        elif maneuver_type == "arrive":
            instruction = "Arrive at destination"
        elif maneuver_type == "turn":
            direction_map = {
                "right": "Turn right",
                "left": "Turn left",
                "slight right": "Turn slight right",
                "slight left": "Turn slight left",
                "sharp right": "Turn sharp right",
                "sharp left": "Turn sharp left",
                "uturn": "Make a U-turn",
            }
            instruction = direction_map.get(maneuver_modifier, "Turn")
        elif maneuver_type == "merge":
            instruction = "Merge"
        elif maneuver_type == "fork":
            direction = "right" if maneuver_modifier == "right" else "left"
            instruction = f"Keep {direction} at fork"
        elif maneuver_type == "new name":
            instruction = "Continue"
        else:
            instruction = maneuver_type.title()

        if street_name:
            instruction += f" onto {street_name}"

        if distance > 0:
            distance_str = self._format_distance(distance)
            instruction += f" for {distance_str}"

        return instruction

    def _format_distance(self, meters: float) -> str:
        """
        Format distance in meters to human-readable string.

        Args:
            meters: Distance in meters

        Returns:
            Formatted distance string
        """
        if meters >= 1000:
            return f"{round(meters / 1000, 1)} km"
        return f"{round(meters)} m"

    async def health_check(self) -> bool:
        """
        Check if OSRM service is reachable.

        Returns:
            True if OSRM is healthy
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning("osrm_health_check_failed", error=str(e))
            return False


# Global OSRM client instance
_osrm_client: Optional[OSRMClient] = None


def get_osrm_client() -> OSRMClient:
    """
    Get global OSRM client instance.

    Returns:
        OSRMClient instance
    """
    global _osrm_client
    if _osrm_client is None:
        _osrm_client = OSRMClient()
    return _osrm_client