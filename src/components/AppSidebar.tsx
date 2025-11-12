import type { LucideIcon } from 'lucide-react'
import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  EllipsisVertical,
  LayoutDashboard,
  LogOut,
  Settings,
  User,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useEffect, useMemo } from 'react'
import { useSidebarState } from '@/context/sidebar-context'
import { useAuth } from '@/context/auth-context'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'

const MAIN_NAV_ITEMS = [
  { label: 'Projetado', href: '/projetado', icon: LayoutDashboard },
]

const MORE_NAV_ITEMS = [
  { label: 'Configurações', href: '/settings', icon: Settings },
]

const EXPANDED_WIDTH = 260
const COLLAPSED_WIDTH = 72
const SIDEBAR_WIDTH_EVENT = 'sidebar-width-change'

export const AppSidebar = () => {
  const { collapsed, setCollapsed } = useSidebarState()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isCollapsed = collapsed
  const location = useLocation()

  const toggleSidebar = () => setCollapsed((prev) => !prev)

  const sidebarWidth = useMemo(
    () => (isCollapsed ? COLLAPSED_WIDTH : EXPANDED_WIDTH),
    [isCollapsed],
  )

  useEffect(() => {
    if (typeof window === 'undefined') return
    window.dispatchEvent(
      new CustomEvent(SIDEBAR_WIDTH_EVENT, {
        detail: { collapsed: isCollapsed, width: sidebarWidth },
      }),
    )
  }, [isCollapsed, sidebarWidth])

  return (
    <aside
      data-state={isCollapsed ? 'collapsed' : 'expanded'}
      className={cn(
        'fixed left-0 top-0 z-50 flex h-screen flex-col border-r bg-card/90 backdrop-blur transition-[width] duration-300 ease-in-out shadow-sm',
      )}
      style={{ width: `${sidebarWidth}px` }}
    >
      <div className="flex h-16 items-center border-b px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-md bg-primary">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-7 w-7"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"
                className="fill-card stroke-card"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8 12h.01M12 12h.01M16 12h.01"
                className="stroke-primary"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          {!isCollapsed && (
            <span className="text-lg tracking-tight text-foreground">
              Financeiro <span className="font-bold">Servis</span>
            </span>
          )}
        </Link>
        {!isCollapsed && (
          <span className="ml-auto text-xs font-medium text-muted-foreground">
            v1.0.0
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col overflow-hidden">
        <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4 sidebar-scroll">
          <div className="space-y-1">
            {MAIN_NAV_ITEMS.map((item) => (
              <NavItem
                key={item.href}
                item={item}
                active={location.pathname === item.href}
                collapsed={isCollapsed}
              />
            ))}
          </div>

          <div className="space-y-1">
            {!isCollapsed && (
              <p className="px-3 text-xs font-semibold uppercase text-muted-foreground">
                Mais
              </p>
            )}
            {MORE_NAV_ITEMS.map((item) => (
              <NavItem
                key={item.href}
                item={item}
                active={location.pathname === item.href}
                collapsed={isCollapsed}
              />
            ))}
          </div>
        </nav>

        <div className="border-t px-3 py-4">
          {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div
                className={cn(
                  'group flex cursor-pointer items-center gap-3 rounded-2xl bg-primary p-3 text-primary-foreground shadow-sm transition-all hover:opacity-90',
                  isCollapsed && 'justify-center p-2',
                )}
              >
                <Avatar className={cn(
                  "shadow-sm ring-1 ring-primary-foreground/20",
                  isCollapsed ? "h-8 w-8" : "h-10 w-10"
                )}>
                  <AvatarFallback className={cn(
                    "font-semibold bg-primary-foreground/20 text-primary-foreground",
                    isCollapsed ? "text-xs" : "text-sm"
                  )}>
                    {user?.firstName?.[0]?.toUpperCase() ?? 'U'}
                  </AvatarFallback>
                </Avatar>
                {!isCollapsed && (
                  <div className="flex flex-col text-foreground">
                    <p className="text-sm font-semibold leading-tight text-primary-foreground">
                      {user?.firstName ?? 'Usuário'}
                    </p>
                    <p className="text-xs text-primary-foreground/80">{user?.role ?? 'Usuário'}</p>
                  </div>
                )}
                {!isCollapsed && (
                  <EllipsisVertical className="ml-auto h-4 w-4 text-primary-foreground/80" />
                )}
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              side="right"
              sideOffset={16}
              className="w-64 p-0"
            >
              <div className="flex items-center gap-3 px-4 py-4">
                <Avatar className="h-12 w-12 ring-2 ring-primary/20">
                  <AvatarFallback className="text-lg font-semibold bg-primary text-primary-foreground">
                    {user?.firstName?.[0]?.toUpperCase() ?? 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold leading-none">{user?.firstName ?? 'Usuário'}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{user?.role ?? 'Usuário'}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 truncate" title={user?.email}>{user?.email ?? 'email@dominio.com'}</p>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="gap-3 py-3" onClick={() => navigate('/projetado')}>
                <User className="h-4 w-4" />
                <span>Perfil</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="gap-3 py-3 text-destructive"
                onSelect={async (event) => {
                  event.preventDefault()
                  await logout().catch(() => {})
                  navigate('/login', { replace: true })
                }}
              >
                <LogOut className="h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          )}
        </div>
      </div>
      <button
        type="button"
        onClick={toggleSidebar}
        className={cn(
          'absolute top-[50px] z-10 hidden h-7 w-7 translate-x-1/2 items-center justify-center rounded-full border bg-background shadow transition-colors hover:bg-muted lg:flex',
          'right-0',
        )}
        aria-label={isCollapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
      >
        {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
    </aside>
  )
}

type NavItemConfig = {
  label: string
  href: string
  icon: LucideIcon
}

type NavItemProps = {
  item: NavItemConfig
  active?: boolean
  collapsed: boolean
}

function NavItem({ item, active, collapsed }: NavItemProps) {
  const button = (
    <div className="relative">
      <Button
        variant={active ? 'default' : 'ghost'}
        className={cn(
          'h-10 w-full rounded-xl border border-transparent transition-colors',
          active
            ? 'shadow-sm'
            : 'hover:bg-accent hover:text-accent-foreground focus-visible:ring-1 focus-visible:ring-ring',
          collapsed ? 'justify-center px-0' : 'justify-start px-3',
        )}
        asChild
      >
        <Link
          to={item.href}
          className={cn(
            'flex w-full items-center gap-3 text-sm font-medium',
            collapsed && 'justify-center gap-0',
          )}
        >
          <item.icon className={cn('h-5 w-5', collapsed && 'mx-auto')} />
          {!collapsed && <span className="truncate">{item.label}</span>}
        </Link>
      </Button>
    </div>
  )

  if (!collapsed) {
    return button
  }

  return (
    <Tooltip delayDuration={150} key={item.href}>
      <TooltipTrigger asChild>{button}</TooltipTrigger>
      <TooltipContent side="right" sideOffset={10} className="bg-card shadow">
        {item.label}
      </TooltipContent>
    </Tooltip>
  )
}
