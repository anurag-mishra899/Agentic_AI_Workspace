interface PersonaSelectorProps {
  selected: string
  onChange: (persona: string) => void
}

const personas = [
  {
    id: 'friendly',
    name: 'Friendly Coach',
    description: 'Supportive and encouraging. Great for building confidence.',
  },
  {
    id: 'neutral',
    name: 'Neutral Professional',
    description: 'Balanced and fair. Standard interview experience.',
  },
  {
    id: 'aggressive',
    name: 'Stress Test',
    description: 'Challenging and direct. Prepares you for tough interviews.',
  },
  {
    id: 'faang',
    name: 'FAANG Style',
    description: 'Structured bar-raiser format. High expectations.',
  },
  {
    id: 'startup',
    name: 'Startup Rapid-fire',
    description: 'Fast-paced and practical. Focus on shipping.',
  },
]

export default function PersonaSelector({ selected, onChange }: PersonaSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {personas.map((persona) => (
        <button
          key={persona.id}
          onClick={() => onChange(persona.id)}
          className={`p-4 rounded-lg border-2 text-left transition-colors ${
            selected === persona.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <h3 className="font-medium text-gray-900">{persona.name}</h3>
          <p className="text-sm text-gray-600 mt-1">{persona.description}</p>
        </button>
      ))}
    </div>
  )
}
