import { useState } from 'react'
import { apiFetch } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'


interface RemoveAccountFormProps {
  user: User
  onLogout: () => void
}

export function RemoveAccountForm({ user, onLogout }: RemoveAccountFormProps) {
  const [confirmName, setConfirmName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleDelete = async () => {
    if (confirmName !== user.github.login) return
    setLoading(true)
    try {
      await apiFetch('/api/auth/me', {
        method: 'DELETE',
        body: JSON.stringify({ username:  user.github.login }),
      })
      await apiFetch('/api/auth/logout', { method: 'POST' })
      onLogout()
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="border shadow-sm">
      <CardHeader>
        <CardTitle>Remove Account</CardTitle>
        <CardDescription>
          Permanently delete your account and all related data, including source code.
          <br/>You can always create new account.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-3">
        <Label htmlFor="confirm">Type your Github username to confirm:</Label>
        <Input
          id="confirm"
          placeholder={ user.github.login}
          value={confirmName}
          onChange={(e) => setConfirmName(e.target.value)}
          onPaste={(e) => e.preventDefault()}
          onCopy={(e) => e.preventDefault()}
          onCut={(e) => e.preventDefault()}
          disabled={loading}
          className="w-full sm:w-[300px]"
        />
      </CardContent>

      <CardFooter>
        <Button
          variant="destructive"
          onClick={handleDelete}
          disabled={confirmName !==  user.github.login || loading}
        >
          {loading ? 'Deleting...' : 'Delete Account'}
        </Button>
      </CardFooter>
    </Card>
  )
}
