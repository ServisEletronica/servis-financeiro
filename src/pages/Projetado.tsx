import { useState, useEffect } from 'react'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ArrowDownRight,
  ArrowUpRight,
  Calendar,
  ChevronDown,
  CreditCard,
  DollarSign,
  Loader2,
  RefreshCw,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'
import { UploadCieloModal } from '@/components/UploadCieloModal'
import { RecebiveisCartaoService, RecebiveisCartaoData } from '@/services/recebiveis-cartao.service'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { DashboardService, type ResumoFinanceiro, type DadosGrafico, type Transacao, type TopItem } from '@/services/dashboard.service'
import { SincronizacaoService } from '@/services/sincronizacao.service'
import { ContasReceberLocalService, type ResumoPorDia } from '@/services/contas-receber-local.service'
import { ContasReceberSeniorService } from '@/services/contas-receber-senior.service'
import { ContasPagarSeniorService } from '@/services/contas-pagar-senior.service'
import { useToast } from '@/hooks/use-toast'

const FILIAIS = [
  { codigo: '1001', nome: 'Servis Eletrônica Ceará' },
  { codigo: '1002', nome: 'Servis Eletrônica Amazonas' },
  { codigo: '1003', nome: 'Servis Eletrônica Maranhão' },
  { codigo: '2002', nome: 'Servis Gerenciamento de Risco' },
  { codigo: '3001', nome: 'Secopi Serviços Teresina' },
  { codigo: '3002', nome: 'Secopi Serviços Picos' },
  { codigo: '3003', nome: 'Secopi Serviços Paraiba' },
]

