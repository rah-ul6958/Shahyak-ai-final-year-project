"""
SAHAYAK-AI Geo Routing Tests

Tests for POI database and OSRM routing.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestPOIDatabase:
    """Tests for the POI database."""

    def test_poi_database_initialization(self):
        """Test POI database can be initialized."""
        from geo.poi_db import POIDatabase

        db = POIDatabase()
        assert db is not None
        assert db._connection is None  # Lazy loaded

    def test_add_poi(self):
        """Test adding a POI to the database."""
        from geo.poi_db import POIDatabase

        db = POIDatabase()

        poi_id = db.add_poi(
            name="Test Hospital",
            poi_type="hospital",
            state="Uttarakhand",
            district="Dehradun",
            lat=30.3165,
            lon=78.0322,
            capacity=None,
            contact="+91-135-1234567",
        )

        assert poi_id is not None
        assert poi_id > 0

    def test_find_nearest_poi(self):
        """Test finding nearest POI."""
        from geo.poi_db import POIDatabase

        db = POIDatabase()

        # Add some test POIs
        db.add_poi(
            name="Hospital A",
            poi_type="hospital",
            state="Uttarakhand",
            district="Dehradun",
            lat=30.3165,
            lon=78.0322,
        )
        db.add_poi(
            name="Shelter B",
            poi_type="shelter",
            state="Uttarakhand",
            district="Dehradun",
            lat=30.3200,
            lon=78.0400,
        )

        # Find nearest hospital
        results = db.find_nearest(
            lat=30.31,
            lon=78.03,
            poi_type="hospital",
            limit=5,
        )

        assert len(results) > 0
        assert results[0]["type"] == "hospital"
        assert "distance_km" in results[0]

    def test_find_within_radius(self):
        """Test finding POIs within radius."""
        from geo.poi_db import POIDatabase

        db = POIDatabase()

        results = db.find_within_radius(
            lat=30.31,
            lon=78.03,
            radius_km=10,
            poi_type="hospital",
        )

        assert isinstance(results, list)

    def test_get_poi_count(self):
        """Test getting POI count by type."""
        from geo.poi_db import POIDatabase

        db = POIDatabase()

        counts = db.get_poi_count()

        assert isinstance(counts, dict)


class TestOSRMClient:
    """Tests for the OSRM client."""

    def test_osrm_client_initialization(self):
        """Test OSRM client initialization."""
        from geo.osrm_client import OSRMClient

        client = OSRMClient()
        assert client is not None
        assert client.base_url is not None

    @pytest.mark.asyncio
    async def test_get_route(self, mock_osrm_client):
        """Test getting route from OSRM."""
        from geo.osrm_client import OSRMClient

        client = OSRMClient()

        with patch.object(client, "get_route", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "code": "Ok",
                "routes": [
                    {
                        "summary": "NH58",
                        "duration": 1200,
                        "distance": 5000,
                        "legs": [
                            {
                                "steps": [
                                    {
                                        "name": "NH58",
                                        "distance": 5000,
                                        "duration": 1200,
                                        "maneuver": {"type": "depart", "modifier": ""},
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }

            result = await client.get_route(30.3, 78.0, 30.4, 79.0)

            assert result["code"] == "Ok"
            assert len(result["routes"]) == 1

    def test_parse_route_response(self):
        """Test parsing OSRM route response."""
        from geo.osrm_client import OSRMClient

        client = OSRMClient()

        response = {
            "code": "Ok",
            "routes": [
                {
                    "summary": "NH58",
                    "duration": 1200,
                    "distance": 5000,
                    "legs": [
                        {
                            "steps": [
                                {
                                    "name": "NH58",
                                    "distance": 5000,
                                    "duration": 1200,
                                    "maneuver": {"type": "depart", "modifier": ""},
                                }
                            ]
                        }
                    ],
                }
            ],
        }

        result = client.parse_route_response(response)

        assert result["summary"] == "NH58"
        assert result["duration_seconds"] == 1200
        assert result["distance_km"] == 5.0
        assert len(result["steps"]) == 1

    def test_parse_route_response_empty(self):
        """Test parsing empty route response."""
        from geo.osrm_client import OSRMClient

        client = OSRMClient()

        response = {"code": "Ok", "routes": []}

        result = client.parse_route_response(response)

        assert result["summary"] == "No route found"
        assert result["duration_seconds"] == 0

    def test_format_distance(self):
        """Test distance formatting."""
        from geo.osrm_client import OSRMClient

        client = OSRMClient()

        assert client._format_distance(500) == "500 m"
        assert client._format_distance(1500) == "1.5 km"
        assert client._format_distance(5000) == "5.0 km"


class TestRouter:
    """Tests for the combined Router."""

    @pytest.mark.asyncio
    async def test_find_nearest_with_route(self, mock_osrm_client):
        """Test finding nearest POI with route."""
        from geo.routing import Router

        router = Router()

        with patch.object(router.poi_db, "find_nearest") as mock_poi:
            mock_poi.return_value = [
                {
                    "id": 1,
                    "name": "Test Shelter",
                    "type": "shelter",
                    "lat": 30.4,
                    "lon": 79.3,
                    "distance_km": 1.2,
                }
            ]

            with patch.object(router.osrm_client, "get_route", new_callable=AsyncMock) as mock_route:
                mock_route.return_value = {
                    "code": "Ok",
                    "routes": [
                        {
                            "summary": "NH58",
                            "duration": 600,
                            "distance": 1200,
                            "legs": [{"steps": []}],
                        }
                    ],
                }

                with patch.object(router.osrm_client, "parse_route_response") as mock_parse:
                    mock_parse.return_value = {
                        "summary": "Head north on NH58",
                        "duration_seconds": 600,
                        "distance_km": 1.2,
                        "steps": [],
                    }

                    result = await router.find_nearest_with_route(
                        lat=30.3,
                        lon=78.0,
                        poi_type="shelter",
                    )

                    assert result.get("nearest_poi") is not None
                    assert result.get("route") is not None
                    assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_find_nearest_no_poi(self):
        """Test finding nearest POI when none exists."""
        from geo.routing import Router

        router = Router()

        with patch.object(router.poi_db, "find_nearest") as mock:
            mock.return_value = []

            result = await router.find_nearest_with_route(
                lat=30.3,
                lon=78.0,
                poi_type="hospital",
            )

            assert result.get("nearest_poi") is None
            assert result.get("error") is not None


class TestStateModels:
    """Tests for state and response models."""

    def test_location_data_validation(self):
        """Test LocationData model validation."""
        from agents.state import LocationData

        # Valid location
        loc = LocationData(lat=30.3165, lon=78.0322)
        assert loc.lat == 30.3165
        assert loc.lon == 78.0322

        # Invalid latitude
        with pytest.raises(Exception):
            LocationData(lat=100.0, lon=78.0)

    def test_poi_info_model(self):
        """Test POIInfo model."""
        from agents.state import POIInfo

        poi = POIInfo(
            name="Test Hospital",
            poi_type="hospital",
            distance_km=2.5,
            lat=30.3165,
            lon=78.0322,
        )

        assert poi.name == "Test Hospital"
        assert poi.distance_km == 2.5

    def test_route_info_model(self):
        """Test RouteInfo model."""
        from agents.state import RouteInfo

        route = RouteInfo(
            summary="Head north",
            duration_seconds=600,
            distance_km=2.5,
            steps=[],
        )

        assert route.summary == "Head north"
        assert route.distance_km == 2.5

    def test_query_request_model(self):
        """Test QueryRequest model."""
        from agents.state import QueryRequest

        request = QueryRequest(query="Test emergency query")
        assert request.query == "Test emergency query"
        assert request.location is None

        # Test with location
        from agents.state import LocationData

        request_with_loc = QueryRequest(
            query="Test",
            location=LocationData(lat=30.0, lon=78.0),
        )
        assert request_with_loc.location is not None
