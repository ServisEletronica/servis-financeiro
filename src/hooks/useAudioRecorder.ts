import { useRef, useState, useCallback, useEffect } from 'react'

// Estados da máquina de estado
export type AudioRecorderState = 'idle' | 'recording' | 'paused' | 'reviewing'

export interface AudioRecorderData {
  state: AudioRecorderState
  duration: number
  audioLevel: number
  error: string | null
  blob: Blob | null
  isSupported: boolean
}

export interface UseAudioRecorderReturn {
  data: AudioRecorderData
  start: () => Promise<void>
  pause: () => void
  resume: () => void
  stop: () => Promise<Blob | null>
  cancel: () => void
  analyserNode: AnalyserNode | null
}

export function useAudioRecorder(maxDurationSec: number = 300): UseAudioRecorderReturn {
  // Estados
  const [state, setState] = useState<AudioRecorderState>('idle')
  const [duration, setDuration] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [blob, setBlob] = useState<Blob | null>(null)
  const [isSupported] = useState(() => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder)
  })

  // Refs para recursos
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const startTimeRef = useRef<number>(0)
  const pausedTimeRef = useRef<number>(0)
  const totalPausedTimeRef = useRef<number>(0)
  const timerRef = useRef<number | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const isTimerActiveRef = useRef<boolean>(false)

  // Função para atualizar timer
  const updateTimer = useCallback(() => {
    if (startTimeRef.current > 0 && isTimerActiveRef.current) {
      const elapsed = (Date.now() - startTimeRef.current - totalPausedTimeRef.current) / 1000
      setDuration(elapsed)
    }
  }, [])

  // Função para iniciar timer
  const startTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    isTimerActiveRef.current = true
    timerRef.current = setInterval(updateTimer, 100) as unknown as number
  }, [updateTimer])

  // Função para parar timer
  const stopTimer = useCallback(() => {
    isTimerActiveRef.current = false
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  // Função para pausar timer (sem parar o setInterval)
  const pauseTimer = useCallback(() => {
    isTimerActiveRef.current = false
  }, [])

  // Função para retomar timer (sem criar novo setInterval)
  const resumeTimer = useCallback(() => {
    isTimerActiveRef.current = true
  }, [])

  // Função para analisar áudio em tempo real
  const analyzeAudio = useCallback(() => {
    if (!analyserRef.current || state !== 'recording') return

    const bufferLength = analyserRef.current.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    analyserRef.current.getByteTimeDomainData(dataArray)

    // Calcular RMS para nível de áudio
    let sum = 0
    for (let i = 0; i < bufferLength; i++) {
      const normalized = (dataArray[i] - 128) / 128
      sum += normalized * normalized
    }
    const rms = Math.sqrt(sum / bufferLength)
    setAudioLevel(rms)

    if (state === 'recording') {
      animationFrameRef.current = requestAnimationFrame(analyzeAudio)
    }
  }, [state])

  // Iniciar gravação
  // Função auxiliar para selecionar o melhor microfone disponível
  const getPreferredMicrophone = useCallback(async () => {
    try {
      // Listar todos os dispositivos de entrada de áudio
      const devices = await navigator.mediaDevices.enumerateDevices()
      const audioInputs = devices.filter(device => device.kind === 'audioinput')

      if (audioInputs.length === 0) return null

      console.log('🎤 Microfones disponíveis:')
      audioInputs.forEach((device, index) => {
        console.log(`  ${index + 1}. ${device.label} (ID: ${device.deviceId.substring(0, 20)}...)`)
      })

      // Priorizar microfones externos (USB/Bluetooth)
      // EXCLUIR chipsets internos comuns: Intel, Realtek, Conexant, etc.
      const externalMic = audioInputs.find(device => {
        const label = device.label.toLowerCase()

        // Primeiro, excluir chipsets internos conhecidos
        const isInternal =
          label.includes('intel') ||
          label.includes('realtek') ||
          label.includes('conexant') ||
          label.includes('built-in') ||
          label.includes('internal') ||
          label.includes('array') ||
          label.includes('integrated')

        if (isInternal) return false

        // Depois, procurar por indicadores de dispositivos externos
        return (
          label.includes('usb') ||
          label.includes('bluetooth') ||
          label.includes('headset') ||
          label.includes('headphone') ||
          label.includes('fone') ||
          label.includes('wireless') ||
          label.includes('external') ||
          label.includes('samsung') ||
          label.includes('jbl') ||
          label.includes('sony') ||
          label.includes('bose') ||
          label.includes('hyperx') ||
          label.includes('logitech')
        )
      })

      if (externalMic) {
        console.log('✅ Microfone EXTERNO selecionado:', externalMic.label)
        return externalMic.deviceId
      }

      // Caso contrário, usar o padrão do sistema (geralmente o interno)
      console.log('ℹ️  Usando microfone PADRÃO do sistema (provavelmente interno)')
      return null

    } catch (err) {
      console.warn('Não foi possível enumerar dispositivos:', err)
      return null
    }
  }, [])

  const start = useCallback(async () => {
    if (!isSupported) {
      setError('Gravação de áudio não é suportada neste navegador')
      return
    }

    try {
      setError(null)
      setState('recording')

      // Obter o melhor microfone disponível
      const preferredDeviceId = await getPreferredMicrophone()

      // Obter stream de áudio otimizado para WhatsApp
      const audioConstraints: any = {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,        // 48kHz padrão WhatsApp
        channelCount: 1           // Mono
      }

      // Se encontrou um dispositivo específico, adicionar deviceId
      if (preferredDeviceId) {
        audioConstraints.deviceId = { exact: preferredDeviceId }
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: audioConstraints
      })
      streamRef.current = stream

      // Configurar MediaRecorder - APENAS formatos aceitos pelo WhatsApp
      let mimeType = null;
      
      // Priorizar WebM+Opus para conversão no backend
      const recordingFormats = [
        'audio/webm;codecs=opus',         // WebM+Opus (mais confiável para conversão)
        'audio/webm',                     // WebM genérico
        'audio/ogg;codecs=opus',          // OGG+Opus (fallback)
        'audio/mp4;codecs=mp4a.40.2',     // AAC-LC (se browser suportar bem)
        'audio/mpeg'                      // MP3 (improvável mas possível)
      ];
      
      // Testar formatos em ordem de prioridade para conversão
      for (const format of recordingFormats) {
        if (MediaRecorder.isTypeSupported(format)) {
          mimeType = format;
          console.log(`✅ Formato de gravação selecionado: ${format} (será convertido para MP3 no backend)`);
          break;
        }
      }
      
      if (!mimeType) {
        throw new Error('Nenhum formato de áudio suportado pelo WhatsApp está disponível neste navegador.');
      }

      console.log(`🎙️ Formato de áudio selecionado: ${mimeType}`);

      // Configurações específicas para melhor compatibilidade
      const mediaRecorderOptions: MediaRecorderOptions = { 
        mimeType,
        audioBitsPerSecond: 128000, // 128kbps para qualidade vs tamanho
        bitsPerSecond: 128000
      };

      const mediaRecorder = new MediaRecorder(stream, mediaRecorderOptions)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      // Configurar análise de áudio
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      
      analyser.fftSize = 2048
      analyser.smoothingTimeConstant = 0.8
      source.connect(analyser)
      
      audioContextRef.current = audioContext
      analyserRef.current = analyser

      // Event listeners
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstart = () => {
        setState('recording')
        startTimeRef.current = Date.now()
        totalPausedTimeRef.current = 0
        setDuration(0)
        startTimer()
        analyzeAudio()
      }

      mediaRecorder.onpause = () => {
        console.log('MediaRecorder onpause event')
        setState('paused')
        pausedTimeRef.current = Date.now()
        pauseTimer()
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
          animationFrameRef.current = null
        }
        setAudioLevel(0)
      }

      mediaRecorder.onresume = () => {
        setState('recording')
        if (pausedTimeRef.current > 0) {
          totalPausedTimeRef.current += Date.now() - pausedTimeRef.current
          pausedTimeRef.current = 0
        }
        resumeTimer()
        analyzeAudio()
      }

      mediaRecorder.onstop = () => {
        console.log('MediaRecorder stopped, chunks count:', chunksRef.current.length)
        setState('reviewing')
        
        // Parar timer e análise
        stopTimer()
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
          animationFrameRef.current = null
        }

        // IMPORTANTE: Parar o stream quando a gravação para
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }

        // Fechar audio context
        if (audioContextRef.current) {
          audioContextRef.current.close()
        }

        // Criar blob
        const finalBlob = new Blob(chunksRef.current, { type: mimeType })
        setBlob(finalBlob)
        setAudioLevel(0)
      }

      // Iniciar gravação
      mediaRecorder.start(100)

    } catch (err) {
      console.error('Erro ao iniciar gravação:', err)
      let errorMessage = 'Erro desconhecido ao acessar microfone'
      
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          errorMessage = 'Permissão para acessar o microfone foi negada'
        } else if (err.name === 'NotFoundError') {
          errorMessage = 'Nenhum microfone encontrado'
        } else if (err.name === 'NotReadableError') {
          errorMessage = 'Microfone está sendo usado por outro aplicativo'
        } else {
          errorMessage = err.message
        }
      }
      
      setError(errorMessage)
      setState('idle')
    }
  }, [isSupported, startTimer, analyzeAudio])

  // Pausar gravação
  const pause = useCallback(() => {
    if (mediaRecorderRef.current && state === 'recording') {
      mediaRecorderRef.current.pause()
    }
  }, [state])

  // Retomar gravação
  const resume = useCallback(() => {
    if (mediaRecorderRef.current && state === 'paused') {
      mediaRecorderRef.current.resume()
    }
  }, [state])

  // Parar gravação
  const stop = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (mediaRecorderRef.current && (state === 'recording' || state === 'paused')) {
        
        // Aguardar um pouco para garantir que dados estejam completos
        setTimeout(() => {
          // Salvar o onstop original e adicionar resolve
          const originalOnStop = mediaRecorderRef.current!.onstop
          mediaRecorderRef.current!.onstop = (event) => {
            // Executar a lógica original (que para o timer)
            if (originalOnStop) {
              originalOnStop.call(mediaRecorderRef.current, event)
            }
            
            // Garantir que temos chunks antes de criar blob
            if (chunksRef.current.length > 0) {
              const finalMimeType = mediaRecorderRef.current?.mimeType || 'audio/mp4'
              const audioBlob = new Blob(chunksRef.current, { type: finalMimeType })
              console.log('Blob criado:', {
                size: audioBlob.size,
                type: audioBlob.type,
                chunks: chunksRef.current.length
              })
              resolve(audioBlob)
            } else {
              console.error('Nenhum chunk de áudio foi gravado')
              resolve(null)
            }
          }
          
          mediaRecorderRef.current!.stop()
        }, 100) // Aguardar 100ms para flush dos dados
      } else {
        resolve(null)
      }
    })
  }, [state, blob])

  // Cancelar gravação
  const cancel = useCallback(() => {
    // Parar recursos
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    
    // IMPORTANTE: Sempre parar o stream para liberar o microfone
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop()
      })
      streamRef.current = null
    }
    
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    // Limpar refs
    analyserRef.current = null
    mediaRecorderRef.current = null
    
    // Limpar timers
    stopTimer()
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    
    // Reset estado
    setState('idle')
    setDuration(0)
    setAudioLevel(0)
    setBlob(null)
    setError(null)
    chunksRef.current = []
    startTimeRef.current = 0
    pausedTimeRef.current = 0
    totalPausedTimeRef.current = 0
  }, [stopTimer])

  // Parar automaticamente quando atingir duração máxima
  useEffect(() => {
    if (duration >= maxDurationSec && state === 'recording') {
      stop()
    }
  }, [duration, maxDurationSec, state, stop])

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      cancel()
    }
  }, [cancel])

  return {
    data: {
      state,
      duration,
      audioLevel,
      error,
      blob,
      isSupported
    },
    start,
    pause,
    resume,
    stop,
    cancel,
    analyserNode: analyserRef.current
  }
}