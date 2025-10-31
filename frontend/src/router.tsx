import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { MapPage } from '@/pages/MapPage/MapPage'
import { BotsPage } from '@/pages/BotsPage/BotsPage'
import { ArmyPage } from '@/pages/ArmyPage'
import { EconomyPage } from '@/pages/EconomyPage'
import { ReposPage } from '@/pages/ReposPage'
import { LegalPage } from '@/pages/LegalPage'
import { ErrorPage } from '@/pages/ErrorPage'


export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <ErrorPage />,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/map', element: <MapPage /> },
      { path: '/army', element: <ArmyPage /> },
      { path: '/economy', element: <EconomyPage /> },
      { path: '/bots', element: <BotsPage /> },
      { path: '/repos', element: <ReposPage /> },
    ],
  },
  { path: '/legal', element: <LegalPage /> },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
