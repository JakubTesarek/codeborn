import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { FolderGit2, Menu, Settings } from 'lucide-react'
import { LogoutButton } from '@/components/layout/LogoutButton'
import { NavLink } from '@/components/layout/NavLink'
import { Link } from 'react-router-dom'


type TopNavProps = {
  user: User
  onLogout: () => void
}

export function TopNav({ user, onLogout }: TopNavProps) {
  const [open, setOpen] = useState(false)

  return (
    <header className="flex items-center justify-between border-b bg-background px-4 py-2">
      
      {/* Left: logo and nav links */}
      <div className="flex items-center gap-4">
        <span className="text-xl font-semibold">Codeborn</span>

        {/* Desktop links */}
        <nav className="hidden md:flex items-center gap-4">
          <NavLink to="/" label="Dashboard" />
          <NavLink to="/map" label="Map" />
          <NavLink to="/army" label="Army" />
          <NavLink to="/economy" label="Economy" />
          <NavLink to="/bots" label="Bots" />
        </nav>

        {/* Mobile menu trigger */}
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>

          <SheetContent side="left" className="w-56 p-4">
            <nav className="flex flex-col gap-3 mt-4">
              <NavLink to="/" label="Dashboard" onClick={() => setOpen(false)} />
              <NavLink to="/map" label="Map" onClick={() => setOpen(false)} />
              <NavLink to="/army" label="Army" onClick={() => setOpen(false)} />
              <NavLink to="/economy" label="Economy" onClick={() => setOpen(false)} />
              <NavLink to="/bots" label="Bots" onClick={() => setOpen(false)} />
            </nav>
          </SheetContent>
        </Sheet>
      </div>

      {/* Right: avatar dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            className="relative rounded-full hover:ring-2 hover:ring-ring hover:ring-offset-2 transition"
            title={user.github?.login}
          >
            <Avatar className="w-8 h-8">
              <AvatarImage src={user.github?.avatar_url} alt={user.github?.login} />
              <AvatarFallback>{user.github?.login ? user.github.login.slice(0, 2).toUpperCase() : '??'}</AvatarFallback>
            </Avatar>
          </button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>{user.github?.login}</DropdownMenuLabel>
          <DropdownMenuSeparator />

          <DropdownMenuItem className="cursor-pointer">
            <Link to="/settings" className="flex items-center">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </DropdownMenuItem>

          <DropdownMenuItem className="cursor-pointer">
             <Link to="/repos" className="flex items-center">
              <FolderGit2 className="mr-2 h-4 w-4" />
                Repositories
              </Link>
          </DropdownMenuItem>

          <DropdownMenuSeparator />
          <LogoutButton onLogout={onLogout} />
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
