import { useEffect, useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { apiFetch } from '@/api/client'
import { formatDatetime, formatDuration } from '@/lib/utils'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'


export function BotCard({ bot, refresh }: { bot: Bot; refresh: () => void }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [showLogs, setShowLogs] = useState(false)

  const fetchMessages = useCallback(async () => {
    const data = await apiFetch<{ messages: Message[] }>(
      `/bots/${bot.gid}/messages?limit=200&offset=0`
    )
    setMessages(data.messages)
  }, [bot.gid])

  const handleAction = async (action: 'restart' | 'enable' | 'disable') => {
    setLoading(true)
    try {
      await apiFetch(`/bots/${bot.gid}/${action}`, { method: 'POST' })
      refresh()
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    fetchMessages()
    const interval = setInterval(fetchMessages, 10000)
    return () => clearInterval(interval)
  }, [fetchMessages])

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
        <Badge className={`${stateColor} text-white capitalize pointer-events-none hover:bg-current focus-visible:ring-0`}>
          {bot.state}
        </Badge>
      </CardHeader>

      <CardContent className="text-sm space-y-1">
        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Entry point:</span>
          <span>{ bot.entry_point }</span>
        </div>
        
        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Heartbeat:</span>
          <span>
            { bot.last_heartbeat
              ? `${formatDatetime(bot.last_heartbeat)} (${formatDuration(bot.heartbeat_age_sec)} ago)`
              : '—'
            }
          </span>
        </div>

        <div className="grid grid-cols-[10ch_1fr] items-start">
          <span className="text-muted-foreground font-medium">Started:</span>
          <span>
            { bot.state === 'running' && bot.start_at
              ? `${formatDatetime(bot.start_at)} (uptime ${formatDuration(bot.uptime_sec)})`
              : '—'
            }
          </span>
        </div>
      </CardContent>

      <CardFooter className="flex gap-2">
        <Button size="sm" onClick={() => handleAction('restart')} disabled={loading}>Restart</Button>
          {
            bot.enabled ? (
              <Button size="sm" variant="secondary" onClick={() => handleAction('disable')} disabled={loading}>Disable</Button>
            ) : (
              <Button size="sm" variant="secondary" onClick={() => handleAction('enable')} disabled={loading}>Enable</Button>
            )
          }
        <Button size="sm" variant="secondary" onClick={() => setShowLogs(!showLogs)}>{showLogs ? 'Hide log' : 'Show log'}</Button>
      </CardFooter>

      {
        showLogs && (
          <div className="p-4 border-t max-h-128 overflow-auto bg-muted/30 text-xs">
            {messages.map((m) => {
              return (
                <div
                  key={m.gid}
                  className="grid grid-cols-[24ch_24ch_1fr] gap-3 px-2 py-1 rounded transition-colors duration-100
                    hover:bg-accent hover:border-l-2 hover:border-primary"
                >
                  <span className="font-mono text-muted-foreground">{formatDatetime(m.datetime)}</span>
                  <span className="font-mono font-semibold truncate" title={m.type}>{m.type}</span>

                  <SyntaxHighlighter
                    language="json"
                    style={oneLight}
                    className="!m-0 !p-0 !bg-transparent font-mono text-xs leading-tight"
                  >
                    {JSON.stringify(m.payload, null, 2)}
                  </SyntaxHighlighter>
                </div>
              )
            })}
          </div>
        )
      }
    </Card>
  )
}


