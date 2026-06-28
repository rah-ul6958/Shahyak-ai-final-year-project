'use client'

import { Loader, CheckCircle, AlertCircle, RotateCw } from 'lucide-react'

type AgentStatus = 'idle' | 'running' | 'completed' | 'error'

interface AgentStatusProps {
  triage: AgentStatus
  librarian: AgentStatus
  safety: AgentStatus
}

const statusConfig = {
  idle: {
    icon: null,
    color: 'bg-gray-200',
    textColor: 'text-gray-500',
    label: 'Waiting',
  },
  running: {
    icon: Loader,
    color: 'bg-disaster-500',
    textColor: 'text-disaster-600',
    label: 'Processing',
  },
  completed: {
    icon: CheckCircle,
    color: 'bg-green-500',
    textColor: 'text-green-600',
    label: 'Complete',
  },
  error: {
    icon: AlertCircle,
    color: 'bg-red-500',
    textColor: 'text-red-600',
    label: 'Error',
  },
}

const agents = [
  { key: 'triage', label: 'Triage Agent', description: 'Classifies hazard type and severity' },
  { key: 'librarian', label: 'Librarian Agent', description: 'Retrieves NDMA protocols' },
  { key: 'safety', label: 'Safety Agent', description: 'Generates safe instructions' },
] as const

export default function AgentStatusIndicator({
  triage,
  librarian,
  safety,
}: AgentStatusProps) {
  const statuses = { triage, librarian, safety }

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <RotateCw className="h-5 w-5 text-disaster-600" />
        Pipeline Status
      </h3>

      <div className="space-y-3">
        {agents.map((agent, idx) => {
          const status = statuses[agent.key as keyof typeof statuses]
          const config = statusConfig[status]
          const Icon = config.icon

          return (
            <div key={agent.key} className="flex items-center gap-3">
              {/* Step number */}
              <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-100 text-sm font-bold text-gray-600">
                {idx + 1}
              </span>

              {/* Connector line */}
              {idx < agents.length - 1 && (
                <div
                  className={`absolute left-[1.75rem] mt-10 w-0.5 h-6 ${
                    status === 'completed' ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}

              {/* Agent info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-900">{agent.label}</p>
                  {Icon && (
                    <Icon
                      className={`h-4 w-4 ${config.textColor} ${
                        status === 'running' ? 'animate-spin' : ''
                      }`}
                    />
                  )}
                  <span className={`text-xs ${config.textColor}`}>{config.label}</span>
                </div>
                <p className="text-xs text-gray-500">{agent.description}</p>
              </div>

              {/* Status indicator */}
              <div
                className={`h-3 w-3 rounded-full ${config.color} ${
                  status === 'running' ? 'animate-pulse' : ''
                }`}
              />
            </div>
          )
        })}
      </div>
    </div>
  )
}
