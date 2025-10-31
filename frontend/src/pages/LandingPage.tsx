import { Button } from '@/components/ui/button'
import { GithubIcon } from '@/components/icons/GithubIcon'
import { useState } from 'react'


export function LoginButton() {
  const [loading, setLoading] = useState(false)

  const handleLogin = () => {
    setLoading(true)
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/github/login`
  }

  return (
    <Button onClick={handleLogin} variant="secondary" disabled={loading}>
      {loading ? (
        <><GithubIcon className="h-4 w-4 animate-bounce mr-2" />Login in progress</>
      ) : (
        <><GithubIcon className="h-4 w-4 mr-2" />Login with GitHub</>
      )}
    </Button>
  )
}


export function LandingPage() {
  return (
    <div className="relative flex h-screen flex-col items-center justify-center overflow-hidden text-center text-zinc-100">
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-900 via-zinc-950 to-black" />
      <div className="absolute w-96 h-96 bg-primary/20 rounded-full blur-3xl top-1/4 -z-10" />

      <div className="relative z-10 max-w-md px-6 space-y-6">
        <h1 className="text-4xl font-bold tracking-tight">Welcome to CodeBorn</h1>
        <p className="text-zinc-400 text-base">
          Build, deploy, and evolve your own AI bots to compete in a strategic coding arena.
        </p>

        <div className="flex justify-center pt-6">
          <LoginButton />
        </div>

        <div className="pt-6 text-xs text-zinc-500">
          By continuing, you agree to our{' '}
          <a href="/legal" className="underline hover:text-zinc-300">
            Terms of Service & Privacy Policy
          </a>{' '}.
        </div>
      </div>
    </div>
  )
}