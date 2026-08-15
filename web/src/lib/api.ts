// @ts-ignore - Vite env types
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function http<T>(path: string, opts?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...opts,
      headers: {
        'Content-Type': 'application/json',
        ...(opts?.headers || {}),
      },
    })
    if (!res.ok) {
      const errorText = await res.text()
      let errorDetail = errorText
      try {
        const errorObj = JSON.parse(errorText)
        errorDetail = errorObj.detail || errorObj.message || errorText
      } catch {
        // If not JSON, use the raw text
      }
      throw new Error(errorDetail)
    }
    return res.json()
  } catch (error: any) {
    // Handle network errors (CORS, connection refused, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Failed to connect to backend. Please ensure the backend is running at ${API_BASE}`)
    }
    // Re-throw other errors
    throw error
  }
}

export type AskResponse = {
  answer_html: string
  citations: { title: string; url?: string; source_type: string; page?: number; chunk_id?: string }[]
  followups: string[]
  query_rewrite: string
  safety_notes: string
}

export type LoginRequest = {
  roll_no: string
  dob: string
}

export type LoginResponse = {
  success: boolean
  message: string
  user_id?: string
  roll_no?: string
}

export type DocumentStatus = {
  document_id: string
  title: string
  status: 'queued' | 'processed'
  chunk_count: number
  message: string
  created_at: string | null
}

export const api = {
  health: () => http('/api/health'),
  login: (body: LoginRequest) => 
    http<LoginResponse>('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  register: (body: LoginRequest) => 
    http<LoginResponse>('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  ask: (body: { question: string; filters?: Record<string, string> }) =>
    http<AskResponse>('/api/ask', { method: 'POST', body: JSON.stringify(body) }),
  search: (q: string, k = 5) => http(`/api/search?query=${encodeURIComponent(q)}&k=${k}`),
  ingestFile: async (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch(`${API_BASE}/api/ingest/file`, { method: 'POST', body: fd })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },
  getDocumentStatus: (documentId: string) => 
    http<DocumentStatus>(`/api/ingest/status/${documentId}`),
}


