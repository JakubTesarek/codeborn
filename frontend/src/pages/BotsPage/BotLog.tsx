import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '@/api/client'
import { formatDatetime } from '@/lib/utils'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

export function BotLog({ bot }: { bot: Bot }) {
  const [messages, setMessages] = useState<Message[]>([])

  const fetchMessages = useCallback(async () => {
    const data = await apiFetch<{ messages: Message[] }>(
      `/bots/${bot.gid}/messages?limit=200&offset=0`
    )
    setMessages(data.messages)
  }, [bot.gid])

  useEffect(() => {
    fetchMessages()
    const interval = setInterval(fetchMessages, 10000)
    return () => clearInterval(interval)
  }, [fetchMessages])

  return (
    <div className="p-4 border-t max-h-128 overflow-auto bg-muted/30 text-xs">
      {messages.map((m) => (
        <div
          key={m.gid}
          className="grid grid-cols-[24ch_24ch_1fr] gap-3 px-2 py-1 rounded transition-colors duration-100
            hover:bg-accent hover:border-l-2 hover:border-primary"
        >
          <span className="font-mono text-muted-foreground">{formatDatetime(m.datetime)}</span>
          <span className="font-mono font-semibold truncate" title={m.type}>
            {m.type}
          </span>
          <SyntaxHighlighter
            language="json"
            style={oneLight}
            className="!m-0 !p-0 !bg-transparent font-mono text-xs leading-tight"
          >
            {JSON.stringify(m.payload, null, 2)}
          </SyntaxHighlighter>
        </div>
      ))}
    </div>
  )
}
