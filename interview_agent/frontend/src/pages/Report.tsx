import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { getSession } from '../services/api'

interface SessionDetail {
  id: number
  persona: string
  depth_mode: string
  domains: string[]
  status: string
  feedback_report: string | null
  declared_weak_areas: string[] | null
}

export default function Report() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [session, setSession] = useState<SessionDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSession = async () => {
      if (!sessionId) return

      try {
        const data = await getSession(parseInt(sessionId))
        setSession(data)
      } catch (e: any) {
        setError(e.response?.data?.detail || 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }

    fetchSession()
  }, [sessionId])

  const handleDownload = () => {
    if (!session?.feedback_report) return

    const blob = new Blob([session.feedback_report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `interview-report-${sessionId}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleNewSession = () => {
    navigate('/config')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Generating report...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={handleNewSession}
            className="text-blue-600 hover:text-blue-500"
          >
            Start New Session
          </button>
        </div>
      </div>
    )
  }

  // Generate a placeholder report if none exists
  const report = session?.feedback_report || generatePlaceholderReport(session)

  return (
    <div className="min-h-screen py-8 px-4 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Session Feedback</h1>
          <div className="space-x-4">
            <button
              onClick={handleDownload}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Download Report
            </button>
            <button
              onClick={handleNewSession}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              New Session
            </button>
          </div>
        </div>

        {/* Report Content */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  )
}

function generatePlaceholderReport(session: SessionDetail | null): string {
  if (!session) return '# Report Not Available'

  return `# Interview Practice Feedback Report

Generated: ${new Date().toISOString().split('T')[0]}

---

## Session Summary

| Metric | Value |
|--------|-------|
| **Persona** | ${session.persona} |
| **Depth Mode** | ${session.depth_mode.replace('_', ' ')} |
| **Domains** | ${session.domains.join(', ')} |
| **Status** | ${session.status} |

## Structured Scorecard

*Detailed scoring will be available after full session completion with Azure OpenAI integration.*

## Detailed Analysis

This session was conducted using the **${session.persona}** interview style at **${session.depth_mode.replace('_', ' ')}** depth level.

### Domains Covered
${session.domains.map(d => `- ${d.replace('_', ' ')}`).join('\n')}

${session.declared_weak_areas?.length ? `
### Declared Weak Areas
${session.declared_weak_areas.map(a => `- ${a}`).join('\n')}
` : ''}

## Next Steps

1. Review the areas covered in this session
2. Practice additional sessions focusing on identified weak areas
3. Gradually increase depth level as you improve

---

*Full feedback reports will be available when Azure OpenAI Realtime integration is configured.*
`
}
