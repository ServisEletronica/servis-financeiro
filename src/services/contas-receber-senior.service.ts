import { api } from './api'

export interface ResumoPorDia {
  data: string
  total: number
  quantidade: number
}

export interface TotalPeriodo {
  total: number
  quantidade: number
  periodo: string
}

export interface ContaReceberSeniorDetalhada {
  CODEMP: number
  CODFIL: string
  CODCLI: number
  NOMCLI: string
  CIDCLI: string
  BAICLI: string
  TIPCLI: string
  DATEMI: string
  NUMTIT: string
  SITTIT: string
  CODTPT: string
  VLRABE: number
  VLRORI: number
  RECDEC: number
  VCTPRO: string
  VCTORI: string
  DATPPT: string
  CODTNS: string
  DESTNS: string
  CODCCU: number
  CTAFIN: number
  DATA_AJUSTADA: string
  DATA_AJUSTADA_STR: string
  VALOR_CR: number
}

export class ContasReceberSeniorService {
  /**
   * Retorna resumo de contas a receber agrupado por dia
   */
  static async obterResumoPorDia(periodo: string, filiais?: string[]): Promise<ResumoPorDia[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ResumoPorDia[]>('/api/contas-receber-senior/resumo-por-dia', { params })
    return response.data
  }

  /**
   * Retorna o total de contas a receber para o período
   */
  static async obterTotalPeriodo(periodo: string, filiais?: string[]): Promise<TotalPeriodo> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<TotalPeriodo>('/api/contas-receber-senior/total-periodo', { params })
    return response.data
  }

  /**
   * Retorna lista detalhada de todas as contas a receber
   */
  static async obterContasDetalhado(periodo: string, filiais?: string[]): Promise<ContaReceberSeniorDetalhada[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ContaReceberSeniorDetalhada[]>('/api/contas-receber-senior/detalhado', { params })
    return response.data
  }

  /**
   * Retorna resumo de contas a receber LIQUIDADAS agrupado por dia
   * Filtra apenas títulos com SITTIT = 'LQ'
   */
  static async obterResumoPorDiaLiquidado(periodo: string, filiais?: string[]): Promise<ResumoPorDia[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ResumoPorDia[]>('/api/contas-receber-senior/resumo-por-dia-liquidado', { params })
    return response.data
  }
}
