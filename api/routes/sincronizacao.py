"""
Rotas para sincronização de dados
"""

from fastapi import APIRouter, HTTPException, Query
from models import SincronizacaoResponse, StatusSincronizacaoResponse
from services.sincronizacao_service import SincronizacaoService
from services.centro_custo_service import CentroCustoService

router = APIRouter(prefix="/api/sincronizacao", tags=["Sincronização"])


@router.post("/contas-receber", response_model=SincronizacaoResponse)
async def sincronizar_contas_receber(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)")
):
    """
    Sincroniza contas a receber de um período específico do banco Senior para o banco local.
    Remove registros do período e reinsere os dados atualizados.
    Usa todas as filiais: 1001, 1002, 1003, 3001, 3002, 3003
    """
    import traceback
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[ROTA] Iniciando sincronização para período: {periodo}")
        resultado = SincronizacaoService.sincronizar_contas_receber_periodo(periodo)
        logger.info(f"[ROTA] Resultado: {resultado}")

        if not resultado['success']:
            logger.error(f"[ROTA] Sincronização falhou: {resultado.get('error')}")
            raise HTTPException(status_code=500, detail=resultado.get('error', 'Erro desconhecido'))

        return SincronizacaoResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ROTA] ERRO CRÍTICO: {str(e)}")
        logger.error(f"[ROTA] Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar contas a receber: {str(e)}")


@router.post("/contas-pagar", response_model=SincronizacaoResponse)
async def sincronizar_contas_pagar(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)")
):
    """
    Sincroniza contas a pagar de um período específico do banco Senior para o banco local.
    Remove registros dos últimos 4 meses e reinsere os dados atualizados com projeção.
    Usa todas as filiais: 1001, 1002, 1003, 3001, 3002, 3003
    """
    import traceback
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[ROTA] Iniciando sincronização contas a pagar para período: {periodo}")
        resultado = SincronizacaoService.sincronizar_contas_pagar_periodo(periodo)
        logger.info(f"[ROTA] Resultado: {resultado}")

        if not resultado['success']:
            logger.error(f"[ROTA] Sincronização falhou: {resultado.get('mensagem')}")
            raise HTTPException(status_code=500, detail=resultado.get('mensagem', 'Erro desconhecido'))

        return SincronizacaoResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ROTA] ERRO CRÍTICO: {str(e)}")
        logger.error(f"[ROTA] Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar contas a pagar: {str(e)}")


@router.post("/centro-custo")
async def sincronizar_centro_custo():
    """
    Sincroniza apenas a tabela de Centro de Custo do banco Senior.
    Remove todos os registros existentes e reinsere os dados atualizados.
    """
    try:
        resultado = CentroCustoService.sincronizar_centro_custo()

        if not resultado['success']:
            raise HTTPException(status_code=500, detail=resultado.get('message', 'Erro ao sincronizar'))

        return {
            'success': resultado['success'],
            'tipo': 'centro_custo',
            'registros_inseridos': resultado['registros_inseridos'],
            'tempo_execucao_ms': 0,  # Pode adicionar controle de tempo se necessário
            'mensagem': resultado['message'],
            'log_id': None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar centro de custo: {str(e)}")


@router.post("/tudo", response_model=SincronizacaoResponse)
async def sincronizar_tudo():
    """
    Sincroniza todas as tabelas (contas a receber, contas a pagar, plano financeiro e centro de custo).
    Remove todos os registros existentes e reinsere os dados atualizados.
    """
    try:
        resultado = SincronizacaoService.sincronizar_tudo()

        if not resultado['success']:
            raise HTTPException(status_code=500, detail=resultado['mensagem'])

        return SincronizacaoResponse(**resultado)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar dados: {str(e)}")


@router.get("/status", response_model=StatusSincronizacaoResponse)
async def obter_status_sincronizacao(tipo: str = None):
    """
    Obtém o status da última sincronização.

    - **tipo**: Tipo de sincronização ('contas_receber', 'contas_pagar', 'ambas').
                Se não fornecido, retorna a última sincronização de qualquer tipo.
    """
    try:
        status = SincronizacaoService.obter_status_ultima_sincronizacao(tipo)
        return StatusSincronizacaoResponse(**status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")
