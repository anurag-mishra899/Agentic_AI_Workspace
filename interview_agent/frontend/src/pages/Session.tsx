import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { InterviewWebSocket, WebSocketMessage } from '../services/websocket'
import { endSession } from '../services/api'
import AudioWaveform from '../components/AudioWaveform'
import Transcript from '../components/Transcript'
import SessionControls from '../components/SessionControls'

interface TranscriptEntry {
  role: 'user' | 'assistant'
  text: string
  timestamp: Date
}

export default function Session() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()

  const [status, setStatus] = useState<string>('connecting')
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const [isMuted, setIsMuted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<InterviewWebSocket | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'status':
        setStatus(message.status || 'unknown')
        break
      case 'transcript':
        if (message.role && message.text) {
          setTranscript((prev) => [
            ...prev,
            {
              role: message.role as 'user' | 'assistant',
              text: message.text,
              timestamp: new Date(),
            },
          ])
        }
        break
      case 'audio':
        // Handle incoming audio from AI
        if (message.data) {
          playAudio(message.data)
        }
        break
      case 'error':
        setError(message.message || 'Unknown error')
        break
    }
  }, [])

  const playAudio = async (base64Audio: string) => {
    try {
      const audioData = atob(base64Audio)
      const arrayBuffer = new ArrayBuffer(audioData.length)
      const view = new Uint8Array(arrayBuffer)
      for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i)
      }

      // In production, decode and play the PCM audio
      // This is a simplified version
      const audioContext = new AudioContext({ sampleRate: 24000 })
      const audioBuffer = audioContext.createBuffer(1, view.length / 2, 24000)
      const channelData = audioBuffer.getChannelData(0)

      for (let i = 0; i < view.length / 2; i++) {
        const sample = (view[i * 2] | (view[i * 2 + 1] << 8)) / 32768
        channelData[i] = sample
      }

      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.destination)
      source.start()
    } catch (e) {
      console.error('Failed to play audio:', e)
    }
  }

  useEffect(() => {
    if (!sessionId) return

    // Connect WebSocket
    wsRef.current = new InterviewWebSocket(parseInt(sessionId), handleMessage)
    wsRef.current.connect()

    // Set up audio capture
    setupAudioCapture()

    return () => {
      wsRef.current?.disconnect()
      stopAudioCapture()
    }
  }, [sessionId, handleMessage])

  const setupAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 24000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      })
      mediaStreamRef.current = stream

      audioContextRef.current = new AudioContext({ sampleRate: 24000 })
      const source = audioContextRef.current.createMediaStreamSource(stream)

      // Use ScriptProcessorNode for simplicity (deprecated but widely supported)
      processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1)

      processorRef.current.onaudioprocess = (e) => {
        if (isMuted || !wsRef.current?.isConnected()) return

        const inputData = e.inputBuffer.getChannelData(0)
        const pcm16 = new Int16Array(inputData.length)

        for (let i = 0; i < inputData.length; i++) {
          pcm16[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768))
        }

        wsRef.current?.sendAudio(pcm16.buffer)
      }

      source.connect(processorRef.current)
      processorRef.current.connect(audioContextRef.current.destination)
    } catch (e) {
      setError('Failed to access microphone. Please grant permission.')
    }
  }

  const stopAudioCapture = () => {
    processorRef.current?.disconnect()
    audioContextRef.current?.close()
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop())
  }

  const handleMuteToggle = () => {
    setIsMuted(!isMuted)
    wsRef.current?.sendControl(isMuted ? 'unmute' : 'mute')
  }

  const handleEndSession = async () => {
    if (!sessionId) return

    try {
      wsRef.current?.sendControl('end')
      wsRef.current?.disconnect()
      await endSession(parseInt(sessionId))
      navigate(`/report/${sessionId}`)
    } catch (e) {
      // Session may have ended already, navigate anyway
      navigate(`/report/${sessionId}`)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 px-4 py-3 flex items-center justify-between">
        <h1 className="text-white font-semibold">Interview Session</h1>
        <div className="flex items-center space-x-2">
          <span
            className={`w-2 h-2 rounded-full ${
              status === 'connected' || status === 'listening'
                ? 'bg-green-500'
                : status === 'speaking'
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
          />
          <span className="text-gray-300 text-sm capitalize">{status}</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Audio Visualization */}
        <div className="w-1/2 flex flex-col items-center justify-center p-8 border-r border-gray-700">
          <AudioWaveform isActive={status === 'speaking' || status === 'listening'} />

          {error && (
            <div className="mt-4 text-red-400 text-sm">{error}</div>
          )}

          <SessionControls
            isMuted={isMuted}
            onMuteToggle={handleMuteToggle}
            onEndSession={handleEndSession}
          />
        </div>

        {/* Right Panel - Transcript */}
        <div className="w-1/2 flex flex-col bg-gray-800">
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-white font-medium">Live Transcript</h2>
          </div>
          <Transcript entries={transcript} />
        </div>
      </div>
    </div>
  )
}
