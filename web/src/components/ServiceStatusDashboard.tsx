import { useCallback, useEffect, useMemo, useState } from 'react'

type HealthPayload = { status?: string; db?: boolean; embeddings_ready?: boolean }
type CheckResult = { ok: boolean; latencyMs?: number; checkedAt: string; payload?: HealthPayload; error?: string }

// @ts-ignore - Vite env types
const DEFAULT_API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const getApiBase = () => (localStorage.getItem('apiBase')?.trim() || DEFAULT_API_BASE).replace(/\/+$/, '')

async function checkBackend(): Promise<CheckResult> {
  const checkedAt = new Date().toISOString()
  const started = performance.now()
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 10000)
  try {
    const response = await fetch(`${getApiBase()}/api/health`, { cache: 'no-store', signal: controller.signal })
    if (!response.ok) throw new Error(`Health endpoint returned HTTP ${response.status}`)
    const payload = await response.json() as HealthPayload
    return { ok: payload.status === 'ok' && payload.db === true, latencyMs: Math.round(performance.now() - started), checkedAt, payload }
  } catch (error: any) {
    return { ok: false, latencyMs: Math.round(performance.now() - started), checkedAt, error: error?.name === 'AbortError' ? 'Health check timed out' : (error?.message || 'Unable to reach backend') }
  } finally {
    window.clearTimeout(timeout)
  }
}

const formatTime = (value?: string) => value ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Not checked yet'
const dot = (ok: boolean, unknown = false) => <span className={`inline-block h-2.5 w-2.5 rounded-full ${unknown ? 'bg-slate-300 dark:bg-slate-600' : ok ? 'bg-emerald-500' : 'bg-rose-500'}`} />

function Metric({ label, ok, value, unknown = false }: { label: string; ok: boolean; value: string; unknown?: boolean }) {
  return <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/70 p-3"><div className="flex items-center justify-between gap-2"><span className="text-xs font-medium text-slate-500 dark:text-slate-400">{label}</span>{dot(ok, unknown)}</div><p className="mt-2 text-sm font-semibold text-slate-800 dark:text-slate-200">{value}</p></div>
}

export default function ServiceStatusDashboard() {
  const [current, setCurrent] = useState<CheckResult | null>(null)
  const [checks, setChecks] = useState<CheckResult[]>([])
  const [loading, setLoading] = useState(false)
  const runCheck = useCallback(async () => { setLoading(true); const result = await checkBackend(); setCurrent(result); setChecks(previous => [result, ...previous].slice(0, 12)); setLoading(false) }, [])
  useEffect(() => { runCheck(); const interval = window.setInterval(runCheck, 30000); return () => window.clearInterval(interval) }, [runCheck])
  const sessionUptime = useMemo(() => checks.length ? `${Math.round((checks.filter(check => check.ok).length / checks.length) * 100)}%` : '—', [checks])
  const databaseOk = current?.payload?.db === true
  const embeddingsReady = current?.payload?.embeddings_ready === true
  const hasResult = current !== null

  return <section className="space-y-4" aria-label="Live service status">
    <div className="flex items-start justify-between gap-3"><div><h3 className="text-lg font-medium text-slate-800 dark:text-slate-200">Live service status</h3><p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Automatic health check every 30 seconds while this page is open.</p></div><button type="button" onClick={runCheck} disabled={loading} className="shrink-0 rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50">{loading ? 'Checking…' : 'Check now'}</button></div>
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3"><Metric label="Backend API" ok={current?.ok === true} value={!hasResult ? 'Checking…' : current?.ok ? 'Online' : 'Unavailable'} unknown={!hasResult} /><Metric label="Database" ok={databaseOk} value={!hasResult ? 'Checking…' : databaseOk ? 'Connected' : 'Unavailable'} unknown={!hasResult} /><Metric label="Embeddings" ok={embeddingsReady} value={!hasResult ? 'Checking…' : embeddingsReady ? 'Ready' : 'Check config'} unknown={!hasResult} /></div>
    <div className="rounded-xl bg-slate-50 dark:bg-slate-800/70 p-4 space-y-2 text-sm"><div className="flex items-center justify-between gap-3"><span className="text-slate-500 dark:text-slate-400">Response time</span><span className="font-medium text-slate-800 dark:text-slate-200">{current?.latencyMs != null ? `${current.latencyMs} ms` : '—'}</span></div><div className="flex items-center justify-between gap-3"><span className="text-slate-500 dark:text-slate-400">Session checks</span><span className="font-medium text-slate-800 dark:text-slate-200">{checks.length}</span></div><div className="flex items-center justify-between gap-3"><span className="text-slate-500 dark:text-slate-400">Session success rate</span><span className="font-medium text-slate-800 dark:text-slate-200">{sessionUptime}</span></div><div className="flex items-center justify-between gap-3"><span className="text-slate-500 dark:text-slate-400">Last checked</span><span className="font-medium text-slate-800 dark:text-slate-200">{formatTime(current?.checkedAt)}</span></div></div>
    {current && !current.ok && <p className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700 dark:border-rose-900/60 dark:bg-rose-950/30 dark:text-rose-300">{current.error || 'The backend health check did not report a healthy service.'}</p>}
    <p className="text-xs leading-5 text-slate-500 dark:text-slate-400">This panel tracks the service while the app is open. For monitoring when the app is closed, use an external uptime monitor against: <span className="font-mono break-all">{getApiBase()}/api/health</span>.</p>
  </section>
}
