import { Link } from "react-router-dom";

export function ErrorPage() {
  return (
    <div className="relative flex h-screen flex-col items-center justify-center overflow-hidden text-center text-zinc-100">
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-900 via-zinc-950 to-black" />
      <div className="absolute w-96 h-96 bg-primary/20 rounded-full blur-3xl top-1/4 -z-10" />

      <div className="relative z-10 max-w-md px-6 space-y-6">
        <h1 className="text-4xl font-bold tracking-tight">404</h1>
        <p className="text-zinc-400 text-base">
            These are not the droids you're looking for. <Link className="underline" to="/">Move&nbsp;along.</Link>
        </p>
      </div>
    </div>
  )
}