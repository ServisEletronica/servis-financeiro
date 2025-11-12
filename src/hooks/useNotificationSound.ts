import { useCallback, useEffect, useRef } from 'react'

const DEBOUNCE_TIME = 1000 // 1 segundo de debounce

/**
 * Hook para tocar som de notificação
 * Usa o arquivo de áudio em /sound/notification-whatsapp.mp3
 * Com debounce para evitar tocar múltiplas vezes em sequência rápida
 */
export function useNotificationSound() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const lastPlayTimeRef = useRef<number>(0)
  const isPlayingRef = useRef<boolean>(false)

  useEffect(() => {
    // Criar elemento de áudio uma vez
    const audio = new Audio('/sound/notification-whatsapp.mp3')
    audio.volume = 0.5 // Volume padrão 50%
    audio.preload = 'auto' // Pré-carregar o áudio

    // Carregar o áudio
    audio.load()

    audioRef.current = audio

    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
        audioRef.current = null
      }
    }
  }, [])

  const playNotificationSound = useCallback(() => {
    const now = Date.now()

    // Debounce: não tocar se tocou recentemente (< 1 segundo)
    if (now - lastPlayTimeRef.current < DEBOUNCE_TIME) {
      return
    }

    // Não tocar se já está tocando
    if (isPlayingRef.current) {
      return
    }

    if (audioRef.current) {
      isPlayingRef.current = true
      lastPlayTimeRef.current = now

      // Resetar e tocar o áudio original (não clonar)
      audioRef.current.currentTime = 0

      audioRef.current.play()
        .catch((error) => {
          console.warn('[NotificationSound] Erro ao tocar som:', error.name, error.message)
        })
        .finally(() => {
          // Marcar como não tocando após o debounce time
          setTimeout(() => {
            isPlayingRef.current = false
          }, DEBOUNCE_TIME)
        })
    } else {
      console.warn('[NotificationSound] audioRef.current é null')
    }
  }, [])

  return { playNotificationSound }
}
