import { useState, useEffect } from 'react'
import { User, hasAdminAccess, isAdmin, isSupervisor, isRegularUser } from '@/lib/auth/roles'

/**
 * Hook para gerenciar autenticação e permissões do usuário
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Tentar obter dados do usuário do localStorage ou API
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          setLoading(false)
          return
        }

        // Fazer requisição para obter dados do usuário atual
        const response = await fetch('/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const userData = await response.json()
          setUser(userData.data)
        } else {
          // Token inválido, remover do localStorage
          localStorage.removeItem('token')
        }
      } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error)
        localStorage.removeItem('token')
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [])

  const login = (userData: User, token: string) => {
    localStorage.setItem('token', token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const updateUser = (userData: User) => {
    setUser(userData)
  }

  return {
    user,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user,
    hasAdminAccess: hasAdminAccess(user),
    isAdmin: isAdmin(user),
    isSupervisor: isSupervisor(user),
    isRegularUser: isRegularUser(user)
  }
}