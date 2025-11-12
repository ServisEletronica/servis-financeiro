"use client"

import React, { createContext, useContext, useState, useCallback } from 'react'
import CustomVariantToast, { type ToastVariant } from './CustomVariantToast'

interface ToastData {
  id: string
  variant: ToastVariant
  title: string
  description: string
  onComplete?: () => void
}

interface CustomToastContextType {
  showToast: (variant: ToastVariant, title: string, description: string, onComplete?: () => void) => void
}

const CustomToastContext = createContext<CustomToastContextType | null>(null)

export function CustomToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastData[]>([])

  const showToast = useCallback((variant: ToastVariant, title: string, description: string, onComplete?: () => void) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast: ToastData = { id, variant, title, description, onComplete }

    setToasts(prev => [...prev, newToast])

    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 5500)
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  // Configurar função global quando o provider é montado
  React.useEffect(() => {
    setGlobalToastFunction(showToast)

    return () => setGlobalToastFunction(null)
  }, [showToast])

  return (
    <CustomToastContext.Provider value={{ showToast }}>
      {children}
      {toasts.map(toast => (
        <CustomVariantToast
          key={toast.id}
          variant={toast.variant}
          customTitle={toast.title}
          customDescription={toast.description}
          onComplete={() => {
            removeToast(toast.id)
            toast.onComplete?.()
          }}
        />
      ))}
    </CustomToastContext.Provider>
  )
}

export function useCustomToast() {
  const context = useContext(CustomToastContext)
  if (!context) {
    throw new Error('useCustomToast must be used within CustomToastProvider')
  }
  return context
}

// Função global para mostrar toast
let globalShowToast: ((variant: ToastVariant, title: string, description: string, onComplete?: () => void) => void) | null = null

export const setGlobalToastFunction = (fn: typeof globalShowToast) => {
  globalShowToast = fn
}

export const showCustomToast = (variant: ToastVariant, title: string, description: string, onComplete?: () => void) => {
  if (globalShowToast) {
    globalShowToast(variant, title, description, onComplete)
  } else {
    console.warn('CustomToastProvider não está configurado')
  }
}
