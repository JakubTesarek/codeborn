// api/client.ts
import { toast } from 'sonner'

const API_BASE = import.meta.env.DEV ? '' : import.meta.env.VITE_API_BASE_URL ?? ''

type ApiOptions = RequestInit & { suppressToast?: boolean }

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
    ...options,
  })

  if (!res.ok) {
    // Try JSON error first; fall back to text
    let message = ''
    try {
      const data = await res.json()
      message = typeof data?.detail === 'string'
        ? data.detail
        : (data?.message ?? JSON.stringify(data))
    } catch {
      message = await res.text()
    }

    if (!options.suppressToast) {
      toast.error(`Error ${res.status}`, {
        description: message || 'An unexpected error occurred.',
      })
    }

    throw new Error(`API error ${res.status}: ${message}`)
  }

  return res.status === 204 ? (undefined as T) : ((await res.json()) as T)
}