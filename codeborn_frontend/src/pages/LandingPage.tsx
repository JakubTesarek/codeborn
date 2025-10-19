import { Button } from '@/components/ui/button'


function GitHubIcon(props: React.SVGProps<SVGSVGElement>) {
    return (
      <svg
        {...props}
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M12 .5a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6a3.2 3.2 0 0 0-1.3-1.7c-1-.7.1-.7.1-.7a2.5 2.5 0 0 1 1.8 1.2 2.6 2.6 0 0 0 3.5 1 2.7 2.7 0 0 1 .8-1.7c-2.7-.3-5.5-1.4-5.5-6a4.7 4.7 0 0 1 1.3-3.2 4.4 4.4 0 0 1 .1-3.1s1-.3 3.3 1.2a11.2 11.2 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2a4.4 4.4 0 0 1 .1 3.1 4.7 4.7 0 0 1 1.3 3.2c0 4.6-2.8 5.6-5.5 5.9a2.9 2.9 0 0 1 .8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .5Z" />
      </svg>
    )
  }


function LoginButton() {
  const handleLogin = () => {
    window.location.href = '/api/auth/github/login'
  }

  return (
    <Button onClick={handleLogin} variant="secondary">
      <GitHubIcon className="h-4 w-4" />
      Login with GitHub
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