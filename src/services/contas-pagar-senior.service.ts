import { api } from './api'

export interface ResumoPorDia {
  data: string
  total: number
  quantidade: number
}

export class ContasPagarSeniorService {
  /**
   * Retorna resumo de contas a pagar LIQUIDADAS agrupado por dia
   * Filtra apenas títulos com SITTIT = 'LQ'
   */
  static async obterResumoPorDiaLiquidado(periodo: string, filiais?: string[]): Promise<ResumoPorDia[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ResumoPorDia[]>('/api/contas-pagar-senior/resumo-por-dia-liquidado', { params })
    return response.data
  }
}
