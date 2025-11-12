from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import traceback

router = APIRouter(prefix="/api/contas-pagar-senior", tags=["Contas a Pagar - Senior"])


@router.get("/resumo-por-dia-liquidado")
async def obter_resumo_por_dia_liquidado(
    periodo: str = Query(..., description="Período no formato YYYY-MM (ex: 2025-11)"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna resumo de contas a pagar LIQUIDADAS agrupado por dia (data ajustada)
    Filtra apenas títulos com SITTIT = 'LQ'
    Busca dados diretamente do Senior
    """
    try:
        from services.contas_pagar_senior_service import ContasPagarSeniorService

        filiais_list = filiais.split(',') if filiais else None
        resultado = ContasPagarSeniorService.obter_resumo_por_dia_liquidado(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_resumo_por_dia_liquidado: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo liquidado por dia: {str(e)}")


@router.get("/debug-total-local")
async def debug_total_local():
    """
    Debug: Retorna contagem total de registros salvos no banco local
    """
    try:
        from database import db

        query = """
        SELECT COUNT(*) as total,
               MIN(VCTPRO) as data_min,
               MAX(VCTPRO) as data_max
        FROM contas_pagar
        """

        resultado = db.execute_query(query)

        return {
            'total_registros': resultado[0]['total'] if resultado else 0,
            'data_minima': resultado[0]['data_min'].strftime('%Y-%m-%d') if resultado and resultado[0]['data_min'] else None,
            'data_maxima': resultado[0]['data_max'].strftime('%Y-%m-%d') if resultado and resultado[0]['data_max'] else None
        }
    except Exception as e:
        print(f"Erro em debug_total_local: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.get("/debug-dia-senior")
async def debug_dia_senior(
    data: str = Query(..., description="Data no formato YYYY-MM-DD (ex: 2025-11-03)"),
    filiais: Optional[str] = Query(None, description="Códigos de filiais separados por vírgula")
):
    """
    Debug: Retorna todas as contas a pagar que foram ajustadas para uma data específica
    BUSCA DIRETO DO SENIOR (não do banco local)
    """
    try:
        from services.contas_pagar_senior_service import ContasPagarSeniorService

        # Extrai período da data
        periodo = data[:7]  # YYYY-MM

        filiais_list = filiais.split(',') if filiais else None
        todas_contas = ContasPagarSeniorService.obter_contas_pagar_do_senior(periodo, filiais_list)

        # Filtra contas que foram ajustadas para a data específica
        contas_do_dia = [
            {
                'NUMTIT': conta.get('NUMTIT'),
                'VCTPRO_ORIGINAL': conta.get('VCTPRO').strftime('%Y-%m-%d') if conta.get('VCTPRO') else None,
                'DATA_AJUSTADA': conta.get('DATA_AJUSTADA_STR'),
                'VLRABE': conta.get('VLRABE'),
                'VLRRAT': conta.get('VLRRAT'),
                'VALOR_CP': conta.get('VALOR_CP'),
                'CODFIL': conta.get('CODFIL'),
                'NOMFOR': conta.get('NOMFOR'),
                'CTAFIN': conta.get('CTAFIN')
            }
            for conta in todas_contas
            if conta.get('DATA_AJUSTADA_STR') == data
        ]

        total = sum(c['VALOR_CP'] for c in contas_do_dia)

        return {
            'data_consultada': data,
            'fonte': 'SENIOR (direto)',
            'quantidade_contas': len(contas_do_dia),
            'total_valor_cp': total,
            'contas': contas_do_dia[:10]  # Mostra apenas 10 primeiras
        }
    except Exception as e:
        print(f"Erro em debug_dia_senior: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.get("/debug-dia-local")
async def debug_dia_local(
    data: str = Query(..., description="Data no formato YYYY-MM-DD (ex: 2025-11-03)"),
    filiais: Optional[str] = Query(None, description="Códigos de filiais separados por vírgula")
):
    """
    Debug: Retorna todas as contas a pagar de uma data específica
    BUSCA DO BANCO LOCAL (após sincronização)
    """
    try:
        from database import db

        # Monta filtro de filiais
        filiais_filter = ""
        if filiais:
            filiais_list = filiais.split(',')
            filiais_str = ','.join([f"'{f.strip()}'" for f in filiais_list])
            filiais_filter = f"AND CODFIL IN ({filiais_str})"

        query = f"""
        SELECT NUMTIT, CODFIL, NOMFOR, CTAFIN, VLRABE, VLRRAT,
               VCTPRO,
               CASE
                   WHEN DATEPART(WEEKDAY, VCTPRO) = 6 THEN DATEADD(DAY, 2, VCTPRO)
                   WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 1, VCTPRO)
                   ELSE VCTPRO
               END AS DATA_AJUSTADA,
               CASE
                   WHEN VLRABE > VLRRAT THEN VLRRAT
                   WHEN VLRABE = 0 THEN VLRRAT
                   ELSE VLRABE
               END AS VALOR_CP
        FROM contas_pagar
        WHERE CONVERT(VARCHAR(10),
            CASE
                WHEN DATEPART(WEEKDAY, VCTPRO) = 6 THEN DATEADD(DAY, 2, VCTPRO)
                WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 1, VCTPRO)
                ELSE VCTPRO
            END, 23) = '{data}'
        {filiais_filter}
        """

        resultados = db.execute_query(query)

        total = sum(float(r.get('VALOR_CP', 0)) for r in resultados)

        contas_formatadas = [
            {
                'NUMTIT': r.get('NUMTIT'),
                'VCTPRO_ORIGINAL': r.get('VCTPRO').strftime('%Y-%m-%d') if r.get('VCTPRO') else None,
                'DATA_AJUSTADA': r.get('DATA_AJUSTADA').strftime('%Y-%m-%d') if r.get('DATA_AJUSTADA') else None,
                'VLRABE': float(r.get('VLRABE', 0)),
                'VLRRAT': float(r.get('VLRRAT', 0)),
                'VALOR_CP': float(r.get('VALOR_CP', 0)),
                'CODFIL': r.get('CODFIL'),
                'NOMFOR': r.get('NOMFOR'),
                'CTAFIN': r.get('CTAFIN')
            }
            for r in resultados
        ]

        return {
            'data_consultada': data,
            'fonte': 'BANCO LOCAL (após sincronização)',
            'quantidade_contas': len(contas_formatadas),
            'total_valor_cp': total,
            'contas': contas_formatadas[:10]  # Mostra apenas 10 primeiras
        }
    except Exception as e:
        print(f"Erro em debug_dia_local: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
