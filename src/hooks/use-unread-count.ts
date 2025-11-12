import { useState, useEffect, useCallback } from 'react'
import { getUnreadMessagesCount } from '@/lib/api/inbox'
import { useAuth } from '@/context/auth-context'

export function useUnreadCount() {
  const { token } = useAuth()
  const [data, setData] = useState<{ count: number } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchUnreadCount = useCallback(async () => {
    if (!token) return

    setIsLoading(true)
    setError(null)

    try {
      const result = await getUnreadMessagesCount(token)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch unread count'))
    } finally {
      setIsLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (!token) return

    // Buscar imediatamente
    fetchUnreadCount()

    // Configurar intervalo de 5 segundos
    const interval = setInterval(fetchUnreadCount, 5000)

    return () => clearInterval(interval)
  }, [fetchUnreadCount, token])

  return {
    data,
    isLoading,
    error,
    refetch: fetchUnreadCount,
  }
}