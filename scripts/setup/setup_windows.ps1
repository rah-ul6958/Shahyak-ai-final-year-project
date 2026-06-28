# SAHAYAK-AI Windows Setup Script
# Downloads OSM data and sets up routing for Windows development

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $SCRIPT_DIR)
$MAP_DIR = Join-Path $PROJECT_ROOT "data\maps"

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "SAHAYAK-AI Windows Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path $MAP_DIR | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $MAP_DIR "osm") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $MAP_DIR "osrm") | Out-Null

# Check for Docker
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        $dockerAvailable = $true
        Write-Host "Docker detected: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "Docker not found. Please install Docker Desktop for Windows." -ForegroundColor Yellow
    Write-Host "Download from: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
}

# Download OSM data
Write-Host "`nDownloading OSM data..." -ForegroundColor Cyan

$states = @("uttarakhand", "kerala", "odisha")
$geofabrikBase = "https://download.geofabrik.de/asia/india"

foreach ($state in $states) {
    $outputFile = Join-Path $MAP_DIR "osm\$state.osm.pbf"
    
    if (Test-Path $outputFile) {
        Write-Host "SKIP: $state data already exists" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Downloading $state OSM data..." -ForegroundColor White
    $url = "$geofabrikBase/$state-latest.osm.pbf"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $outputFile -UseBasicParsing
        $size = (Get-Item $outputFile).Length / 1MB
        Write-Host "Downloaded: $state ($([math]::Round($size, 1)) MB)" -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Failed to download $state data" -ForegroundColor Yellow
    }
}

# Process OSRM data using Docker
if ($dockerAvailable) {
    Write-Host "`nProcessing OSRM data with Docker..." -ForegroundColor Cyan
    
    foreach ($state in $states) {
        $osmFile = Join-Path $MAP_DIR "osm\$state.osm.pbf"
        $osrmDir = Join-Path $MAP_DIR "osrm"
        
        if (-not (Test-Path $osmFile)) {
            continue
        }
        
        Write-Host "Processing $state for OSRM..." -ForegroundColor White
        
        # Extract routing data
        $extractCmd = "docker run --rm -v `"${osrmDir}:/data`" osrm/osrm-backend osrm-extract --profile=/usr/local/share/osrm/profiles/car.lua /data/$state.osm.pbf"
        try {
            Invoke-Expression $extractCmd
        } catch {
            Write-Host "WARNING: OSRM extraction failed for $state" -ForegroundColor Yellow
            continue
        }
        
        # Partition and customize
        $partitionCmd = "docker run --rm -v `"${osrmDir}:/data`" osrm/osrm-backend osrm-partition /data/$state.osrm"
        $customizeCmd = "docker run --rm -v `"${osrmDir}:/data`" osrm/osrm-backend osrm-customize /data/$state.osrm"
        
        try {
            Invoke-Expression $partitionCmd
            Invoke-Expression $customizeCmd
            Write-Host "Completed: $state" -ForegroundColor Green
        } catch {
            Write-Host "WARNING: OSRM processing failed for $state" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "`nDocker not available. OSRM processing skipped." -ForegroundColor Yellow
    Write-Host "Install Docker Desktop to enable routing functionality." -ForegroundColor Yellow
}

# Create development fallback for routing
Write-Host "`nCreating development routing fallback..." -ForegroundColor Cyan

$fallbackScript = @'
# SAHAYAK-AI Development Routing Fallback
# This provides basic straight-line routing when OSRM is not available

import math
from typing import Dict, Any, Optional

class FallbackRouter:
    """Simple straight-line routing for development without OSRM."""
    
    def __init__(self):
        self.earth_radius_km = 6371
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return self.earth_radius_km * c
    
    def get_route(self, origin_lat: float, origin_lon: float,
                  dest_lat: float, dest_lon: float) -> Dict[str, Any]:
        """Get simple straight-line route."""
        distance = self._haversine_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        
        # Estimate driving time (assuming 40 km/h average speed)
        duration_seconds = (distance / 40) * 3600
        
        return {
            "code": "Ok",
            "routes": [{
                "summary": f"Straight-line route ({distance:.1f} km)",
                "distance": distance * 1000,
                "duration": duration_seconds,
                "legs": [{
                    "steps": [
                        {
                            "instruction": "Start",
                            "distance": 0,
                            "duration": 0,
                            "name": "",
                            "maneuver": {"type": "depart"}
                        },
                        {
                            "instruction": f"Continue straight for {distance:.1f} km",
                            "distance": distance * 1000,
                            "duration": duration_seconds,
                            "name": "",
                            "maneuver": {"type": "continue"}
                        },
                        {
                            "instruction": "Arrive at destination",
                            "distance": 0,
                            "duration": 0,
                            "name": "",
                            "maneuver": {"type": "arrive"}
                        }
                    ]
                }]
            }]
        }

# Global instance
_fallback_router = None

def get_fallback_router() -> FallbackRouter:
    global _fallback_router
    if _fallback_router is None:
        _fallback_router = FallbackRouter()
    return _fallback_router
'@

$fallbackPath = Join-Path $PROJECT_ROOT "backend\geo\fallback_router.py"
Set-Content -Path $fallbackPath -Value $fallbackScript -Encoding UTF8
Write-Host "Created fallback router at $fallbackPath" -ForegroundColor Green

# Update .env for local development
Write-Host "`nUpdating .env for local development..." -ForegroundColor Cyan

$envPath = Join-Path $PROJECT_ROOT ".env"
$envContent = Get-Content $envPath -Raw

# Update OSRM_HOST for local development
if ($envContent -match "OSRM_HOST=http://osrm:5000") {
    $envContent = $envContent -replace "OSRM_HOST=http://osrm:5000", "OSRM_HOST=http://localhost:5000"
    Set-Content -Path $envPath -Value $envContent -Encoding UTF8
    Write-Host "Updated OSRM_HOST to http://localhost:5000" -ForegroundColor Green
}

Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "`nData directories created:" -ForegroundColor White
Write-Host "  - data/maps/osm/      (OSM PBF files)" -ForegroundColor White
Write-Host "  - data/maps/osrm/     (OSRM processed data)" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Install Docker Desktop for Windows (if not installed)" -ForegroundColor Yellow
Write-Host "  2. Start OSRM: docker run -p 5000:5000 -v `"$(Join-Path $MAP_DIR 'osrm'):/data`" osrm/osrm-backend osrm-routed --algorithm mld /data/uttarakhand.osrm" -ForegroundColor Yellow
Write-Host "  3. Start Ollama: ollama serve" -ForegroundColor Yellow
Write-Host "  4. Start backend: python backend/main.py" -ForegroundColor Yellow
Write-Host "  5. Start frontend: cd frontend; npm run dev" -ForegroundColor Yellow
