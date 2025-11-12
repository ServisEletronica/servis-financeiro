import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Eye, EyeOff, Loader2, MessageSquare, ShieldCheck, Users, Zap, BarChart3 } from 'lucide-react'
import { useAuth } from '@/context/auth-context'
import { showCustomToastSuccess, showCustomToastError } from '@/lib/toast'

const highlights = [
  'Centralize conversas em um só lugar',
  'Conecte sua equipe e automatize fluxos',
  'Aumente a conversão com campanhas multicanal',
]

const features = [
  { icon: MessageSquare, label: 'Atendimento Rápido', description: 'WhatsApp, Chat e mais' },
  { icon: Zap, label: 'Automação Inteligente', description: 'Workflows e Chatbots' },
  { icon: BarChart3, label: 'Analytics Avançado', description: 'Métricas em tempo real' },
]

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [remember, setRemember] = useState(true)
  const [loginStep, setLoginStep] = useState<'idle' | 'authenticating'>('idle')
  const navigate = useNavigate()
  const { login, token } = useAuth()

  useEffect(() => {
    if (token) {
      navigate('/projetado', { replace: true })
    }
  }, [token, navigate])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const email = String(formData.get('email') || '')
    const password = String(formData.get('password') || '')

    setIsLoading(true)
    setLoginStep('authenticating')

    try {
      await login({ email, password, remember })
      await new Promise(resolve => setTimeout(resolve, 300))
      navigate('/projetado', { replace: true })
      setTimeout(() => {
        showCustomToastSuccess(
          'Login realizado com sucesso!',
          'Bem-vindo de volta à plataforma.'
        )
      }, 100)
    } catch (error: any) {
      showCustomToastError(
        'Erro ao fazer login',
        error.message || 'Verifique suas credenciais e tente novamente.'
      )
      setLoginStep('idle')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen md:grid-cols-[1.1fr_1fr]">
        <div className="relative hidden overflow-hidden border-r bg-sidebar p-12 text-sidebar-foreground md:flex">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(138,121,171,0.35),transparent_55%),radial-gradient(circle_at_bottom_right,rgba(168,141,214,0.25),transparent_55%)]" />
          <div className="relative z-10 flex w-full flex-col">
            <div className="flex items-center justify-between text-sm font-medium text-sidebar-foreground/80">
              <div className="flex items-center gap-2 text-lg font-semibold">
                <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary shadow-sm">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    className="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"
                      className="fill-sidebar stroke-sidebar"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M8 12h.01M12 12h.01M16 12h.01"
                      className="stroke-primary"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                Template App
              </div>
              <span className="rounded-full bg-sidebar-primary/20 px-3 py-1 text-xs font-medium text-sidebar-primary">
                CRM & Atendimento
              </span>
            </div>

            <div className="mt-auto space-y-8">
              <div>
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-sidebar-primary/20">
                      <Users className="h-6 w-6 text-sidebar-primary" />
                    </div>
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-sidebar-primary/30 -ml-4">
                      <MessageSquare className="h-5 w-5 text-sidebar-primary" />
                    </div>
                  </div>
                </div>
                <h1 className="text-3xl font-bold tracking-tight text-sidebar-foreground">
                  Converse com seus clientes no ritmo que eles esperam.
                </h1>
                <p className="mt-4 max-w-sm text-sm text-sidebar-foreground/80">
                  Automação inteligente, campanhas mensuráveis e integrações em tempo real para transformar o atendimento em relacionamento.
                </p>
              </div>

              <ul className="space-y-3 text-sm">
                {highlights.map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-sidebar-primary" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>

              <div className="space-y-3 rounded-2xl bg-sidebar-accent/30 p-4 shadow-sm border border-sidebar-border/20">
                {features.map((feature) => {
                  const Icon = feature.icon
                  return (
                    <div key={feature.label} className="flex items-start gap-3 rounded-lg bg-sidebar/40 p-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary/20">
                        <Icon className="h-5 w-5 text-sidebar-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-sidebar-foreground">{feature.label}</p>
                        <p className="text-xs text-sidebar-foreground/60">{feature.description}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="relative flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/40 p-6 md:p-12">
          <Card className="relative z-10 w-full max-w-md border-none bg-card/80 shadow-xl backdrop-blur">
            <CardHeader className="space-y-3 text-center">
              <div className="flex items-center justify-center gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    className="h-7 w-7"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"
                      className="fill-card stroke-card"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M8 12h.01M12 12h.01M16 12h.01"
                      className="stroke-primary"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <span className="text-lg tracking-tight text-foreground">
                  Template<span className="font-bold">App</span>
                </span>
              </div>
              <div>
                <CardTitle className="text-2xl font-semibold">Bem-vindo de volta</CardTitle>
                <CardDescription>
                  Acesse sua conta para acompanhar conversas, campanhas e relatórios em tempo real.
                </CardDescription>
              </div>
            </CardHeader>
          <CardContent className="space-y-5">
              <form onSubmit={handleLogin} className="space-y-5">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="nome@empresa.com"
                    className="h-11"
                    defaultValue="admin@teste.com"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <Label htmlFor="password">Senha</Label>
                  </div>
                  <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    className="h-11 pr-12"
                    defaultValue="12345678"
                    required
                  />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-2 top-1/2 h-7 w-7 -translate-y-1/2 text-muted-foreground"
                      onClick={() => setShowPassword((prev) => !prev)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Use: admin@teste.com / 12345678
                  </p>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      id="remember-me"
                      checked={remember}
                      onCheckedChange={(checked) => setRemember(Boolean(checked))}
                    />
                    <Label htmlFor="remember-me" className="text-sm font-normal">
                      Permanecer conectado
                    </Label>
                  </div>
                </div>

                <Button type="submit" className="w-full h-11" disabled={isLoading}>
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  {loginStep === 'authenticating' && 'Autenticando...'}
                  {loginStep === 'idle' && 'Entrar'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
