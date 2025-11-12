import { api } from './api'

export interface ResumoFinanceiro {
  saldo_atual: number
  receitas_total: number
  despesas_total: number
  saldo_mes: number
  periodo_inicio: string
  periodo_fim: string
  percentual_mudanca_saldo: number
  percentual_mudanca_receita: number
  percentual_mudanca_despesa: number
}

export interface DadosGrafico {
  mes: string
  data_completa: string
  receitas: number
  despesas: number
  saldo: number
}

export interface Transacao {
  id: number
  date: string
  description: string
  category: string
  type: 'receita' | 'despesa'
  value: number
}

export interface TopItem {
  nome: string
  total: number
}

export interface CentroCusto {
  centro_custo: string
  total: number
}

export interface FluxoCaixa {
  data: string
  saldo: number
  receitas: number
  despesas: number
}

export class DashboardService {
  static async obterResumo(periodo: string = 'mes-atual', filiais?: string[]): Promise<ResumoFinanceiro> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ResumoFinanceiro>('/api/dashboard/resumo', { params })
    return response.data
  }

  static async obterGraficoReceitasDespesas(periodo: string = 'mes-atual', filiais?: string[]): Promise<DadosGrafico[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<DadosGrafico[]>('/api/dashboard/grafico-receitas-despesas', { params })
    return response.data
  }

  static async obterGraficoEvolucao(periodo: string = 'mes-atual'): Promise<DadosGrafico[]> {
    const response = await api.get<DadosGrafico[]>('/api/dashboard/grafico-evolucao', {
      params: { periodo }
    })
    return response.data
  }

  static async obterTransacoes(periodo: string = 'mes-atual', tipo: string = 'todos'): Promise<Transacao[]> {
    const response = await api.get<Transacao[]>('/api/dashboard/transacoes', {
      params: { periodo, tipo }
    })
    return response.data
  }

  static async obterTopDespesas(periodo: string = 'mes-atual', limit: number = 10, filiais?: string[]): Promise<TopItem[]> {
    const params: any = { periodo, limit }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<TopItem[]>('/api/dashboard/top-despesas', { params })
    return response.data
  }

  static async obterTopFornecedores(periodo: string = 'mes-atual', limit: number = 10): Promise<TopItem[]> {
    const response = await api.get<TopItem[]>('/api/dashboard/top-fornecedores', {
      params: { periodo, limit }
    })
    return response.data
  }

  static async obterTopReceitas(periodo: string = 'mes-atual', limit: number = 10, filiais?: string[]): Promise<TopItem[]> {
    const params: any = { periodo, limit }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<TopItem[]>('/api/dashboard/top-receitas', { params })
    return response.data
  }

  static async obterTopClientes(periodo: string = 'mes-atual', limit: number = 10): Promise<TopItem[]> {
    const response = await api.get<TopItem[]>('/api/dashboard/top-clientes', {
      params: { periodo, limit }
    })
    return response.data
  }

  static async obterDespesasPorCentroCusto(periodo: string = 'mes-atual'): Promise<CentroCusto[]> {
    const response = await api.get<CentroCusto[]>('/api/dashboard/despesas-por-centro-custo', {
      params: { periodo }
    })
    return response.data
  }

  static async obterFluxoCaixa(periodo: string = 'mes-atual', filiais?: string[]): Promise<FluxoCaixa[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<FluxoCaixa[]>('/api/dashboard/fluxo-caixa', { params })
    return response.data
  }
}
