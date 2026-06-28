#!/bin/bash
# SAHAYAK-AI OSM Data Download Script
# Downloads OpenStreetMap data for target states

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
MAP_DIR="$PROJECT_ROOT/data/maps/osm"

echo "==========================================="
echo "SAHAYAK-AI OSM Data Download"
echo "==========================================="

# Create directories
mkdir -p "$MAP_DIR"

# Download OSM data for target states
STATES=(
    "uttarakhand"
    "kerala"
    "odisha"
)

GEOFABRIK_BASE="https://download.geofabrik.de/asia/india"

for state in "${STATES[@]}"; do
    OUTPUT_FILE="$MAP_DIR/${state}.osm.pbf"
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo "SKIP: $state data already exists"
        continue
    fi
    
    echo "Downloading $state OSM data..."
    wget -O "$OUTPUT_FILE" "${GEOFABRIK_BASE}/${state}-latest.osm.pbf" || {
        echo "WARNING: Failed to download $state data"
        continue
    }
    
    echo "Downloaded: $state ($(du -h "$OUTPUT_FILE" | cut -f1))"
done

echo ""
echo "OSM data download complete!"
echo "Files in $MAP_DIR:"
ls -lh "$MAP_DIR"/*.osm.pbf 2>/dev/null || echo "No OSM files found"
