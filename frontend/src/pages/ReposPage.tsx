import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { apiFetch } from '@/api/client'
import { formatSize } from '@/lib/utils'
import { Download, RefreshCw, Trash2 } from 'lucide-react'


export function ReposPage() {
  const [repos, setRepos] = useState<Repo[]>([])
  const [lastUpdate, setLastUpdate] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [loadingRepos, setLoadingRepos] = useState<Record<string, boolean>>({})

  async function fetchRepos() {
    setLoading(true)
    try {
      const data = await apiFetch<ReposResponse>('/repos/')
      setRepos(data.repos)
      setLastUpdate(data.last_update)
    } finally {
      setLoading(false)
    }
  }

  async function refreshRepos() {
    setLoading(true)
    try {
      const data = await apiFetch<ReposResponse>('/repos/refresh', { method: 'POST' })
      setRepos(data.repos)
      setLastUpdate(data.last_update)
    } finally {
      setLoading(false)
    }
  }
  
  function setRepoLoading(gid: string, loading: boolean) {
    setLoadingRepos((prev) => ({ ...prev, [gid]: loading }))
  }
  
  async function updateRepo(repo: Repo) {
    setRepoLoading(repo.gid, true)
    try {
      const data = await apiFetch<Repo>(`/repos/${repo.gid}/update`, { method: 'POST' })
      setRepos((prev) => prev.map((r) => (r.gid === repo.gid ? data : r)))
    } finally {
      setRepoLoading(repo.gid, false)
    }
  }

  async function deleteRepo(repo: Repo) {
    setRepoLoading(repo.gid, true)
    try {
      const data = await apiFetch<Repo>(`/repos/${repo.gid}/delete`, { method: 'POST' })
      setRepos((prev) => prev.map((r) => (r.gid === repo.gid ? data : r)))
    } finally {
      setRepoLoading(repo.gid, false)
    }
  }
  
  useEffect(() => {
    fetchRepos()
  }, [])

  const filteredRepos = repos.filter((r) => r.name.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="p-6 space-y-4">
    
      {/* Header with filter */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Repositories</h1>
        <div className="flex items-center gap-3">
        {lastUpdate && (
          <span className="text-sm text-muted-foreground">
          Last updated: {new Date(lastUpdate).toLocaleString()}
          </span>
        )}
          <input
            type="text"
            placeholder="Filter by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-9 px-2 rounded-md border border-input bg-background text-sm"
          />
          <Button onClick={refreshRepos} disabled={loading}>{loading ? 'Refreshing...' : 'Refresh'}</Button>
        </div>
      </div>
    
      <Card>
        <CardHeader>
          <CardTitle>Your GitHub Repositories</CardTitle>
        </CardHeader>
        <CardContent>

          {/* Main table with repos */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead className="text-right">Size</TableHead>
                <TableHead className="text-right">Remote SHA</TableHead>
                <TableHead className="text-right">Remote Version</TableHead>
                <TableHead className="text-right">Local SHA</TableHead>
                <TableHead className="text-right">Local Version</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRepos.map((repo) => {
                const hasRemote = !!repo.remote_version
                const hasLocal = !!repo.local_sha
                const sameSha = repo.local_sha && repo.remote_sha && repo.local_sha === repo.remote_sha

                return (
                  <TableRow key={repo.gid} className={!hasRemote ? 'opacity-50' : ''}>
                    <TableCell>
                      <a
                        href={repo.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        {repo.name}
                      </a>
                    </TableCell>

                    <TableCell className="text-right font-mono">{formatSize(repo.size)}</TableCell>
                    <TableCell className="text-right font-mono">{repo.remote_sha ? `#${repo.remote_sha}` : ''}</TableCell>
                    <TableCell className="text-right font-mono">{repo.remote_version ?? ''}</TableCell>
                    <TableCell className="text-right font-mono">{repo.local_sha ? `#${repo.local_sha}` : ''}</TableCell>
                    <TableCell className="text-right font-mono">{repo.local_version ?? ''}</TableCell>

                    <TableCell className="text-right space-x-2">
                      {hasRemote && (
                        <Button
                          size="sm"
                          variant="secondary"
                          disabled={sameSha || loadingRepos[repo.gid]}
                          onClick={() => updateRepo(repo)}
                          className="inline-flex items-center gap-1"
                        >
                          {hasLocal ? (
                            <>
                              <RefreshCw className={`w-4 h-4 ${loadingRepos[repo.gid] ? 'animate-spin' : ''}`} />
                              Pull
                            </>
                          ) : (
                            <>
                              <Download className={`w-4 h-4 ${loadingRepos[repo.gid] ? 'animate-bounce' : ''}`} />
                              Clone
                            </>
                          )}
                        </Button>
                      )}

                      {hasLocal && (
                        <Button
                          size="sm"
                          variant="destructive"
                          disabled={loadingRepos[repo.gid]}
                          onClick={() => deleteRepo(repo)}
                          className="inline-flex items-center gap-1"
                        >
                          <Trash2 className={`w-4 h-4 ${loadingRepos[repo.gid] ? 'animate-pulse' : ''}`} />
                          Delete
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                )
              })}
        
              {repos.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-muted-foreground">No repositories found.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
