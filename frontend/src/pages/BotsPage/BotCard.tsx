import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { formatDatetime, formatDuration } from '@/lib/utils'
import { BotLog } from './BotLog'
import { BotMemory } from './BotMemory'
import { apiFetch } from '@/api/client'

export function BotCard({ bot, refresh }: { bot: Bot; refresh: () => void }) {
  const [loading, setLoading] = useState(false)
  const [showLogs, setShowLogs] = useState(false)
  const [showMemory, setShowMemory] = useState(false)

  const handleAction = async (action: 'restart' | 'enable' | 'disable') => {
    setLoading(true)
    try {
      await apiFetch(`/bots/${bot.gid}/${action}`, { method: 'POST' })
      refresh()
    } finally {
      setLoading(false)
    }
  }

  const toggleLogs = () => {
    if (showLogs) setShowLogs(false)
    else {
      setShowMemory(false)
      setShowLogs(true)
    }
  }

  const toggleMemory = () => {
    if (showMemory) setShowMemory(false)
    else {
      setShowLogs(false)
      setShowMemory(true)
    }
  }

  const stateColor = {
    running: 'bg-green-500',
    starting: 'bg-yellow-500',
    restarting: 'bg-yellow-500',
    unresponsive: 'bg-red-500',
    disabled: 'bg-gray-400',
  }[bot.state]

  return (
    <Card className="border shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{bot.name}</CardTitle>
        <Badge
          className={`${stateColor} text-white capitalize pointer-events-none hover:bg-current focus-visible:ring-0`}
        >
          {bot.state}
        </Badge>
      </CardHeader>

      <CardContent className="text-sm space-y-1">
        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Entry point:</span>
          <span>{bot.entry_point}</span>
        </div>

        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Heartbeat:</span>
          <span>
            {bot.last_heartbeat
              ? `${formatDatetime(bot.last_heartbeat)} (${formatDuration(bot.heartbeat_age_sec)} ago)`
              : '—'}
          </span>
        </div>

        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Started:</span>
          <span>
            {bot.state === 'running' && bot.start_at
              ? `${formatDatetime(bot.start_at)} (uptime ${formatDuration(bot.uptime_sec)})`
              : '—'}
          </span>
        </div>
      </CardContent>

      <CardFooter className="flex gap-2">
        <Button size="sm" onClick={() => handleAction('restart')} disabled={loading}>
          Restart
        </Button>
        {bot.enabled ? (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => handleAction('disable')}
            disabled={loading}
          >
            Disable
          </Button>
        ) : (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => handleAction('enable')}
            disabled={loading}
          >
            Enable
          </Button>
        )}
        <Button size="sm" variant="secondary" onClick={toggleLogs}>
          {showLogs ? 'Hide log' : 'Show log'}
        </Button>
        <Button size="sm" variant="secondary" onClick={toggleMemory}>
          {showMemory ? 'Hide memory' : 'Show memory'}
        </Button>
      </CardFooter>

      {showLogs && <BotLog bot={bot} />}
      {showMemory && <BotMemory bot={bot} />}
    </Card>
  )
}
