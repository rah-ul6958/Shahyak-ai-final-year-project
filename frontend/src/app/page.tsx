'use client'

import { useState, useEffect, useCallback } from 'react'
import { AlertCircle, MapPin } from 'lucide-react'
import QueryInput from '@/components/QueryInput'
import ResponseCard from '@/components/ResponseCard'
import NavigationPanel from '@/components/NavigationPanel'
import AgentStatusIndicator from '@/components/AgentStatus'
import HardwareProfileBadge from '@/components/HardwareProfile'
import { api } from '@/lib/api'

interface TriageResult {
  hazard_type: string
  severity_level: string
  location_string: string
  confidence: number
}

interface POIInfo {
  name: string
  poi_type: string
  distance_km: number
  lat: number
  lon: number
}

interface QueryResult {
  triage: TriageResult
  instructions: string[]
  sources: string[]
  redline_triggered: boolean
  reflection_passed: boolean
  nearest_shelter?: POIInfo
  route_summary?: string
  ttfi_ms: number
}

type AgentStage = 'idle' | 'running' | 'completed' | 'error'

export default function Home() {
  const [result, setResult] = useState<QueryResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null)
  const [queryLocation, setQueryLocation] = useState<{ lat: number; lon: number } | null>(null)
  const [healthStatus, setHealthStatus] = useState<any>(null)
  const [agentStatuses, setAgentStatuses] = useState<{
    triage: AgentStage
    librarian: AgentStage
    safety: AgentStage
  }>({ triage: 'idle', librarian: 'idle', safety: 'idle' })
  const [activeTab, setActiveTab] = useState<'results' | 'map'>('results')

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          })
        },
        () => {
          // Default to Uttarakhand
          setUserLocation({ lat: 30.0672, lon: 79.0143 })
        }
      )
    } else {
      setUserLocation({ lat: 30.0672, lon: 79.0143 })
    }
  }, [])

  // Check health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await api.health()
        setHealthStatus(health)
      } catch {
        setHealthStatus(null)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const simulateAgentProgress = useCallback(() => {
    setAgentStatuses({ triage: 'running', librarian: 'idle', safety: 'idle' })
    setTimeout(() => {
      setAgentStatuses({ triage: 'completed', librarian: 'running', safety: 'idle' })
    }, 1000)
    setTimeout(() => {
      setAgentStatuses({ triage: 'completed', librarian: 'completed', safety: 'running' })
    }, 2000)
  }, [])

  const handleSubmit = async (query: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    simulateAgentProgress()

    try {
      const location = userLocation || undefined
      const response = await api.query(query, location)
      setResult(response)
      setAgentStatuses({ triage: 'completed', librarian: 'completed', safety: 'completed' })

      // Extract location from triage result for map
      if (response.triage?.location_string) {
        // Try to geocode the location (use user location as fallback)
        setQueryLocation(userLocation)
      }

      // Switch to map tab to show results
      setActiveTab('map')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setAgentStatuses({ triage: 'error', librarian: 'idle', safety: 'idle' })
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceSubmit = async (audioBlob: Blob) => {
    setLoading(true)
    setError(null)
    setResult(null)
    simulateAgentProgress()

    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.wav')

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/v1/voice`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Voice processing failed')
      }

      const data = await response.json()
      setResult(data)
      setAgentStatuses({ triage: 'completed', librarian: 'completed', safety: 'completed' })
      setQueryLocation(userLocation)
      setActiveTab('map')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Voice processing failed')
      setAgentStatuses({ triage: 'error', librarian: 'idle', safety: 'idle' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white shadow-sm sticky top-0 z-50">
        <div className="container py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-disaster-600">
                <AlertCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">SAHAYAK-AI</h1>
                <p className="text-xs text-gray-500">Disaster Response Intelligence</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {healthStatus && (
                <HardwareProfileBadge
                  profile={healthStatus.hardware_profile || 'mid'}
                  model={healthStatus.model}
                />
              )}
              <div className="flex items-center gap-1.5">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    healthStatus?.status === 'healthy'
                      ? 'bg-green-500'
                      : healthStatus
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                />
                <span className="text-xs text-gray-500">
                  {healthStatus?.status || 'Connecting...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Query and Results */}
          <div className="lg:col-span-2 space-y-5">
            {/* Hero */}
            <div className="text-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                Emergency Response in Seconds
              </h2>
              <p className="text-sm text-gray-500">
                Describe your emergency and get instant guidance from verified NDMA protocols.
              </p>
            </div>

            {/* Query Input */}
            <QueryInput
              onSubmit={handleSubmit}
              onVoiceSubmit={handleVoiceSubmit}
              loading={loading}
            />

            {/* Error */}
            {error && (
              <div className="rounded-lg bg-red-50 p-4 text-red-700 border border-red-200">
                <div className="flex gap-3">
                  <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Error</p>
                    <p className="text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Tab Switcher */}
            {result && (
              <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
                <button
                  onClick={() => setActiveTab('results')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'results'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Instructions
                </button>
                <button
                  onClick={() => setActiveTab('map')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                    activeTab === 'map'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <MapPin className="h-4 w-4" />
                  Navigation Map
                </button>
              </div>
            )}

            {/* Results Tab */}
            {result && activeTab === 'results' && (
              <ResponseCard
                triage={result.triage}
                instructions={result.instructions}
                sources={result.sources}
                redline_triggered={result.redline_triggered}
                reflection_passed={result.reflection_passed}
                ttfi_ms={result.ttfi_ms}
              />
            )}

            {/* Map Tab */}
            {activeTab === 'map' && (
              <NavigationPanel
                userLocation={userLocation || undefined}
                queryLocation={queryLocation || userLocation || undefined}
              />
            )}

            {/* Info Cards */}
            {!result && (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 mt-6">
                {[
                  { icon: '🔒', title: '100% Offline', desc: 'No internet required after setup' },
                  { icon: '⚡', title: 'Instant Response', desc: 'Guidance in seconds' },
                  { icon: '✓', title: 'Verified Protocols', desc: 'NDMA/SDMA sourced' },
                ].map((item, idx) => (
                  <div key={idx} className="text-center p-4 bg-white rounded-lg shadow-sm border border-gray-100">
                    <div className="text-3xl mb-2">{item.icon}</div>
                    <h3 className="font-semibold text-gray-900 text-sm">{item.title}</h3>
                    <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column - Status and Quick Map */}
          <div className="space-y-5">
            {/* Agent Status */}
            <AgentStatusIndicator {...agentStatuses} />

            {/* Quick Map Preview (always visible) */}
            <div className="card p-0 overflow-hidden" style={{ height: '300px' }}>
              <div className="p-3 border-b border-gray-100">
                <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-disaster-600" />
                  Quick Map
                </h3>
              </div>
              <NavigationPanel
                userLocation={userLocation || undefined}
                queryLocation={queryLocation || userLocation || undefined}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 py-6 mt-8">
        <div className="container text-center text-xs text-gray-500">
          <p>SAHAYAK-AI v1.0 — State-Aware Hazard Assistance & Yielding Action Knowledge</p>
          <p className="mt-1">B.Tech CSP497 Final Year Project, Sharda University</p>
        </div>
      </footer>
    </main>
  )
}
