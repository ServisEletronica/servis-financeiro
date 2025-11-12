import { useState, useRef, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  id: number
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: '👋 Olá! Sou seu assistente financeiro inteligente. Como posso ajudá-lo hoje?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto scroll para última mensagem
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    // Adiciona mensagem do usuário
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')

    // Simula resposta do bot após 1 segundo
    setTimeout(() => {
      const botResponse = getBotResponse(inputValue)
      const botMessage: Message = {
        id: messages.length + 2,
        text: botResponse,
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    }, 1000)
  }

  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase()

    // Respostas baseadas em palavras-chave
    if (input.includes('saldo') || input.includes('balanço')) {
      return '💰 Para consultar seu saldo, acesse a página Dashboard onde você encontrará um resumo completo de suas finanças!'
    }

    if (input.includes('receber') || input.includes('receita')) {
      return '📈 As contas a receber estão disponíveis na página Projetado. Lá você pode visualizar todos os recebimentos futuros e gráficos detalhados.'
    }

    if (input.includes('pagar') || input.includes('despesa')) {
      return '📉 Para visualizar contas a pagar, vá até a página Projetado. Você encontrará todas as despesas programadas e análises por fornecedor.'
    }

    if (input.includes('sincronizar') || input.includes('atualizar')) {
      return '🔄 Para sincronizar os dados com o sistema Senior, clique no botão "Sincronizar" no topo da página Projetado.'
    }

    if (input.includes('gráfico') || input.includes('relatório')) {
      return '📊 Temos diversos gráficos disponíveis: Fluxo de Caixa, Top Fornecedores, Top Clientes e muito mais na página Projetado!'
    }

    if (input.includes('ajuda') || input.includes('help')) {
      return '🤝 Estou aqui para ajudar! Posso te orientar sobre:\n• Consultar saldo e receitas\n• Visualizar despesas\n• Sincronizar dados\n• Gráficos e relatórios\n\nO que você gostaria de saber?'
    }

    // Resposta padrão
    return '🤔 Entendi! No momento, estou em desenvolvimento e posso te ajudar com informações básicas sobre o sistema. Tente perguntar sobre saldo, receitas, despesas ou gráficos!'
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {/* Botão Flutuante - Orbe Glassmorphism */}
      <div className="fixed bottom-6 right-6 z-[100]">
        <button
          onClick={() => setIsOpen(true)}
          className="group relative h-14 w-14 rounded-full transition-all duration-300 hover:scale-110 focus:outline-none animate-float"
          style={{ pointerEvents: isOpen ? 'none' : 'auto' }}
        >
          {/* Orbe principal com glassmorphism */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 shadow-2xl animate-glow overflow-hidden">
            {/* Brilho superior (efeito de vidro) - animado */}
            <div className="absolute inset-x-3 top-2 h-5 rounded-full bg-gradient-to-b from-white/50 to-transparent blur-sm animate-shimmer-move" />

            {/* Reflexo lateral - animado */}
            <div className="absolute left-2 top-5 h-6 w-2 rounded-full bg-white/30 blur-[2px] animate-reflect-move" />

            {/* Nuvem interna 1 - movendo */}
            <div className="absolute right-3 top-4 h-4 w-4 rounded-full bg-white/20 blur-md animate-cloud-drift" />

            {/* Nuvem interna 2 - movendo (delay) */}
            <div className="absolute left-3 bottom-3 h-3 w-3 rounded-full bg-white/15 blur-md animate-cloud-drift" style={{ animationDelay: '1.5s' }} />

            {/* Nuvem interna 3 - movendo (delay) */}
            <div className="absolute right-4 bottom-4 h-3 w-3 rounded-full bg-white/25 blur-sm animate-cloud-drift" style={{ animationDelay: '3s' }} />
          </div>

          {/* Anel externo pulsante */}
          <div className="absolute inset-0 rounded-full animate-pulse-ring">
            <div className="absolute inset-[-4px] rounded-full bg-gradient-to-br from-orange-400 to-orange-600 opacity-30 blur-md" />
          </div>
        </button>
      </div>

      {/* Modal de Chat */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[600px] h-[600px] p-0 gap-0">
          {/* Header */}
          <DialogHeader className="px-6 py-4 border-b">
            <div className="flex items-center gap-3">
              <div className="relative h-10 w-10">
                {/* Orbe igual ao botão flutuante - com animações */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 shadow-lg overflow-hidden">
                  {/* Brilho superior (efeito de vidro) - animado */}
                  <div className="absolute inset-x-2 top-1.5 h-4 rounded-full bg-gradient-to-b from-white/50 to-transparent blur-sm animate-shimmer-move" />

                  {/* Reflexo lateral - animado */}
                  <div className="absolute left-1.5 top-3.5 h-5 w-1.5 rounded-full bg-white/30 blur-[1px] animate-reflect-move" />

                  {/* Nuvem interna 1 - movendo */}
                  <div className="absolute right-2 top-3 h-3 w-3 rounded-full bg-white/20 blur-md animate-cloud-drift" />

                  {/* Nuvem interna 2 - movendo (delay) */}
                  <div className="absolute left-2 bottom-2 h-2 w-2 rounded-full bg-white/15 blur-md animate-cloud-drift" style={{ animationDelay: '1.5s' }} />

                  {/* Nuvem interna 3 - movendo (delay) */}
                  <div className="absolute right-3 bottom-3 h-2 w-2 rounded-full bg-white/25 blur-sm animate-cloud-drift" style={{ animationDelay: '3s' }} />
                </div>

                {/* Indicador de status online */}
                <span className="absolute bottom-0 right-0 h-3 w-3 bg-green-500 rounded-full border-2 border-background animate-pulse" />
              </div>
              <div>
                <DialogTitle>Assistente IA Financeiro</DialogTitle>
                <DialogDescription>
                  Online • Pronto para ajudar
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          {/* Chat Messages */}
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex',
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[80%] rounded-2xl px-4 py-3',
                      message.sender === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-foreground'
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                    <span className="text-xs opacity-70 mt-1 block">
                      {message.timestamp.toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua pergunta..."
                className="flex-1"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Powered by IA • Desenvolvido para Servis
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
