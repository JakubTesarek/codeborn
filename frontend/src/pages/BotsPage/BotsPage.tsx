import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '@/api/client'
import { BotCard } from './BotCard'
import { CreateBotForm } from './CreateBotForm'


export function BotsPage() {
  const [bots, setBots] = useState<Bot[]>([])

  const fetchBots = useCallback(async () => {
    try {
      const data = await apiFetch<{ bots: Bot[] }>('/bots/')
      setBots(data.bots)
    } finally {
    }
  }, [])

  useEffect(() => {
    fetchBots()
    const interval = setInterval(fetchBots, 5000)
    return () => clearInterval(interval)
  }, [fetchBots])

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold mb-4">Bots</h1>
      <CreateBotForm botsCount={bots.length} onBotCreated={fetchBots} />
      {bots.map((bot) => (
        <BotCard key={bot.gid} bot={bot} refresh={fetchBots} />
      ))}
      {bots.length === 0 && <p className="text-muted-foreground">No bots found.</p>}
    </div>
  )
}
