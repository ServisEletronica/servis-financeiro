import { api } from './api'

export interface RecebiveisCartaoData {
  data: string
  total: number
}

export interface UploadResult {
  message: string
  data: {
    sucesso: boolean
    total_imagens: number
    total_registros_inseridos: number
    erros: any[]
    detalhes: any[]
  }
}

export interface EstatisticasMes {
  total_registros: number
  total_estabelecimentos: number
  valor_total: number
  valor_medio: number
  primeira_carga: string | null
  ultima_carga: string | null
}

export class RecebiveisCartaoService {
  /**
   * Faz upload de calendários Cielo
   */
  static async uploadCalendarios(
    files: File[],
    status: 'projetado' | 'recebido' = 'projetado'
  ): Promise<UploadResult> {
    const formData = new FormData()

    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post<UploadResult>(
      `/api/recebiveis-cartao/upload?status=${status}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  }

  /**
   * Obtém recebíveis de cartão por período
   */
  static async obterRecebiveis(
    dataInicio: string,
    dataFim: string,
    estabelecimentos?: string[],
    status: 'projetado' | 'recebido' = 'projetado'
  ): Promise<RecebiveisCartaoData[]> {
    const params: any = {
      data_inicio: dataInicio,
      data_fim: dataFim,
      status
    }

    // Adiciona filtro de estabelecimentos se fornecido
    if (estabelecimentos && estabelecimentos.length > 0) {
      params.estabelecimentos = estabelecimentos.join(',')
    }

    const response = await api.get<RecebiveisCartaoData[]>('/api/recebiveis-cartao', { params })
    return response.data
  }

  /**
   * Obtém estatísticas de recebíveis de um mês
   */
  static async obterEstatisticas(mesReferencia: string): Promise<EstatisticasMes> {
    const response = await api.get<EstatisticasMes>(`/api/recebiveis-cartao/estatisticas/${mesReferencia}`)
    return response.data
  }

  /**
   * Remove dados de um mês
   */
  static async limparDadosMes(mesReferencia: string, estabelecimento?: string): Promise<void> {
    await api.delete(`/api/recebiveis-cartao/${mesReferencia}`, {
      params: estabelecimento ? { estabelecimento } : {}
    })
  }

  /**
   * Insere um recebível manualmente
   */
  static async inserirRecebidoManual(data: {
    data_recebimento: string
    valor: number
    estabelecimento: string
    mes_referencia: string
  }): Promise<void> {
    await api.post('/api/recebiveis-cartao/manual', data)
  }
}
