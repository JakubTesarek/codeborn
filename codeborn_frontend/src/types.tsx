type User = {
  gid: string
  github: {
    gid: string
    github_id: number
    login: string
    avatar_url: string
    last_update: string
  }
}

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

type ReposResponse = {
  last_update: string | null
  repos: Repo[]
}

type Bot = {
  gid: string
  name: string
  entry_point: string
  restart_requested: boolean
  last_heartbeat: string | null
  start_at: string | null
  enabled: boolean
  state: 'running' | 'disabled' | 'starting' | 'restarting' | 'unresponsive'
  heartbeat_age_sec: number | null
  uptime_sec: number | null
}

type Message = {
  gid: string
  type: string
  datetime: string
  payload: any
}

type EligibilityResponse = {
  max_bots: number
  repos: Repo[]
}