import { useState } from 'react'

interface WeakAreaInputProps {
  weakAreas: string[]
  onChange: (areas: string[]) => void
}

export default function WeakAreaInput({ weakAreas, onChange }: WeakAreaInputProps) {
  const [input, setInput] = useState('')

  const handleAdd = () => {
    const trimmed = input.trim()
    if (trimmed && !weakAreas.includes(trimmed)) {
      onChange([...weakAreas, trimmed])
      setInput('')
    }
  }

  const handleRemove = (area: string) => {
    onChange(weakAreas.filter((a) => a !== area))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }

  const suggestions = [
    'Dynamic Programming',
    'System Design scaling',
    'SQL window functions',
    'Backpropagation',
    'Graph algorithms',
    'Distributed systems',
  ]

  return (
    <div>
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., Dynamic Programming"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
        <button
          onClick={handleAdd}
          disabled={!input.trim()}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Add
        </button>
      </div>

      {/* Tags */}
      {weakAreas.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {weakAreas.map((area) => (
            <span
              key={area}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              {area}
              <button
                onClick={() => handleRemove(area)}
                className="ml-2 text-blue-600 hover:text-blue-500"
              >
                &times;
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Suggestions */}
      {weakAreas.length === 0 && (
        <div className="mt-3">
          <p className="text-sm text-gray-500 mb-2">Suggestions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => onChange([...weakAreas, suggestion])}
                className="px-3 py-1 text-sm text-gray-700 bg-gray-100 rounded-full hover:bg-gray-200"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
