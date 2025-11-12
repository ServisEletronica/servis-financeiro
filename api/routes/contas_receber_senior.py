from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.contas_receber_senior_service import ContasReceberSeniorService
import traceback

router = APIRouter(prefix="/api/contas-receber-senior", tags=["Contas a Receber - Senior"])


@router.get("/resumo-por-dia")
async def obter_resumo_por_dia(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula (ex: 1001,1002)")
):
    """
    Retorna resumo de contas a receber agrupado por dia (data ajustada)
    Busca dados diretamente do Senior
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = ContasReceberSeniorService.obter_resumo_por_dia(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_resumo_por_dia: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo por dia: {str(e)}")


@router.get("/resumo-por-dia-liquidado")
async def obter_resumo_por_dia_liquidado(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula (ex: 1001,1002)")
):
    """
    Retorna resumo de contas a receber LIQUIDADAS agrupado por dia (data ajustada)
    Filtra apenas títulos com SITTIT = 'LQ'
    Busca dados diretamente do Senior
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = ContasReceberSeniorService.obter_resumo_por_dia_liquidado(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_resumo_por_dia_liquidado: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo liquidado por dia: {str(e)}")


@router.get("/total-periodo")
async def obter_total_periodo(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna o total de contas a receber para o período
    Busca dados diretamente do Senior
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = ContasReceberSeniorService.obter_total_periodo(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_total_periodo: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar total do período: {str(e)}")


@router.get("/detalhado")
async def obter_contas_detalhado(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna lista detalhada de todas as contas a receber
    Busca dados diretamente do Senior
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = ContasReceberSeniorService.obter_contas_receber_do_senior(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_contas_detalhado: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar contas detalhadas: {str(e)}")


@router.get("/debug-dia")
async def debug_dia_especifico(
    data: str = Query(..., description="Data no formato YYYY-MM-DD (ex: 2025-11-03)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula (ex: 1001,1002,1003)")
):
    """
    Debug: Retorna todas as contas que foram ajustadas para uma data específica
    """
    try:
        # Extrai período da data
        periodo = data[:7]  # YYYY-MM

        filiais_list = filiais.split(',') if filiais else None
        todas_contas = ContasReceberSeniorService.obter_contas_receber_do_senior(periodo, filiais_list)

        # Filtra contas que foram ajustadas para a data específica
        contas_do_dia = [
            {
                'NUMTIT': conta.get('NUMTIT'),
                'DATPPT_ORIGINAL': conta.get('DATPPT').strftime('%Y-%m-%d') if conta.get('DATPPT') else None,
                'DATA_AJUSTADA': conta.get('DATA_AJUSTADA_STR'),
                'VLRABE': conta.get('VLRABE'),
                'VLRORI': conta.get('VLRORI'),
                'RECDEC': conta.get('RECDEC'),
                'VALOR_CR': conta.get('VALOR_CR'),
                'CODFIL': conta.get('CODFIL'),
                'NOMCLI': conta.get('NOMCLI')
            }
            for conta in todas_contas
            if conta.get('DATA_AJUSTADA_STR') == data
        ]

        total = sum(c['VALOR_CR'] for c in contas_do_dia)

        return {
            'data_consultada': data,
            'quantidade_contas': len(contas_do_dia),
            'total_valor_cr': total,
            'contas': contas_do_dia
        }
    except Exception as e:
        print(f"Erro em debug_dia_especifico: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
