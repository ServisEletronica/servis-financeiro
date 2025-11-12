from datetime import date
from typing import Optional, List
from database import db
from utils.calculos import calcular_valor_receber


class ContasReceberService:
    """Service para operações de Contas a Receber"""

    @staticmethod
    def buscar_contas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
        """
        Busca contas a receber com filtros de data
        Query completa com todos os JOINs necessários
        """

        # Query completa conforme script original
        query = """
        SELECT
            E301TCR.CODEMP,
            E301TCR.CODFIL,
            E301TCR.CODCLI,
            E085CLI.NOMCLI,
            E085CLI.CIDCLI,
            E085CLI.BAICLI,
            E085CLI.TIPCLI,
            E301TCR.DATEMI,
            E301TCR.NUMTIT,
            E301TCR.SITTIT,
            E301TCR.CODTPT,
            CAST(E301TCR.VLRABE AS DECIMAL(18,2)) AS VLRABE,
            CAST(E301TCR.VLRORI AS DECIMAL(18,2)) AS VLRORI,
            E001TNS.RECDEC,
            E301TCR.VCTPRO,
            E301TCR.VCTORI,
            E301TCR.PERMUL,
            E301TCR.TOLMUL,
            E301TCR.DATPPT,
            E002TPT.RECSOM,
            E070FIL.RECVJM,
            E070FIL.RECVMM,
            E070FIL.RECVDM,
            E301TCR.PERDSC,
            E301TCR.VLRDSC,
            E301TCR.TOLJRS,
            E301TCR.TIPJRS,
            E301TCR.PERJRS,
            E301TCR.JRSDIA,
            E301TCR.CODTNS,
            E001TNS.DESTNS,
            E301TCR.OBSTCR,
            E301TCR.CODREP,
            E301TCR.NUMCTR,
            E301TCR.CODSNF,
            E301TCR.NUMNFV,
            E301TCR.CODFPG,
            E085CLI.USU_UNICLI,
            CASE WHEN YEAR(E301TCR.ULTPGT) = 1900 THEN ''
                ELSE CONVERT(VARCHAR(10), E301TCR.ULTPGT, 103)
            END AS ULTPGT,
            ISNULL((SELECT TOP 1 E301RAT.CODCCU FROM E301RAT
                WHERE E301RAT.CODEMP = E301TCR.CODEMP
                    AND E301RAT.CODFIL = E301TCR.CODFIL
                    AND E301RAT.NUMTIT = E301TCR.NUMTIT
                    AND E301RAT.CODTPT = E301TCR.CODTPT
            ), 0) AS CODCCU,
            ISNULL((SELECT TOP 1 E301RAT.CTAFIN FROM E301RAT
                WHERE E301RAT.CODEMP = E301TCR.CODEMP
                    AND E301RAT.CODFIL = E301TCR.CODFIL
                    AND E301RAT.NUMTIT = E301TCR.NUMTIT
                    AND E301RAT.CODTPT = E301TCR.CODTPT
            ), 0) AS CTAFIN,
            DataAjustada.DATPPT_AJUSTADO
        FROM E301TCR
        INNER JOIN E085CLI ON E301TCR.CODCLI = E085CLI.CODCLI
        INNER JOIN E085HCL ON E085HCL.CODCLI = E301TCR.CODCLI
            AND E085HCL.CODEMP = E301TCR.CODEMP
            AND E085HCL.CODFIL = E301TCR.CODFIL
        INNER JOIN E039POR ON E301TCR.CODEMP = E039POR.CODEMP
            AND E301TCR.CODPOR = E039POR.CODPOR
        INNER JOIN E001TNS ON E301TCR.CODEMP = E001TNS.CODEMP
            AND E301TCR.CODTNS = E001TNS.CODTNS
        INNER JOIN E002TPT ON E301TCR.CODTPT = E002TPT.CODTPT
        INNER JOIN E070FIL ON E301TCR.CODEMP = E070FIL.CODEMP
            AND E301TCR.CODFIL = E070FIL.CODFIL
        INNER JOIN E070EMP ON E301TCR.CODEMP = E070EMP.CODEMP
        CROSS APPLY (
            -- Calcula data ajustada baseada em DATPPT
            SELECT
                CASE
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 6 THEN DATEADD(DAY, 3, E301TCR.DATPPT)  -- Sexta +3
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 7 THEN DATEADD(DAY, 3, E301TCR.DATPPT)  -- Sábado +3
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 1 THEN DATEADD(DAY, 2, E301TCR.DATPPT)  -- Domingo +2
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 2 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Segunda +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 3 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Terça +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 4 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Quarta +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 5 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Quinta +1
                    ELSE E301TCR.DATPPT
                END AS DATPPT_AJUSTADO
        ) AS DataAjustada
        WHERE E301TCR.CODEMP IN (10,20,30)
          AND E301TCR.SITTIT IN ('AB','LQ')
          AND E301TCR.VLRABE >= 0
          AND E001TNS.LISMOD = 'CRE'
          AND E301TCR.VCTORI >= '20250101'
        """

        # Adiciona filtro de data usando DATPPT_AJUSTADO (filtro do frontend)
        params = []
        if data_inicio and data_fim:
            query += " AND DataAjustada.DATPPT_AJUSTADO BETWEEN %s AND %s"
            params = (data_inicio, data_fim)
        elif data_inicio:
            query += " AND DataAjustada.DATPPT_AJUSTADO >= %s"
            params = (data_inicio,)

        query += " ORDER BY DataAjustada.DATPPT_AJUSTADO DESC"

        # Executa query
        results = db.execute_query(query, tuple(params) if params else None)

        # Processa resultados aplicando cálculos
        contas_processadas = []
        for row in results:
            valor_calculado = calcular_valor_receber(
                row['VLRABE'],
                row['RECDEC'],
                row['VLRORI']
            )

            conta = {
                'codemp': row['CODEMP'],
                'codfil': row['CODFIL'],
                'codcli': row['CODCLI'],
                'nomcli': row['NOMCLI'],
                'cidcli': row['CIDCLI'],
                'baicli': row['BAICLI'],
                'tipcli': row['TIPCLI'],
                'numtit': row['NUMTIT'],
                'sittit': row['SITTIT'],
                'codtpt': row['CODTPT'],
                'vlrabe': row['VLRABE'],
                'vlrori': row['VLRORI'],
                'recdec': row['RECDEC'],
                'vctpro': row['VCTPRO'],
                'vctori': row['VCTORI'],
                'datppt': row['DATPPT'],
                'datppt_ajustado': row['DATPPT_AJUSTADO'],  # Data ajustada calculada no SQL
                'datemi': row['DATEMI'],
                'destns': row['DESTNS'],
                'codccu': row['CODCCU'],
                'ctafin': row['CTAFIN'],
                'ultpgt': row['ULTPGT'],
                'valor_calculado': valor_calculado
            }
            contas_processadas.append(conta)

        return contas_processadas

    @staticmethod
    def calcular_total_receitas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> float:
        """Calcula o total de receitas no período - OTIMIZADO COM AJUSTE DE DATA"""

        # Query otimizada que calcula direto no SQL com data ajustada usando DATPPT
        query = """
        SELECT
            CAST(SUM(
                CASE
                    WHEN E301TCR.VLRABE != 0 AND E001TNS.RECDEC = 2 THEN -E301TCR.VLRABE
                    WHEN E301TCR.VLRABE = 0 AND E001TNS.RECDEC = 2 THEN -E301TCR.VLRORI
                    WHEN E301TCR.VLRABE != 0 AND E001TNS.RECDEC = 1 THEN E301TCR.VLRABE
                    ELSE E301TCR.VLRORI
                END
            ) AS DECIMAL(18,2)) AS total_receitas
        FROM E301TCR
        INNER JOIN E085CLI ON E301TCR.CODCLI = E085CLI.CODCLI
        INNER JOIN E085HCL ON E085HCL.CODCLI = E301TCR.CODCLI
            AND E085HCL.CODEMP = E301TCR.CODEMP
            AND E085HCL.CODFIL = E301TCR.CODFIL
        INNER JOIN E039POR ON E301TCR.CODEMP = E039POR.CODEMP
            AND E301TCR.CODPOR = E039POR.CODPOR
        INNER JOIN E001TNS ON E301TCR.CODEMP = E001TNS.CODEMP
            AND E301TCR.CODTNS = E001TNS.CODTNS
        INNER JOIN E002TPT ON E301TCR.CODTPT = E002TPT.CODTPT
        INNER JOIN E070FIL ON E301TCR.CODEMP = E070FIL.CODEMP
            AND E301TCR.CODFIL = E070FIL.CODFIL
        INNER JOIN E070EMP ON E301TCR.CODEMP = E070EMP.CODEMP
        CROSS APPLY (
            -- Calcula data ajustada baseada em DATPPT
            SELECT
                CASE
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 6 THEN DATEADD(DAY, 3, E301TCR.DATPPT)  -- Sexta +3
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 7 THEN DATEADD(DAY, 3, E301TCR.DATPPT)  -- Sábado +3
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 1 THEN DATEADD(DAY, 2, E301TCR.DATPPT)  -- Domingo +2
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 2 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Segunda +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 3 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Terça +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 4 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Quarta +1
                    WHEN DATEPART(WEEKDAY, E301TCR.DATPPT) = 5 THEN DATEADD(DAY, 1, E301TCR.DATPPT)  -- Quinta +1
                    ELSE E301TCR.DATPPT
                END AS DATPPT_AJUSTADO
        ) AS DataAjustada
        WHERE E301TCR.CODEMP IN (10,20,30)
          AND E301TCR.SITTIT IN ('AB','LQ')
          AND E301TCR.VLRABE >= 0
          AND E001TNS.LISMOD = 'CRE'
          AND E301TCR.VCTORI >= '20250101'
        """

        params = []
        if data_inicio and data_fim:
            query += " AND DataAjustada.DATPPT_AJUSTADO BETWEEN %s AND %s"
            params = (data_inicio, data_fim)
        elif data_inicio:
            query += " AND DataAjustada.DATPPT_AJUSTADO >= %s"
            params = (data_inicio,)

        results = db.execute_query(query, tuple(params) if params else None)

        total = results[0]['total_receitas'] if results and results[0]['total_receitas'] else 0
        return max(total, 0)  # Retorna apenas valores positivos

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

        return ContasReceberService.calcular_total_receitas(
            inicio_anterior.strftime('%Y-%m-%d'),
            fim_anterior.strftime('%Y-%m-%d')
        )
