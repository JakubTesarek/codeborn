import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FolderGit2 } from 'lucide-react'
import { Link } from 'react-router-dom'

type Repo = {
  gid: string
  name: string
  full_name: string
  html_url: string
  size: number
  remote_version: string | null
  remote_sha: string | null
  local_version: string | null
  local_sha: string | null
}

type EligibilityResponse = {
  max_bots: number
  repos: Repo[]
}

type CreateBotFormProps = {
  botsCount: number
  onBotCreated: () => void
}

export function CreateBotForm({ botsCount, onBotCreated }: CreateBotFormProps) {
  const [eligibility, setEligibility] = useState<EligibilityResponse | null>(null)
  const [botName, setBotName] = useState('')
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [enabled, setEnabled] = useState(true)
  const [creating, setCreating] = useState(false)

  const fetchEligibility = useCallback(async () => {
    const data = await apiFetch<EligibilityResponse>('/bots/eligibility')
    setEligibility(data)
  }, [])

  const createBot = useCallback(async () => {
    if (!selectedRepo || !botName.trim()) return
    setCreating(true)
    try {
      await apiFetch('/bots/', {
        method: 'POST',
        body: JSON.stringify({
          name: botName.trim(),
          repo_gid: selectedRepo,
          enabled,
        }),
      })
      await onBotCreated()
      setBotName('')
      setSelectedRepo(null)
      setEnabled(true)
    } finally {
      setCreating(false)
      fetchEligibility()
    }
  }, [botName, selectedRepo, enabled, onBotCreated, fetchEligibility])

  useEffect(() => {
    fetchEligibility()
  }, [fetchEligibility])

  const canCreate = eligibility && botsCount < eligibility.max_bots
  const localRepos = eligibility?.repos.filter((r) => r.local_version) ?? []

  if (!canCreate) return null

  if (canCreate && localRepos.length === 0) {
    return (
      <Card className="border shadow-sm">
        <CardHeader>
          <CardTitle>Create a new Bot</CardTitle>
          <CardDescription>
            You have no usable <Link
              to="/repos"
              className="inline-flex items-center text-primary hover:underline"
            >repositories</Link> that could run a bot.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            to="/repos"
            className="inline-flex items-center text-primary hover:underline"
          >
            <FolderGit2 className="mr-2 h-4 w-4" />
            Repositories
          </Link>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border shadow-sm">
      <CardHeader>
        <CardTitle>Create a new Bot</CardTitle>
        <CardDescription>
          Choose a local <Link
              to="/repos"
              className="inline-flex items-center text-primary hover:underline"
            >repository</Link> to create a new bot instance.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-3">
        
        <div className="flex flex-col gap-2">
          <Label htmlFor="botName">Bot Name</Label>
          <Input
            id="botName"
            placeholder="e.g. alexander_the_great"
            value={botName}
            onChange={(e) => setBotName(e.target.value)}
            className="w-full sm:w-[300px]"
          />
        </div>
        
        <Select value={selectedRepo ?? ''} onValueChange={setSelectedRepo}>
          <SelectTrigger className="w-full sm:w-[300px]">
            <SelectValue placeholder="Select repository..." />
          </SelectTrigger>
          <SelectContent>
            {localRepos.map((repo) => (
              <SelectItem key={repo.gid} value={repo.gid}>
                {repo.full_name} ({repo.local_version})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2">
          <Checkbox
            id="enabled"
            checked={enabled}
            onCheckedChange={(v) => setEnabled(!!v)}
          />
          <Label htmlFor="enabled" className="text-sm">
            Enabled
          </Label>
        </div>
      </CardContent>

      <CardFooter>
        <Button
          size="sm"
          onClick={createBot}
          disabled={!selectedRepo || !botName.trim() || creating}
        >
          {creating ? 'Creating...' : 'Create Bot'}
        </Button>
      </CardFooter>
    </Card>
  )
}
