import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '@/api/client'
import { formatDatetime } from '@/lib/utils'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

export function BotMemory({ bot }: { bot: Bot }) {
  const [memory, setMemory] = useState<{ updated_at: string; data: any } | null>(null)

  const fetchMemory = useCallback(async () => {
    const data = await apiFetch<{ updated_at: string; data: any }>(
      `/bots/${bot.gid}/memory`
    )
    setMemory(data)
  }, [bot.gid])

  useEffect(() => {
    fetchMemory()
    const interval = setInterval(fetchMemory, 60000) // 1 minute
    return () => clearInterval(interval)
  }, [fetchMemory])

  if (!memory) {
    return (
      <div className="p-4 border-t bg-muted/30 text-xs">
        <div className="text-muted-foreground">Loading memory…</div>
      </div>
    )
  }

  return (
    <div className="p-4 border-t max-h-128 overflow-auto bg-muted/30 text-xs">
      <div className="mb-2 text-muted-foreground">
        Last updated: {formatDatetime(memory.updated_at)}
      </div>
      <SyntaxHighlighter
        language="json"
        style={oneLight}
        className="!m-0 !p-0 !bg-transparent font-mono text-xs leading-tight"
      >
        {JSON.stringify(memory.data, null, 2)}
      </SyntaxHighlighter>
    </div>
  )
}
