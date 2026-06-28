"""
SAHAYAK-AI Test Configuration

Shared fixtures for pytest test suite.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def mock_ollama_client() -> Generator[MagicMock, None, None]:
    """Mock Ollama client for testing."""
    with patch("llm.ollama_client.get_ollama_client") as mock:
        client = MagicMock()
        client.chat.return_value = {
            "message": {
                "content": '{"hazard_type": "FLOOD", "location_string": "Uttarakhand, Chamoli", "severity_level": "HIGH", "semantic_query": "flood evacuation protocol", "confidence": 0.9}'
            }
        }
        client.list.return_value = {"models": []}
        mock.return_value = client
        yield client


@pytest.fixture
def mock_chroma_client() -> Generator[MagicMock, None, None]:
    """Mock ChromaDB client for testing."""
    with patch("rag.vector_store.get_chroma_client") as mock:
        client = MagicMock()
        collection = MagicMock()
        collection.count.return_value = 100
        collection.query.return_value = {
            "documents": [["Test document about flood protocols"]],
            "metadatas": [[{"source": "NDMA_Flood.pdf, p.1"}]],
            "distances": [[0.3]],
        }
        client.get_collection.return_value = collection
        client.create_collection.return_value = collection
        mock.return_value = client
        yield client


@pytest.fixture
def mock_whisper() -> Generator[MagicMock, None, None]:
    """Mock Whisper ASR for testing."""
    with patch("voice.whisper_asr.get_whisper_asr") as mock:
        asr = MagicMock()
        asr.transcribe.return_value = "There is a flood in Chamoli district"
        mock.return_value = asr
        yield asr


@pytest.fixture
def mock_osrm_client() -> Generator[MagicMock, None, None]:
    """Mock OSRM client for testing."""
    with patch("geo.osrm_client.get_osrm_client") as mock:
        client = MagicMock()
        client.get_route.return_value = {
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
        client.parse_route_response.return_value = {
            "summary": "NH58",
            "duration_seconds": 1200,
            "distance_km": 5.0,
            "steps": [
                {
                    "instruction": "Start on NH58 for 5.0 km",
                    "distance_km": 5.0,
                    "duration_min": 20.0,
                    "name": "NH58",
                    "maneuver": "depart",
                }
            ],
        }
        mock.return_value = client
        yield client


@pytest.fixture
def mock_poi_db() -> Generator[MagicMock, None, None]:
    """Mock POI database for testing."""
    with patch("geo.poi_db.get_poi_db") as mock:
        db = MagicMock()
        db.find_nearest.return_value = [
            {
                "id": 1,
                "name": "Govt. School Shelter",
                "type": "shelter",
                "state": "Uttarakhand",
                "district": "Chamoli",
                "lat": 30.4,
                "lon": 79.3,
                "capacity": 200,
                "contact": "+91-1234567890",
                "distance_km": 1.2,
            }
        ]
        db.get_poi_count.return_value = {"shelter": 10, "hospital": 5}
        mock.return_value = db
        yield db


@pytest.fixture
def sample_triage_result() -> Dict[str, Any]:
    """Sample triage result for testing."""
    return {
        "hazard_type": "FLOOD",
        "location_string": "Uttarakhand, Chamoli",
        "severity_level": "HIGH",
        "semantic_query": "flood evacuation protocol Uttarakhand",
        "confidence": 0.92,
    }


@pytest.fixture
def sample_safety_output() -> Dict[str, Any]:
    """Sample safety output for testing."""
    return {
        "instructions": [
            "1. Move to higher ground immediately.",
            "2. Do not attempt to cross flooded roads.",
            "3. Listen to emergency broadcasts for updates.",
        ],
        "redline_triggered": False,
        "redline_override_applied": False,
        "reflection_passed": True,
        "sources": ["NDMA_Flood_Protocol_2019.pdf, p.14"],
    }


@pytest.fixture
def sample_retrieved_chunks() -> list:
    """Sample retrieved chunks for testing."""
    return [
        {
            "content": "During floods, immediately move to higher ground. Avoid walking through floodwater.",
            "source": "NDMA_Flood_Protocol_2019.pdf, p.14",
            "relevance_score": 0.95,
        },
        {
            "content": "Evacuate to designated shelters. Do not use elevators during flood evacuation.",
            "source": "NDMA_Flood_Protocol_2019.pdf, p.15",
            "relevance_score": 0.88,
        },
    ]


@pytest.fixture
def sample_dangerous_queries() -> list:
    """Sample dangerous queries for redline testing."""
    return [
        {
            "query": "Use water on the electrical fire",
            "expected_triggered": True,
            "hazard_type": "FIRE",
        },
        {
            "query": "Move the person with spinal injury",
            "expected_triggered": True,
            "hazard_type": "MEDICAL",
        },
        {
            "query": "Re-enter the damaged building after earthquake",
            "expected_triggered": True,
            "hazard_type": "EARTHQUAKE",
        },
        {
            "query": "Drive through the flooded road",
            "expected_triggered": True,
            "hazard_type": "FLOOD",
        },
        {
            "query": "Go outside to watch the cyclone",
            "expected_triggered": True,
            "hazard_type": "CYCLONE",
        },
    ]
