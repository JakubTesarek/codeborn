import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { MapPage } from '@/pages/MapPage/MapPage'
import { BotsPage } from '@/pages/BotsPage/BotsPage'
import { ArmyPage } from '@/pages/ArmyPage'
import { EconomyPage } from '@/pages/EconomyPage'
import { ReposPage } from '@/pages/ReposPage'
import { LegalPage } from './pages/LegalPage'


export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/map', element: <MapPage /> },
      { path: '/army', element: <ArmyPage /> },
      { path: '/economy', element: <EconomyPage /> },
      { path: '/bots', element: <BotsPage /> },
      { path: '/repos', element: <ReposPage /> },
    ],
  },
  { path: '/legal', element: <LegalPage /> }, // standalone page, no AppLayout
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
