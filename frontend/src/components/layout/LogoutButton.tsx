import { LogOut } from 'lucide-react'
import { DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { apiFetch } from '@/api/client'

type LogoutButtonProps = {
  onLogout: () => void
}

export function LogoutButton({ onLogout }: LogoutButtonProps) {
  const handleLogout = async () => {
    await apiFetch('/api/auth/logout', { method: 'POST' })
    onLogout()
  }

  return (
    <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
      <LogOut className="mr-2 h-4 w-4" />
      <span>Log out</span>
    </DropdownMenuItem>
  )
}