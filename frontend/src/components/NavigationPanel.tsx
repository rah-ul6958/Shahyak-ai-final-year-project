'use client'

import { useState, useEffect, useCallback } from 'react'
import { Navigation, MapPin, Clock, Phone, Users, ChevronDown, ChevronUp, Loader, AlertCircle } from 'lucide-react'
import MapView, { POI, RouteData } from './MapView'

interface NavigationPanelProps {
  userLocation?: { lat: number; lon: number }
  queryLocation?: { lat: number; lon: number }
  onNavigate?: (poi: POI) => void
}

const POI_TYPE_LABELS: Record<string, string> = {
  hospital: 'Hospital',
  shelter: 'Shelter',
  police_station: 'Police Station',
  relief_centre: 'Relief Centre',
}

const POI_TYPE_COLORS: Record<string, string> = {
  hospital: 'bg-red-100 text-red-800 border-red-200',
  shelter: 'bg-blue-100 text-blue-800 border-blue-200',
  police_station: 'bg-purple-100 text-purple-800 border-purple-200',
  relief_centre: 'bg-amber-100 text-amber-800 border-amber-200',
}

export default function NavigationPanel({
  userLocation,
  queryLocation,
  onNavigate,
}: NavigationPanelProps) {
  const [nearbyPois, setNearbyPois] = useState<POI[]>([])
  const [selectedPoi, setSelectedPoi] = useState<POI | null>(null)
  const [route, setRoute] = useState<RouteData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)
  const [filterType, setFilterType] = useState<string>('all')

  const location = queryLocation || userLocation

  // Fetch nearby POIs
  const fetchNearbyPois = useCallback(async () => {
    if (!location) return

    setLoading(true)
    setError(null)

    try {
      const types = ['hospital', 'shelter', 'police_station', 'relief_centre']
      const allPois: POI[] = []

      for (const type of types) {
        try {
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/poi?lat=${location.lat}&lon=${location.lon}&poi_type=${type}&radius_km=50`
          )
          if (res.ok) {
            const data = await res.json()
            if (data.poi) {
              allPois.push({
                ...data.poi,
                poi_type: type,
              })
            }
          }
        } catch {}
      }

      if (allPois.length > 0) {
        // Sort by distance
        allPois.sort((a, b) => (a.distance_km || 0) - (b.distance_km || 0))
        setNearbyPois(allPois)
      } else {
        setError('No emergency points found nearby. Try expanding your search area.')
      }
    } catch (err) {
      setError('Failed to load emergency points. Check if the backend is running.')
    } finally {
      setLoading(false)
    }
  }, [location])

  useEffect(() => {
    fetchNearbyPois()
  }, [fetchNearbyPois])

  // Fetch route when a POI is selected
  const handlePoiSelect = useCallback(async (poi: POI) => {
    if (!location) return

    setSelectedPoi(poi)
    setRoute(null)
    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/route?from_lat=${location.lat}&from_lon=${location.lon}&poi_type=${poi.poi_type || 'shelter'}`
      )

      if (response.ok) {
        const data = await response.json()
        if (data.route) {
          setRoute(data.route)
        }
      }
    } catch (err) {
      console.error('Route fetch failed:', err)
    } finally {
      setLoading(false)
    }

    onNavigate?.(poi)
  }, [location, onNavigate])

  const handleMapPoiClick = useCallback((poi: POI) => {
    handlePoiSelect(poi)
  }, [handlePoiSelect])

  // Filter POIs
  const filteredPois = filterType === 'all'
    ? nearbyPois
    : nearbyPois.filter((p) => (p.poi_type || p.type) === filterType)

  const displayedPois = showAll ? filteredPois : filteredPois.slice(0, 5)

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remaining = minutes % 60
    return `${hours}h ${remaining}m`
  }

  return (
    <div className="space-y-4">
      {/* Map */}
      <div className="card p-0 overflow-hidden" style={{ height: '450px' }}>
        <MapView
          userLocation={userLocation}
          pois={filteredPois}
          selectedPoi={selectedPoi}
          route={route}
          onPoiClick={handleMapPoiClick}
          className="h-full"
        />
      </div>

      {/* Filter Chips */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilterType('all')}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            filterType === 'all'
              ? 'bg-disaster-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          All ({nearbyPois.length})
        </button>
        {Object.entries(POI_TYPE_LABELS).map(([type, label]) => {
          const count = nearbyPois.filter((p) => (p.poi_type || p.type) === type).length
          return (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filterType === type
                  ? 'bg-disaster-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {label} ({count})
            </button>
          )
        })}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Loader className="h-4 w-4 animate-spin" />
          <span>Loading emergency points...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* POI List */}
      {displayedPois.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-700">
            Nearby Emergency Points ({filteredPois.length})
          </h3>

          {displayedPois.map((poi, idx) => {
            const type = poi.poi_type || poi.type || 'hospital'
            const isSelected = selectedPoi?.name === poi.name

            return (
              <div
                key={`${poi.name}-${idx}`}
                onClick={() => handlePoiSelect(poi)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-disaster-500 bg-disaster-50 ring-1 ring-disaster-500'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm ${
                    type === 'hospital' ? 'bg-red-500' :
                    type === 'shelter' ? 'bg-blue-500' :
                    type === 'police_station' ? 'bg-purple-500' :
                    'bg-amber-500'
                  }`}>
                    {type === 'hospital' ? 'H' :
                     type === 'shelter' ? 'S' :
                     type === 'police_station' ? 'P' : 'R'}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-gray-900 truncate">{poi.name}</p>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${POI_TYPE_COLORS[type] || 'bg-gray-100 text-gray-600'}`}>
                        {POI_TYPE_LABELS[type] || type}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {poi.distance_km != null && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {poi.distance_km} km
                        </span>
                      )}
                      {poi.capacity && (
                        <span className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {poi.capacity}
                        </span>
                      )}
                      {poi.contact && (
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {poi.contact}
                        </span>
                      )}
                    </div>
                    {poi.district && (
                      <p className="text-xs text-gray-400 mt-0.5">{poi.district}</p>
                    )}
                  </div>

                  {isSelected && (
                    <div className="flex-shrink-0">
                      <Navigation className="h-5 w-5 text-disaster-600" />
                    </div>
                  )}
                </div>
              </div>
            )
          })}

          {filteredPois.length > 5 && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="w-full text-center text-sm text-disaster-600 hover:text-disaster-700 py-2"
            >
              {showAll ? (
                <span className="flex items-center justify-center gap-1">
                  Show less <ChevronUp className="h-4 w-4" />
                </span>
              ) : (
                <span className="flex items-center justify-center gap-1">
                  Show all {filteredPois.length} <ChevronDown className="h-4 w-4" />
                </span>
              )}
            </button>
          )}
        </div>
      )}

      {/* Route Details */}
      {selectedPoi && route && (
        <div className="card border-disaster-200 bg-disaster-50/30">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Navigation className="h-4 w-4 text-disaster-600" />
            Route to {selectedPoi.name}
          </h3>

          {/* Summary */}
          <div className="flex gap-4 mb-3 p-2 bg-white rounded-lg border border-gray-100">
            <div className="flex items-center gap-1.5 text-sm">
              <MapPin className="h-4 w-4 text-disaster-500" />
              <span className="font-medium">{route.distance_km} km</span>
            </div>
            {route.duration_seconds != null && (
              <div className="flex items-center gap-1.5 text-sm">
                <Clock className="h-4 w-4 text-disaster-500" />
                <span className="font-medium">{formatDuration(route.duration_seconds)}</span>
              </div>
            )}
          </div>

          {/* Steps */}
          {route.steps && route.steps.length > 0 && (
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {route.steps.map((step, idx) => (
                <div
                  key={idx}
                  className="flex gap-2.5 p-2 bg-white rounded text-xs"
                >
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-disaster-100 text-disaster-700 flex items-center justify-center font-bold text-[10px]">
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-700">{step.instruction}</p>
                    <p className="text-gray-400 text-[11px]">
                      {step.distance_km > 0 && `${step.distance_km} km`}
                      {step.distance_km > 0 && step.duration_min > 0 && ' · '}
                      {step.duration_min > 0 && `${step.duration_min} min`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* First step highlight */}
          {route.steps && route.steps.length > 0 && (
            <div className="mt-3 p-2.5 bg-disaster-100 rounded-lg border border-disaster-200">
              <p className="text-xs font-semibold text-disaster-800">
                First step: {route.steps[0].instruction}
              </p>
            </div>
          )}

          {/* Contact button */}
          {selectedPoi.contact && (
            <a
              href={`tel:${selectedPoi.contact.replace(/[^0-9+]/g, '')}`}
              className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-disaster-600 text-white rounded-lg text-sm font-medium hover:bg-disaster-700 transition-colors"
            >
              <Phone className="h-4 w-4" />
              Call {selectedPoi.name}
            </a>
          )}
        </div>
      )}
    </div>
  )
}
