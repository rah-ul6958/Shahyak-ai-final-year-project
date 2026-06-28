#!/bin/bash
# SAHAYAK-AI Tile Conversion Script
# Converts OSM PBF files to MBTiles for offline map rendering

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
MAP_DIR="$PROJECT_ROOT/data/maps"
OSM_DIR="$MAP_DIR/osm"
TILES_DIR="$MAP_DIR/tiles"
OSRM_DIR="$MAP_DIR/osrm"

echo "==========================================="
echo "SAHAYAK-AI Tile Conversion"
echo "==========================================="

# Create output directories
mkdir -p "$TILES_DIR" "$OSRM_DIR"

# Check for required tools
if ! command -v tilemaker &> /dev/null; then
    echo "ERROR: tilemaker not found."
    echo "Install with: apt-get install tilemaker"
    echo "Or download from: https://github.com/systemed/tilemaker"
    exit 1
fi

if ! command -v osmium &> /dev/null; then
    echo "ERROR: osmium-tool not found."
    echo "Install with: apt-get install osmium-tool"
    exit 1
fi

# Process each OSM file
for osm_file in "$OSM_DIR"/*.osm.pbf; do
    if [ ! -f "$osm_file" ]; then
        echo "No OSM files found in $OSM_DIR"
        exit 1
    fi
    
    filename=$(basename "$osm_file" .osm.pbf)
    
    echo ""
    echo "Processing: $filename"
    
    # Extract routing data for OSRM
    echo "  Extracting routing data..."
    osmium extract \
        --strategy="complete_ways" \
        --overwrite \
        -o "$OSRM_DIR/${filename}_routing.osm.pbf" \
        "$osm_file"
    
    # Process with OSRM for routing
    echo "  Processing OSRM graph..."
    cd "$OSRM_DIR"
    osrm-extract \
        --profile="/usr/local/share/osrm/profiles/car.lua" \
        "${filename}_routing.osm.pbf" || {
        echo "  WARNING: OSRM extraction failed for $filename"
        continue
    }
    
    osrm-partition "${filename}_routing.osrm" || true
    osrm-customize "${filename}_routing.osrm" || true
    
    # Generate MBTiles for map display
    echo "  Generating map tiles..."
    tilemaker \
        --input "$osm_file" \
        --output "$TILES_DIR/${filename}.mbtiles" \
        --config "$PROJECT_ROOT/scripts/setup/tilemaker-config.json" 2>/dev/null || {
        echo "  WARNING: Tile generation failed for $filename (using default config)"
    }
    
    cd "$PROJECT_ROOT"
    
    echo "  Completed: $filename"
done

echo ""
echo "Tile conversion complete!"
echo "Tiles: $(ls -1 "$TILES_DIR"/*.mbtiles 2>/dev/null | wc -l) MBTiles files"
echo "OSRM: $(ls -1 "$OSRM_DIR"/*.osrm 2>/dev/null | wc -l) OSRM graphs"
