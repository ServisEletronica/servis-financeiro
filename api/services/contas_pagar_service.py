from datetime import date, datetime, timedelta
from typing import Optional, List
from database import db
from utils.calculos import calcular_valor_pagar


class ContasPagarService:
    """Service para operações de Contas a Pagar"""

    @staticmethod
    def buscar_contas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
        """
        Busca contas a pagar com filtros de data
        Query otimizada removendo JOINs desnecessários
        """

        # Query base otimizada com data ajustada
        query = """
        SELECT
            E501MCP.CODEMP,
            E501MCP.CODFIL,
            E501MCP.NUMTIT,
            E501MCP.CODFOR,
            E095FOR.NOMFOR,
            E501MCP.SEQMOV,
            E501MCP.CODTNS,
            E501MCP.DATMOV,
            E501MCP.CODFPG,
            E501TCP.CODTPT,
            E501TCP.SITTIT,
            E501TCP.OBSTCP,
            CAST(E501TCP.VLRORI AS DECIMAL(18,2)) AS VLRORI,
            E501TCP.DATEMI,
            E501TCP.ULTPGT,
            E501MCP.VCTPRO,
            CAST(E501RAT.VLRRAT AS DECIMAL(18,2)) AS VLRRAT,
            E501RAT.CTAFIN,
            E501RAT.CODCCU,
            E501RAT.CTARED,
            CAST(E501TCP.VLRABE AS DECIMAL(18,2)) AS VLRABE,
            DataAjustada.VCTPRO_AJUSTADO
        FROM E501MCP
        INNER JOIN E501TCP ON E501MCP.CODEMP = E501TCP.CODEMP
                           AND E501MCP.CODFIL = E501TCP.CODFIL
                           AND E501MCP.NUMTIT = E501TCP.NUMTIT
                           AND E501MCP.CODTPT = E501TCP.CODTPT
                           AND E501MCP.CODFOR = E501TCP.CODFOR
        INNER JOIN E001TNS ON E501TCP.CODEMP = E001TNS.CODEMP
                           AND E501TCP.CODTNS = E001TNS.CODTNS
        INNER JOIN E095FOR ON E501MCP.CODFOR = E095FOR.CODFOR
        INNER JOIN E501RAT ON E501MCP.CODEMP = E501RAT.CODEMP
                           AND E501MCP.CODFIL = E501RAT.CODFIL
                           AND E501MCP.CODFOR = E501RAT.CODFOR
                           AND E501MCP.NUMTIT = E501RAT.NUMTIT
                           AND E501MCP.SEQMOV = E501RAT.SEQMOV
                           AND E501MCP.CODTPT = E501RAT.CODTPT
        CROSS APPLY (
            -- Calcula data ajustada: Sábado/Domingo → Segunda
            SELECT
                CASE
                    WHEN DATEPART(WEEKDAY, E501MCP.VCTPRO) = 7 THEN DATEADD(DAY, 2, E501MCP.VCTPRO)  -- Sábado +2
                    WHEN DATEPART(WEEKDAY, E501MCP.VCTPRO) = 1 THEN DATEADD(DAY, 1, E501MCP.VCTPRO)  -- Domingo +1
                    ELSE E501MCP.VCTPRO
                END AS VCTPRO_AJUSTADO
        ) AS DataAjustada
        WHERE E501MCP.CODEMP IN (10,20,30)
          AND E501TCP.SITTIT <> 'CA'
          AND E501MCP.SEQMOV = 1
          AND E501TCP.VLRABE >= 0
          AND E001TNS.LISMOD = 'CPE'
          AND E501RAT.CTAFIN NOT IN (407,408,409,410,411,412,501)
        """

        # Adiciona filtro de data usando data ajustada
        params = []
        if data_inicio and data_fim:
            query += " AND DataAjustada.VCTPRO_AJUSTADO BETWEEN %s AND %s"
            params = (data_inicio, data_fim)
        elif data_inicio:
            query += " AND DataAjustada.VCTPRO_AJUSTADO >= %s"
            params = (data_inicio,)

        query += " ORDER BY DataAjustada.VCTPRO_AJUSTADO DESC"

        # Executa query
        results = db.execute_query(query, tuple(params) if params else None)

        # Processa resultados aplicando cálculos
        contas_processadas = []
        for row in results:
            valor_calculado = calcular_valor_pagar(
                row['VLRABE'],
                row['VLRRAT']
            )

            conta = {
                'codemp': row['CODEMP'],
                'codfil': row['CODFIL'],
                'numtit': row['NUMTIT'],
                'codfor': row['CODFOR'],
                'nomfor': row['NOMFOR'],
                'seqmov': row['SEQMOV'],
                'codtns': row['CODTNS'],
                'sittit': row['SITTIT'],
                'vlrori': row['VLRORI'],
                'vlrabe': row['VLRABE'],
                'vlrrat': row['VLRRAT'],
                'vctpro': row['VCTPRO'],
                'vctpro_ajustado': row['VCTPRO_AJUSTADO'],  # Já vem calculado do SQL
                'datemi': row['DATEMI'],
                'ctafin': row['CTAFIN'],
                'codccu': row['CODCCU'],
                'valor_calculado': valor_calculado
            }
            contas_processadas.append(conta)

        return contas_processadas

    @staticmethod
    def calcular_total_despesas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> float:
        """Calcula o total de despesas no período - OTIMIZADO COM AJUSTE DE DATA"""

        # Query otimizada que calcula direto no SQL com data ajustada
        query = """
        SELECT
            CAST(SUM(
                CASE
                    WHEN E501TCP.VLRABE > E501RAT.VLRRAT THEN E501RAT.VLRRAT
                    WHEN E501TCP.VLRABE = 0 THEN E501RAT.VLRRAT
                    ELSE E501TCP.VLRABE
                END
            ) AS DECIMAL(18,2)) AS total_despesas
        FROM E501MCP
        INNER JOIN E501TCP ON E501MCP.CODEMP = E501TCP.CODEMP
                           AND E501MCP.CODFIL = E501TCP.CODFIL
                           AND E501MCP.NUMTIT = E501TCP.NUMTIT
                           AND E501MCP.CODTPT = E501TCP.CODTPT
                           AND E501MCP.CODFOR = E501TCP.CODFOR
        INNER JOIN E001TNS ON E501TCP.CODEMP = E001TNS.CODEMP
                           AND E501TCP.CODTNS = E001TNS.CODTNS
        INNER JOIN E501RAT ON E501MCP.CODEMP = E501RAT.CODEMP
                           AND E501MCP.CODFIL = E501RAT.CODFIL
                           AND E501MCP.CODFOR = E501RAT.CODFOR
                           AND E501MCP.NUMTIT = E501RAT.NUMTIT
                           AND E501MCP.SEQMOV = E501RAT.SEQMOV
                           AND E501MCP.CODTPT = E501RAT.CODTPT
        CROSS APPLY (
            -- Calcula data ajustada: Sábado/Domingo → Segunda
            SELECT
                CASE
                    WHEN DATEPART(WEEKDAY, E501MCP.VCTPRO) = 7 THEN DATEADD(DAY, 2, E501MCP.VCTPRO)  -- Sábado +2
                    WHEN DATEPART(WEEKDAY, E501MCP.VCTPRO) = 1 THEN DATEADD(DAY, 1, E501MCP.VCTPRO)  -- Domingo +1
                    ELSE E501MCP.VCTPRO
                END AS VCTPRO_AJUSTADO
        ) AS DataAjustada
        WHERE E501MCP.CODEMP IN (10,20,30)
          AND E501TCP.SITTIT <> 'CA'
          AND E501MCP.SEQMOV = 1
          AND E501TCP.VLRABE >= 0
          AND E001TNS.LISMOD = 'CPE'
          AND E501RAT.CTAFIN NOT IN (407,408,409,410,411,412,501)
        """

        params = []
        if data_inicio and data_fim:
            query += " AND DataAjustada.VCTPRO_AJUSTADO BETWEEN %s AND %s"
            params = (data_inicio, data_fim)
        elif data_inicio:
            query += " AND DataAjustada.VCTPRO_AJUSTADO >= %s"
            params = (data_inicio,)

        results = db.execute_query(query, tuple(params) if params else None)

        total = results[0]['total_despesas'] if results and results[0]['total_despesas'] else 0
        return total if total > 0 else 0

    @staticmethod
    def calcular_total_periodo_anterior(data_inicio: str, data_fim: str) -> float:
        """Calcula total do período anterior para comparação"""
        from datetime import datetime, timedelta

        # Converte strings para datas
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')

        # Calcula duração do período
        duracao = (fim - inicio).days

        # Calcula período anterior
        inicio_anterior = inicio - timedelta(days=duracao + 1)
        fim_anterior = inicio - timedelta(days=1)

        return ContasPagarService.calcular_total_despesas(
            inicio_anterior.strftime('%Y-%m-%d'),
            fim_anterior.strftime('%Y-%m-%d')
        )
