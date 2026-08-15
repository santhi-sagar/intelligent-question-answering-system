import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = { role: 'user' | 'assistant'; content: string }

export default function Message({ role, content }: Props) {
  return (
    <div className={`flex gap-4 ${role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar - Modern Style */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        role === 'assistant' 
          ? 'bg-gradient-to-br from-blue-500 to-purple-600' 
          : 'bg-gradient-to-br from-slate-600 to-slate-700'
      }`}>
        {role === 'assistant' ? (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        )}
      </div>

      {/* Message Content - ChatGPT Style */}
      <div className={`flex-1 ${role === 'user' ? 'flex flex-col items-end' : ''}`}>
        <div className={`max-w-[85%] ${role === 'user' ? 'ml-auto' : ''}`}>
          {role === 'assistant' ? (
            <div className="prose prose-slate max-w-none dark:prose-invert prose-headings:text-slate-900 dark:prose-headings:text-slate-100 prose-p:text-slate-700 dark:prose-p:text-slate-300 prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-strong:text-slate-900 dark:prose-strong:text-slate-100">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-slate-900 dark:text-slate-100 leading-relaxed">
              {content}
            </div>
          )}
        </div>
        
        {/* Timestamp - Subtle Style */}
        <div className={`text-xs text-slate-500 dark:text-slate-400 mt-2 ${role === 'user' ? 'text-right' : 'text-left'}`}>
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}


