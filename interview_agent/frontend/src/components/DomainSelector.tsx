interface DomainSelectorProps {
  selected: string[]
  onChange: (domains: string[]) => void
}

const domains = [
  {
    id: 'coding',
    name: 'Coding',
    description: 'DSA, APIs, debugging, testing strategies',
  },
  {
    id: 'system_design',
    name: 'System Design',
    description: 'Scaling, consistency, availability, architecture',
  },
  {
    id: 'ml',
    name: 'Machine Learning',
    description: 'Theory, applied ML, MLOps, production systems',
  },
]

export default function DomainSelector({ selected, onChange }: DomainSelectorProps) {
  const toggleDomain = (domainId: string) => {
    if (selected.includes(domainId)) {
      onChange(selected.filter((d) => d !== domainId))
    } else {
      onChange([...selected, domainId])
    }
  }

  return (
    <div className="space-y-3">
      {domains.map((domain) => (
        <label
          key={domain.id}
          className={`flex items-start p-4 rounded-lg border-2 cursor-pointer transition-colors ${
            selected.includes(domain.id)
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <input
            type="checkbox"
            checked={selected.includes(domain.id)}
            onChange={() => toggleDomain(domain.id)}
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
          />
          <div className="ml-3">
            <span className="font-medium text-gray-900">{domain.name}</span>
            <p className="text-sm text-gray-600">{domain.description}</p>
          </div>
        </label>
      ))}
      {selected.length === 0 && (
        <p className="text-sm text-red-600">Please select at least one domain</p>
      )}
    </div>
  )
}
