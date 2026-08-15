import { useMemo, useState, useRef, useEffect } from 'react'
import Message from './Message'
import Sources from './Sources'
import { api, AskResponse } from '../lib/api'
import { saveSession, createSession, updateSession, getHistory, type ChatMessage, type ChatSession } from '../lib/history'

type PresetQuestion = {
  id: number
  text: string
}

type Props = {
  inputValue?: string
  onInputChange?: (input: string) => void
  presetQuestion?: PresetQuestion | null
  onOpenSettings?: () => void
  isLoggedIn?: boolean
  onLogout?: () => void
  sessionId?: string | null
  onSessionChange?: (sessionId: string | null) => void
}

export default function Chat({ inputValue, onInputChange, presetQuestion, onOpenSettings, isLoggedIn, onLogout, sessionId, onSessionChange }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId || null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [attachedFile, setAttachedFile] = useState<{ name: string; kind: string } | null>(null)

  const storedFilters = useMemo(() => {
    try { return JSON.parse(localStorage.getItem('filters') || '{}') } catch { return {} }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load session when sessionId changes
  useEffect(() => {
    if (sessionId && sessionId !== currentSessionId) {
      const history = getHistory()
      const session = history.find(s => s.id === sessionId)
      if (session) {
        setMessages(session.messages)
        setCurrentSessionId(sessionId)
        if (onSessionChange) {
          onSessionChange(sessionId)
        }
      }
    } else if (sessionId === null && currentSessionId) {
      // New chat - clear messages
      setMessages([])
      setCurrentSessionId(null)
      if (onSessionChange) {
        onSessionChange(null)
      }
    }
  }, [sessionId, currentSessionId, onSessionChange])

  // Save messages to history
  useEffect(() => {
    if (messages.length > 0) {
      if (currentSessionId) {
        updateSession(currentSessionId, messages)
      } else {
        const newSession = createSession(messages)
        setCurrentSessionId(newSession.id)
        saveSession(newSession)
        if (onSessionChange) {
          onSessionChange(newSession.id)
        }
      }
    }
  }, [messages, currentSessionId, onSessionChange])

  // Handle external input changes
  useEffect(() => {
    if (inputValue !== undefined && inputValue !== input) {
      setInput(inputValue)
    }
  }, [inputValue])

  // Handle input changes
  const handleInputChange = (value: string) => {
    setInput(value)
    if (onInputChange) {
      onInputChange(value)
    }
  }

  async function onAsk(explicitQuestion?: string) {
    const q = explicitQuestion ?? input
    if (!q.trim() || busy) return
    const userMessage: ChatMessage = { role: 'user', content: q }
    setMessages(m => [...m, userMessage])
    setInput('')
    if (onInputChange) onInputChange('')
    setBusy(true)
    try {
      const res = await api.ask({ question: q, filters: storedFilters })
      const assistantMessage: ChatMessage = { role: 'assistant', content: res.answer_html, citations: res.citations }
      setMessages(m => [...m, assistantMessage])
    } catch (e: any) {
      const errorMessage: ChatMessage = { role: 'assistant', content: 'Request failed. Check server logs.' }
      setMessages(m => [...m, errorMessage])
    } finally { setBusy(false) }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onAsk()
    }
  }

  const handleAttachClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Derive a simple label like "PDF", "DOCX" etc.
    const ext = file.name.split('.').pop() || ''
    const kind = ext ? ext.toUpperCase() : 'FILE'
    setAttachedFile({ name: file.name, kind })

    setUploading(true)
    setUploadMessage(`Uploading "${file.name}"...`)

    try {
      const res = await api.ingestFile(file)
      const docId = res.document_id || res.documentId || ''
      setUploadMessage(
        docId
          ? `Uploaded "${file.name}". Document ID: ${docId}`
          : `Uploaded "${file.name}" successfully.`
      )
    } catch (err: any) {
      setUploadMessage(err?.message || 'Upload failed. Check server logs.')
    } finally {
      setUploading(false)
      // Reset input so selecting the same file again still triggers change
      e.target.value = ''
    }
  }

  const handleRemoveFile = () => {
    setAttachedFile(null)
    setUploadMessage(null)
  }

  const processedPresetId = useRef<number | null>(null)

  useEffect(() => {
    if (!presetQuestion) return
    if (processedPresetId.current === presetQuestion.id) return
    if (busy) return
    processedPresetId.current = presetQuestion.id
    setInput(presetQuestion.text)
    if (onInputChange) onInputChange(presetQuestion.text)
    setTimeout(() => {
      onAsk(presetQuestion.text)
    }, 50)
  }, [presetQuestion, busy]) // intentionally omit onAsk/onInputChange to avoid re-trigger loops

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900">
      {/* Header buttons integrated at top */}
      <div className="flex-shrink-0 px-4 py-3 mt-4 flex items-center justify-end">
        <div className="flex items-center gap-2">
          <button 
            onClick={onOpenSettings}
            className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 flex items-center justify-center transition-colors"
            title="Settings"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          
          <button 
            className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 flex items-center justify-center transition-colors"
            onClick={(e) => {
              e.preventDefault()
              document.documentElement.classList.toggle('dark')
            }}
            title="Toggle theme"
          >
            <svg className="w-4 h-4 dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <svg className="w-4 h-4 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </button>

          {isLoggedIn && onLogout && (
            <button
              onClick={onLogout}
              className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
            >
              Logout
            </button>
          )}
        </div>
      </div>
      
      {/* Chat Messages Area - Modern ChatGPT Style */}
      <div className="flex-1 overflow-y-auto min-h-0 pt-6 pb-4">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-8 px-4">
              {/* Modern AI Avatar */}
              <div className="w-24 h-24 rounded-2xl flex items-center justify-center mb-8 shadow-2xl" style={{background: 'linear-gradient(135deg, #8FA31E, #556B2F)'}}>
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              
              <h1 className="text-4xl font-bold bg-clip-text text-transparent mb-4" style={{background: 'linear-gradient(to right, #1e293b, #8FA31E)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
                How can I help you today?
              </h1>
              
              <p className="text-lg text-slate-600 dark:text-slate-400 mb-12 max-w-2xl">
                I'm your AI assistant for SRM University. Ask me about admissions, fees, deadlines, courses, or upload documents for instant insights.
              </p>
              
              {/* Modern Suggestion Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
                {[
                  { icon: "🎓", title: "Admission Requirements", desc: "Get detailed admission criteria", query: "What are the admission requirements for engineering programs?" },
                  { icon: "💰", title: "Fee Structure", desc: "Understand tuition and fees", query: "What is the fee structure for different programs?" },
                  { icon: "📅", title: "Important Deadlines", desc: "Stay updated with dates", query: "What are the important deadlines for this semester?" },
                  { icon: "📞", title: "Contact Information", desc: "Find department contacts", query: "How can I contact different departments?" }
                ].map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleInputChange(suggestion.query)}
                    className="group p-6 text-left bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                    style={{'--hover-border-color': '#8FA31E'} as React.CSSProperties}
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-2xl">{suggestion.icon}</div>
                      <div>
                        <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1 transition-colors" style={{'--hover-color': '#8FA31E'} as React.CSSProperties}>
                          {suggestion.title}
                        </h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                          {suggestion.desc}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-0">
              {messages.map((m, i) => (
                <div key={i} className={`py-6 px-4 ${m.role === 'user' ? 'bg-slate-50 dark:bg-slate-800/50' : 'bg-white dark:bg-slate-900'}`}>
                  <div className="max-w-3xl mx-auto">
                    <Message role={m.role} content={m.content} />
                    {m.role === 'assistant' && m.citations && <Sources items={m.citations} />}
                  </div>
                </div>
              ))}
              {busy && (
                <div className="py-6 px-4 bg-slate-50 dark:bg-slate-800/50">
                  <div className="max-w-3xl mx-auto">
                    <div className="flex items-center gap-4 p-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{background: 'linear-gradient(to right, #8FA31E, #556B2F)'}}>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-700 dark:text-slate-300 font-medium">AI is thinking</span>
                        <div className="flex gap-1">
                          <div className="w-2 h-2 rounded-full animate-bounce" style={{backgroundColor: '#8FA31E'}}></div>
                          <div className="w-2 h-2 rounded-full animate-bounce" style={{backgroundColor: '#8FA31E', animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 rounded-full animate-bounce" style={{backgroundColor: '#8FA31E', animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Modern Input Area - ChatGPT Style - Slightly lifted from bottom */}
      <div className="flex-shrink-0 bg-white dark:bg-slate-900 mb-6">
        <div className="max-w-4xl mx-auto p-4 pb-4">
          <div className="relative">
            {/* Attached file preview */}
            {attachedFile && (
              <div className="mb-3 flex items-center justify-between rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-3 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-red-500 text-white flex-shrink-0">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 3h8l4 4v14H7z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 13h6M9 17h4"
                      />
                    </svg>
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {attachedFile.name}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {attachedFile.kind}
                      {uploading && ' · Uploading...'}
                      {!uploading && uploadMessage && ' · Uploaded'}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="w-6 h-6 rounded-full flex items-center justify-center bg-black text-white hover:bg-slate-700 transition-colors flex-shrink-0"
                  aria-label="Remove file"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            <div className="flex items-end gap-3 p-3 bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 transition-all duration-200" style={{'--focus-border': '#8FA31E', '--focus-ring': '#8FA31E'} as React.CSSProperties}>
              {/* Add file button */}
              <button
                type="button"
                onClick={handleAttachClick}
                disabled={uploading || busy}
                className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 ${
                  uploading
                    ? 'bg-slate-300 dark:bg-slate-600 text-slate-500 dark:text-slate-400 cursor-not-allowed'
                    : 'bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
                title="Add file"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </button>

              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => handleInputChange(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message SRM UniChat..."
                className="flex-1 bg-transparent border-none outline-none resize-none text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 min-h-[24px] max-h-32"
                rows={1}
                style={{
                  height: 'auto',
                  minHeight: '24px',
                  maxHeight: '128px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement
                  target.style.height = 'auto'
                  target.style.height = Math.min(target.scrollHeight, 128) + 'px'
                }}
              />
              <button
                onClick={onAsk}
                disabled={!input.trim() || busy}
                className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 ${
                  input.trim() && !busy
                    ? 'text-white hover:scale-105'
                    : 'bg-slate-300 dark:bg-slate-600 text-slate-500 dark:text-slate-400 cursor-not-allowed'
                }`}
                style={input.trim() && !busy ? {backgroundColor: '#8FA31E'} : {}}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>

              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.csv,.xlsx"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
            
            {/* Quick Actions - Modern Style */}
            {messages.length > 0 && (
              <div className="flex gap-2 mt-3 overflow-x-auto pb-2">
                {[
                  'Explain more',
                  'Give examples',
                  'Summarize',
                  'What next?'
                ].map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleInputChange(action)}
                    className="flex-shrink-0 px-4 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


