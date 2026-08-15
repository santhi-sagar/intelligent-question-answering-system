import { useState } from 'react'

type Props = {
  onLogin: (rollNo: string, dob: string) => void
  error?: string
}

export default function LoginPage({ onLogin, error }: Props) {
  const [rollNo, setRollNo] = useState('')
  const [dob, setDob] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!rollNo.trim() || !dob.trim()) {
      return
    }
    setIsSubmitting(true)
    // Simulate API call - replace with actual backend call later
    setTimeout(() => {
      onLogin(rollNo.trim(), dob.trim())
      setIsSubmitting(false)
    }, 500)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-green-50 dark:from-slate-900 dark:to-slate-800 px-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl" style={{background: 'linear-gradient(135deg, #8FA31E, #556B2F)'}}>
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent mb-2" style={{background: 'linear-gradient(to right, #1e293b, #8FA31E, #556B2F)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
            SRM UniChat
          </h1>
          <p className="text-slate-600 dark:text-slate-300">Sign in to continue</p>
        </div>

        {/* Login Form */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Roll Number Input */}
            <div>
              <label htmlFor="rollNo" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Roll Number
              </label>
              <input
                id="rollNo"
                type="text"
                value={rollNo}
                onChange={(e) => setRollNo(e.target.value)}
                placeholder="Enter your roll number"
                required
                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all"
                style={{'--tw-ring-color': '#8FA31E'} as React.CSSProperties}
                onFocus={(e) => e.target.style.borderColor = '#8FA31E'}
                onBlur={(e) => e.target.style.borderColor = ''}
              />
            </div>

            {/* Date of Birth Input */}
            <div>
              <label htmlFor="dob" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Date of Birth
              </label>
              <input
                id="dob"
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all"
                style={{'--tw-ring-color': '#8FA31E'} as React.CSSProperties}
                onFocus={(e) => e.target.style.borderColor = '#8FA31E'}
                onBlur={(e) => e.target.style.borderColor = ''}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting || !rollNo.trim() || !dob.trim()}
              className="w-full py-3 px-4 rounded-xl font-semibold text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transform hover:scale-[1.02]"
              style={{
                background: isSubmitting || !rollNo.trim() || !dob.trim() 
                  ? 'linear-gradient(to right, #94a3b8, #64748b)' 
                  : 'linear-gradient(to right, #8FA31E, #556B2F)'
              }}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Info Text */}
          <p className="mt-6 text-xs text-center text-slate-500 dark:text-slate-400">
            Use your SRM University roll number and date of birth to sign in
          </p>
        </div>
      </div>
    </div>
  )
}

