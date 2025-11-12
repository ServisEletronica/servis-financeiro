import { createContext, useContext, useState, ReactNode } from 'react'

type SidebarContextValue = {
  collapsed: boolean
  setCollapsed: (value: boolean | ((prev: boolean) => boolean)) => void
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined)

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <SidebarContext.Provider value={{ collapsed, setCollapsed }}>
      {children}
    </SidebarContext.Provider>
  )
}

export function useSidebarState() {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error('useSidebarState deve ser usado dentro de SidebarProvider')
  }
  return context
}
