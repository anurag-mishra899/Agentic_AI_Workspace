import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSession, uploadResume, SessionConfig as SessionConfigType } from '../services/api'
import PersonaSelector from '../components/PersonaSelector'
import DepthSelector from '../components/DepthSelector'
import DomainSelector from '../components/DomainSelector'
import ResumeUpload from '../components/ResumeUpload'
import WeakAreaInput from '../components/WeakAreaInput'

interface SessionConfigProps {
  onLogout: () => void
}

export default function SessionConfig({ onLogout }: SessionConfigProps) {
  const navigate = useNavigate()
  const [persona, setPersona] = useState('neutral')
  const [depthMode, setDepthMode] = useState('interview_ready')
  const [domains, setDomains] = useState<string[]>(['coding'])
  const [weakAreas, setWeakAreas] = useState<string[]>([])
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const canStart = (resumeFile || weakAreas.length > 0) && domains.length > 0

  const handleStart = async () => {
    if (!canStart) return

    setLoading(true)
    setError('')

    try {
      const config: SessionConfigType = {
        persona,
        depth_mode: depthMode,
        domains,
        declared_weak_areas: weakAreas.length > 0 ? weakAreas : undefined,
      }

      const session = await createSession(config)

      if (resumeFile) {
        await uploadResume(session.id, resumeFile)
      }

      navigate(`/session/${session.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start session')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Interview Practice Setup</h1>
          <button
            onClick={onLogout}
            className="text-gray-600 hover:text-gray-900"
          >
            Logout
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 space-y-8">
          {/* Resume Upload */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Resume (Optional)</h2>
            <ResumeUpload onFileSelect={setResumeFile} selectedFile={resumeFile} />
          </section>

          {/* Weak Areas */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Weak Areas to Focus On</h2>
            <p className="text-sm text-gray-600 mb-3">
              Tell us what you want to improve (e.g., "Dynamic Programming", "System Design scaling")
            </p>
            <WeakAreaInput weakAreas={weakAreas} onChange={setWeakAreas} />
          </section>

          {!resumeFile && weakAreas.length === 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <p className="text-yellow-800 text-sm">
                Please upload a resume OR declare at least one weak area to start.
              </p>
            </div>
          )}

          {/* Persona Selection */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Interview Style</h2>
            <PersonaSelector selected={persona} onChange={setPersona} />
          </section>

          {/* Depth Selection */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Depth Level</h2>
            <DepthSelector selected={depthMode} onChange={setDepthMode} />
          </section>

          {/* Domain Selection */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Domains to Cover</h2>
            <DomainSelector selected={domains} onChange={setDomains} />
          </section>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}

          {/* Start Button */}
          <div className="pt-4">
            <button
              onClick={handleStart}
              disabled={!canStart || loading}
              className="w-full py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Starting...' : 'Start Interview'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
