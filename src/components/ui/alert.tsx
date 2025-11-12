import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
  XCircle,
} from 'lucide-react'

export interface NotificationAlertProps {
  type: 'success' | 'error' | 'info'
  message: string
  onClose?: () => void
}

export interface ConfirmationAlertProps {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
  isOpen: boolean
}

type NotificationStyle = {
  icon: React.ComponentType<{ className?: string }>
  container: string
  iconWrapper: string
  text: string
}

const NOTIFICATION_STYLES: Record<NotificationAlertProps['type'], NotificationStyle> = {
  success: {
    icon: CheckCircle2,
    container:
      'border-l-4 border-emerald-500 bg-emerald-500/10 text-emerald-900 shadow-lg dark:border-emerald-400 dark:bg-emerald-500/10 dark:text-emerald-100',
    iconWrapper: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-200',
    text: 'text-emerald-900 dark:text-emerald-100',
  },
  error: {
    icon: XCircle,
    container:
      'border-l-4 border-rose-500 bg-rose-500/10 text-rose-900 shadow-lg dark:border-rose-400 dark:bg-rose-500/10 dark:text-rose-100',
    iconWrapper: 'bg-rose-500/15 text-rose-600 dark:text-rose-200',
    text: 'text-rose-900 dark:text-rose-100',
  },
  info: {
    icon: Info,
    container:
      'border-l-4 border-sky-500 bg-sky-500/10 text-sky-900 shadow-lg dark:border-sky-400 dark:bg-sky-500/10 dark:text-sky-100',
    iconWrapper: 'bg-sky-500/15 text-sky-600 dark:text-sky-200',
    text: 'text-sky-900 dark:text-sky-100',
  },
}

export const NotificationAlert: React.FC<NotificationAlertProps> = ({
  type,
  message,
  onClose,
}) => {
  const [visible, setVisible] = useState(false)
  const [isRemoving, setIsRemoving] = useState(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const autoCloseTimerRef = useRef<NodeJS.Timeout | null>(null)

  const style = useMemo(() => NOTIFICATION_STYLES[type], [type])

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))
    autoCloseTimerRef.current = setTimeout(() => {
      handleClose()
    }, 5000)

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (autoCloseTimerRef.current) clearTimeout(autoCloseTimerRef.current)
    }
  }, [])

  const handleClose = useCallback(() => {
    if (isRemoving) return
    setIsRemoving(true)
    setVisible(false)
    timerRef.current = setTimeout(() => {
      onClose?.()
    }, 250)
  }, [isRemoving, onClose])

  const Icon = style.icon

  return (
    <div className="pointer-events-none fixed inset-x-0 top-0 z-[100] flex justify-center">
      <div
        role="alert"
        className={[
          'pointer-events-auto m-4 flex w-full max-w-md transform items-start gap-3 rounded-xl border bg-card/95 p-4 backdrop-blur transition-all duration-300',
          style.container,
          visible ? 'translate-y-0 opacity-100' : '-translate-y-6 opacity-0',
        ].join(' ')}
      >
        <span
          className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full ${style.iconWrapper}`}
        >
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="flex-1">
          <p className={`text-sm font-medium leading-tight ${style.text}`}>{message}</p>
        </div>
        <button
          type="button"
          onClick={handleClose}
          className="ml-2 inline-flex h-7 w-7 items-center justify-center rounded-full text-muted-foreground transition hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          aria-label="Fechar notificação"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

export const ConfirmationAlert: React.FC<ConfirmationAlertProps> = ({
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  onConfirm,
  onCancel,
  isOpen,
}) => {
  const [animation, setAnimation] = useState(false)
  const animationRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (isOpen) {
      animationRef.current = setTimeout(() => setAnimation(true), 50)
    } else {
      setAnimation(false)
    }
    return () => {
      if (animationRef.current) clearTimeout(animationRef.current)
    }
  }, [isOpen])

  if (!isOpen && !animation) return null

  const handleCancel = () => {
    setAnimation(false)
    setTimeout(() => onCancel(), 220)
  }

  const handleConfirm = () => {
    setAnimation(false)
    setTimeout(() => onConfirm(), 220)
  }

  return (
    <div
      className={`fixed inset-0 z-[110] flex items-center justify-center transition-all duration-300 ${
        animation ? 'backdrop-blur-sm bg-black/40' : 'pointer-events-none bg-transparent opacity-0'
      }`}
      onClick={handleCancel}
    >
      <div
        onClick={(event) => event.stopPropagation()}
        className={`w-full max-w-md transform rounded-xl border border-border/60 bg-card p-6 shadow-xl transition-all duration-300 dark:border-border/40 ${
          animation ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        <div className="mb-4 flex items-center gap-3 text-amber-500">
          <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          <h3 className="text-base font-semibold text-foreground">{title}</h3>
        </div>
        <p className="mb-6 text-sm text-muted-foreground">{message}</p>
        <div className="flex justify-end gap-3 text-sm">
          <button
            type="button"
            onClick={handleCancel}
            className="rounded-lg border border-border/80 bg-transparent px-4 py-2 font-medium text-muted-foreground transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            className="rounded-lg bg-destructive px-4 py-2 font-medium text-destructive-foreground transition hover:bg-destructive/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive focus-visible:ring-offset-2"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}

export const useAlert = () => {
  const [notification, setNotification] = useState<NotificationAlertProps | null>(null)
  const [confirmation, setConfirmation] = useState<Omit<ConfirmationAlertProps, 'isOpen'> | null>(
    null,
  )
  const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)
  const notificationTimerRef = useRef<NodeJS.Timeout | null>(null)
  const confirmationTimerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    return () => {
      if (notificationTimerRef.current) clearTimeout(notificationTimerRef.current)
      if (confirmationTimerRef.current) clearTimeout(confirmationTimerRef.current)
    }
  }, [])

  const showNotification = useCallback((props: NotificationAlertProps) => {
    if (notificationTimerRef.current) {
      clearTimeout(notificationTimerRef.current)
    }
    setNotification(props)
  }, [])

  const closeNotification = useCallback(() => {
    setNotification(null)
    if (notificationTimerRef.current) clearTimeout(notificationTimerRef.current)
  }, [])

  const showConfirmation = useCallback((props: Omit<ConfirmationAlertProps, 'isOpen'>) => {
    setConfirmation(props)
    requestAnimationFrame(() => {
      setIsConfirmationOpen(true)
    })
  }, [])

  const closeConfirmation = useCallback(() => {
    setIsConfirmationOpen(false)
    if (confirmationTimerRef.current) clearTimeout(confirmationTimerRef.current)
    confirmationTimerRef.current = setTimeout(() => {
      setConfirmation(null)
    }, 220)
  }, [])

  return {
    notification,
    showNotification,
    closeNotification,
    confirmation,
    isConfirmationOpen,
    showConfirmation,
    closeConfirmation,
  }
}
