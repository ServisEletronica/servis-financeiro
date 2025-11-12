import { useEffect, useRef } from 'react'
import { useAuth } from '@/context/auth-context'
import { listAppointments, type Appointment } from '@/lib/api/appointments'

const NOTIFICATION_CHECK_INTERVAL = 60000 // 1 minuto

interface UseAppointmentNotificationsOptions {
  enabled?: boolean
}

const NOTIFIED_IDS_KEY = 'appointment_notified_ids'

export function useAppointmentNotifications(options: UseAppointmentNotificationsOptions = {}) {
  const { enabled = true } = options
  const { token } = useAuth()
  const notifiedIds = useRef<Set<string>>(new Set())
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Carregar IDs notificados do localStorage na inicialização
  useEffect(() => {
    try {
      const stored = localStorage.getItem(NOTIFIED_IDS_KEY)
      if (stored) {
        const ids = JSON.parse(stored) as string[]
        notifiedIds.current = new Set(ids)
      }
    } catch (error) {
      console.error('Erro ao carregar IDs notificados:', error)
    }
  }, [])

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      console.warn('Este navegador não suporta notificações')
      return false
    }

    if (Notification.permission === 'granted') {
      return true
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }

    return false
  }

  const showNotification = (appointment: Appointment) => {
    if (!('Notification' in window)) return

    // Verificar se já notificou este agendamento
    if (notifiedIds.current.has(appointment.id)) {
      return
    }

    // Marcar como notificado
    notifiedIds.current.add(appointment.id)

    // Salvar no localStorage
    try {
      const ids = Array.from(notifiedIds.current)
      localStorage.setItem(NOTIFIED_IDS_KEY, JSON.stringify(ids))
    } catch (error) {
      console.error('Erro ao salvar IDs notificados:', error)
    }

    const notification = new Notification('Lembrete de Agendamento', {
      body: appointment.description || appointment.title,
      icon: '/logo.png', // Ajuste para o caminho do seu logo
      badge: '/logo.png',
      tag: `appointment-${appointment.id}`,
      requireInteraction: true,
      timestamp: new Date(appointment.scheduledAt).getTime(),
    })

    notification.onclick = () => {
      window.focus()
      // Navegar para a página de agendamentos
      window.location.href = '/appointments'
      notification.close()
    }

    // Auto-close após 10 segundos se não interagir
    setTimeout(() => {
      notification.close()
    }, 10000)
  }

  const checkPendingAppointments = async () => {
    if (!token) return

    try {
      const now = new Date()
      const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60000)

      // Buscar agendamentos das próximas 5 minutos
      const appointments = await listAppointments(token, {
        status: 'completed', // Agendamentos que foram marcados como concluídos pelo backend
      })

      // Limpar IDs notificados de agendamentos que já passaram há mais de 24h
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      const activeAppointmentIds = new Set(
        appointments
          .filter(apt => new Date(apt.scheduledAt) > oneDayAgo)
          .map(apt => apt.id)
      )

      // Filtrar IDs notificados para manter apenas os recentes
      const currentNotifiedIds = Array.from(notifiedIds.current)
      const filteredIds = currentNotifiedIds.filter(id => activeAppointmentIds.has(id))

      if (filteredIds.length !== currentNotifiedIds.length) {
        notifiedIds.current = new Set(filteredIds)
        try {
          localStorage.setItem(NOTIFIED_IDS_KEY, JSON.stringify(filteredIds))
        } catch (error) {
          console.error('Erro ao limpar IDs antigos:', error)
        }
      }

      // Filtrar apenas agendamentos pessoais que devem notificar
      const toNotify = appointments.filter((appointment) => {
        // Apenas agendamentos pessoais
        if (appointment.appointmentType !== 'personal') return false

        // Já foi notificado?
        if (notifiedIds.current.has(appointment.id)) return false

        // Agendamento está dentro dos próximos 5 minutos ou já passou há menos de 5 minutos?
        const scheduledAt = new Date(appointment.scheduledAt)
        const fiveMinutesAgo = new Date(now.getTime() - 5 * 60000)
        return scheduledAt >= fiveMinutesAgo && scheduledAt <= fiveMinutesFromNow
      })

      // Solicitar permissão se necessário
      if (toNotify.length > 0) {
        const hasPermission = await requestNotificationPermission()
        if (!hasPermission) {
          console.warn('Permissão de notificação negada')
          return
        }

        // Enviar notificações
        toNotify.forEach(showNotification)
      }
    } catch (error) {
      console.error('Erro ao verificar agendamentos pendentes:', error)
    }
  }

  useEffect(() => {
    if (!enabled || !token) {
      return
    }

    // Verificar imediatamente
    checkPendingAppointments()

    // Configurar intervalo
    intervalRef.current = setInterval(checkPendingAppointments, NOTIFICATION_CHECK_INTERVAL)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [enabled, token])

  return {
    requestNotificationPermission,
  }
}
