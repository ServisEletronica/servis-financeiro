import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import { showCustomToastSuccess, showCustomToastError } from '@/lib/toast'

type AuthUser = {
  id: string
  firstName: string
  fullName: string
  email: string
  role: string
  roleId: number
  isActive: boolean
  profilePictureUrl?: string | null
}

type LoginPayload = {
  email: string
  password: string
  remember?: boolean
}

type AuthContextValue = {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (payload: LoginPayload) => Promise<{ token: string; user: AuthUser }>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const TOKEN_KEY = 'app_token'
const USER_KEY = 'app_user'

// Usuário mock para teste
const MOCK_USER: AuthUser = {
  id: '1',
  firstName: 'Admin',
  fullName: 'Admin User',
  email: 'admin@teste.com',
  role: 'Administrador',
  roleId: 1,
  isActive: true,
  profilePictureUrl: null,
}

function clearStoredSession() {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_KEY)
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser) as AuthUser)
      } catch (error) {
        clearStoredSession()
      }
    }
    setLoading(false)
  }, [])

  const login = useCallback(
    async ({ email, password, remember }: LoginPayload) => {
      // Simula uma chamada de API
      await new Promise(resolve => setTimeout(resolve, 500))

      // Validação mock - aceita qualquer email com senha "12345678"
      if (password !== '12345678') {
        throw new Error('Credenciais inválidas. Use a senha: 12345678')
      }

      const mockToken = `mock-token-${Date.now()}`
      const mockUser = { ...MOCK_USER, email }

      setToken(mockToken)
      setUser(mockUser)

      if (remember !== false && typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, mockToken)
        localStorage.setItem(USER_KEY, JSON.stringify(mockUser))
      }

      return { token: mockToken, user: mockUser }
    },
    []
  )

  const logout = useCallback(async () => {
    setToken(null)
    setUser(null)
    clearStoredSession()
  }, [])

  const value = useMemo(
    () => ({ user, token, loading, login, logout }),
    [user, token, loading, login, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider')
  }
  return context
}
