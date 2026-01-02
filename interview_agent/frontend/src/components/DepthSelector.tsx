interface DepthSelectorProps {
  selected: string
  onChange: (depth: string) => void
}

const depths = [
  {
    id: 'surface',
    name: 'Surface Review',
    description: 'High-level understanding. Breadth over depth.',
  },
  {
    id: 'interview_ready',
    name: 'Interview Ready',
    description: 'Common follow-ups and typical traps. Balanced preparation.',
  },
  {
    id: 'expert',
    name: 'Expert / Stress Test',
    description: 'Edge cases, theoretical limits, design tradeoffs.',
  },
]

export default function DepthSelector({ selected, onChange }: DepthSelectorProps) {
  return (
    <div className="space-y-3">
      {depths.map((depth) => (
        <label
          key={depth.id}
          className={`flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors ${
            selected === depth.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <input
            type="radio"
            name="depth"
            value={depth.id}
            checked={selected === depth.id}
            onChange={() => onChange(depth.id)}
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
          />
          <div className="ml-3">
            <span className="font-medium text-gray-900">{depth.name}</span>
            <p className="text-sm text-gray-600">{depth.description}</p>
          </div>
        </label>
      ))}
    </div>
  )
}
