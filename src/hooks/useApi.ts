import { useState, useCallback } from 'react'
import { api, ApiError } from '@/services/api'

type UseApiState<T> = {
  data: T | null
  loading: boolean
  error: string | null
}

type UseApiReturn<T> = UseApiState<T> & {
  execute: (...args: any[]) => Promise<T | null>
  reset: () => void
}

/**
 * Hook para fazer requisições de API com gerenciamento de estado
 *
 * Exemplo de uso:
 * ```tsx
 * const { data, loading, error, execute } = useApi(
 *   () => api.get('/users')
 * )
 *
 * useEffect(() => {
 *   execute()
 * }, [])
 * ```
 */
export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState((prev) => ({ ...prev, loading: true, error: null }))

      try {
        const result = await apiFunction(...args)
        setState({ data: result, loading: false, error: null })
        return result
      } catch (err) {
        const errorMessage =
          err instanceof ApiError ? err.message : 'Erro ao processar requisição'
        setState((prev) => ({ ...prev, loading: false, error: errorMessage }))
        return null
      }
    },
    [apiFunction]
  )

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    execute,
    reset,
  }
}

/**
 * Hook para fazer requisições GET com carregamento automático
 */
export function useApiGet<T = any>(
  endpoint: string,
  autoFetch = true
): UseApiReturn<T> {
  const result = useApi<T>(() => api.get(endpoint))

  // Auto-fetch no mount
  if (autoFetch && !result.loading && !result.data && !result.error) {
    result.execute()
  }

  return result
}

/**
 * Hook para fazer requisições POST
 */
export function useApiPost<T = any>(endpoint: string) {
  return useApi<T>((data: any) => api.post(endpoint, data))
}

/**
 * Hook para fazer requisições PUT
 */
export function useApiPut<T = any>(endpoint: string) {
  return useApi<T>((data: any) => api.put(endpoint, data))
}

/**
 * Hook para fazer requisições DELETE
 */
export function useApiDelete<T = any>(endpoint: string) {
  return useApi<T>(() => api.delete(endpoint))
}
