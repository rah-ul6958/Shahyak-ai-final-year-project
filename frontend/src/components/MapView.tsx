'use client'

import { useEffect, useRef, useState } from 'react'

export interface POI {
  name: string
  lat: number
  lon: number
  distance_km?: number
  poi_type?: string
  type?: string
  contact?: string
  capacity?: number
  district?: string
}

export interface RouteData {
  geometry?: number[][][]
  summary?: string
  distance_km?: number
  duration_seconds?: number
  steps?: Array<{
    instruction: string
    distance_km: number
    duration_min: number
    maneuver?: string
  }>
}

interface MapViewProps {
  userLocation?: { lat: number; lon: number }
  pois?: POI[]
  selectedPoi?: POI | null
  route?: RouteData | null
  onPoiClick?: (poi: POI) => void
  className?: string
}

const POI_COLORS: Record<string, string> = {
  hospital: '#ef4444',
  shelter: '#3b82f6',
  police_station: '#8b5cf6',
  relief_centre: '#f59e0b',
}

const POI_ICONS: Record<string, string> = {
  hospital: 'H',
  shelter: 'S',
  police_station: 'P',
  relief_centre: 'R',
}

export default function MapView({
  userLocation,
  pois = [],
  selectedPoi,
  route,
  onPoiClick,
  className = '',
}: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any>(null)
  const maplibreglRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const routeLayerRef = useRef<string | null>(null)
  const [mapReady, setMapReady] = useState(false)

  // Store onPoiClick in ref for access in marker creation
  const onPoiClickRef = useRef(onPoiClick)
  onPoiClickRef.current = onPoiClick

  // Store selectedPoi in ref
  const selectedPoiRef = useRef(selectedPoi)
  selectedPoiRef.current = selectedPoi

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return

    let cancelled = false

    const initMap = async () => {
      const maplibregl = (await import('maplibre-gl')).default
      maplibreglRef.current = maplibregl

      if (cancelled || !mapContainer.current) return

      const center: [number, number] = userLocation
        ? [userLocation.lon, userLocation.lat]
        : [79.0, 30.0]

      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            'osm-tiles': {
              type: 'raster',
              tiles: [
                'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
              ],
              tileSize: 256,
              attribution: '© OpenStreetMap contributors',
            },
          },
          layers: [
            {
              id: 'osm-layer',
              type: 'raster',
              source: 'osm-tiles',
              minzoom: 0,
              maxzoom: 19,
            },
          ],
        },
        center,
        zoom: userLocation ? 12 : 6,
        maxZoom: 18,
      })

      map.addControl(new maplibregl.NavigationControl(), 'top-right')
      map.addControl(new maplibregl.ScaleControl(), 'bottom-right')

      map.on('load', () => {
        if (!cancelled) {
          mapRef.current = map
          setMapReady(true)
        }
      })
    }

    initMap()

    return () => {
      cancelled = true
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Register global POI click handler
  useEffect(() => {
    if (onPoiClick) {
      (window as any).__poiClick = onPoiClick
    }
    return () => {
      delete (window as any).__poiClick
    }
  }, [onPoiClick])

  // Add user location marker
  useEffect(() => {
    if (!mapReady || !mapRef.current || !userLocation) return

    const map = mapRef.current
    const maplibregl = maplibreglRef.current
    const el = document.createElement('div')
    el.style.cssText = `
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #3b82f6;
      border: 4px solid white;
      box-shadow: 0 2px 8px rgba(59,130,246,0.5);
      position: relative;
    `
    const pulse = document.createElement('div')
    pulse.style.cssText = `
      position: absolute;
      top: -8px;
      left: -8px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: rgba(59,130,246,0.3);
      animation: pulse 2s infinite;
    `
    el.appendChild(pulse)

    // Add pulse animation
    const style = document.createElement('style')
    style.textContent = `@keyframes pulse { 0% { transform: scale(0.8); opacity: 1; } 100% { transform: scale(2); opacity: 0; } }`
    document.head.appendChild(style)

    new maplibregl.Marker({ element: el })
      .setLngLat([userLocation.lon, userLocation.lat])
      .setPopup(new maplibregl.Popup().setText('Your Location'))
      .addTo(map)
  }, [mapReady, userLocation])

  // Add POI markers
  useEffect(() => {
    if (!mapReady || !mapRef.current) return

    const map = mapRef.current
    const maplibregl = maplibreglRef.current

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    // Add new markers
    pois.forEach((poi) => {
      const color = POI_COLORS[poi.poi_type || poi.type || 'hospital'] || '#ef4444'
      const icon = POI_ICONS[poi.poi_type || poi.type || 'hospital'] || '?'
      const isSelected = selectedPoiRef.current?.name === poi.name

      const el = document.createElement('div')
      el.style.cssText = `
        width: ${isSelected ? '36px' : '28px'};
        height: ${isSelected ? '36px' : '28px'};
        border-radius: 50%;
        background: ${color};
        border: 3px solid ${isSelected ? '#1f2937' : 'white'};
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${isSelected ? '14px' : '11px'};
        cursor: pointer;
        transition: transform 0.2s;
        transform: ${isSelected ? 'scale(1.2)' : 'scale(1)'};
        z-index: ${isSelected ? 1000 : 1};
      `
      el.textContent = icon

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([poi.lon, poi.lat])
        .setPopup(
          new maplibregl.Popup({ offset: 25, maxWidth: '280px' }).setHTML(`
            <div style="padding: 6px 0; font-family: system-ui, sans-serif; min-width: 180px;">
              <div style="font-weight: 700; font-size: 14px; color: #111827; margin-bottom: 6px;">${poi.name}</div>
              <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};margin-right:6px;"></span>
                ${(poi.poi_type || poi.type || 'Unknown').replace('_', ' ')}
                ${poi.district ? ` • ${poi.district}` : ''}
              </div>
              ${poi.distance_km != null ? `<div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">📍 ${poi.distance_km} km away</div>` : ''}
              ${poi.capacity ? `<div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">👥 Capacity: ${poi.capacity}</div>` : ''}
              ${poi.contact ? `<div style="font-size: 12px; color: #6b7280; margin-bottom: 2px;">📞 ${poi.contact}</div>` : ''}
              <button onclick="window.__poiClick && window.__poiClick(${JSON.stringify(poi).replace(/"/g, '&quot;')})" style="margin-top: 8px; width: 100%; padding: 6px 12px; background: ${color}; color: white; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 600;">Navigate Here</button>
            </div>
          `)
        )
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Fit bounds to show all markers
    if (pois.length > 0) {
      const bounds = new maplibregl.LngLatBounds()
      if (userLocation) {
        bounds.extend([userLocation.lon, userLocation.lat])
      }
      pois.forEach((poi) => {
        bounds.extend([poi.lon, poi.lat])
      })
      map.fitBounds(bounds, { padding: 60, maxZoom: 14 })
    }
  }, [mapReady, pois, userLocation])

  // Draw route
  useEffect(() => {
    if (!mapReady || !mapRef.current) return

    const map = mapRef.current

    // Remove existing route layer
    if (routeLayerRef.current) {
      try {
        map.removeLayer(routeLayerRef.current)
        map.removeSource(routeLayerRef.current)
      } catch {}
      routeLayerRef.current = null
    }

    if (!route?.geometry || !userLocation) return

    const routeId = `route-${Date.now()}`
    routeLayerRef.current = routeId

    const coordinates = route.geometry[0] || route.geometry

    map.addSource(routeId, {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: coordinates,
        },
      },
    })

    // Route shadow
    map.addLayer({
      id: `${routeId}-shadow`,
      type: 'line',
      source: routeId,
      paint: {
        'line-color': '#1f2937',
        'line-width': 8,
        'line-opacity': 0.3,
      },
    })

    // Route line
    map.addLayer({
      id: routeId,
      type: 'line',
      source: routeId,
      paint: {
        'line-color': '#f97316',
        'line-width': 5,
        'line-dasharray': [2, 1],
      },
    })

    // Fit map to show route
    const bounds = new (maplibreglRef.current).LngLatBounds()
    bounds.extend([userLocation.lon, userLocation.lat])
    coordinates.forEach((coord: number[]) => bounds.extend(coord as [number, number]))
    map.fitBounds(bounds, { padding: 60 })
  }, [mapReady, route, userLocation])

  // Fly to selected POI
  useEffect(() => {
    if (!mapReady || !mapRef.current || !selectedPoi) return
    mapRef.current.flyTo({
      center: [selectedPoi.lon, selectedPoi.lat],
      zoom: 14,
      essential: true,
    })
  }, [mapReady, selectedPoi])

  return (
    <div className={`relative ${className}`}>
      <div ref={mapContainer} className="w-full h-full min-h-[400px] rounded-lg overflow-hidden" />

      {/* POI Legend */}
      {pois.length > 0 && (
        <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-sm rounded-lg p-2.5 shadow-lg text-xs space-y-1.5">
          <div className="font-semibold text-gray-700 mb-1">Legend</div>
          {Object.entries(POI_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <span
                className="h-4 w-4 rounded-full flex items-center justify-center text-white text-[8px] font-bold"
                style={{ background: color }}
              >
                {POI_ICONS[type]}
              </span>
              <span className="capitalize text-gray-600">{type.replace('_', ' ')}</span>
            </div>
          ))}
          <div className="flex items-center gap-2 pt-1 border-t border-gray-200">
            <span className="h-3 w-3 rounded-full bg-blue-500 border-2 border-white shadow" />
            <span className="text-gray-600">You</span>
          </div>
          {route && (
            <div className="flex items-center gap-2">
              <span className="h-0.5 w-4 bg-disaster-500 rounded" />
              <span className="text-gray-600">Route</span>
            </div>
          )}
        </div>
      )}

      {/* POI Count */}
      {pois.length > 0 && (
        <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-sm rounded-lg px-3 py-1.5 shadow-lg text-xs font-medium text-gray-700">
          {pois.length} emergency point{pois.length !== 1 ? 's' : ''} nearby
        </div>
      )}
    </div>
  )
}
