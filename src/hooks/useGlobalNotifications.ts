import { useEffect, useRef } from 'react'
import { useAuth } from '@/context/auth-context'
import { getUserSettings } from '@/lib/api/userSettings'
import { getNewInboundMessages } from '@/lib/api/inbox'
import { useNotificationSound } from './useNotificationSound'

const NOTIFICATION_POLL_INTERVAL = 3000 // 3 segundos

/**
 * Hook global para tocar som de notificação quando há novas mensagens
 * Funciona em qualquer página da aplicação
 * NÃO interfere com as notificações do Windows (não marca como notificado)
 */
export function useGlobalNotifications() {
  const { token } = useAuth()
  const { playNotificationSound } = useNotificationSound()
  const soundEnabledRef = useRef(false)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isCheckingRef = useRef(false)
  const processedMessagesRef = useRef<Set<string>>(new Set())

  // Carregar configurações do usuário e atualizar ref
  useEffect(() => {
    if (!token) return

    getUserSettings(token)
      .then((settings) => {
        soundEnabledRef.current = settings.soundNotificationsEnabled
        console.log('[GlobalNotifications] Som habilitado:', settings.soundNotificationsEnabled)
      })
      .catch((error) => {
        console.error('[GlobalNotifications] Erro ao carregar configurações:', error)
      })
  }, [token])

  // Polling para detectar novas mensagens
  useEffect(() => {
    if (!token) return

    const checkNewMessages = async () => {
      if (isCheckingRef.current) return

      try {
        isCheckingRef.current = true

        const response = await getNewInboundMessages(token)

        if (response.messages && response.messages.length > 0) {
          // Filtrar apenas mensagens que ainda não foram processadas
          const newMessages = response.messages.filter(
            msg => !processedMessagesRef.current.has(msg.messageId)
          )

          if (newMessages.length > 0) {
            console.log('[GlobalNotifications] Novas mensagens detectadas:', newMessages.length)

            // Tocar som se habilitado
            if (soundEnabledRef.current) {
              console.log('[GlobalNotifications] Tocando som de notificação...')
              playNotificationSound()
            }

            // Adicionar mensagens ao set de processadas
            newMessages.forEach(msg => {
              processedMessagesRef.current.add(msg.messageId)
            })

            // Limpar mensagens antigas do set (manter apenas últimas 100)
            if (processedMessagesRef.current.size > 100) {
              const messagesArray = Array.from(processedMessagesRef.current)
              processedMessagesRef.current = new Set(messagesArray.slice(-100))
            }
          }
        }
      } catch (error) {
        console.error('[GlobalNotifications] Erro ao verificar novas mensagens:', error)
      } finally {
        isCheckingRef.current = false
      }
    }

    // Verificar imediatamente ao montar
    checkNewMessages()

    // Configurar polling
    pollingIntervalRef.current = setInterval(checkNewMessages, NOTIFICATION_POLL_INTERVAL)

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [token, playNotificationSound])
}
