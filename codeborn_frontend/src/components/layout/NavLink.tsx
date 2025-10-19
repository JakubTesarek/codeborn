import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type NavLinkProps = {
  to: string
  label: string
  onClick?: () => void
}

export function NavLink({ to, label, onClick }: NavLinkProps) {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <Button
      asChild
      variant="ghost"
      className={cn(
        'font-medium justify-start transition-colors',
        isActive
          ? 'text-primary border-b-2 border-primary rounded-none'
          : 'text-muted-foreground hover:text-foreground'
      )}
    >
      <Link to={to} onClick={onClick}>{label}</Link>
    </Button>
  )
}
