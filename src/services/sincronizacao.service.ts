import { api } from './api'

export interface SincronizacaoResponse {
  success: boolean
  tipo: string
  registros_inseridos: number
  tempo_execucao_ms: number
  mensagem: string
  log_id?: string
}

export interface StatusSincronizacaoResponse {
  ultima_sincronizacao?: string
  tipo?: string
  status?: string
  registros_inseridos?: number
  tempo_execucao_ms?: number
  mensagem_erro?: string
}

export class SincronizacaoService {
  /**
   * Sincroniza contas a receber do Senior para o banco local
   * @param periodo Período no formato YYYY-MM (ex: 2025-11)
   */
  static async sincronizarContasReceber(periodo: string): Promise<SincronizacaoResponse> {
    const response = await api.post<SincronizacaoResponse>(
      '/api/sincronizacao/contas-receber',
      {},
      {
        params: { periodo },
        timeout: 600000 // 10 minutos
      }
    )
    return response.data
  }

  /**
   * Sincroniza contas a pagar do Senior para o banco local
   * @param periodo Período no formato YYYY-MM (ex: 2025-11)
   */
  static async sincronizarContasPagar(periodo: string): Promise<SincronizacaoResponse> {
    const response = await api.post<SincronizacaoResponse>(
      '/api/sincronizacao/contas-pagar',
      {},
      {
        params: { periodo },
        timeout: 600000 // 10 minutos
      }
    )
    return response.data
  }

  /**
   * Sincroniza centro de custo do Senior para o banco local
   */
  static async sincronizarCentroCusto(): Promise<SincronizacaoResponse> {
    const response = await api.post<SincronizacaoResponse>(
      '/api/sincronizacao/centro-custo',
      {},
      { timeout: 600000 } // 10 minutos
    )
    return response.data
  }

  /**
   * Sincroniza ambas as tabelas (contas a receber e contas a pagar)
   */
  static async sincronizarTudo(): Promise<SincronizacaoResponse> {
    const response = await api.post<SincronizacaoResponse>(
      '/api/sincronizacao/tudo',
      {},
      { timeout: 600000 } // 10 minutos
    )
    return response.data
  }

  /**
   * Obtém o status da última sincronização
   */
  static async obterStatus(tipo?: string): Promise<StatusSincronizacaoResponse> {
    const response = await api.get<StatusSincronizacaoResponse>('/api/sincronizacao/status', {
      params: tipo ? { tipo } : undefined
    })
    return response.data
  }
}
