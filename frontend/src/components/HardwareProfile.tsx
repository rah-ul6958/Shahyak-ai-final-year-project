'use client'

import { Cpu } from 'lucide-react'

interface HardwareProfileProps {
  profile: 'low' | 'mid' | 'high'
  model?: string
}

const profileConfig = {
  low: {
    label: 'Low-End',
    description: 'CPU-only, Gemma-2 2B',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    dotColor: 'bg-yellow-500',
  },
  mid: {
    label: 'Mid-Range',
    description: '16GB RAM, LLaMA-3 8B Q4',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    dotColor: 'bg-blue-500',
  },
  high: {
    label: 'High-End',
    description: '32GB+ RAM + GPU, LLaMA-3 8B',
    color: 'bg-green-100 text-green-800 border-green-200',
    dotColor: 'bg-green-500',
  },
}

export default function HardwareProfileBadge({
  profile,
  model,
}: HardwareProfileProps) {
  const config = profileConfig[profile]

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${config.color}`}
    >
      <Cpu className="h-4 w-4" />
      <div className="flex items-center gap-1.5">
        <span className={`h-2 w-2 rounded-full ${config.dotColor}`} />
        <span className="text-sm font-medium">{config.label}</span>
      </div>
      {model && (
        <span className="text-xs opacity-75 ml-1">({model})</span>
      )}
    </div>
  )
}
