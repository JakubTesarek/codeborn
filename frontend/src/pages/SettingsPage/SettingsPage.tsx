import { useOutletContext } from 'react-router-dom'
import { RemoveAccountForm } from "./RemoveAccountForm";
import { useNavigate } from 'react-router-dom'


export function SettingsPage() {
  const { user, setUser } = useOutletContext<LayoutContext>()
  const navigate = useNavigate()

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold mb-4">Settings</h1>
      <RemoveAccountForm user={user} onLogout={() => {
          setUser(null)
          navigate('/')
        }}/>
    </div>
  )
}
