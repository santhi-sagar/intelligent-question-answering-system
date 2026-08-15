import { useEffect, useState } from 'react'

type Props = { open: boolean; onClose: () => void }

export default function SettingsDrawer({ open, onClose }: Props) {
  const [apiBase, setApiBase] = useState('')
  const [filters, setFilters] = useState({ campus: '', program: '', year: '' })

  useEffect(() => {
    setApiBase(localStorage.getItem('apiBase') || '')
    const f = localStorage.getItem('filters')
    if (f) setFilters(JSON.parse(f))
  }, [open])

  function save() {
    localStorage.setItem('apiBase', apiBase)
    localStorage.setItem('filters', JSON.stringify(filters))
    onClose()
  }

  return (
    <div className={`fixed inset-0 z-50 ${open ? '' : 'pointer-events-none'}`}>
      <div className={`absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity duration-300 ${open ? 'opacity-100' : 'opacity-0'}`} onClick={onClose} />
      <div className={`absolute right-0 top-0 h-full w-full max-w-md bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-700 shadow-2xl transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-purple-500 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">Settings</h2>
            </div>
            <button 
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 flex items-center justify-center transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* API Configuration */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200 mb-2">API Configuration</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">API Base URL</label>
                    <input 
                      className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors" 
                      value={apiBase} 
                      onChange={e=>setApiBase(e.target.value)} 
                      placeholder={import.meta.env.VITE_API_BASE || 'http://localhost:8000'} 
                    />
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Leave empty to use default API endpoint</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200 mb-2">Search Filters</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">Customize your search results by setting default filters</p>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Campus</label>
                    <input 
                      className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors" 
                      value={filters.campus} 
                      onChange={e=>setFilters({...filters, campus: e.target.value})} 
                      placeholder="e.g., Chennai, Delhi, etc."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Program</label>
                    <input 
                      className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors" 
                      value={filters.program} 
                      onChange={e=>setFilters({...filters, program: e.target.value})} 
                      placeholder="e.g., Computer Science, Engineering, etc."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Academic Year</label>
                    <input 
                      className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors" 
                      value={filters.year} 
                      onChange={e=>setFilters({...filters, year: e.target.value})} 
                      placeholder="e.g., 2024, 2023-24, etc."
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* App Info */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200 mb-2">About</h3>
                <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <span className="font-medium">Version:</span>
                    <span>1.0.0</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <span className="font-medium">Status:</span>
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Connected</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-slate-200 dark:border-slate-700">
            <div className="flex gap-3">
              <button 
                className="flex-1 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 hover:scale-105" 
                style={{background: 'linear-gradient(to right, #8FA31E, #556B2F)'}}
                onClick={save}
              >
                Save Settings
              </button>
              <button 
                className="px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors" 
                onClick={onClose}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


