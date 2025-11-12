import { Outlet, useLocation } from 'react-router-dom'
import { AppSidebar } from '@/components/AppSidebar'
import { MobileNav } from '@/components/MobileNav'
import { ChatBot } from '@/components/ChatBot'
import { cn } from '@/lib/utils'
import { type CSSProperties, useEffect, useMemo, useState } from 'react'
import { useSidebarState } from '@/context/sidebar-context'

export default function Layout() {
  const location = useLocation()
  const { collapsed } = useSidebarState()
  const isLoginPage = location.pathname === '/login'
  const [isDesktop, setIsDesktop] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(min-width: 768px)').matches
  })

  useEffect(() => {
    if (typeof window === 'undefined') return
    const mediaQuery = window.matchMedia('(min-width: 768px)')
    const handleMediaChange = (event: MediaQueryListEvent) => {
      setIsDesktop(event.matches)
    }
    setIsDesktop(mediaQuery.matches)
    mediaQuery.addEventListener('change', handleMediaChange)
    return () => mediaQuery.removeEventListener('change', handleMediaChange)
  }, [])

  if (isLoginPage) {
    return <Outlet />
  }

  const sidebarWidth = useMemo(() => (collapsed ? 72 : 260), [collapsed])

  const desktopContentStyle = useMemo(() => {
    if (!isDesktop) return undefined
    return {
      marginLeft: `${sidebarWidth}px`,
    } satisfies CSSProperties
  }, [isDesktop, sidebarWidth])

  return (
    <div className="flex min-h-screen w-full overflow-x-hidden">
      <div className="hidden md:block">
        <AppSidebar />
      </div>
      <div
        className="flex flex-1 flex-col transition-[margin-left] duration-300 ease-in-out max-w-full overflow-x-hidden"
        id="main-content"
        style={desktopContentStyle}
      >
        <header className="flex h-14 items-center justify-between gap-4 border-b bg-background px-4 md:hidden sticky top-0 z-40">
          <MobileNav />
        </header>
        <main className="flex-1 flex flex-col overflow-hidden max-w-full">
          <Outlet />
        </main>
      </div>
      <ChatBot />
    </div>
  )
}
