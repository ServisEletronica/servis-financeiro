import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
  theme: 'system',
  setTheme: () => null,
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

// Função para decodificar JWT e extrair a cor primária do cliente
function getClientPrimaryColor(): string | null {
  try {
    const token = localStorage.getItem('whatsapp_token')
    if (!token) return null

    const base64Url = token.split('.')[1]
    if (!base64Url) return null

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    const decoded = JSON.parse(jsonPayload)
    return decoded.clientPrimaryColor || null
  } catch {
    return null
  }
}

// Função para converter hex para HSL
function hexToHSL(hex: string): { h: number; s: number; l: number } | null {
  try {
    // Remove # se houver
    hex = hex.replace('#', '')

    // Converte para RGB
    const r = parseInt(hex.substring(0, 2), 16) / 255
    const g = parseInt(hex.substring(2, 4), 16) / 255
    const b = parseInt(hex.substring(4, 6), 16) / 255

    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h = 0,
      s = 0
    const l = (max + min) / 2

    if (max !== min) {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6
          break
        case g:
          h = ((b - r) / d + 2) / 6
          break
        case b:
          h = ((r - g) / d + 4) / 6
          break
      }
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100),
    }
  } catch {
    return null
  }
}

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'vite-ui-theme',
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
  )

  // Aplicar tema (dark/light)
  useEffect(() => {
    const root = window.document.documentElement

    root.classList.remove('light', 'dark')

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches
        ? 'dark'
        : 'light'

      root.classList.add(systemTheme)
      return
    }

    root.classList.add(theme)
  }, [theme])

  // Aplicar cor primária do cliente
  useEffect(() => {
    const resetToDefaultTheme = () => {
      const root = window.document.documentElement
      const isDark = root.classList.contains('dark')

      // Resetar para cores padrão do sistema (do main.css)
      if (isDark) {
        root.style.setProperty('--background', '0 0% 12%')
        root.style.setProperty('--foreground', '0 0% 90%')
        root.style.setProperty('--card', '0 0% 16%')
        root.style.setProperty('--card-foreground', '0 0% 90%')
        root.style.setProperty('--popover', '0 0% 16%')
        root.style.setProperty('--popover-foreground', '0 0% 90%')
        // Primary padrão: fundo mais visível, texto MUITO vibrante e mais claro
        root.style.setProperty('--primary', '244 30% 25%')
        root.style.setProperty('--primary-foreground', '244 56% 85%') // Mais claro
        root.style.setProperty('--secondary', '0 0% 25%')
        root.style.setProperty('--secondary-foreground', '0 0% 90%')
        root.style.setProperty('--muted', '0 0% 15%')
        root.style.setProperty('--muted-foreground', '0 0% 64%')
        root.style.setProperty('--accent', '0 0% 22%')
        root.style.setProperty('--accent-foreground', '0 0% 88%')
        root.style.setProperty('--border', '0 0% 21%')
        root.style.setProperty('--input', '0 0% 19%')
        root.style.setProperty('--ring', '244 56% 85%') // Mais claro
        root.style.setProperty('--sidebar', '0 0% 10%')
        root.style.setProperty('--sidebar-foreground', '0 0% 90%')
        root.style.setProperty('--sidebar-primary', '244 30% 25%')
        root.style.setProperty('--sidebar-primary-foreground', '244 56% 85%') // Mais claro
        root.style.setProperty('--sidebar-accent', '0 0% 22%')
        root.style.setProperty('--sidebar-accent-foreground', '0 0% 88%')
        root.style.setProperty('--sidebar-border', '0 0% 19%')
        root.style.setProperty('--sidebar-ring', '244 56% 85%') // Mais claro
      } else {
        root.style.setProperty('--background', '244 23% 97%')
        root.style.setProperty('--foreground', '244 14% 27%')
        root.style.setProperty('--card', '0 0% 100%')
        root.style.setProperty('--card-foreground', '244 14% 27%')
        root.style.setProperty('--popover', '0 0% 100%')
        root.style.setProperty('--popover-foreground', '244 14% 27%')
        root.style.setProperty('--primary', '244 47% 37%')
        root.style.setProperty('--primary-foreground', '0 0% 98%')
        root.style.setProperty('--secondary', '244 35% 87%')
        root.style.setProperty('--secondary-foreground', '244 47% 22%')
        root.style.setProperty('--muted', '244 3% 96%')
        root.style.setProperty('--muted-foreground', '244 3% 45%')
        root.style.setProperty('--accent', '244 35% 90%')
        root.style.setProperty('--accent-foreground', '244 47% 20%')
        root.style.setProperty('--border', '244 18% 82%')
        root.style.setProperty('--input', '244 23% 92%')
        root.style.setProperty('--ring', '244 47% 37%')
        root.style.setProperty('--sidebar', '244 23% 95%')
        root.style.setProperty('--sidebar-foreground', '244 14% 27%')
        root.style.setProperty('--sidebar-primary', '244 47% 37%')
        root.style.setProperty('--sidebar-primary-foreground', '0 0% 98%')
        root.style.setProperty('--sidebar-accent', '244 35% 90%')
        root.style.setProperty('--sidebar-accent-foreground', '244 47% 20%')
        root.style.setProperty('--sidebar-border', '244 18% 85%')
        root.style.setProperty('--sidebar-ring', '244 47% 37%')
      }
    }

    const applyClientTheme = () => {
      const primaryColor = getClientPrimaryColor()

      // Se não houver token/cor do cliente, resetar para tema padrão
      if (!primaryColor) {
        resetToDefaultTheme()
        return
      }

      const hsl = hexToHSL(primaryColor)
      if (!hsl) {
        resetToDefaultTheme()
        return
      }

      const root = window.document.documentElement

      // Detectar modo dark/light DINAMICAMENTE
      const isDark = root.classList.contains('dark')

      // Aplicar cor primária do cliente como CSS variables
      if (isDark) {
        // Dark mode: inverter o esquema
        // Fundo do botão: tom mais visível (saturação e luminosidade maiores)
        const bgSat = Math.min(hsl.s * 0.6, 50) // 60% da saturação original, máx 50%
        const bgL = 25 // Luminosidade maior para melhor visibilidade
        root.style.setProperty('--primary', `${hsl.h} ${bgSat}% ${bgL}%`)

        // Texto do botão: cor MUITO vibrante e mais claro
        let textL = hsl.l
        if (hsl.l < 60) {
          textL = Math.min(hsl.l + 35, 85) // Clarear ainda mais para melhor visibilidade
        } else {
          textL = Math.min(hsl.l + 15, 90) // Cores claras ficam bem brilhantes
        }
        const textS = Math.min(hsl.s * 1.2, 100) // Aumentar saturação em 20% (até 100%)
        root.style.setProperty('--primary-foreground', `${hsl.h} ${textS}% ${textL}%`)
      } else {
        // Light mode: manter como estava
        root.style.setProperty('--primary', `${hsl.h} ${hsl.s}% ${hsl.l}%`)
        const foregroundL = hsl.l > 65 ? 10 : 98
        root.style.setProperty('--primary-foreground', `0 0% ${foregroundL}%`)
      }

      // Hover states e Ring (para focus)
      if (isDark) {
        // Dark mode: hover um pouco mais claro que o fundo
        root.style.setProperty('--primary-hover', `${hsl.h} ${Math.min(hsl.s * 0.6, 50)}% 30%`)
        // Ring: cor MUITO vibrante (mesma lógica do texto)
        let ringL = hsl.l < 60 ? Math.min(hsl.l + 35, 85) : Math.min(hsl.l + 15, 90)
        const ringS = Math.min(hsl.s * 1.2, 100)
        root.style.setProperty('--ring', `${hsl.h} ${ringS}% ${ringL}%`)
      } else {
        // Light mode
        const hoverL = hsl.l > 50 ? hsl.l - 5 : hsl.l + 5
        root.style.setProperty('--primary-hover', `${hsl.h} ${hsl.s}% ${hoverL}%`)
        root.style.setProperty('--ring', `${hsl.h} ${hsl.s}% ${hsl.l}%`)
      }

      // Background e cores de base
      if (isDark) {
        // Dark mode: background NEUTRO (cinza puro, sem toque da primary)
        root.style.setProperty('--background', `0 0% 12%`)
        root.style.setProperty('--foreground', `0 0% 90%`)

        // Card
        root.style.setProperty('--card', `0 0% 16%`)
        root.style.setProperty('--card-foreground', `0 0% 90%`)

        // Popover
        root.style.setProperty('--popover', `0 0% 16%`)
        root.style.setProperty('--popover-foreground', `0 0% 90%`)

        // Input
        root.style.setProperty('--input', `0 0% 19%`)

        // Sidebar
        root.style.setProperty('--sidebar', `0 0% 10%`)
        root.style.setProperty('--sidebar-foreground', `0 0% 90%`)
      } else {
        // Light mode: background neutro
        root.style.setProperty('--background', `${hsl.h} 23% 97%`)
        root.style.setProperty('--foreground', `${hsl.h} 14% 27%`)

        // Card
        root.style.setProperty('--card', `0 0% 100%`)
        root.style.setProperty('--card-foreground', `${hsl.h} 14% 27%`)

        // Popover
        root.style.setProperty('--popover', `0 0% 100%`)
        root.style.setProperty('--popover-foreground', `${hsl.h} 14% 27%`)

        // Input
        root.style.setProperty('--input', `${hsl.h} 23% 92%`)

        // Sidebar
        root.style.setProperty('--sidebar', `${hsl.h} 23% 95%`)
        root.style.setProperty('--sidebar-foreground', `${hsl.h} 14% 27%`)
      }

      // Secondary (badges, etc) - NEUTRO no dark mode
      if (isDark) {
        root.style.setProperty('--secondary', `0 0% 25%`)
        root.style.setProperty('--secondary-foreground', `0 0% 90%`)
      } else {
        const secondarySat = Math.max(hsl.s * 0.5, 35) // Mesma saturação do accent
        const secondaryL = 87 // Um pouco mais escuro que accent (90%)
        root.style.setProperty('--secondary', `${hsl.h} ${secondarySat}% ${secondaryL}%`)
        root.style.setProperty('--secondary-foreground', `${hsl.h} ${Math.min(hsl.s, 60)}% 22%`)
      }

      // Border - NEUTRO no dark mode
      if (isDark) {
        root.style.setProperty('--border', `0 0% 21%`)
        root.style.setProperty('--sidebar-border', `0 0% 19%`)
      } else {
        root.style.setProperty('--border', `${hsl.h} 18% 82%`)
        root.style.setProperty('--sidebar-border', `${hsl.h} 18% 85%`)
      }

      // Muted e muted-foreground - TOTALMENTE NEUTROS no dark mode
      // Tabs, backgrounds secundários devem ser cinza puro
      if (isDark) {
        // Dark mode: cinza puro
        root.style.setProperty('--muted', `0 0% 15%`)
        root.style.setProperty('--muted-foreground', `0 0% 64%`)

        // Accent para hover - NEUTRO no dark mode
        root.style.setProperty('--accent', `0 0% 22%`)
        root.style.setProperty('--accent-foreground', `0 0% 88%`)
      } else {
        // Light mode: cinza quase puro
        root.style.setProperty('--muted', `${hsl.h} 3% 96%`)
        root.style.setProperty('--muted-foreground', `${hsl.h} 3% 45%`)

        // Accent para hover (suave mas com cor visível - 35% saturação)
        const accentSat = Math.max(hsl.s * 0.5, 35)
        root.style.setProperty('--accent', `${hsl.h} ${accentSat}% 90%`)
        root.style.setProperty('--accent-foreground', `${hsl.h} ${Math.min(hsl.s, 60)}% 20%`)
      }

      // Sidebar colors
      if (isDark) {
        // Dark mode: fundo mais visível, texto MUITO vibrante e mais claro
        const bgSat = Math.min(hsl.s * 0.6, 50)
        root.style.setProperty('--sidebar-primary', `${hsl.h} ${bgSat}% 25%`)
        // Texto: cor MUITO vibrante e mais claro
        const textL = hsl.l < 60 ? Math.min(hsl.l + 35, 85) : Math.min(hsl.l + 15, 90)
        const textS = Math.min(hsl.s * 1.2, 100)
        root.style.setProperty('--sidebar-primary-foreground', `${hsl.h} ${textS}% ${textL}%`)
        // Ring: cor MUITO vibrante
        root.style.setProperty('--sidebar-ring', `${hsl.h} ${textS}% ${textL}%`)
      } else {
        // Light mode
        root.style.setProperty('--sidebar-primary', `${hsl.h} ${hsl.s}% ${hsl.l}%`)
        const foregroundL = hsl.l > 65 ? 10 : 98
        root.style.setProperty('--sidebar-primary-foreground', `0 0% ${foregroundL}%`)
        root.style.setProperty('--sidebar-ring', `${hsl.h} ${hsl.s}% ${hsl.l}%`)
      }

      // Sidebar accent para hover - NEUTRO no dark mode
      if (isDark) {
        root.style.setProperty('--sidebar-accent', `0 0% 22%`)
        root.style.setProperty('--sidebar-accent-foreground', `0 0% 88%`)
      } else {
        const accentSat = Math.max(hsl.s * 0.5, 35)
        root.style.setProperty('--sidebar-accent', `${hsl.h} ${accentSat}% 90%`)
        root.style.setProperty('--sidebar-accent-foreground', `${hsl.h} ${Math.min(hsl.s, 60)}% 20%`)
      }
    }

    applyClientTheme()

    // Listener para mudanças no localStorage (quando troca de cliente)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'whatsapp_token') {
        applyClientTheme()
      }
    }

    // Listener para evento customizado (quando troca de cliente na mesma aba)
    const handleClientThemeChange = () => {
      applyClientTheme()
    }

    // Listener para mudanças de tema (dark/light) - reaplicar cores
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          applyClientTheme()
        }
      })
    })

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('clientThemeChange', handleClientThemeChange)
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('clientThemeChange', handleClientThemeChange)
      observer.disconnect()
    }
  }, [])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error('useTheme must be used within a ThemeProvider')

  return context
}
