'use client'

import { useState, useRef, useCallback } from 'react'
import { Send, Mic, MicOff, Loader } from 'lucide-react'

interface QueryInputProps {
  onSubmit: (query: string) => void
  onVoiceSubmit?: (audioBlob: Blob) => void
  loading?: boolean
  disabled?: boolean
}

export default function QueryInput({
  onSubmit,
  onVoiceSubmit,
  loading = false,
  disabled = false,
}: QueryInputProps) {
  const [query, setQuery] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !loading && !disabled) {
      onSubmit(query.trim())
    }
  }

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/wav' })

      audioChunksRef.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        if (onVoiceSubmit) {
          onVoiceSubmit(audioBlob)
        }
        stream.getTracks().forEach((track) => track.stop())
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsRecording(true)
    } catch (err) {
      console.error('Failed to start recording:', err)
    }
  }, [onVoiceSubmit])

  const stopRecording = useCallback(() => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setIsRecording(false)
      setMediaRecorder(null)
    }
  }, [mediaRecorder])

  return (
    <form onSubmit={handleSubmit} className="card mb-8">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Describe your emergency:
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., There is a fire in Mumbai with thick smoke and people need evacuation..."
          className="input-base h-24 resize-none"
          disabled={loading || disabled || isRecording}
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading || disabled || !query.trim() || isRecording}
          className="btn-primary flex-1 gap-2"
        >
          {loading ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              Get Guidance
            </>
          )}
        </button>

        <button
          type="button"
          disabled={loading || disabled}
          onClick={isRecording ? stopRecording : startRecording}
          className={`gap-2 ${
            isRecording
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'btn-secondary'
          }`}
        >
          {isRecording ? (
            <>
              <MicOff className="h-5 w-5" />
              Stop
            </>
          ) : (
            <>
              <Mic className="h-5 w-5" />
              Voice
            </>
          )}
        </button>
      </div>

      {isRecording && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600">
          <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
          Recording... Speak now
        </div>
      )}
    </form>
  )
}
