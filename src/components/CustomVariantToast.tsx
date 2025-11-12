"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import {
  CircleCheckIcon,
  XIcon,
  AlertTriangleIcon,
  InfoIcon,
  XCircleIcon
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Toast,
  ToastAction,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast-new"

interface UseProgressTimerProps {
  duration: number
  interval?: number
  onComplete?: () => void
}

function useProgressTimer({
  duration,
  interval = 100,
  onComplete,
}: UseProgressTimerProps) {
  const [progress, setProgress] = useState(duration)
  const timerRef = useRef(0)
  const timerState = useRef({
    startTime: 0,
    remaining: duration,
    isPaused: false,
  })

  const cleanup = useCallback(() => {
    window.clearInterval(timerRef.current)
  }, [])

  const reset = useCallback(() => {
    cleanup()
    setProgress(duration)
    timerState.current = {
      startTime: 0,
      remaining: duration,
      isPaused: false,
    }
  }, [duration, cleanup])

  const start = useCallback(() => {
    const state = timerState.current
    state.startTime = Date.now()
    state.isPaused = false

    timerRef.current = window.setInterval(() => {
      const elapsedTime = Date.now() - state.startTime
      const remaining = Math.max(0, state.remaining - elapsedTime)

      setProgress(remaining)

      if (remaining <= 0) {
        cleanup()
        onComplete?.()
      }
    }, interval)
  }, [interval, cleanup, onComplete])

  const pause = useCallback(() => {
    const state = timerState.current
    if (!state.isPaused) {
      cleanup()
      state.remaining = Math.max(
        0,
        state.remaining - (Date.now() - state.startTime)
      )
      state.isPaused = true
    }
  }, [cleanup])

  const resume = useCallback(() => {
    const state = timerState.current
    if (state.isPaused && state.remaining > 0) {
      start()
    }
  }, [start])

  useEffect(() => {
    return cleanup
  }, [cleanup])

  return {
    progress,
    start,
    pause,
    resume,
    reset,
  }
}

type ToastVariant = 'success' | 'error' | 'warning' | 'info'

interface ToastConfig {
  icon: React.ComponentType<any>
  iconColor: string
  progressColor: string
  title: string
  description: string
  actionText: string
}

const toastConfigs: Record<ToastVariant, ToastConfig> = {
  success: {
    icon: CircleCheckIcon,
    iconColor: "text-emerald-500",
    progressColor: "bg-emerald-500",
    title: "Operação Concluída!",
    description: "Sua solicitação foi processada com sucesso.",
    actionText: "Desfazer alterações"
  },
  error: {
    icon: XCircleIcon,
    iconColor: "text-red-500",
    progressColor: "bg-red-500",
    title: "Erro na Operação!",
    description: "Ocorreu um erro ao processar sua solicitação.",
    actionText: "Tentar novamente"
  },
  warning: {
    icon: AlertTriangleIcon,
    iconColor: "text-yellow-500",
    progressColor: "bg-yellow-500",
    title: "Atenção Necessária!",
    description: "Alguns dados podem precisar de verificação.",
    actionText: "Verificar dados"
  },
  info: {
    icon: InfoIcon,
    iconColor: "text-blue-500",
    progressColor: "bg-blue-500",
    title: "Informação Importante!",
    description: "Há uma atualização disponível para o sistema.",
    actionText: "Ver detalhes"
  }
}

interface CustomVariantToastProps {
  variant?: ToastVariant
  customTitle?: string
  customDescription?: string
  customActionText?: string
  onComplete?: () => void
  onClose?: () => void
}

export default function CustomVariantToast({
  variant = 'success',
  customTitle,
  customDescription,
  customActionText,
  onComplete,
  onClose
}: CustomVariantToastProps) {
  const [open, setOpen] = useState(false)
  const toastDuration = 5000
  const { progress, start, pause, resume, reset } = useProgressTimer({
    duration: toastDuration,
    onComplete: () => {
      setOpen(false)
      onComplete?.()
    },
  })

  const config = toastConfigs[variant]
  const IconComponent = config.icon

  const handleOpenChange = useCallback(
    (isOpen: boolean) => {
      setOpen(isOpen)
      if (isOpen) {
        reset()
        start()
      } else {
        // Quando o toast é fechado (seja pelo usuário ou automaticamente)
        onClose?.()
      }
    },
    [reset, start, onClose]
  )

  const handleButtonClick = useCallback(() => {
    if (open) {
      setOpen(false)
      window.setTimeout(() => {
        handleOpenChange(true)
      }, 150)
    } else {
      handleOpenChange(true)
    }
  }, [open, handleOpenChange])

  return (
    <ToastProvider>
      <Button variant="outline" onClick={handleButtonClick}>
        {variant.charAt(0).toUpperCase() + variant.slice(1)} Toast
      </Button>
      <Toast
        open={open}
        onOpenChange={handleOpenChange}
        onPause={pause}
        onResume={resume}
        className="p-3 bg-background border shadow-lg touch-none select-none"
        style={{
          userSelect: 'none',
          WebkitUserSelect: 'none',
          MozUserSelect: 'none',
          msUserSelect: 'none',
          touchAction: 'none'
        }}
      >
        <div className="flex w-full justify-between gap-3">
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            variant === 'success' ? 'bg-green-50 dark:bg-green-900/20' :
            variant === 'error' ? 'bg-red-50 dark:bg-red-900/20' :
            variant === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
            'bg-blue-50 dark:bg-blue-900/20'
          }`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center ${
              variant === 'success' ? 'bg-green-100 dark:bg-green-800/50' :
              variant === 'error' ? 'bg-red-100 dark:bg-red-800/50' :
              variant === 'warning' ? 'bg-yellow-100 dark:bg-yellow-800/50' :
              'bg-blue-100 dark:bg-blue-800/50'
            }`}>
              <IconComponent className={config.iconColor} size={14} aria-hidden="true" />
            </div>
          </div>
          <div className="flex grow flex-col">
            <div className="space-y-1">
              <ToastTitle className="text-sm font-medium">{customTitle || config.title}</ToastTitle>
              <ToastDescription className="text-xs text-muted-foreground">
                {customDescription || config.description}
              </ToastDescription>
            </div>
          </div>
          <ToastClose asChild>
            <Button variant="ghost" className="group -my-1 -me-1 size-6 shrink-0 p-0 hover:bg-transparent" aria-label="Close notification">
              <XIcon size={12} className="opacity-60 transition-opacity group-hover:opacity-100" aria-hidden="true" />
            </Button>
          </ToastClose>
        </div>
        <div className="contents" aria-hidden="true">
          <div
            className={`pointer-events-none absolute bottom-0 left-0 h-1 w-full ${config.progressColor}`}
            style={{ width: `${(progress / toastDuration) * 100}%`, transition: "width 100ms linear" }}
          />
        </div>
      </Toast>
      <ToastViewport />
    </ToastProvider>
  )
}

// Exports para uso externo
export type { ToastVariant, CustomVariantToastProps }
export { toastConfigs }

// Hook para usar o toast de forma global
let toastInstance: ((variant: ToastVariant, title: string, description: string) => void) | null = null

export const setToastInstance = (fn: typeof toastInstance) => {
  toastInstance = fn
}

export const showCustomToast = (variant: ToastVariant, title: string, description: string) => {
  if (toastInstance) {
    toastInstance(variant, title, description)
  } else {
    console.warn('Toast instance not initialized. Add ToastProvider to your app.')
  }
}
