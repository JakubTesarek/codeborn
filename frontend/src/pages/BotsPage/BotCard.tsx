import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { formatDatetime, formatDuration } from '@/lib/utils'
import { apiFetch } from '@/api/client'
import { BotLog } from './BotLog'
import { BotMemory } from './BotMemory'

export function BotCard({ bot, refresh }: { bot: Bot; refresh: () => void }) {
  const [loading, setLoading] = useState(false)

  const handleAction = async (action: 'restart' | 'enable' | 'disable') => {
    setLoading(true)
    try {
      await apiFetch(`/api/bots/${bot.gid}/${action}`, { method: 'POST' })
      refresh()
    } finally {
      setLoading(false)
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
    <Card className="border shadow-sm hover:shadow-md transition-shadow duration-200">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold">{bot.name}</CardTitle>
        <Badge
          className={`${stateColor} text-white capitalize pointer-events-none hover:bg-current focus-visible:ring-0`}
        >
          {bot.state}
        </Badge>
      </CardHeader>

      <CardContent className="text-sm space-y-1">
        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Repository:</span>
          <span className="font-mono">{bot.entry_point}</span>
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

      <CardFooter className="flex flex-wrap justify-between items-center gap-2 border-t pt-3">
        <div className="flex gap-2">
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
        </div>

        <Tabs defaultValue="log" className="w-full">
          <TabsList className="w-full grid grid-cols-2 mt-3">
            <TabsTrigger value="log">Log</TabsTrigger>
            <TabsTrigger value="memory">Memory</TabsTrigger>
          </TabsList>

          <TabsContent value="log">
            <BotLog bot={bot} />
          </TabsContent>

          <TabsContent value="memory">
            <BotMemory bot={bot} />
          </TabsContent>
        </Tabs>
      </CardFooter>
    </Card>
  )
}
