export function LegalPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col items-center">
      <div className="absolute inset-0 bg-gradient-to-b from-zinc-900 via-zinc-950 to-black" />

        <div className="relative z-10 max-w-2xl px-6 py-12 space-y-6 text-sm">
          <h1 className="text-2xl font-semibold">Privacy & Terms</h1>
          <p className="text-zinc-300">
          CodeBorn is a personal side project where users can create bots that compete in a strategy game.
        </p>

        <section>
          <h2 className="text-lg font-medium text-zinc-100">Data collection</h2>
          <ul className="list-disc pl-5 space-y-1 text-zinc-300">
            <li>Your GitHub account info (username, and possibly email in the future if you grant access).</li>
            <li>Repositories you explicitly authorize CodeBorn to access.</li>
            <li>Game-related data such as bot configurations, matches, scores, and logs.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-medium text-zinc-100">What is not collected or shared</h2>
          <ul className="list-disc pl-5 space-y-1 text-zinc-300">
            <li>No tracking, analytics, or marketing data.</li>
            <li>Emails (if collected later) are used only for game-related features.</li>
            <li>We'll always ask you before sending you anything.</li>
            <li>No data is ever sold or shared with third parties.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-medium text-zinc-100">Your control</h2>
          <ul className="list-disc pl-5 space-y-1 text-zinc-300">
            <li>You can revoke GitHub access at any time.</li>
            <li>You can delete your account at any time from within the app.</li>
            <li>Account deletion immediately removes all associated data.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-medium text-zinc-100 text-zinc-300">Project status</h2>
          <p className="text-zinc-300">CodeBorn is an experimental personal project and may be paused or discontinued at any time.</p>
        </section>

        <p className="text-zinc-300">
          For any questions, please{' '}
          <a
            href="https://github.com/JakubTesarek"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-zinc-300"
          >
            contact me on GitHub
          </a>.
        </p>

        <div className="pt-8">
          <a href="/" className="text-sm text-zinc-400 underline hover:text-zinc-200">
            ← Back to CodeBorn
          </a>
        </div>
      </div>
    </div>
  )
}
