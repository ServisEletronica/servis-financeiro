import { useState, useEffect, useCallback, useRef } from 'react'
import { getNewInboundMessages, markMessagesAsNotified } from '@/lib/api/inbox'
import { getUserSettings } from '@/lib/api/userSettings'
import { useAuth } from '@/context/auth-context'
import { NotificationService } from '@/services/notificationService'
import { useNotificationSound } from './useNotificationSound'

const POLLING_INTERVAL = 5000 // 5 segundos
const MAX_CACHED_MESSAGE_IDS = 100 // Limitar cache para evitar crescimento infinito

export function useNotifications() {
  const { token } = useAuth()
  const [enabled, setEnabled] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const notificationService = useRef(NotificationService.getInstance())
  const processingRef = useRef(false)
  const [settingsLoaded, setSettingsLoaded] = useState(false)
  const { playNotificationSound } = useNotificationSound()
  const soundEnabledRef = useRef(false)
  const playNotificationSoundRef = useRef(playNotificationSound)
  const processedMessageIds = useRef<Set<string>>(new Set())

  // Atualizar ref quando a função mudar
  useEffect(() => {
    playNotificationSoundRef.current = playNotificationSound
  }, [playNotificationSound])

  // Carregar configurações do usuário do backend
  useEffect(() => {
    if (!token) return

    const loadSettings = async () => {
      try {
        const settings = await getUserSettings(token)

        // Verificar se settings existe e tem as propriedades necessárias
        if (!settings) {
          setSettingsLoaded(true)
          return
        }

        // Salvar configuração de som
        soundEnabledRef.current = settings.soundNotificationsEnabled

        // Habilitar notificações apenas se:
        // 1. O usuário habilitou nas configurações
        // 2. O navegador deu permissão
        if ('Notification' in window) {
          const browserPermission = Notification.permission
          setPermission(browserPermission)
          setEnabled(settings.desktopNotificationsEnabled && browserPermission === 'granted')
        }

        setSettingsLoaded(true)
      } catch (err) {
        console.error('Erro ao carregar configurações:', err)
        setSettingsLoaded(true)
      }
    }

    loadSettings()
  }, [token])

  // Verificar permissão do navegador
  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission)
    }
  }, [])

  // Solicitar permissão
  const requestPermission = useCallback(async () => {
    const granted = await notificationService.current.requestPermission()
    setPermission(Notification.permission)
    return granted
  }, [])

  // Função para atualizar estado de enabled externamente (quando user muda settings)
  const updateEnabled = useCallback((value: boolean) => {
    setEnabled(value && Notification.permission === 'granted')
  }, [])

  // Polling de novas mensagens
  const checkNewMessages = useCallback(async () => {
    if (!token || processingRef.current) return

    processingRef.current = true

    try {
      const response = await getNewInboundMessages(token)

      // Verificar se response existe e tem messages
      if (!response || !response.messages) {
        console.warn('⚠️ Resposta inválida da API:', response)
        return
      }

      const newMessages = response.messages

      if (newMessages.length === 0) {
        return
      }

      // Filtrar mensagens já processadas
      const unprocessedMessages = newMessages.filter(msg => {
        if (processedMessageIds.current.has(msg.messageId)) {
          return false
        }
        processedMessageIds.current.add(msg.messageId)

        // Limitar tamanho do cache
        if (processedMessageIds.current.size > MAX_CACHED_MESSAGE_IDS) {
          const firstKey = processedMessageIds.current.values().next().value
          processedMessageIds.current.delete(firstKey)
        }

        return true
      })

      if (unprocessedMessages.length === 0) {
        return
      }

      // console.log('[Notifications] Novas mensagens detectadas:', unprocessedMessages.length)

      // Tocar som se habilitado (SEMPRE, independente da notificação visual)
      if (soundEnabledRef.current) {
        // console.log('[Notifications] Tocando som de notificação...')
        playNotificationSoundRef.current()
      }

      // Mostrar notificações visuais se habilitado
      const notifiedIds: string[] = []

      if (enabled) {
        for (const message of unprocessedMessages) {
          try {
            notificationService.current.showMessageNotification(message)
            notifiedIds.push(message.messageId)
          } catch (err) {
            console.error('Erro ao mostrar notificação:', err)
          }
        }
      }

      // Marcar como notificadas apenas se mostrou notificação visual
      if (notifiedIds.length > 0) {
        await markMessagesAsNotified(token, notifiedIds)
      }
    } catch (err) {
      console.error('Erro ao verificar novas mensagens:', err)
    } finally {
      processingRef.current = false
    }
  }, [token, enabled])

  // Configurar polling (roda sempre que tiver token, independente de notificações visuais)
  useEffect(() => {
    if (!token) return

    // Primeira verificação imediata
    checkNewMessages()

    // Polling
    const interval = setInterval(checkNewMessages, POLLING_INTERVAL)

    return () => clearInterval(interval)
  }, [token, checkNewMessages])

  return {
    enabled,
    permission,
    requestPermission,
    updateEnabled,
    canNotify: enabled && permission === 'granted',
    settingsLoaded
  }
}