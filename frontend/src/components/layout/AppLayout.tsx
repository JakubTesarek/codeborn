import { Outlet } from 'react-router-dom'
import { TopNav } from '@/components/layout/TopNav'
import { useState, useEffect } from 'react'
import { apiFetch } from '@/api/client'
import { LandingPage } from '@/pages/LandingPage'
import { Toaster } from '@/components/ui/sonner'


export function AppLayout() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch<User>('/api/auth/me', { suppressToast: true })
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) 
    return <div className="flex h-screen items-center justify-center">Loading...</div>

  if (!user)
    return <LandingPage />

  return (
    <div className="min-h-screen flex flex-col items-center bg-background">
      <div className="w-full max-w-9xl flex flex-col flex-1">
        <TopNav user={user} onLogout={() => setUser(null)} />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
      <Toaster richColors position="bottom-right" />
    </div>
  )
}
