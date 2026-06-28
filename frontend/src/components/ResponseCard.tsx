'use client'

import { AlertCircle, Shield, CheckCircle, XCircle } from 'lucide-react'
import { getHazardColor, getSeverityColor } from '@/lib/api'

interface TriageResult {
  hazard_type: string
  severity_level: string
  location_string: string
  confidence: number
}

interface ResponseCardProps {
  triage: TriageResult
  instructions: string[]
  sources: string[]
  redline_triggered: boolean
  reflection_passed: boolean
  ttfi_ms: number
}

export default function ResponseCard({
  triage,
  instructions,
  sources,
  redline_triggered,
  reflection_passed,
  ttfi_ms,
}: ResponseCardProps) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Triage Info */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-disaster-600" />
          Emergency Classification
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Type</p>
            <span
              className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${getHazardColor(
                triage.hazard_type
              )}`}
            >
              {triage.hazard_type}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-600">Severity</p>
            <span
              className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${getSeverityColor(
                triage.severity_level
              )}`}
            >
              {triage.severity_level}
            </span>
          </div>
          <div className="col-span-2">
            <p className="text-sm text-gray-600">Location</p>
            <p className="text-gray-900">{triage.location_string}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Confidence</p>
            <p className="text-gray-900">{(triage.confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Recommended Actions
        </h3>
        <ol className="space-y-3">
          {instructions.map((instruction, idx) => (
            <li key={idx} className="flex gap-3">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-disaster-600 text-xs font-bold text-white">
                {idx + 1}
              </span>
              <span className="pt-0.5 text-gray-700">{instruction}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Safety Status */}
      <div className="card">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Shield className="h-5 w-5 text-disaster-600" />
          Safety Verification
        </h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            {redline_triggered ? (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            ) : (
              <CheckCircle className="h-4 w-4 text-green-500" />
            )}
            <span className="text-sm text-gray-700">
              Redline Check: {redline_triggered ? 'Override Applied' : 'Passed'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {reflection_passed ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
            <span className="text-sm text-gray-700">
              Self-Reflection: {reflection_passed ? 'Passed' : 'Failed'}
            </span>
          </div>
        </div>
      </div>

      {/* Redline Warning */}
      {redline_triggered && (
        <div className="rounded-lg bg-yellow-50 p-4 border border-yellow-200">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-yellow-800">Safety Override Applied</p>
              <p className="text-sm text-yellow-700">
                Dangerous instructions were detected and replaced with safe alternatives.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="text-sm text-gray-500 space-y-1">
        <p>Response time: {ttfi_ms.toFixed(0)}ms</p>
        <p>Sources: {sources.length} verified protocols</p>
        {sources.length > 0 && (
          <div className="mt-2">
            <p className="font-medium text-gray-600">Referenced Documents:</p>
            <ul className="list-disc list-inside text-xs">
              {sources.map((source, idx) => (
                <li key={idx}>{source}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
