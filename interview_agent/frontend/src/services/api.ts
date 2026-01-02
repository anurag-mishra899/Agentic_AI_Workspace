import axios from 'axios'
import { getToken } from './auth'

const api = axios.create({
  baseURL: '/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth endpoints
export async function login(email: string, password: string) {
  const response = await api.post('/auth/login', { email, password })
  return response.data
}

export async function register(email: string, password: string, fullName?: string) {
  const response = await api.post('/auth/register', {
    email,
    password,
    full_name: fullName,
  })
  return response.data
}

export async function getCurrentUser() {
  const response = await api.get('/users/me')
  return response.data
}

// Session endpoints
export interface SessionConfig {
  persona: string
  depth_mode: string
  domains: string[]
  declared_weak_areas?: string[]
}

export async function createSession(config: SessionConfig) {
  const response = await api.post('/sessions', config)
  return response.data
}

export async function getSession(sessionId: number) {
  const response = await api.get(`/sessions/${sessionId}`)
  return response.data
}

export async function listSessions() {
  const response = await api.get('/sessions')
  return response.data
}

export async function endSession(sessionId: number) {
  const response = await api.delete(`/sessions/${sessionId}`)
  return response.data
}

// Resume endpoints
export async function uploadResume(sessionId: number, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(`/resume/parse?session_id=${sessionId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export default api
