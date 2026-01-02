import { useEffect, useRef } from 'react'

interface AudioWaveformProps {
  isActive: boolean
}

export default function AudioWaveform({ isActive }: AudioWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const bars = 40
    const barWidth = canvas.width / bars
    const heights = new Array(bars).fill(0)

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (let i = 0; i < bars; i++) {
        // Generate smooth wave pattern
        if (isActive) {
          const targetHeight = Math.sin(Date.now() / 200 + i * 0.3) * 30 + 40
          heights[i] += (targetHeight - heights[i]) * 0.1
        } else {
          heights[i] *= 0.95
        }

        const height = Math.max(4, heights[i])
        const x = i * barWidth + barWidth / 4
        const y = (canvas.height - height) / 2

        ctx.fillStyle = isActive ? '#3B82F6' : '#6B7280'
        ctx.fillRect(x, y, barWidth / 2, height)
      }

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isActive])

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={400}
        height={100}
        className="rounded-lg"
      />
      <div className="mt-4 text-center">
        <div
          className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
            isActive ? 'bg-blue-500' : 'bg-gray-600'
          }`}
        >
          <svg
            className="w-8 h-8 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z" />
          </svg>
        </div>
        <p className="text-gray-400 text-sm mt-2">
          {isActive ? 'Listening...' : 'Microphone ready'}
        </p>
      </div>
    </div>
  )
}
