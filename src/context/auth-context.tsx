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
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

type AuthUser = {
  id: string
  firstName: string
  fullName: string
  email: string
  role: string
  roleId: number
  clientId: string | null
  isActive: boolean
  profilePictureUrl?: string | null
}

type LoginPayload = {
  email: string
  password: string
  remember?: boolean
}

type Verify2FAPayload = {
  email: string
  code: string
  remember?: boolean
}

type AuthContextValue = {
  user: AuthUser | null
  token: string | null
  loading: boolean
  requires2FA: boolean
  pendingEmail: string | null
  login: (payload: LoginPayload) => Promise<void>
  verify2FA: (payload: Verify2FAPayload) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const TOKEN_KEY = 'app_token'
const REFRESH_TOKEN_KEY = 'app_refresh_token'
const USER_KEY = 'app_user'

function clearStoredSession() {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [token, setToken] = useState<string | null>(null)
  const [refreshTokenState, setRefreshTokenState] = useState<string | null>(null)
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [requires2FA, setRequires2FA] = useState(false)
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)

  // Configura interceptor do axios para adicionar token
  useEffect(() => {
    const interceptor = axios.interceptors.request.use((config) => {
      if (token && config.url?.startsWith(API_URL)) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    return () => {
      axios.interceptors.request.eject(interceptor)
    }
  }, [token])

  // Carrega sessão salva
  useEffect(() => {
    if (typeof window === 'undefined') return

    const loadSession = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY)
      const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      const storedUser = localStorage.getItem(USER_KEY)

      if (storedToken && storedUser) {
        try {
          setToken(storedToken)
          setRefreshTokenState(storedRefreshToken)
          setUser(JSON.parse(storedUser) as AuthUser)

          // Valida token obtendo dados do usuário
          const response = await axios.get(`${API_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${storedToken}` }
          })

          const userData = response.data
          const mappedUser: AuthUser = {
            id: userData.id,
            firstName: userData.first_name,
            fullName: userData.full_name,
            email: userData.email,
            role: userData.role_name,
            roleId: userData.role_id,
            clientId: userData.client_id,
            isActive: userData.is_active,
          }

          setUser(mappedUser)
          localStorage.setItem(USER_KEY, JSON.stringify(mappedUser))
        } catch (error) {
          // Token inválido, limpa sessão
          clearStoredSession()
          setToken(null)
          setRefreshTokenState(null)
          setUser(null)
        }
      }
      setLoading(false)
    }

    loadSession()
  }, [])

  const login = useCallback(
    async ({ email, password, remember }: LoginPayload) => {
      try {
        const response = await axios.post(`${API_URL}/auth/login`, {
          email,
          password,
        })

        const data = response.data

        if (data.requires_2fa) {
          // Requer 2FA
          setRequires2FA(true)
          setPendingEmail(email)
          showCustomToastSuccess(data.message || 'Código enviado para seu WhatsApp')
        } else {
          // Login direto (sem 2FA)
          const newToken = data.access_token
          const newRefreshToken = data.refresh_token

          setToken(newToken)
          setRefreshTokenState(newRefreshToken)

          const userData = data.user
          const mappedUser: AuthUser = {
            id: userData.id,
            firstName: userData.first_name,
            fullName: userData.full_name,
            email: userData.email,
            role: userData.role_name,
            roleId: userData.role_id,
            clientId: userData.client_id,
            isActive: userData.is_active,
          }

          setUser(mappedUser)

          if (remember !== false && typeof window !== 'undefined') {
            localStorage.setItem(TOKEN_KEY, newToken)
            localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
            localStorage.setItem(USER_KEY, JSON.stringify(mappedUser))
          }

          showCustomToastSuccess('Login realizado com sucesso!')
          navigate('/')
        }
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Erro ao fazer login'
        showCustomToastError(message)
        throw error
      }
    },
    [navigate]
  )

  const verify2FA = useCallback(
    async ({ email, code, remember }: Verify2FAPayload) => {
      try {
        const response = await axios.post(`${API_URL}/auth/verify-2fa`, {
          email,
          code,
        })

        const data = response.data
        const newToken = data.access_token
        const newRefreshToken = data.refresh_token

        setToken(newToken)
        setRefreshTokenState(newRefreshToken)
        setRequires2FA(false)
        setPendingEmail(null)

        // Busca dados do usuário
        const userResponse = await axios.get(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${newToken}` }
        })

        const userData = userResponse.data
        const mappedUser: AuthUser = {
          id: userData.id,
          firstName: userData.first_name,
          fullName: userData.full_name,
          email: userData.email,
          role: userData.role_name,
          roleId: userData.role_id,
          clientId: userData.client_id,
          isActive: userData.is_active,
        }

        setUser(mappedUser)

        if (remember !== false && typeof window !== 'undefined') {
          localStorage.setItem(TOKEN_KEY, newToken)
          localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
          localStorage.setItem(USER_KEY, JSON.stringify(mappedUser))
        }

        showCustomToastSuccess('Login realizado com sucesso!')
        navigate('/')
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Código inválido'
        showCustomToastError(message)
        throw error
      }
    },
    [navigate]
  )

  const refreshToken = useCallback(async () => {
    if (!refreshTokenState) {
      throw new Error('Nenhum refresh token disponível')
    }

    try {
      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshTokenState,
      })

      const data = response.data
      const newToken = data.access_token
      const newRefreshToken = data.refresh_token

      setToken(newToken)
      setRefreshTokenState(newRefreshToken)

      if (typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, newToken)
        localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
      }
    } catch (error) {
      // Refresh token inválido, faz logout
      await logout()
      throw error
    }
  }, [refreshTokenState])

  const logout = useCallback(async () => {
    setToken(null)
    setRefreshTokenState(null)
    setUser(null)
    setRequires2FA(false)
    setPendingEmail(null)
    clearStoredSession()
    showCustomToastSuccess('Logout realizado com sucesso')
    navigate('/login')
  }, [navigate])

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      requires2FA,
      pendingEmail,
      login,
      verify2FA,
      logout,
      refreshToken
    }),
    [user, token, loading, requires2FA, pendingEmail, login, verify2FA, logout, refreshToken]
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
