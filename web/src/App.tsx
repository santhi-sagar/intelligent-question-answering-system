import { useState, useEffect } from 'react'
import Chat from './components/Chat'
import Footer from './components/Footer'
import SettingsDrawer from './components/SettingsDrawer'
import HistoryDrawer from './components/HistoryDrawer'
import LoginPage from './components/LoginPage'
import { type ChatSession, type ChatMessage } from './lib/history'

const getIconComponent = (iconType: string) => {
  const iconClass = "w-5 h-5"
  
  switch (iconType) {
    case 'grid':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 3h6v6H3V3zm8 0h6v6h-6V3zm-8 8h6v6H3v-6zm8 0h6v6h-6v-6z"/>
        </svg>
      )
    case 'building':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 21h18v-2H3v2zm0-4h18v-2H3v2zm0-4h18v-2H3v2zm0-4h18V7H3v2zm0-6v2h18V3H3z"/>
        </svg>
      )
    case 'dollar':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .78.31 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.2z"/>
        </svg>
      )
    case 'document-plus':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          <path d="M12 11h2v2h-2v-2zm0-4h2v2h-2V7z"/>
        </svg>
      )
    case 'document-lines':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
      )
    case 'bars':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
      )
    case 'airplane':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
        </svg>
      )
    case 'wifi':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.07 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
        </svg>
      )
    case 'books':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
        </svg>
      )
    case 'document-play':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          <path d="M10 12l3 2-3 2v-4z"/>
        </svg>
      )
    case 'checklist':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
        </svg>
      )
    case 'briefcase':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 6h-3V4c0-1.11-.89-2-2-2H9c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zM9 4h6v2H9V4zm11 15H4V8h16v11z"/>
        </svg>
      )
    case 'graduation-cap':
      return (
        <svg className={iconClass} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/>
        </svg>
      )
    default:
      return null
  }
}

