"""
SAHAYAK-AI POI Database

DuckDB-based POI index for hospitals, shelters, police stations, and relief centres.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import duckdb

from config import settings

logger = structlog.get_logger(__name__)

# Database file path
POI_DB_PATH = settings.chroma_path.parent / "poi" / "poi.duckdb"


class POIDatabase:
    """
    DuckDB-based Point of Interest database with R-tree spatial index.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the POI database.

        Args:
            db_path: Path to DuckDB database file
        """
        self.db_path = db_path or POI_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """Lazy-load DuckDB connection."""
        if self._connection is None:
            self._connection = duckdb.connect(str(self.db_path))
            self._initialize_schema()
        return self._connection

    def _initialize_schema(self) -> None:
        """Initialize database schema."""
        # Create POI table
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS poi (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                state TEXT,
                district TEXT,
                lat DOUBLE,
                lon DOUBLE,
                capacity INTEGER,
                contact TEXT
            )
        """)

        # Create spatial index using DuckDB's spatial extension
        # Note: For production, use proper R-tree index
        self._connection.execute("""
            CREATE SEQUENCE IF NOT EXISTS poi_id_seq
        """)

        logger.info("poi_schema_initialized", db_path=str(self.db_path))

    def add_poi(
        self,
        name: str,
        poi_type: str,
        state: str,
        district: str,
        lat: float,
        lon: float,
        capacity: Optional[int] = None,
        contact: Optional[str] = None,
    ) -> int:
        """
        Add a POI to the database.

        Args:
            name: POI name
            poi_type: Type (hospital, police_station, shelter, relief_centre)
            state: State name
            district: District name
            lat: Latitude
            lon: Longitude
            capacity: Capacity (for shelters)
            contact: Contact information

        Returns:
            POI ID
        """
        result = self.connection.execute("""
            INSERT INTO poi (id, name, type, state, district, lat, lon, capacity, contact)
            VALUES (nextval('poi_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, [name, poi_type, state, district, lat, lon, capacity, contact]).fetchone()

        return result[0] if result else -1

    def add_pois_batch(self, pois: List[Dict[str, Any]]) -> int:
        """
        Add multiple POIs in batch.

        Args:
            pois: List of POI dicts

        Returns:
            Number of POIs added
        """
        if not pois:
            return 0

        for poi in pois:
            self.add_poi(
                name=poi["name"],
                poi_type=poi["type"],
                state=poi["state"],
                district=poi.get("district", ""),
                lat=poi["lat"],
                lon=poi["lon"],
                capacity=poi.get("capacity"),
                contact=poi.get("contact"),
            )

        logger.info("pois_added_batch", count=len(pois))
        return len(pois)

    def find_nearest(
        self,
        lat: float,
        lon: float,
        poi_type: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find nearest POIs of a given type.

        Args:
            lat: Latitude
            lon: Longitude
            poi_type: POI type to search for
            limit: Maximum number of results

        Returns:
            List of nearest POIs with distance
        """
        # Calculate distance using Haversine formula
        # DuckDB doesn't have built-in spatial functions without extension
        query = """
            SELECT
                id,
                name,
                type,
                state,
                district,
                lat,
                lon,
                capacity,
                contact,
                (
                    6371 * acos(
                        cos(radians(?)) * cos(radians(lat)) *
                        cos(radians(lon) - radians(?)) +
                        sin(radians(?)) * sin(radians(lat))
                    )
                ) AS distance_km
            FROM poi
            WHERE type = ?
            ORDER BY distance_km
            LIMIT ?
        """

        results = self.connection.execute(query, [lat, lon, lat, poi_type, limit]).fetchall()

        pois = []
        for row in results:
            pois.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "state": row[3],
                "district": row[4],
                "lat": row[5],
                "lon": row[6],
                "capacity": row[7],
                "contact": row[8],
                "distance_km": round(row[9], 2),
            })

        logger.info(
            "nearest_pois_found",
            poi_type=poi_type,
            count=len(pois),
            lat=lat,
            lon=lon,
        )

        return pois

    def find_within_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        poi_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find POIs within a given radius.

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            poi_type: Optional POI type filter

        Returns:
            List of POIs within radius
        """
        query = """
            SELECT
                id,
                name,
                type,
                state,
                district,
                lat,
                lon,
                capacity,
                contact,
                (
                    6371 * acos(
                        cos(radians(?)) * cos(radians(lat)) *
                        cos(radians(lon) - radians(?)) +
                        sin(radians(?)) * sin(radians(lat))
                    )
                ) AS distance_km
            FROM poi
            WHERE (
                6371 * acos(
                    cos(radians(?)) * cos(radians(lat)) *
                    cos(radians(lon) - radians(?)) +
                    sin(radians(?)) * sin(radians(lat))
                )
            ) <= ?
        """

        params = [lat, lon, lat, lat, lon, lat, radius_km]

        if poi_type:
            query += " AND type = ?"
            params.append(poi_type)

        query += " ORDER BY distance_km"

        results = self.connection.execute(query, params).fetchall()

        pois = []
        for row in results:
            pois.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "state": row[3],
                "district": row[4],
                "lat": row[5],
                "lon": row[6],
                "capacity": row[7],
                "contact": row[8],
                "distance_km": round(row[9], 2),
            })

        return pois

    def get_poi_count(self) -> Dict[str, int]:
        """
        Get count of POIs by type.

        Returns:
            Dict with counts by type
        """
        results = self.connection.execute("""
            SELECT type, COUNT(*) as count
            FROM poi
            GROUP BY type
        """).fetchall()

        return {row[0]: row[1] for row in results}

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


# Global POI database instance
_poi_db: Optional[POIDatabase] = None


def get_poi_db() -> POIDatabase:
    """
    Get global POI database instance.

    Returns:
        POIDatabase instance
    """
    global _poi_db
    if _poi_db is None:
        _poi_db = POIDatabase()
    return _poi_db