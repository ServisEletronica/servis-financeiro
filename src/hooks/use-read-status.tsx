import { useCallback, useRef } from 'react'
import { useAuth } from '@/context/auth-context'
import { 
  markMessageAsReadNew, 
  markMultipleMessagesAsRead,
  type MarkMessageAsReadNewParams,
  type MarkMultipleMessagesAsReadParams,
  type InboxMessage 
} from '@/lib/api/inbox'
import { isUnauthorizedError } from '@/lib/api/errors'
import { showCustomToastError } from '@/lib/toast'

export function useReadStatus() {
  const { token } = useAuth()
  const errorShownRef = useRef<Set<string>>(new Set())

  const markSingleMessageAsRead = useCallback(async (params: MarkMessageAsReadNewParams) => {
    if (!token) return false

    try {
      const response = await markMessageAsReadNew(token, params)
      return response.success
    } catch (error) {
      if (isUnauthorizedError(error)) {
        // Deixa o componente pai lidar com erro de autorização
        throw error
      }
      console.error('Erro ao marcar mensagem como lida:', error)
      showCustomToastError(
        'Erro ao marcar como lida',
        error instanceof Error ? error.message : 'Não foi possível marcar a mensagem como lida.'
      )
      return false
    }
  }, [token])

  const markMultipleAsRead = useCallback(async (params: MarkMultipleMessagesAsReadParams) => {
    if (!token) return { success: false, results: [] }

    try {
      const response = await markMultipleMessagesAsRead(token, params)
      
      // Se algumas mensagens falharam, mostra um aviso (apenas uma vez por chat)
      if (response.summary.failed > 0) {
        const errorKey = `multiple-failed-${response.summary.failed}-${response.summary.total}`
        if (!errorShownRef.current.has(errorKey)) {
          errorShownRef.current.add(errorKey)
          showCustomToastError(
            'Algumas mensagens não foram marcadas',
            `${response.summary.failed} de ${response.summary.total} mensagens não foram marcadas como lidas.`
          )
        }
      }
      
      return response
    } catch (error) {
      if (isUnauthorizedError(error)) {
        // Deixa o componente pai lidar com erro de autorização
        throw error
      }
      console.error('Erro ao marcar múltiplas mensagens como lidas:', error)
      
      const errorKey = `multiple-error-${error instanceof Error ? error.message : 'unknown'}`
      if (!errorShownRef.current.has(errorKey)) {
        errorShownRef.current.add(errorKey)
        showCustomToastError(
          'Erro ao marcar mensagens como lidas',
          error instanceof Error ? error.message : 'Não foi possível marcar as mensagens como lidas.'
        )
      }
      return { success: false, results: [] }
    }
  }, [token])

  const markUnreadMessagesInChatAsRead = useCallback(async (
    messages: InboxMessage[],
    connectionId: string,
    contactWaId: string,
    ghostMode: boolean = false
  ) => {
    if (!token || !messages.length) return false

    // Se ghostMode está ativo, não marca mensagens como lidas
    if (ghostMode) {
      console.log('Ghost mode active - messages NOT marked as read')
      return true // Retorna sucesso sem fazer nada
    }

    try {
      // Filtra apenas mensagens inbound que estão como 'delivered' (não 'read')
      const unreadMessages = messages.filter(
        message =>
          message.direction === 'inbound' &&
          (message.status === 'delivered' || message.status === null || message.status === undefined) &&
          message.status !== 'read'
      )


      if (unreadMessages.length === 0) {
        return true // Nada para marcar
      }

      // Se há apenas uma mensagem, usa a API single
      if (unreadMessages.length === 1) {
        const message = unreadMessages[0]
        return await markSingleMessageAsRead({
          messageId: message.id,
          contactWaId,
          connectionId
        })
      }

      // Se há múltiplas mensagens, usa a API batch
      const messagesToMark = unreadMessages.map(message => ({
        id: message.id,
        contactWaId
      }))

      const response = await markMultipleAsRead({
        messages: messagesToMark,
        connectionId
      })

      return response.success && response.summary.failed === 0
    } catch (error) {
      if (isUnauthorizedError(error)) {
        // Deixa o componente pai lidar com erro de autorização
        throw error
      }

      // Não mostra toast para erros nesta função, apenas log
      console.error('Erro ao marcar mensagens não lidas como lidas:', error)
      return false
    }
  }, [token, markSingleMessageAsRead, markMultipleAsRead])

  return {
    markSingleMessageAsRead,
    markMultipleAsRead,
    markUnreadMessagesInChatAsRead
  }
}