import { api } from './api'

export interface ResumoPorDia {
  data: string
  total: number
  quantidade: number
}

export class ContasReceberLocalService {
  /**
   * Retorna resumo de contas a receber agrupado por dia do banco LOCAL
   */
  static async obterResumoPorDia(periodo: string, filiais?: string[]): Promise<ResumoPorDia[]> {
    const params: any = { periodo }
    if (filiais && filiais.length > 0) {
      params.filiais = filiais.join(',')
    }
    const response = await api.get<ResumoPorDia[]>('/api/projetado/contas-receber/resumo-por-dia', { params })
    return response.data
  }
}
