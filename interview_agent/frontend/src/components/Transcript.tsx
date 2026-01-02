import { useEffect, useRef } from 'react'

interface TranscriptEntry {
  role: 'user' | 'assistant'
  text: string
  timestamp: Date
}

interface TranscriptProps {
  entries: TranscriptEntry[]
}

export default function Transcript({ entries }: TranscriptProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new entries are added
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [entries])

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4"
    >
      {entries.length === 0 ? (
        <p className="text-gray-500 text-center mt-8">
          The conversation will appear here...
        </p>
      ) : (
        entries.map((entry, index) => (
          <div
            key={index}
            className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                entry.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-100'
              }`}
            >
              <p className="text-xs text-opacity-70 mb-1">
                {entry.role === 'user' ? 'You' : 'Interviewer'}
              </p>
              <p className="text-sm">{entry.text}</p>
              <p className="text-xs text-opacity-50 mt-1">
                {entry.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