export default function ProjetadoPage() {
  const { toast } = useToast()
  // Define o mês vigente como padrão
  const mesVigente = new Date().toISOString().slice(0, 7) // Formato: YYYY-MM
  const diaAtual = new Date().toISOString().slice(0, 10) // Formato: YYYY-MM-DD
  const [selectedPeriod, setSelectedPeriod] = useState(mesVigente)
  const [selectedFilter, setSelectedFilter] = useState('todos')
  const [selectedFiliais, setSelectedFiliais] = useState<string[]>([])
  const [selectedDay, setSelectedDay] = useState<string>('todos') // 'todos' ou 'YYYY-MM-DD'

  // Estados para dados da API
  const [resumo, setResumo] = useState<ResumoFinanceiro | null>(null)
  const [dadosGrafico, setDadosGrafico] = useState<DadosGrafico[]>([])
  const [transacoes, setTransacoes] = useState<Transacao[]>([])
  const [topDespesas, setTopDespesas] = useState<TopItem[]>([])
  const [topReceitas, setTopReceitas] = useState<TopItem[]>([])
  const [topFornecedores, setTopFornecedores] = useState<TopItem[]>([])
  const [topClientes, setTopClientes] = useState<TopItem[]>([])
  const [recebiveisCartao, setRecebiveisCartao] = useState<RecebiveisCartaoData[]>([])
  const [contasReceberSenior, setContasReceberSenior] = useState<ResumoPorDia[]>([])
  const [contasReceberLiquidadas, setContasReceberLiquidadas] = useState<ResumoPorDia[]>([])
  const [contasPagarLiquidadas, setContasPagarLiquidadas] = useState<ResumoPorDia[]>([])

  // Estados de loading
  const [loadingResumo, setLoadingResumo] = useState(true)
  const [loadingGrafico, setLoadingGrafico] = useState(true)
  const [loadingNovosGraficos, setLoadingNovosGraficos] = useState(true)
  const [loadingContasReceberSenior, setLoadingContasReceberSenior] = useState(true)
  const [loadingLiquidadas, setLoadingLiquidadas] = useState(true)

  // Estado do modal de upload
  const [uploadModalOpen, setUploadModalOpen] = useState(false)

  // Estados de sincronização
  const [sincronizando, setSincronizando] = useState(false)

  // Função para sincronizar dados
  const handleSincronizar = async (tipo: 'tudo' | 'centro-custo' | 'contas-pagar' | 'contas-receber') => {
    try {
      setSincronizando(true)

      const tipoNomes = {
        'tudo': 'todos os dados',
        'centro-custo': 'Centro de Custo',
        'contas-pagar': 'Contas a Pagar',
        'contas-receber': 'Contas a Receber'
      }

      toast({
        title: "Sincronização Iniciada",
        description: `Sincronizando ${tipoNomes[tipo]} do sistema Senior...`,
      })

      let resultado: any
      switch (tipo) {
        case 'tudo':
          resultado = await SincronizacaoService.sincronizarTudo()
          break
        case 'centro-custo':
          resultado = await SincronizacaoService.sincronizarCentroCusto()
          break
        case 'contas-pagar':
          resultado = await SincronizacaoService.sincronizarContasPagar(selectedPeriod)
          break
        case 'contas-receber':
          resultado = await SincronizacaoService.sincronizarContasReceber(selectedPeriod)
          break
      }

      if (resultado.success) {
        toast({
          title: "Sincronização Concluída!",
          description: `${resultado.registros_inseridos} registros de ${tipoNomes[tipo]} sincronizados em ${(resultado.tempo_execucao_ms / 1000).toFixed(2)}s`,
        })

        // Recarregar dados após sincronização
        window.location.reload()
      } else {
        toast({
          title: "Erro na Sincronização",
          description: resultado.mensagem,
          variant: "destructive",
        })
      }
    } catch (err) {
      console.error('Erro ao sincronizar:', err)
      toast({
        title: "Erro na Sincronização",
        description: "Não foi possível sincronizar os dados. Verifique se a API está rodando.",
        variant: "destructive",
      })
    } finally {
      setSincronizando(false)
    }
  }

  // Busca dados do resumo
  useEffect(() => {
    const fetchResumo = async () => {
      try {
        setLoadingResumo(true)
        console.log('Buscando resumo para período:', selectedPeriod, 'filiais:', selectedFiliais)
        const filiais = selectedFiliais.length > 0 ? selectedFiliais : undefined
        const data = await DashboardService.obterResumo(selectedPeriod, filiais)
        console.log('Resumo recebido:', data)
        setResumo(data)
      } catch (err: any) {
        console.error('Erro ao buscar resumo:', err)
        console.error('Erro detalhado:', err.response?.data, err.message)
      } finally {
        setLoadingResumo(false)
      }
    }

    fetchResumo()
  }, [selectedPeriod, selectedFiliais])

  // Busca dados dos gráficos
  useEffect(() => {
    const fetchGrafico = async () => {
      try {
        setLoadingGrafico(true)
        const filiais = selectedFiliais.length > 0 ? selectedFiliais : undefined
        const data = await DashboardService.obterGraficoReceitasDespesas(selectedPeriod, filiais)
        setDadosGrafico(data)
      } catch (err) {
        console.error('Erro ao buscar gráfico:', err)
      } finally {
        setLoadingGrafico(false)
      }
    }

    fetchGrafico()
  }, [selectedPeriod, selectedFiliais])

  // Busca dados dos novos gráficos
  useEffect(() => {
    const fetchNovosGraficos = async () => {
      try {
        setLoadingNovosGraficos(true)
        const filiais = selectedFiliais.length > 0 ? selectedFiliais : undefined
        const [despesas, receitas] = await Promise.all([
          DashboardService.obterTopDespesas(selectedPeriod, 10, filiais),
          DashboardService.obterTopReceitas(selectedPeriod, 10, filiais)
        ])

        setTopDespesas(despesas)
        setTopReceitas(receitas)
      } catch (err) {
        console.error('Erro ao buscar novos gráficos:', err)
      } finally {
        setLoadingNovosGraficos(false)
      }
    }

    fetchNovosGraficos()
  }, [selectedPeriod, selectedFiliais])

  // Busca dados de recebíveis de cartão
  useEffect(() => {
    const fetchRecebiveisCartao = async () => {
      try {
        // Converte período YYYY-MM para data_inicio e data_fim
        const [ano, mes] = selectedPeriod.split('-')
        const dataInicio = `${ano}-${mes}-01`

        // Calcula último dia do mês
        const ultimoDia = new Date(parseInt(ano), parseInt(mes), 0).getDate()
        const dataFim = `${ano}-${mes}-${ultimoDia.toString().padStart(2, '0')}`

        const data = await RecebiveisCartaoService.obterRecebiveis(dataInicio, dataFim)
        setRecebiveisCartao(data)
      } catch (err) {
        console.error('Erro ao buscar recebíveis de cartão:', err)
        setRecebiveisCartao([])
      }
    }

    fetchRecebiveisCartao()
  }, [selectedPeriod])

  // Busca dados de contas a receber do banco local (sincronizado do Senior)
  useEffect(() => {
    const fetchContasReceber = async () => {
      try {
        setLoadingContasReceberSenior(true)
        // Busca do banco local que foi sincronizado do Senior
        // Filtra por filiais se especificado
        const filiais = selectedFiliais.length > 0 ? selectedFiliais : undefined
        const data = await ContasReceberLocalService.obterResumoPorDia(selectedPeriod, filiais)
        setContasReceberSenior(data)
      } catch (err) {
        console.error('Erro ao buscar contas a receber:', err)
        setContasReceberSenior([])
      } finally {
        setLoadingContasReceberSenior(false)
      }
    }

    fetchContasReceber()
  }, [selectedPeriod, selectedFiliais])

  // Busca dados de contas liquidadas (RECEBIDO e PAGO) diretamente do Senior
  useEffect(() => {
    const fetchContasLiquidadas = async () => {
      try {
        setLoadingLiquidadas(true)
        const filiais = selectedFiliais.length > 0 ? selectedFiliais : undefined

        // Busca contas recebidas e pagas em paralelo
        const [recebidas, pagas] = await Promise.all([
          ContasReceberSeniorService.obterResumoPorDiaLiquidado(selectedPeriod, filiais),
          ContasPagarSeniorService.obterResumoPorDiaLiquidado(selectedPeriod, filiais)
        ])

        setContasReceberLiquidadas(recebidas)
        setContasPagarLiquidadas(pagas)
      } catch (err) {
        console.error('Erro ao buscar contas liquidadas:', err)
        setContasReceberLiquidadas([])
        setContasPagarLiquidadas([])
      } finally {
        setLoadingLiquidadas(false)
      }
    }

    fetchContasLiquidadas()
  }, [selectedPeriod, selectedFiliais])

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value)
  }

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}%`
  }

  // Função para gerar os dias do mês selecionado
  const getDiasDoMes = () => {
    const [ano, mes] = selectedPeriod.split('-').map(Number)
    const ultimoDia = new Date(ano, mes, 0).getDate()
    const dias = []

    for (let dia = 1; dia <= ultimoDia; dia++) {
      const dataStr = `${ano}-${mes.toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`
      const data = new Date(ano, mes - 1, dia)
      const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
      const diaSemana = diasSemana[data.getDay()]

      dias.push({
        value: dataStr,
        label: `${dia.toString().padStart(2, '0')} - ${diaSemana}`
      })
    }

    return dias
  }

  // Função para recarregar todos os dados
  const carregarDados = () => {
    // Força a recarga disparando um setState
    setSelectedPeriod(prev => prev)
  }

  // Componente customizado para renderizar labels nas barras
  const renderCustomLabel = (props: any, maxValue: number, darkColor: string, lightColor: string) => {
    const { x, y, width, height, value } = props
    const formattedValue = formatCurrency(value)

    // Calcula se o valor cabe dentro da barra (considera que barras < 30% do máximo são pequenas)
    const percentage = (value / maxValue) * 100
    const fitsInside = percentage > 30

    if (fitsInside) {
      // Valor dentro da barra, alinhado à direita
      return (
        <text
          x={x + width - 8}
          y={y + height / 2}
          fill={darkColor}
          textAnchor="end"
          dominantBaseline="middle"
          fontSize="11px"
        >
          {formattedValue}
        </text>
      )
    } else {
      // Valor fora da barra, à direita
      return (
        <text
          x={x + width + 8}
          y={y + height / 2}
          fill={lightColor}
          textAnchor="start"
          dominantBaseline="middle"
          fontSize="11px"
        >
          {formattedValue}
        </text>
      )
    }
  }

  // Componente customizado para tooltip com formatação em R$
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border bg-background p-2 shadow-sm">
          <div className="grid gap-2">
            <div className="flex flex-col">
              <span className="text-[0.70rem] uppercase text-muted-foreground">
                {payload[0].payload.nome}
              </span>
              <span className="font-bold text-muted-foreground">
                {formatCurrency(payload[0].value)}
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8 overflow-x-hidden max-w-full">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl md:text-2xl font-bold">Projetado</h1>
          <p className="text-sm text-muted-foreground">
            Gerencie seus compromissos financeiros
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setUploadModalOpen(true)}
            className="gap-2"
          >
            <CreditCard className="h-4 w-4" />
            Upload Cielo
          </Button>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-[200px] justify-start">
                <DollarSign className="mr-2 h-4 w-4" />
                {selectedFiliais.length === 0
                  ? 'Todas as filiais'
                  : selectedFiliais.length === 1
                  ? FILIAIS.find(f => f.codigo === selectedFiliais[0])?.nome
                  : `${selectedFiliais.length} filiais`
                }
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[300px] p-0" align="start">
              <div className="p-4">
                <h4 className="font-medium mb-3">Selecionar Filiais</h4>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 p-2 hover:bg-accent rounded-md">
                    <Checkbox
                      id="todas-filiais"
                      checked={selectedFiliais.length === 0}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedFiliais([])
                        }
                      }}
                    />
                    <label
                      htmlFor="todas-filiais"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                    >
                      Todas as filiais
                    </label>
                  </div>
                  {FILIAIS.map((filial) => (
                    <div key={filial.codigo} className="flex items-center space-x-2 p-2 hover:bg-accent rounded-md">
                      <Checkbox
                        id={`filial-${filial.codigo}`}
                        checked={selectedFiliais.includes(filial.codigo)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedFiliais([...selectedFiliais, filial.codigo])
                          } else {
                            setSelectedFiliais(selectedFiliais.filter(c => c !== filial.codigo))
                          }
                        }}
                      />
                      <label
                        htmlFor={`filial-${filial.codigo}`}
                        className="text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                      >
                        {filial.nome}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </PopoverContent>
          </Popover>
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-[180px]">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2025-01">Janeiro 2025</SelectItem>
              <SelectItem value="2025-02">Fevereiro 2025</SelectItem>
              <SelectItem value="2025-03">Março 2025</SelectItem>
              <SelectItem value="2025-04">Abril 2025</SelectItem>
              <SelectItem value="2025-05">Maio 2025</SelectItem>
              <SelectItem value="2025-06">Junho 2025</SelectItem>
              <SelectItem value="2025-07">Julho 2025</SelectItem>
              <SelectItem value="2025-08">Agosto 2025</SelectItem>
              <SelectItem value="2025-09">Setembro 2025</SelectItem>
              <SelectItem value="2025-10">Outubro 2025</SelectItem>
              <SelectItem value="2025-11">Novembro 2025</SelectItem>
              <SelectItem value="2025-12">Dezembro 2025</SelectItem>
            </SelectContent>
          </Select>
          <Select value={selectedDay} onValueChange={setSelectedDay}>
            <SelectTrigger className="w-[140px]">
              <Calendar className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Dia" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos os dias</SelectItem>
              {getDiasDoMes().map((dia) => (
                <SelectItem key={dia.value} value={dia.value}>
                  {dia.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                className="gap-2"
                disabled={sincronizando}
              >
                {sincronizando ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                <span className="hidden sm:inline">
                  {sincronizando ? 'Sincronizando...' : 'Sincronizar'}
                </span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleSincronizar('tudo')}>
                Sincronizar Tudo
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleSincronizar('centro-custo')}>
                Centro de Custo
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleSincronizar('contas-pagar')}>
                Contas a Pagar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleSincronizar('contas-receber')}>
                Contas a Receber
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Cards de Resumo */}
      <div className="grid gap-4 md:grid-cols-2 md:gap-8 lg:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">A Receber</CardTitle>
              <ArrowUpRight className="h-4 w-4" style={{ color: 'hsl(var(--chart-2))' }} />
            </CardHeader>
            <CardContent>
              {loadingContasReceberSenior ? (
                <>
                  <Skeleton className="h-8 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </>
              ) : (
                <>
                  {(() => {
                    // Filtra por dia se um dia específico for selecionado
                    const dadosFiltrados = selectedDay === 'todos'
                      ? contasReceberSenior
                      : contasReceberSenior.filter(item => item.data === selectedDay)

                    const total = dadosFiltrados.reduce((acc, item) => acc + item.total, 0)

                    return (
                      <>
                        <div className="text-2xl font-bold" style={{ color: 'hsl(var(--chart-2))' }}>
                          {formatCurrency(total)}
                        </div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                          <TrendingUp className="h-3 w-3" style={{ color: 'hsl(var(--chart-2))' }} />
                          <span style={{ color: 'hsl(var(--chart-2))' }}>
                            {selectedDay === 'todos' ? 'Período selecionado' : 'Dia específico'}
                          </span>
                        </p>
                      </>
                    )
                  })()}
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">A Pagar</CardTitle>
              <ArrowDownRight className="h-4 w-4" style={{ color: 'hsl(var(--chart-5))' }} />
            </CardHeader>
            <CardContent>
              {loadingGrafico ? (
                <>
                  <Skeleton className="h-8 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </>
              ) : (
                <>
                  {(() => {
                    // Filtra dias úteis do mês
                    let diasUteis = dadosGrafico.filter((item) => {
                      const date = new Date(item.data_completa + 'T00:00:00')
                      const dayOfWeek = date.getDay()
                      const mesAnoData = item.data_completa.substring(0, 7)
                      return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                    })

                    // Filtra por dia se um dia específico for selecionado
                    if (selectedDay !== 'todos') {
                      diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                    }

                    const total = diasUteis.reduce((acc, item) => acc + item.despesas, 0)

                    return (
                      <>
                        <div className="text-2xl font-bold" style={{ color: 'hsl(var(--chart-5))' }}>
                          {formatCurrency(total)}
                        </div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                          <TrendingDown className="h-3 w-3" style={{ color: 'hsl(var(--chart-5))' }} />
                          <span style={{ color: 'hsl(var(--chart-5))' }}>
                            {selectedDay === 'todos' ? 'Período selecionado' : 'Dia específico'}
                          </span>
                        </p>
                      </>
                    )
                  })()}
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Saldo</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loadingGrafico || loadingContasReceberSenior ? (
                <>
                  <Skeleton className="h-8 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </>
              ) : (
                <>
                  {(() => {
                    // RECEITAS: Filtra por dia se um dia específico for selecionado
                    const dadosReceitasFiltrados = selectedDay === 'todos'
                      ? contasReceberSenior
                      : contasReceberSenior.filter(item => item.data === selectedDay)

                    const receitasTotal = dadosReceitasFiltrados.reduce((acc, item) => acc + item.total, 0)

                    // DESPESAS: Usa a MESMA LÓGICA do Card "A Pagar" e do bloco "Visualização Diária"
                    let diasUteis = dadosGrafico.filter((item) => {
                      const date = new Date(item.data_completa + 'T00:00:00')
                      const dayOfWeek = date.getDay()
                      const mesAnoData = item.data_completa.substring(0, 7)
                      return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                    })

                    // Filtra por dia se específico
                    if (selectedDay !== 'todos') {
                      diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                    }

                    const despesasTotal = diasUteis.reduce((acc, item) => acc + item.despesas, 0)
                    const saldoMes = receitasTotal - despesasTotal

                    return (
                      <>
                        <div className="text-2xl font-bold">{formatCurrency(saldoMes)}</div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                          {saldoMes >= 0 ? (
                            <TrendingUp className="h-3 w-3" style={{ color: 'hsl(var(--primary))' }} />
                          ) : (
                            <TrendingDown className="h-3 w-3" style={{ color: 'hsl(var(--chart-5))' }} />
                          )}
                          <span style={{ color: saldoMes >= 0 ? 'hsl(var(--primary))' : 'hsl(var(--chart-5))' }}>
                            {selectedDay === 'todos' ? 'Resultado do período' : 'Saldo do dia'}
                          </span>
                        </p>
                      </>
                    )
                  })()}
                </>
              )}
            </CardContent>
          </Card>
        </div>

      {/* Gráfico Principal */}
      <Card>
        <CardHeader>
          <CardTitle>A Receber vs A Pagar</CardTitle>
          <CardDescription>Comparativo diário de contas a receber e a pagar do mês selecionado</CardDescription>
        </CardHeader>
        <CardContent className="pl-2">
          {loadingGrafico || loadingContasReceberSenior ? (
            <div className="h-[300px] w-full flex items-center justify-center">
              <Skeleton className="h-full w-full" />
            </div>
          ) : (
            <ChartContainer config={{}} className="h-[300px] w-full">
              <LineChart data={(() => {
                // Cria mapa de contas a receber do Senior por data
                const receitasSeniorMap = new Map<string, number>()
                contasReceberSenior.forEach(conta => {
                  receitasSeniorMap.set(conta.data, conta.total)
                })

                // Mescla dados do gráfico com dados do Senior
                let dadosMesclados = dadosGrafico.map(item => ({
                  ...item,
                  receitas: receitasSeniorMap.get(item.data_completa) || 0
                }))

                // Filtra por dia se um dia específico for selecionado
                if (selectedDay !== 'todos') {
                  dadosMesclados = dadosMesclados.filter(item => item.data_completa === selectedDay)
                }

                return dadosMesclados
              })()}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis
                  dataKey="mes"
                  tickLine={false}
                  tickMargin={10}
                  axisLine={false}
                  label={{ value: 'Dia do Mês', position: 'insideBottom', offset: -5 }}
                />
                <YAxis label={{ value: 'Valor (R$)', angle: -90, position: 'insideLeft' }} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line dataKey="receitas" stroke="hsl(var(--chart-2))" strokeWidth={2} dot={{ fill: "hsl(var(--chart-2))" }} name="A Receber" />
                <Line dataKey="despesas" stroke="hsl(var(--chart-5))" strokeWidth={2} dot={{ fill: "hsl(var(--chart-5))" }} name="A Pagar" />
              </LineChart>
            </ChartContainer>
          )}
        </CardContent>
      </Card>

      {/* Visualização Diária - Apenas Dias Úteis */}
      <Card className="w-full max-w-full">
        <CardHeader>
          <CardTitle>Caixa Diário Projetado</CardTitle>
          <CardDescription>Valores a receber e a pagar por dia</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loadingGrafico ? (
            <div className="h-[200px] w-full flex items-center justify-center px-6">
              <Skeleton className="h-full w-full" />
            </div>
          ) : (
            <div className="flex max-w-full">
              {/* Coluna Fixa da Esquerda */}
              <div className="flex-shrink-0 border-r bg-background">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[280px] px-6 bg-background h-[57px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {/* Linha A RECEBER */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-2))' }}></div>
                          <span className="whitespace-nowrap">A RECEBER</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha INADIMPLÊNCIA DO MÊS */}
                    <TableRow className="bg-muted/30">
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-1))' }}></div>
                          <span className="whitespace-nowrap text-xs">INADIMPLÊNCIA DO MÊS</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha A RECEBER INADIMPLÊNCIA ANTERIOR */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-3))' }}></div>
                          <span className="whitespace-nowrap text-xs">A RECEBER INADIMP. ANTERIOR</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha A RECEBER CARTÕES */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-4))' }}></div>
                          <span className="whitespace-nowrap text-xs">A RECEBER CARTÕES</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha A PAGAR */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-5))' }}></div>
                          <span className="whitespace-nowrap">A PAGAR</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha TOTAL GERAL */}
                    <TableRow className="border-t-2">
                      <TableCell className="font-bold px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <span className="whitespace-nowrap">TOTAL GERAL</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>

              {/* Área Scrollável com os Dias */}
              <div className="overflow-x-auto flex-1 kanban-scroll" style={{ WebkitOverflowScrolling: 'touch' }}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const date = new Date(item.data_completa + 'T00:00:00')
                              const diasSemana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
                              const diaSemana = diasSemana[date.getDay()]
                              const dataFormatada = date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

                              return (
                                <TableHead key={item.mes} className="text-center w-[140px] px-4 h-[57px]">
                                  <div className="font-semibold text-xs whitespace-nowrap">{diaSemana}</div>
                                  <div className="text-xs text-muted-foreground whitespace-nowrap">{dataFormatada}</div>
                                </TableHead>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableHead className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[57px]">
                                <div className="font-bold text-xs whitespace-nowrap">TOTAL</div>
                              </TableHead>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {/* Linha A RECEBER */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de contas a receber do Senior por data
                        const receitasSeniorMap = new Map<string, number>()
                        contasReceberSenior.forEach(conta => {
                          receitasSeniorMap.set(conta.data, conta.total)
                        })

                        const totalReceitas = diasUteis.reduce((acc, item) => {
                          const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                          return acc + valorSenior
                        }, 0)

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-2))' }}>
                                    {formatCurrency(valorSenior)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-2))' }}>
                                  {formatCurrency(totalReceitas)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha INADIMPLÊNCIA DO MÊS (10% de A RECEBER) */}
                    <TableRow className="bg-muted/30">
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de contas a receber do Senior por data
                        const receitasSeniorMap = new Map<string, number>()
                        contasReceberSenior.forEach(conta => {
                          receitasSeniorMap.set(conta.data, conta.total)
                        })

                        const totalInadimplenciaMes = diasUteis.reduce((acc, item) => {
                          const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                          return acc + (valorSenior * 0.10) // 10% do valor de A RECEBER
                        }, 0)

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                              const inadimplencia = valorSenior * 0.10 // 10% do valor
                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-1))' }}>
                                    {formatCurrency(inadimplencia)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-1))' }}>
                                  {formatCurrency(totalInadimplenciaMes)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha A RECEBER INADIMPLÊNCIA ANTERIOR */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        const totalInadimp = diasUteis.length * 20000

                        return (
                          <>
                            {diasUteis.map((item) => (
                              <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-3))' }}>
                                  {formatCurrency(20000)}
                                </span>
                              </TableCell>
                            ))}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-3))' }}>
                                  {formatCurrency(totalInadimp)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha A RECEBER CARTÕES */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de recebíveis por data
                        const recebiveisMap = new Map<string, number>()
                        recebiveisCartao.forEach(rec => {
                          recebiveisMap.set(rec.data, rec.total)
                        })

                        const totalCartoes = diasUteis.reduce((acc, item) => {
                          const valor = recebiveisMap.get(item.data_completa) || 0
                          return acc + valor
                        }, 0)

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valor = recebiveisMap.get(item.data_completa) || 0
                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-4))' }}>
                                    {formatCurrency(valor)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-4))' }}>
                                  {formatCurrency(totalCartoes)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha A PAGAR */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        const totalDespesas = diasUteis.reduce((acc, item) => acc + item.despesas, 0)

                        return (
                          <>
                            {diasUteis.map((item) => (
                              <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-5))' }}>
                                  {formatCurrency(item.despesas)}
                                </span>
                              </TableCell>
                            ))}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-5))' }}>
                                  {formatCurrency(totalDespesas)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha TOTAL GERAL */}
                    <TableRow className="border-t-2">
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de recebíveis por data
                        const recebiveisMap = new Map<string, number>()
                        recebiveisCartao.forEach(rec => {
                          recebiveisMap.set(rec.data, rec.total)
                        })

                        // Cria mapa de contas a receber do Senior por data
                        const receitasSeniorMap = new Map<string, number>()
                        contasReceberSenior.forEach(conta => {
                          receitasSeniorMap.set(conta.data, conta.total)
                        })

                        const totalReceitas = diasUteis.reduce((acc, item) => {
                          const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                          return acc + valorSenior
                        }, 0)
                        const totalInadimplenciaMes = diasUteis.reduce((acc, item) => {
                          const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                          return acc + (valorSenior * 0.10) // 10% de A RECEBER
                        }, 0)
                        const totalInadimp = diasUteis.length * 20000
                        const totalCartoes = diasUteis.reduce((acc, item) => {
                          const valor = recebiveisMap.get(item.data_completa) || 0
                          return acc + valor
                        }, 0)
                        const totalDespesas = diasUteis.reduce((acc, item) => acc + item.despesas, 0)
                        const totalGeral = totalReceitas + totalInadimplenciaMes + totalInadimp + totalCartoes - totalDespesas

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valorSenior = receitasSeniorMap.get(item.data_completa) || 0
                              const inadimplenciaMes = valorSenior * 0.10 // 10% de A RECEBER
                              const valorCartao = recebiveisMap.get(item.data_completa) || 0
                              const totalDia = valorSenior + inadimplenciaMes + 20000 + valorCartao - item.despesas
                              const cor = totalDia >= 0 ? 'hsl(var(--chart-2))' : 'hsl(var(--chart-5))'

                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-bold whitespace-nowrap" style={{ color: cor }}>
                                    {formatCurrency(totalDia)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap text-lg" style={{ color: totalGeral >= 0 ? 'hsl(var(--chart-2))' : 'hsl(var(--chart-5))' }}>
                                  {formatCurrency(totalGeral)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Visualização Diária Realizado - Apenas RECEBIDO e PAGO */}
      <Card className="w-full max-w-full">
        <CardHeader>
          <CardTitle>Caixa Diário Realizado</CardTitle>
          <CardDescription>Valores recebidos e pagos por dia</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loadingLiquidadas ? (
            <div className="h-[200px] w-full flex items-center justify-center px-6">
              <Skeleton className="h-full w-full" />
            </div>
          ) : (
            <div className="flex max-w-full">
              {/* Coluna Fixa da Esquerda */}
              <div className="flex-shrink-0 border-r bg-background">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[280px] px-6 bg-background h-[57px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {/* Linha RECEBIDO */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-2))' }}></div>
                          <span className="whitespace-nowrap">RECEBIDO</span>
                        </div>
                      </TableCell>
                    </TableRow>

                    {/* Linha PAGO */}
                    <TableRow>
                      <TableCell className="font-medium px-6 w-[280px] h-[53px]">
                        <div className="flex items-center gap-2">
                          <div className="h-3 w-3 rounded-full" style={{ backgroundColor: 'hsl(var(--chart-5))' }}></div>
                          <span className="whitespace-nowrap">PAGO</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>

              {/* Área Scrollável com os Dias */}
              <div className="overflow-x-auto flex-1 kanban-scroll" style={{ WebkitOverflowScrolling: 'touch' }}>
                <Table>
                  <TableHeader>
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const date = new Date(item.data_completa + 'T00:00:00')
                              const diasSemana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
                              const diaSemana = diasSemana[date.getDay()]
                              const dataFormatada = date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

                              return (
                                <TableHead key={item.mes} className="text-center w-[140px] px-4 h-[57px]">
                                  <div className="font-semibold text-xs whitespace-nowrap">{diaSemana}</div>
                                  <div className="text-xs text-muted-foreground whitespace-nowrap">{dataFormatada}</div>
                                </TableHead>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableHead className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[57px]">
                                <div className="font-bold text-xs whitespace-nowrap">TOTAL</div>
                              </TableHead>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {/* Linha RECEBIDO */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de contas recebidas por data
                        const recebidasMap = new Map<string, number>()
                        contasReceberLiquidadas.forEach(conta => {
                          recebidasMap.set(conta.data, conta.total)
                        })

                        const totalRecebido = diasUteis.reduce((acc, item) => {
                          const valor = recebidasMap.get(item.data_completa) || 0
                          return acc + valor
                        }, 0)

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valor = recebidasMap.get(item.data_completa) || 0
                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-2))' }}>
                                    {formatCurrency(valor)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-2))' }}>
                                  {formatCurrency(totalRecebido)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>

                    {/* Linha PAGO */}
                    <TableRow>
                      {(() => {
                        let diasUteis = dadosGrafico.filter((item) => {
                          const date = new Date(item.data_completa + 'T00:00:00')
                          const dayOfWeek = date.getDay()
                          const mesAnoData = item.data_completa.substring(0, 7)
                          return (dayOfWeek >= 1 && dayOfWeek <= 5) && (mesAnoData === selectedPeriod)
                        })

                        // Filtra por dia se um dia específico for selecionado
                        if (selectedDay !== 'todos') {
                          diasUteis = diasUteis.filter(item => item.data_completa === selectedDay)
                        }

                        // Cria mapa de contas pagas por data
                        const pagasMap = new Map<string, number>()
                        contasPagarLiquidadas.forEach(conta => {
                          pagasMap.set(conta.data, conta.total)
                        })

                        const totalPago = diasUteis.reduce((acc, item) => {
                          const valor = pagasMap.get(item.data_completa) || 0
                          return acc + valor
                        }, 0)

                        return (
                          <>
                            {diasUteis.map((item) => {
                              const valor = pagasMap.get(item.data_completa) || 0
                              return (
                                <TableCell key={item.mes} className="text-center w-[140px] px-4 h-[53px]">
                                  <span className="font-semibold whitespace-nowrap" style={{ color: 'hsl(var(--chart-5))' }}>
                                    {formatCurrency(valor)}
                                  </span>
                                </TableCell>
                              )
                            })}
                            {selectedDay === 'todos' && (
                              <TableCell className="text-center w-[140px] px-4 bg-muted/50 border-l-2 h-[53px]">
                                <span className="font-bold whitespace-nowrap" style={{ color: 'hsl(var(--chart-5))' }}>
                                  {formatCurrency(totalPago)}
                                </span>
                              </TableCell>
                            )}
                          </>
                        )
                      })()}
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gráficos de Top */}
      <div className="grid gap-4 md:gap-8 lg:grid-cols-2">
        {/* Top 10 Despesas */}
        <Card>
          <CardHeader>
            <CardTitle>Top 10 Despesas</CardTitle>
            <CardDescription>Maiores despesas por conta reduzida no período</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingNovosGraficos ? (
              <div className="h-[300px] w-full flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : (
              <ChartContainer config={{}} className="h-[300px] w-full">
                <BarChart data={topDespesas} layout="vertical" barSize={20}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    tickFormatter={(value) => {
                      return new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0,
                      }).format(value)
                    }}
                  />
                  <YAxis
                    dataKey="nome"
                    type="category"
                    width={280}
                    style={{ fontSize: '10px' }}
                  />
                  <ChartTooltip content={<CustomTooltip />} />
                  <Bar dataKey="total" fill="hsl(var(--chart-5))" name="Valor">
                    <LabelList
                      dataKey="total"
                      content={(props) => {
                        const maxValue = Math.max(...topDespesas.map(d => d.total))
                        return renderCustomLabel(props, maxValue, '#7f1d1d', '#ef4444')
                      }}
                    />
                  </Bar>
                </BarChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>

        {/* Top 10 Receitas */}
        <Card>
          <CardHeader>
            <CardTitle>Top 10 Receitas</CardTitle>
            <CardDescription>Maiores receitas por conta reduzida no período</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingNovosGraficos ? (
              <div className="h-[300px] w-full flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : (
              <ChartContainer config={{}} className="h-[300px] w-full">
                <BarChart data={topReceitas} layout="vertical" barSize={20}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    tickFormatter={(value) => {
                      return new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0,
                      }).format(value)
                    }}
                  />
                  <YAxis
                    dataKey="nome"
                    type="category"
                    width={280}
                    style={{ fontSize: '10px' }}
                  />
                  <ChartTooltip content={<CustomTooltip />} />
                  <Bar dataKey="total" fill="hsl(var(--chart-2))" name="Valor">
                    <LabelList
                      dataKey="total"
                      content={(props) => {
                        const maxValue = Math.max(...topReceitas.map(d => d.total))
                        return renderCustomLabel(props, maxValue, '#065f46', '#22c55e')
                      }}
                    />
                  </Bar>
                </BarChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Modal de Upload Cielo */}
      <UploadCieloModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
        onUploadSuccess={() => {
          // Recarrega os dados quando upload for bem-sucedido
          carregarDados()
        }}
      />
    </div>
  )
}