export default function App() {
  const [open, setOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const [selectedOffice, setSelectedOffice] = useState<string | null>(null)
  const [presetQuestion, setPresetQuestion] = useState<{ id: number; text: string } | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [loginError, setLoginError] = useState<string>('')
  const [userInfo, setUserInfo] = useState<{ rollNo: string; dob: string } | null>(null)

  // Load login state from localStorage
  useEffect(() => {
    const savedLoginState = localStorage.getItem('srm-unichat-logged-in')
    const savedUserInfo = localStorage.getItem('srm-unichat-user-info')
    if (savedLoginState === 'true' && savedUserInfo) {
      try {
        const user = JSON.parse(savedUserInfo)
        setIsLoggedIn(true)
        setUserInfo(user)
      } catch {
        // Invalid data, clear it
        localStorage.removeItem('srm-unichat-logged-in')
        localStorage.removeItem('srm-unichat-user-info')
      }
    }
  }, [])

  const handleLogin = async (rollNo: string, dob: string) => {
    setLoginError('')
    
    // Basic validation
    if (!rollNo.trim()) {
      setLoginError('Please enter your roll number')
      return
    }
    
    if (!dob.trim()) {
      setLoginError('Please enter your date of birth')
      return
    }

    try {
      const { api } = await import('./lib/api')
      const response = await api.login({
        roll_no: rollNo.trim(),
        dob: dob.trim()
      })
      
      if (response.success) {
        const userData = { rollNo: response.roll_no || rollNo.trim(), dob: dob.trim() }
        setIsLoggedIn(true)
        setUserInfo(userData)
        localStorage.setItem('srm-unichat-logged-in', 'true')
        localStorage.setItem('srm-unichat-user-info', JSON.stringify(userData))
        setLoginError('')
      } else {
        setLoginError(response.message || 'Login failed. Please try again.')
      }
    } catch (error: any) {
      // Handle API errors
      const errorMessage = error?.message || 'Login failed. Please try again.'
      setLoginError(errorMessage)
    }
  }

  const handleLogout = () => {
    // Clear all state
    setIsLoggedIn(false)
    setUserInfo(null)
    setCurrentSessionId(null)
    setLoginError('')
    
    // Clear localStorage
    localStorage.removeItem('srm-unichat-logged-in')
    localStorage.removeItem('srm-unichat-user-info')
    
    // TODO: Call backend logout endpoint if needed
  }

  const handleLoadSession = (session: ChatSession) => {
    setCurrentSessionId(session.id)
    // Chat component will load the session via sessionId prop
  }

  const handleNewChat = () => {
    setCurrentSessionId(null)
    setInputValue('')
    setSelectedOffice(null)
    setPresetQuestion(null)
  }

  // Show login page if not logged in
  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} error={loginError} />
  }
  
  return (
    <div className="h-screen flex flex-col bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 overflow-hidden">
      <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <div className="flex-1 flex min-h-0 overflow-hidden h-full">
          {/* Desktop Sidebar */}
          <div className="hidden lg:block w-80 h-full overflow-y-auto border-r border-slate-200 dark:border-slate-700">
            <div className="px-4 space-y-4 flex flex-col h-full">
              {/* Sidebar brand at the top with ~1 inch gap */}
              <div className="flex items-center gap-3 pt-4 pb-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{background: 'linear-gradient(135deg, #8FA31E, #556B2F)'}} aria-label="Logo">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">SRM UniChat</h1>
              </div>

              {/* History Button */}
              <button
                onClick={() => setHistoryOpen(true)}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
              >
                <svg className="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">History</span>
              </button>
              
              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                className="mt-2 w-full flex items-center gap-3 p-3 rounded-lg bg-slate-900 text-slate-50 dark:bg-slate-100 dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-200 transition-colors text-left"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-sm font-medium">New chat</span>
              </button>
              
              <div className="rounded-2xl p-4">
                <h3 className="font-semibold mb-4 text-slate-900 dark:text-slate-100">Administrative Offices</h3>
                <div className="space-y-1">
                  {[
                    { 
                      icon: "building", 
                      title: "Academic Affairs", 
                      action: "Tell me about academic affairs"
                    },
                    { 
                      icon: "dollar", 
                      title: "Accounts & Finance", 
                      action: "Tell me about accounts and finance"
                    },
                    { 
                      icon: "document-plus", 
                      title: "Admissions", 
                      action: "Tell me about admissions"
                    },
                    { 
                      icon: "document-lines", 
                      title: "Campus Life", 
                      action: "Tell me about campus life"
                    },
                    { 
                      icon: "bars", 
                      title: "CRCS", 
                      action: "Tell me about CRCS"
                    },
                    { 
                      icon: "document-lines", 
                      title: "Examinations", 
                      action: "Tell me about examinations"
                    },
                    { 
                      icon: "building", 
                      title: "HR", 
                      action: "Tell me about HR"
                    },
                    { 
                      icon: "airplane", 
                      title: "International Relations", 
                      action: "Tell me about international relations"
                    },
                    { 
                      icon: "wifi", 
                      title: "ITKM", 
                      action: "Tell me about ITKM"
                    },
                    { 
                      icon: "books", 
                      title: "Library", 
                      action: "Tell me about the library"
                    },
                    { 
                      icon: "document-play", 
                      title: "Media & Communications", 
                      action: "Tell me about media and communications"
                    },
                    { 
                      icon: "checklist", 
                      title: "Registrar Office", 
                      action: "Tell me about the registrar office"
                    },
                    { 
                      icon: "briefcase", 
                      title: "Research Office", 
                      action: "Tell me about the research office"
                    },
                    { 
                      icon: "graduation-cap", 
                      title: "Student Affairs", 
                      action: "Tell me about student affairs"
                    }
                  ].map((item, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        const prompt = `Using reliable and up-to-date public information from official SRM University AP (SRMAP) websites or trusted news coverage, explain the role, responsibilities, and key services of the ${item.title} office. Make sure the answer is specific to SRM AP and include at least two direct website URLs from credible sources (prefer srmap.edu.in or other reputable SRM AP resources).`
                        setInputValue(prompt)
                        setSelectedOffice(item.title)
                        setPresetQuestion({ id: Date.now(), text: prompt })
                      }}
                      className={`w-full text-left p-3 rounded-lg transition-all duration-200 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 ${
                        selectedOffice === item.title 
                          ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800' 
                          : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-5 h-5 ${selectedOffice === item.title ? 'text-orange-500' : 'text-slate-600 dark:text-slate-400'}`}>
                            {getIconComponent(item.icon)}
                          </div>
                          <span className={`text-sm font-medium ${
                            selectedOffice === item.title 
                              ? 'text-orange-600 dark:text-orange-400' 
                              : 'text-slate-700 dark:text-slate-300'
                          }`}>
                            {item.title}
                          </span>
                        </div>
                        
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            {/* Chat Interface - Full height with internal scrolling */}
            <div className="flex-1 min-h-0">
              <Chat 
                inputValue={inputValue} 
                onInputChange={setInputValue}
                presetQuestion={presetQuestion}
                onOpenSettings={() => setOpen(true)}
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                sessionId={currentSessionId}
                onSessionChange={setCurrentSessionId}
              />
            </div>
          </div>
        </div>
      </main>
      
      <SettingsDrawer open={open} onClose={() => setOpen(false)} />
      <HistoryDrawer 
        open={historyOpen} 
        onClose={() => setHistoryOpen(false)}
        onLoadSession={handleLoadSession}
        onNewChat={handleNewChat}
      />
    </div>
  )
}


