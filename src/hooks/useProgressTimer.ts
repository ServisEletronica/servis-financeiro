import { useCallback, useEffect, useRef, useState } from 'react'

interface UseProgressTimerProps {
  duration: number
}

// Hook de progresso simples para toasts com barra de progresso
export function useProgressTimer({ duration }: UseProgressTimerProps) {
  const [progress, setProgress] = useState(0)
  const [isRunning, setIsRunning] = useState(false)
  const startTimeRef = useRef<number | null>(null)
  const rafRef = useRef<number | null>(null)

  const step = useCallback((timestamp: number) => {
    if (startTimeRef.current === null) startTimeRef.current = timestamp
    const elapsed = timestamp - startTimeRef.current
    const pct = Math.min(100, (elapsed / duration) * 100)
    setProgress(pct)
    if (pct < 100 && isRunning) {
      rafRef.current = requestAnimationFrame(step)
    }
  }, [duration, isRunning])

  const start = useCallback(() => {
    if (isRunning) return
    setIsRunning(true)
    startTimeRef.current = null
    rafRef.current = requestAnimationFrame(step)
  }, [isRunning, step])

  const pause = useCallback(() => {
    setIsRunning(false)
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
  }, [])

  const resume = useCallback(() => {
    if (!isRunning && progress < 100) {
      setIsRunning(true)
      rafRef.current = requestAnimationFrame(step)
    }
  }, [isRunning, progress, step])

  useEffect(() => {
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [])

  return { progress, isRunning, start, pause, resume }
}
