"""
Rotas para consulta de dados do banco local (Projetado)
Substitui as consultas diretas ao banco Senior
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import db

router = APIRouter(prefix="/api/projetado", tags=["Projetado"])


@router.get("/contas-receber")
async def obter_contas_receber(
    codemp: Optional[int] = Query(None, description="Código da empresa"),
    codfil: Optional[int] = Query(None, description="Código da filial"),
    sittit: Optional[str] = Query(None, description="Situação do título (AB, LQ)"),
    limit: int = Query(100, description="Limite de registros", le=1000)
):
    """
    Retorna contas a receber do banco local (sincronizado).

    Filtros opcionais:
    - **codemp**: Código da empresa
    - **codfil**: Código da filial
    - **sittit**: Situação do título
    - **limit**: Limite de registros (máximo 1000)
    """
    try:
        query = "SELECT * FROM contas_receber WHERE 1=1"
        params = []

        if codemp is not None:
            query += " AND CODEMP = %s"
            params.append(codemp)

        if codfil is not None:
            query += " AND CODFIL = %s"
            params.append(codfil)

        if sittit:
            query += " AND SITTIT = %s"
            params.append(sittit)

        query += " ORDER BY VCTPRO DESC"
        query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        resultados = db.execute_query(query, tuple(params) if params else None)

        return {
            "success": True,
            "total": len(resultados),
            "dados": resultados
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar contas a receber: {str(e)}")


@router.get("/contas-pagar")
async def obter_contas_pagar(
    codemp: Optional[int] = Query(None, description="Código da empresa"),
    codfil: Optional[int] = Query(None, description="Código da filial"),
    sittit: Optional[str] = Query(None, description="Situação do título"),
    limit: int = Query(100, description="Limite de registros", le=1000)
):
    """
    Retorna contas a pagar do banco local (sincronizado).

    Filtros opcionais:
    - **codemp**: Código da empresa
    - **codfil**: Código da filial
    - **sittit**: Situação do título
    - **limit**: Limite de registros (máximo 1000)
    """
    try:
        query = "SELECT * FROM contas_pagar WHERE 1=1"
        params = []

        if codemp is not None:
            query += " AND CODEMP = %s"
            params.append(codemp)

        if codfil is not None:
            query += " AND CODFIL = %s"
            params.append(codfil)

        if sittit:
            query += " AND SITTIT = %s"
            params.append(sittit)

        query += " ORDER BY VCTPRO DESC"
        query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"

        resultados = db.execute_query(query, tuple(params) if params else None)

        return {
            "success": True,
            "total": len(resultados),
            "dados": resultados
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar contas a pagar: {str(e)}")


@router.get("/resumo")
async def obter_resumo(
    codemp: Optional[int] = Query(None, description="Código da empresa")
):
    """
    Retorna um resumo das contas a receber e pagar.
    """
    try:
        # Resumo Contas a Receber
        query_receber = """
            SELECT
                COUNT(*) as total_titulos,
                SUM(VLRABE) as valor_total,
                SUM(CASE WHEN SITTIT = 'AB' THEN VLRABE ELSE 0 END) as valor_aberto,
                SUM(CASE WHEN SITTIT = 'LQ' THEN VLRABE ELSE 0 END) as valor_liquidado
            FROM contas_receber
        """

        # Resumo Contas a Pagar
        query_pagar = """
            SELECT
                COUNT(*) as total_titulos,
                SUM(VLRABE) as valor_total,
                SUM(CASE WHEN SITTIT = 'AB' THEN VLRABE ELSE 0 END) as valor_aberto,
                SUM(CASE WHEN SITTIT = 'LQ' THEN VLRABE ELSE 0 END) as valor_liquidado
            FROM contas_pagar
        """

        params = None
        if codemp is not None:
            query_receber += " WHERE CODEMP = %s"
            query_pagar += " WHERE CODEMP = %s"
            params = (codemp,)

        resumo_receber = db.execute_single(query_receber, params)
        resumo_pagar = db.execute_single(query_pagar, params)

        return {
            "success": True,
            "contas_receber": resumo_receber,
            "contas_pagar": resumo_pagar,
            "saldo_projetado": (resumo_receber.get('valor_aberto', 0) or 0) - (resumo_pagar.get('valor_aberto', 0) or 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo: {str(e)}")


@router.get("/contas-receber/resumo-por-dia")
async def obter_resumo_por_dia(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(None, description="Códigos de filiais separados por vírgula (ex: 1001,1002,1003)")
):
    """
    Retorna resumo de contas a receber agrupado por dia (data ajustada) do banco LOCAL
    Filtra apenas datas ajustadas que sejam dias úteis do mês solicitado
    """
    try:
        from services.contas_receber_local_service import ContasReceberLocalService
        from datetime import datetime

        # Calcula data_inicio e data_fim do período
        ano, mes = map(int, periodo.split('-'))
        data_inicio = datetime(ano, mes, 1).strftime('%Y-%m-%d')

        # Último dia do mês
        import calendar
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_fim = datetime(ano, mes, ultimo_dia).strftime('%Y-%m-%d')

        # Converte filiais para lista se fornecido
        filiais_list = filiais.split(',') if filiais else None

        # Busca dados do banco local
        dados = ContasReceberLocalService.obter_dados_diarios(data_inicio, data_fim, filiais_list)

        # Retorna no mesmo formato que o endpoint do Senior
        resultado = []
        for item in dados:
            # Filtra apenas datas que pertencem ao período e são dias úteis
            data_str = item.get('data')
            if data_str and data_str[:7] == periodo:  # Verifica se pertence ao mês
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                if data_obj.weekday() < 5:  # Segunda a Sexta (0-4)
                    resultado.append({
                        'data': data_str,
                        'total': item.get('total', 0),
                        'quantidade': item.get('quantidade', 0) if 'quantidade' in item else 0
                    })

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo por dia: {str(e)}")
