import { useCallback, useState } from 'react'
import { useAuth } from '@/context/auth-context'
import { 
  archiveChat,
  unarchiveChat,
  listArchivedChats,
  getChatArchivedStatus,
  type ArchiveChatParams,
  type ListArchivedChatsParams,
  type ArchivedChatsResponse 
} from '@/lib/api/inbox'
import { isUnauthorizedError } from '@/lib/api/errors'
import { showCustomToastError, showCustomToastSuccess } from '@/lib/toast'

export function useArchivedChats() {
  const { token } = useAuth()
  const [archivedChats, setArchivedChats] = useState<ArchivedChatsResponse['items']>([])
  const [isLoading, setIsLoading] = useState(false)
  const [nextCursor, setNextCursor] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(false)

  const archiveChatAction = useCallback(async (params: ArchiveChatParams) => {
    if (!token) return false

    try {
      const response = await archiveChat(token, params)
      if (response.success) {
        showCustomToastSuccess('Chat arquivado', 'O chat foi arquivado com sucesso.')
        return true
      } else {
        showCustomToastError('Erro ao arquivar', response.message || 'Não foi possível arquivar o chat.')
        return false
      }
    } catch (error) {
      if (isUnauthorizedError(error)) {
        throw error
      }
      console.error('Erro ao arquivar chat:', error)
      showCustomToastError(
        'Erro ao arquivar',
        error instanceof Error ? error.message : 'Não foi possível arquivar o chat.'
      )
      return false
    }
  }, [token])

  const unarchiveChatAction = useCallback(async (params: ArchiveChatParams) => {
    if (!token) return false

    try {
      const response = await unarchiveChat(token, params)
      if (response.success) {
        showCustomToastSuccess('Chat desarquivado', 'O chat foi desarquivado com sucesso.')
        // Remove o chat da lista local de arquivados
        setArchivedChats(prev => prev.filter(chat => 
          !(chat.connectionId === params.connectionId && chat.contactWaId === params.contactWaId)
        ))
        return true
      } else {
        showCustomToastError('Erro ao desarquivar', response.message || 'Não foi possível desarquivar o chat.')
        return false
      }
    } catch (error) {
      if (isUnauthorizedError(error)) {
        throw error
      }
      console.error('Erro ao desarquivar chat:', error)
      showCustomToastError(
        'Erro ao desarquivar',
        error instanceof Error ? error.message : 'Não foi possível desarquivar o chat.'
      )
      return false
    }
  }, [token])

  const loadArchivedChats = useCallback(async (params: ListArchivedChatsParams = {}, append = false) => {
    if (!token) return

    setIsLoading(true)
    try {
      const response = await listArchivedChats(token, params)
      
      if (append) {
        setArchivedChats(prev => [...prev, ...response.items])
      } else {
        setArchivedChats(response.items)
      }
      
      setNextCursor(response.nextCursor)
      setHasMore(response.hasMore)
    } catch (error) {
      if (isUnauthorizedError(error)) {
        throw error
      }
      console.error('Erro ao carregar chats arquivados:', error)
      showCustomToastError(
        'Erro ao carregar chats',
        error instanceof Error ? error.message : 'Não foi possível carregar os chats arquivados.'
      )
    } finally {
      setIsLoading(false)
    }
  }, [token])

  const loadMoreArchivedChats = useCallback(async (params: ListArchivedChatsParams = {}) => {
    if (!hasMore || !nextCursor || isLoading) return
    
    await loadArchivedChats({ ...params, cursor: nextCursor }, true)
  }, [hasMore, nextCursor, isLoading, loadArchivedChats])

  const checkIfChatIsArchived = useCallback(async (params: ArchiveChatParams) => {
    if (!token) return false

    try {
      const response = await getChatArchivedStatus(token, params)
      return response.isArchived
    } catch (error) {
      if (isUnauthorizedError(error)) {
        throw error
      }
      console.error('Erro ao verificar status do chat:', error)
      return false
    }
  }, [token])

  const refreshArchivedChats = useCallback((params: ListArchivedChatsParams = {}) => {
    setArchivedChats([])
    setNextCursor(null)
    setHasMore(false)
    return loadArchivedChats(params)
  }, [loadArchivedChats])

  return {
    // Estado
    archivedChats,
    isLoading,
    hasMore,
    nextCursor,
    
    // Ações
    archiveChat: archiveChatAction,
    unarchiveChat: unarchiveChatAction,
    loadArchivedChats,
    loadMoreArchivedChats,
    checkIfChatIsArchived,
    refreshArchivedChats,
    
    // Utilitários
    setArchivedChats
  }
}