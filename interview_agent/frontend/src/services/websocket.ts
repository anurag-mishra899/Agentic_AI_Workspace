import { getToken } from './auth'

export type MessageHandler = (message: WebSocketMessage) => void

export interface WebSocketMessage {
  type: 'audio' | 'transcript' | 'status' | 'error'
  data?: string
  role?: 'user' | 'assistant'
  text?: string
  status?: string
  message?: string
  session_id?: number
}

export class InterviewWebSocket {
  private ws: WebSocket | null = null
  private sessionId: number
  private messageHandler: MessageHandler
  private reconnectAttempts = 0
  private maxReconnectAttempts = 3

  constructor(sessionId: number, messageHandler: MessageHandler) {
    this.sessionId = sessionId
    this.messageHandler = messageHandler
  }

  connect(): void {
    const token = getToken()
    if (!token) {
      this.messageHandler({ type: 'error', message: 'Not authenticated' })
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/v1/ws/session/${this.sessionId}?token=${token}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.messageHandler({ type: 'status', status: 'connected' })
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage
        this.messageHandler(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    this.ws.onclose = (event) => {
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => this.connect(), 2000 * this.reconnectAttempts)
      } else {
        this.messageHandler({ type: 'status', status: 'disconnected' })
      }
    }

    this.ws.onerror = () => {
      this.messageHandler({ type: 'error', message: 'WebSocket error' })
    }
  }

  sendAudio(audioData: ArrayBuffer): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const base64 = btoa(
        String.fromCharCode(...new Uint8Array(audioData))
      )
      this.ws.send(JSON.stringify({ type: 'audio', data: base64 }))
    }
  }

  sendControl(action: 'mute' | 'unmute' | 'end'): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'control', action }))
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000)
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}
