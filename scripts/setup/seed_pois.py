#!/usr/bin/env python3
"""
SAHAYAK-AI POI Seed Script

Populates the DuckDB POI database with sample Indian emergency locations.
Covers: Hospitals, Shelters, Police Stations, Relief Centres
Focus states: Uttarakhand, Kerala, Odisha (NDMA priority states)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from geo.poi_db import get_poi_db


SAMPLE_POIS = [
    # ===== UTTARAKHAND =====
    # Chamoli District
    {"name": "District Hospital Chamoli", "type": "hospital", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.4086, "lon": 79.3174, "capacity": 200, "contact": "+91-1372-252201"},
    {"name": "Primary Health Centre Gopeshwar", "type": "hospital", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.3908, "lon": 79.3198, "capacity": 50, "contact": "+91-1372-252302"},
    {"name": "Govt. Inter College Shelter, Chamoli", "type": "shelter", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.4120, "lon": 79.3210, "capacity": 500, "contact": "+91-1372-252400"},
    {"name": "Community Centre Joshimath", "type": "shelter", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.5556, "lon": 79.5684, "capacity": 300, "contact": "+91-1372-274233"},
    {"name": "Police Station Gopeshwar", "type": "police_station", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.3912, "lon": 79.3205, "capacity": None, "contact": "+91-1372-252205"},
    {"name": "Relief Centre Chamoli Base Camp", "type": "relief_centre", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.4050, "lon": 79.3150, "capacity": 1000, "contact": "+91-1372-252500"},

    # Dehradun District
    {"name": "Doon Hospital, Dehradun", "type": "hospital", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3219, "lon": 78.0322, "capacity": 500, "contact": "+91-135-2658866"},
    {"name": "Coronation Hospital, Dehradun", "type": "hospital", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3165, "lon": 78.0288, "capacity": 300, "contact": "+91-135-2651177"},
    {"name": "Rajkiya Mahila & Bal Chikitsalaya", "type": "hospital", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3250, "lon": 78.0350, "capacity": 200, "contact": "+91-135-2654400"},
    {"name": "Nehru Colony Shelter Home", "type": "shelter", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3300, "lon": 78.0400, "capacity": 800, "contact": "+91-135-2656600"},
    {"name": "MDDA Ground Relief Camp", "type": "shelter", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3180, "lon": 78.0300, "capacity": 1500, "contact": "+91-135-2657700"},
    {"name": "Police Control Room, Dehradun", "type": "police_station", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3200, "lon": 78.0310, "capacity": None, "contact": "+91-135-2651000"},
    {"name": "District Relief Centre, Dehradun", "type": "relief_centre", "state": "Uttarakhand", "district": "Dehradun", "lat": 30.3190, "lon": 78.0295, "capacity": 2000, "contact": "+91-135-2658800"},

    # Haridwar District
    {"name": "MMBS Hospital, Haridwar", "type": "hospital", "state": "Uttarakhand", "district": "Haridwar", "lat": 29.9457, "lon": 78.1642, "capacity": 400, "contact": "+91-1334-230155"},
    {"name": "BHEL Hospital, Haridwar", "type": "hospital", "state": "Uttarakhand", "district": "Haridwar", "lat": 29.8543, "lon": 78.1348, "capacity": 250, "contact": "+91-1332-275400"},
    {"name": "Shelter Camp, Har Ki Pauri", "type": "shelter", "state": "Uttarakhand", "district": "Haridwar", "lat": 29.9492, "lon": 78.1643, "capacity": 1000, "contact": "+91-1334-231234"},
    {"name": "Police Station Haridwar", "type": "police_station", "state": "Uttarakhand", "district": "Haridwar", "lat": 29.9460, "lon": 78.1650, "capacity": None, "contact": "+91-1334-230200"},

    # ===== KERALA =====
    # Thiruvananthapuram District
    {"name": "Government Medical College, Thiruvananthapuram", "type": "hospital", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "capacity": 600, "contact": "+91-471-2528221"},
    {"name": "KIMS Hospital, Thiruvananthapuram", "type": "hospital", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5474, "lon": 76.9128, "capacity": 400, "contact": "+91-471-3044444"},
    {"name": "Vizhinjam Relief Camp", "type": "shelter", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.3667, "lon": 76.9833, "capacity": 800, "contact": "+91-471-2485000"},
    {"name": "Beemapally Shelter Home", "type": "shelter", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5100, "lon": 76.9300, "capacity": 500, "contact": "+91-471-2475000"},
    {"name": "Police Commissionerate, Thiruvananthapuram", "type": "police_station", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5069, "lon": 76.9560, "capacity": None, "contact": "+91-471-2334500"},
    {"name": "District Disaster Management Centre", "type": "relief_centre", "state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5200, "lon": 76.9400, "capacity": 2000, "contact": "+91-471-2320000"},

    # Ernakulam District
    {"name": "Government Medical College, Ernakulam", "type": "hospital", "state": "Kerala", "district": "Ernakulam", "lat": 9.9816, "lon": 76.2996, "capacity": 500, "contact": "+91-484-2370000"},
    {"name": "Amrita Hospital, Kochi", "type": "hospital", "state": "Kerala", "district": "Ernakulam", "lat": 9.9380, "lon": 76.3420, "capacity": 700, "contact": "+91-484-2851234"},
    {"name": "Flood Relief Camp, Aluva", "type": "shelter", "state": "Kerala", "district": "Ernakulam", "lat": 10.1070, "lon": 76.3530, "capacity": 1200, "contact": "+91-484-2620000"},
    {"name": "Municipal Shelter, Fort Kochi", "type": "shelter", "state": "Kerala", "district": "Ernakulam", "lat": 9.9650, "lon": 76.2420, "capacity": 600, "contact": "+91-484-2215000"},
    {"name": "Police Station Ernakulam North", "type": "police_station", "state": "Kerala", "district": "Ernakulam", "lat": 9.9850, "lon": 76.2850, "capacity": None, "contact": "+91-484-2352000"},

    # ===== ODISHA =====
    # Khordha District (Bhubaneswar)
    {"name": "AIIMS Bhubaneswar", "type": "hospital", "state": "Odisha", "district": "Khordha", "lat": 20.2150, "lon": 85.8200, "capacity": 1000, "contact": "+9674-2301234"},
    {"name": "Capital Hospital, Bhubaneswar", "type": "hospital", "state": "Odisha", "district": "Khordha", "lat": 20.2700, "lon": 85.8300, "capacity": 400, "contact": "+9674-2531000"},
    {"name": "Cyclone Shelter, Puri Beach", "type": "shelter", "state": "Odisha", "district": "Puri", "lat": 19.7983, "lon": 85.8254, "capacity": 1500, "contact": "+9672-222000"},
    {"name": "Relief Camp, Bhubaneswar", "type": "shelter", "state": "Odisha", "district": "Khordha", "lat": 20.2500, "lon": 85.8100, "capacity": 2000, "contact": "+9674-2540000"},
    {"name": "Commissionerate Police, Bhubaneswar", "type": "police_station", "state": "Odisha", "district": "Khordha", "lat": 20.2750, "lon": 79.2750, "capacity": None, "contact": "+9674-2531100"},
    {"name": "State Disaster Response Centre", "type": "relief_centre", "state": "Odisha", "district": "Khordha", "lat": 20.2600, "lon": 85.8200, "capacity": 3000, "contact": "+9674-2590000"},

    # Cuttack District
    {"name": "SCB Medical College, Cuttack", "type": "hospital", "state": "Odisha", "district": "Cuttack", "lat": 20.4833, "lon": 85.8833, "capacity": 600, "contact": "+9671-241400"},
    {"name": "Cuttack Municipal Shelter", "type": "shelter", "state": "Odisha", "district": "Cuttack", "lat": 20.4700, "lon": 85.8800, "capacity": 800, "contact": "+9671-240500"},
    {"name": "Police Station Cuttack", "type": "police_station", "state": "Odisha", "district": "Cuttack", "lat": 20.4800, "lon": 85.8850, "capacity": None, "contact": "+9671-241200"},

    # ===== MAHARASHTRA =====
    # Mumbai
    {"name": "Brihanmumbai Municipal Corporation Hospital", "type": "hospital", "state": "Maharashtra", "district": "Mumbai", "lat": 19.0760, "lon": 72.8777, "capacity": 800, "contact": "+91-22-23080000"},
    {"name": "Sion Hospital, Mumbai", "type": "hospital", "state": "Maharashtra", "district": "Mumbai", "lat": 19.0430, "lon": 72.8670, "capacity": 500, "contact": "+91-22-24076381"},
    {"name": "KEM Hospital, Mumbai", "type": "hospital", "state": "Maharashtra", "district": "Mumbai", "lat": 19.0050, "lon": 72.8440, "capacity": 700, "contact": "+91-22-24107000"},
    {"name": "Flood Relief Camp, Dharavi", "type": "shelter", "state": "Maharashtra", "district": "Mumbai", "lat": 19.0430, "lon": 72.8530, "capacity": 1500, "contact": "+91-22-24010000"},
    {"name": "Mumbai Disaster Management Centre", "type": "relief_centre", "state": "Maharashtra", "district": "Mumbai", "lat": 18.9388, "lon": 72.8354, "capacity": 5000, "contact": "+91-22-22620000"},
    {"name": "Police Control Room, Mumbai", "type": "police_station", "state": "Maharashtra", "district": "Mumbai", "lat": 18.9432, "lon": 72.8322, "capacity": None, "contact": "+91-22-22621000"},

    # ===== DELHI =====
    {"name": "AIIMS Delhi", "type": "hospital", "state": "Delhi", "district": "New Delhi", "lat": 28.5672, "lon": 77.2100, "capacity": 2000, "contact": "+91-11-26588500"},
    {"name": "Safdarjung Hospital", "type": "hospital", "state": "Delhi", "district": "New Delhi", "lat": 28.5690, "lon": 77.2080, "capacity": 1500, "contact": "+91-11-26165060"},
    {"name": "Lok Nayak Relief Shelter", "type": "shelter", "state": "Delhi", "district": "New Delhi", "lat": 28.6350, "lon": 77.2380, "capacity": 3000, "contact": "+91-11-23220000"},
    {"name": "Delhi Police HQ", "type": "police_station", "state": "Delhi", "district": "New Delhi", "lat": 28.6328, "lon": 77.2197, "capacity": None, "contact": "+91-11-23220000"},
    {"name": "Delhi Disaster Management Authority", "type": "relief_centre", "state": "Delhi", "district": "New Delhi", "lat": 28.6139, "lon": 77.2090, "capacity": 5000, "contact": "+91-11-23380000"},
]


def seed_pois():
    """Seed the POI database with sample data."""
    print("=" * 50)
    print("SAHAYAK-AI POI Database Seeder")
    print("=" * 50)

    db = get_poi_db()

    # Clear existing data
    db.connection.execute("DELETE FROM poi")
    print("Cleared existing POI data")

    # Insert sample POIs
    count = db.add_pois_batch(SAMPLE_POIS)
    print(f"Inserted {count} POIs")

    # Show stats
    stats = db.get_poi_count()
    print("\nPOI counts by type:")
    for poi_type, cnt in stats.items():
        print(f"  {poi_type}: {cnt}")

    # Show sample queries
    print("\n--- Sample nearest POI queries ---")

    test_locations = [
        ("Chamoli", 30.4086, 79.3174),
        ("Dehradun", 30.3219, 78.0322),
        ("Mumbai", 19.0760, 72.8777),
        ("Bhubaneswar", 20.2150, 85.8200),
    ]

    for name, lat, lon in test_locations:
        nearest = db.find_nearest(lat, lon, "shelter", limit=3)
        print(f"\n  Nearest shelters to {name}:")
        for poi in nearest:
            print(f"    - {poi['name']} ({poi['distance_km']} km)")

    print("\n" + "=" * 50)
    print("Seeding complete!")
    print("=" * 50)


if __name__ == "__main__":
    seed_pois()
