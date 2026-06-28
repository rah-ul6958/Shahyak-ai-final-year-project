'use client'

import { Navigation, Clock, MapPin } from 'lucide-react'

interface RouteStep {
  instruction: string
  distance_km: number
  duration_min: number
  maneuver?: string
}

interface RoutePanelProps {
  route: {
    summary: string
    distance_km: number
    duration_seconds: number
    steps: RouteStep[]
  }
  destinationName: string
}

export default function RoutePanel({ route, destinationName }: RoutePanelProps) {
  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}h ${remainingMinutes}m`
  }

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Navigation className="h-5 w-5 text-disaster-600" />
        Route to {destinationName}
      </h3>

      {/* Route Summary */}
      <div className="flex gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">
            {route.distance_km} km
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">
            {formatDuration(route.duration_seconds)}
          </span>
        </div>
      </div>

      {/* Turn-by-Turn Directions */}
      {route.steps.length > 0 ? (
        <div className="space-y-2">
          {route.steps.map((step, idx) => (
            <div
              key={idx}
              className="flex gap-3 p-2 hover:bg-gray-50 rounded transition-colors"
            >
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-disaster-100 text-disaster-700 text-xs font-bold">
                {idx + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 truncate">{step.instruction}</p>
                <p className="text-xs text-gray-500">
                  {step.distance_km > 0 && `${step.distance_km} km`}
                  {step.distance_km > 0 && step.duration_min > 0 && ' · '}
                  {step.duration_min > 0 && `${step.duration_min} min`}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500 italic">
          Turn-by-turn directions not available for this route.
        </p>
      )}

      {/* First instruction highlight */}
      {route.steps.length > 0 && (
        <div className="mt-4 p-3 bg-disaster-50 rounded-lg border border-disaster-200">
          <p className="text-sm font-medium text-disaster-800">
            First step: {route.steps[0].instruction}
          </p>
        </div>
      )}
    </div>
  )
}
