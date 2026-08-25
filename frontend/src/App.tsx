import { useCallback, useEffect, useMemo, useState } from 'react'
import { api, type Film, type Job, pipelineStages } from './api'
import './styles.css'

function statusClass(status: string) {
  return `status status-${status.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
}

function App() {
  const [clientId, setClientId] = useState(localStorage.getItem('ai-film-studio.client-id') || '')
  const [clientName, setClientName] = useState('')
  const [films, setFilms] = useState<Film[]>([])
  const [selectedFilm, setSelectedFilm] = useState<Film | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [script, setScript] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [aiStatus, setAiStatus] = useState('checking')

  const refresh = useCallback(async (filmId = selectedFilm?.film_id) => {
    if (!clientId) return
    try {
      const nextFilms = await api.listFilms(clientId)
      setFilms(nextFilms)
      const film = nextFilms.find((item) => item.film_id === filmId) || selectedFilm || nextFilms[0] || null
      setSelectedFilm(film)
      if (film) setJobs(await api.listJobs(film.film_id))
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load studio data') }
  }, [clientId, selectedFilm])

  useEffect(() => { api.aiHealth().then((x) => setAiStatus(x.status)).catch(() => setAiStatus('unavailable')) }, [])
  useEffect(() => { if (clientId) refresh() }, [clientId])
  useEffect(() => {
    if (!selectedFilm) return
    const timer = window.setInterval(() => refresh(selectedFilm.film_id), 4000)
    return () => window.clearInterval(timer)
  }, [selectedFilm, refresh])

  async function createClient() {
    setLoading(true); setError('')
    try {
      const client = await api.createClient(clientName.trim())
      setClientId(client.client_id); localStorage.setItem('ai-film-studio.client-id', client.client_id); setClientName(''); setMessage('Client created')
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to create client') } finally { setLoading(false) }
  }

  async function createFilm() {
    if (!clientId) return
    setLoading(true); setError('')
    try {
      const film = await api.createFilm({ client_id: clientId, name: `Untitled Film ${films.length + 1}`, source_language: 'en', target_languages: ['en'] })
      await refresh(film.film_id); setMessage('Film created')
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to create film') } finally { setLoading(false) }
  }

  async function startProduction() {
    if (!selectedFilm) return
    setLoading(true); setError('')
    try {
      await api.startProduction(selectedFilm.film_id, { screenplay: script, source_language: selectedFilm.source_language, target_languages: selectedFilm.target_languages })
      await refresh(selectedFilm.film_id); setMessage('Production pipeline queued')
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to start production') } finally { setLoading(false) }
  }

  async function cancel(jobId: string) {
    try { await api.cancelJob(jobId); if (selectedFilm) await refresh(selectedFilm.film_id); setMessage('Job cancelled') }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to cancel job') }
  }

  const counts = useMemo(() => ({ running: jobs.filter(j => ['running', 'retrying'].includes(j.status)).length, done: jobs.filter(j => j.status === 'completed').length, failed: jobs.filter(j => j.status === 'failed').length }), [jobs])

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">AI</span><div><strong>Film Studio</strong><small>Control Plane</small></div></div>
      <nav><button className="nav-active">Studio</button><button>Films</button><button>Assets</button><button>Jobs</button><button>Settings</button></nav>
      <div className="connection"><span className={aiStatus === 'ok' ? 'dot online' : 'dot'} /> AI Engine <b>{aiStatus}</b></div>
    </aside>
    <main className="main">
      <header><div><p className="eyebrow">PRODUCTION CONTROL</p><h1>{selectedFilm?.name || 'AI Film Studio'}</h1><p className="muted">Client-scoped film generation and AI pipeline operations.</p></div><button className="primary" onClick={createFilm} disabled={!clientId || loading}>+ New film</button></header>
      {error && <div className="alert error">{error}<button onClick={() => setError('')}>×</button></div>}
      {message && <div className="alert success">{message}<button onClick={() => setMessage('')}>×</button></div>}
      {!clientId ? <section className="onboarding card"><div><p className="eyebrow">GET STARTED</p><h2>Create your studio client</h2><p className="muted">The frontend talks only to the authenticated backend control plane. AI execution stays behind the backend → AI Engine boundary.</p></div><div className="inline-form"><input value={clientName} onChange={e => setClientName(e.target.value)} placeholder="Studio / client name"/><button className="primary" onClick={createClient} disabled={!clientName.trim() || loading}>Create client</button></div></section> : <>
        <section className="film-strip">{films.map(film => <button key={film.film_id} className={selectedFilm?.film_id === film.film_id ? 'film-card selected' : 'film-card'} onClick={() => setSelectedFilm(film)}><span className="film-icon">▣</span><span><b>{film.name}</b><small>{film.source_language.toUpperCase()} · {film.target_languages.join(', ').toUpperCase()}</small></span><em>{film.status}</em></button>)}{films.length === 0 && <div className="empty">No films yet. Create one to begin.</div>}</section>
        {selectedFilm && <>
          <section className="metrics"><div><span>Running</span><strong>{counts.running}</strong></div><div><span>Completed</span><strong>{counts.done}</strong></div><div><span>Failed</span><strong>{counts.failed}</strong></div><div><span>Total jobs</span><strong>{jobs.length}</strong></div></section>
          <section className="workspace">
            <div className="card screenplay"><div className="section-title"><div><p className="eyebrow">INPUT</p><h2>Screenplay</h2></div><span className="pill">{selectedFilm.source_language.toUpperCase()}</span></div><textarea value={script} onChange={e => setScript(e.target.value)} placeholder="Paste the screenplay or production brief here..."/><button className="primary wide" onClick={startProduction} disabled={loading || !script.trim()}>{loading ? 'Queueing…' : 'Generate film pipeline'}</button><p className="hint">Creates the complete dependency graph in PostgreSQL. The worker then sends each executable stage to the AI Engine.</p></div>
            <div className="card pipeline"><div className="section-title"><div><p className="eyebrow">PIPELINE</p><h2>Production stages</h2></div></div><div className="stage-list">{pipelineStages.map(stage => { const job = jobs.find(j => j.job_type === stage); return <div className="stage" key={stage}><span className={job ? statusClass(job.status) : 'stage-dot'}></span><div><b>{stage.replaceAll('_', ' ')}</b><small>{job ? `${job.status} · attempt ${job.attempts}/${job.max_attempts}` : 'waiting'}</small></div>{job && ['queued','running','retrying'].includes(job.status) && <button onClick={() => cancel(job.job_id)}>Cancel</button>}</div> })}</div></div>
          </section>
          <section className="card jobs"><div className="section-title"><div><p className="eyebrow">OBSERVABILITY</p><h2>Job activity</h2></div><button className="ghost" onClick={() => refresh(selectedFilm.film_id)}>Refresh</button></div>{jobs.length === 0 ? <div className="empty">No jobs. Start the production pipeline above.</div> : <div className="job-table"><div className="job-head"><span>Stage</span><span>Status</span><span>Attempts</span><span>Updated</span></div>{jobs.map(job => <div className="job-row" key={job.job_id}><span>{job.job_type.replaceAll('_', ' ')}</span><span className={statusClass(job.status)}>{job.status}</span><span>{job.attempts}/{job.max_attempts}</span><span>{job.updated_at ? new Date(job.updated_at).toLocaleString() : '—'}</span></div>)}</div>}</section>
        </>}
      </>}
    </main>
  </div>
}

export default App
