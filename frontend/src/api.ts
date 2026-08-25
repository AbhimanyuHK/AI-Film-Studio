export type Client = { client_id: string; name: string; status: string }
export type Film = { film_id: string; client_id: string; name: string; source_language: string; target_languages: string[]; status: string }
export type Job = {
  job_id: string; film_id: string; environment_id?: string; job_type: string; status: string;
  attempts: number; max_attempts: number; error_code?: string | null; result?: unknown;
  created_at?: string; updated_at?: string; started_at?: string | null; completed_at?: string | null;
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')
const ACTOR_KEY = 'ai-film-studio.actor-id'

export function actorId(): string {
  const existing = localStorage.getItem(ACTOR_KEY)
  if (existing) return existing
  const value = `web-${crypto.randomUUID()}`
  localStorage.setItem(ACTOR_KEY, value)
  return value
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  headers.set('X-Actor-Id', actorId())
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`
    try {
      const body = await response.json()
      message = body.detail || message
    } catch { /* keep HTTP error */ }
    throw new Error(message)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  aiHealth: () => request<{ status: string }>('/api/v1/ai-engine/health'),
  getClient: (id: string) => request<Client>(`/api/v1/clients/${id}`),
  createClient: (name: string) => request<Client>('/api/v1/clients', { method: 'POST', body: JSON.stringify({ name }) }),
  listFilms: (clientId: string) => request<Film[]>(`/api/v1/clients/${clientId}/films`),
  getFilm: (filmId: string) => request<Film>(`/api/v1/films/${filmId}`),
  createFilm: (payload: Omit<Film, 'film_id' | 'status' | 'client_id'> & { client_id: string }) => request<Film>('/api/v1/films', { method: 'POST', body: JSON.stringify(payload) }),
  startProduction: (filmId: string, payload: Record<string, unknown>) => request<{ film_id: string; environment_id: string; status: string; job_ids: string[] }>(`/api/v1/films/${filmId}/production/start`, { method: 'POST', body: JSON.stringify({ payload }) }),
  enqueueJob: (filmId: string, jobType: string, payload: Record<string, unknown> = {}) => request<{ job_id: string; status: string }>(`/api/v1/films/${filmId}/jobs`, { method: 'POST', body: JSON.stringify({ job_type: jobType, payload }) }),
  listJobs: (filmId: string) => request<Job[]>(`/api/v1/films/${filmId}/jobs`),
  getJob: (jobId: string) => request<Job>(`/api/v1/jobs/${jobId}`),
  cancelJob: (jobId: string) => request<{ job_id: string; status: string }>(`/api/v1/jobs/${jobId}/cancel`, { method: 'POST' }),
}

export const pipelineStages = [
  'script_analysis', 'character_generation', 'environment_generation', 'storyboard',
  'shot_generation', 'video_generation', 'voice_generation', 'translation', 'dubbing',
  'music', 'sfx', 'editing', 'upscaling', 'final_render',
]
