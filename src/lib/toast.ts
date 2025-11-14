import { createElement } from 'react'
import { createRoot } from 'react-dom/client'
import CustomVariantToast from '@/components/CustomVariantToast'

type CustomToastOptions = {
  onComplete?: () => void
  onClose?: () => void
}

const AUTO_DISMISS_TIMEOUT = 5500

// Sistema para prevenir spam de toasts de sessão expirada
let sessionExpirationInProgress = false
let sessionExpirationTimer: number | undefined

const resetSessionExpirationState = () => {
  sessionExpirationInProgress = false
  if (sessionExpirationTimer) {
    window.clearTimeout(sessionExpirationTimer)
    sessionExpirationTimer = undefined
  }
}

function mountToast(
  variant: 'success' | 'error' | 'warning' | 'info',
  title: string,
  description: string,
  options?: CustomToastOptions,
) {
  const toastElement = document.createElement('div')
  toastElement.style.position = 'fixed'
  toastElement.style.top = '0'
  toastElement.style.left = '0'
  toastElement.style.pointerEvents = 'none'
  toastElement.style.zIndex = '9999'
  toastElement.style.width = '0'
  toastElement.style.height = '0'
  toastElement.style.overflow = 'hidden'
  document.body.appendChild(toastElement)

  const root = createRoot(toastElement)
  const resolvedOptions = options ?? {}
  let hasCompleted = false
  let autoDismissTimer: number | undefined

  const cleanup = () => {
    if (hasCompleted) {
      return
    }
    hasCompleted = true
    if (autoDismissTimer !== undefined) {
      window.clearTimeout(autoDismissTimer)
    }
    root.unmount()
    if (toastElement.parentNode) {
      toastElement.parentNode.removeChild(toastElement)
    }
    resolvedOptions.onComplete?.()
  }

  const handleClose = () => {
    if (hasCompleted) {
      return
    }
    hasCompleted = true
    if (autoDismissTimer !== undefined) {
      window.clearTimeout(autoDismissTimer)
    }
    root.unmount()
    if (toastElement.parentNode) {
      toastElement.parentNode.removeChild(toastElement)
    }
    resolvedOptions.onClose?.()
  }

  const component = createElement(CustomVariantToast, {
    variant,
    customTitle: title,
    customDescription: description,
    onComplete: cleanup,
    onClose: handleClose,
  })

  root.render(component)

  autoDismissTimer = window.setTimeout(cleanup, AUTO_DISMISS_TIMEOUT)

  window.setTimeout(() => {
    toastElement.style.pointerEvents = 'auto'
    const button = toastElement.querySelector('button')
    if (button instanceof HTMLButtonElement) {
      button.click()
    }
  }, 10)
}

// Funções para usar os Custom Toasts nos CRUDs
export const showCustomToastSuccess = (
  title: string,
  description: string,
  options?: CustomToastOptions,
) => {
  mountToast('success', title, description, options)
}

export const showCustomToastError = (
  title: string,
  description: string,
  options?: CustomToastOptions,
) => {
  // Previne spam de toasts de sessão expirada
  const isSessionExpiredToast = title.toLowerCase().includes('sessão expirada') ||
                               title.toLowerCase().includes('session') ||
                               (description && description.toLowerCase().includes('login novamente'))

  if (isSessionExpiredToast) {
    // Se já está em progresso um toast de sessão expirada, ignora os novos
    if (sessionExpirationInProgress) {
      return
    }

    // Marca como em progresso
    sessionExpirationInProgress = true

    // Reseta o estado após 10 segundos para permitir novos toasts caso necessário
    sessionExpirationTimer = window.setTimeout(resetSessionExpirationState, 10000)

    // Cria opções especiais para toast de sessão expirada
    const sessionOptions: CustomToastOptions = {
      ...options,
      onComplete: () => {
        resetSessionExpirationState()
        options?.onComplete?.()
      },
      onClose: () => {
        resetSessionExpirationState()
        options?.onClose?.()
        // Se o usuário fechar manualmente, também executa onComplete (para redirecionar)
        options?.onComplete?.()
      }
    }

    mountToast('error', title, description, sessionOptions)
  } else {
    mountToast('error', title, description, options)
  }
}

export const showCustomToastWarning = (
  title: string,
  description: string,
  options?: CustomToastOptions,
) => {
  mountToast('warning', title, description, options)
}

export const showCustomToastInfo = (
  title: string,
  description: string,
  options?: CustomToastOptions,
) => {
  mountToast('info', title, description, options)
}

// Função especial para toasts de sessão expirada com proteção contra spam
export const showSessionExpiredToast = (options?: CustomToastOptions) => {
  // Se já está em progresso um toast de sessão expirada, ignora
  if (sessionExpirationInProgress) {
    return
  }

  // Marca como em progresso
  sessionExpirationInProgress = true

  // Reseta o estado após 15 segundos (tempo suficiente para o redirecionamento)
  sessionExpirationTimer = window.setTimeout(resetSessionExpirationState, 15000)

  // Cria opções especiais para toast de sessão expirada
  const sessionOptions: CustomToastOptions = {
    ...options,
    onComplete: () => {
      resetSessionExpirationState()
      options?.onComplete?.()
    },
    onClose: () => {
      resetSessionExpirationState()
      // Se o usuário fechar manualmente, também executa onComplete (para redirecionar)
      options?.onComplete?.()
    }
  }

  mountToast('error', 'Sessão expirada', 'Faça login novamente para continuar.', sessionOptions)
}
