export type ChatMessage = { 
  role: 'user' | 'assistant'; 
  content: string; 
  citations?: any[] 
}

export type ChatSession = {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

const HISTORY_KEY = 'srm-unichat-history'
const MAX_HISTORY_ITEMS = 50

export function getHistory(): ChatSession[] {
  try {
    const stored = localStorage.getItem(HISTORY_KEY)
    if (!stored) return []
    return JSON.parse(stored)
  } catch {
    return []
  }
}

export function saveSession(session: ChatSession): void {
  try {
    const history = getHistory()
    const existingIndex = history.findIndex(s => s.id === session.id)
    
    if (existingIndex >= 0) {
      history[existingIndex] = session
    } else {
      history.unshift(session)
      // Keep only the most recent sessions
      if (history.length > MAX_HISTORY_ITEMS) {
        history.splice(MAX_HISTORY_ITEMS)
      }
    }
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
  } catch (error) {
    console.error('Failed to save session:', error)
  }
}

export function deleteSession(sessionId: string): void {
  try {
    const history = getHistory()
    const filtered = history.filter(s => s.id !== sessionId)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered))
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

export function createSession(messages: ChatMessage[]): ChatSession {
  const id = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  const title = messages[0]?.content?.substring(0, 50) || 'New Chat'
  const now = new Date().toISOString()
  
  return {
    id,
    title,
    messages,
    createdAt: now,
    updatedAt: now
  }
}

export function updateSession(sessionId: string, messages: ChatMessage[]): void {
  const history = getHistory()
  const session = history.find(s => s.id === sessionId)
  
  if (session) {
    session.messages = messages
    session.updatedAt = new Date().toISOString()
    session.title = messages[0]?.content?.substring(0, 50) || 'New Chat'
    saveSession(session)
  }
}

