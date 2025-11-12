"""
Service para consultas de Contas a Receber usando o banco LOCAL (sincronizado)
Substitui as consultas complexas ao banco Senior por consultas simples ao banco local
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from database import db
from utils.calculos import calcular_valor_receber


class ContasReceberLocalService:
    """Service para operações de Contas a Receber no banco LOCAL"""

    @staticmethod
    def buscar_contas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
        """
        Busca contas a receber da tabela local sincronizada
        Filtra pela DATA AJUSTADA (dias úteis) ao invés da data original
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CODEMP, CODFIL, CODCLI, NOMCLI, CIDCLI, BAICLI, TIPCLI,
                NUMTIT, SITTIT, CODTPT, VLRABE, VLRORI, RECDEC,
                VCTPRO, VCTORI, DATPPT, DATEMI, DESTNS, CODCCU,
                CTAFIN, ULTPGT,
                -- Calcula a data ajustada (move finais de semana para terça-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)  -- Sexta → +3 = Segunda
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)  -- Sábado → +3 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)  -- Domingo → +2 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)  -- Segunda → +1 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)  -- Terça → +1 = Quarta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)  -- Quarta → +1 = Quinta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)  -- Quinta → +1 = Sexta
                    ELSE DATPPT
                END as DATA_AJUSTADA
            FROM contas_receber
        )
        SELECT
            CODEMP, CODFIL, CODCLI, NOMCLI, CIDCLI, BAICLI, TIPCLI,
            NUMTIT, SITTIT, CODTPT, VLRABE, VLRORI, RECDEC,
            VCTPRO, VCTORI, DATPPT, DATEMI, DESTNS, CODCCU,
            CTAFIN, ULTPGT
        FROM contas_ajustadas
        WHERE 1=1
        """

        params = []

        # Filtro de data (usando DATA_AJUSTADA ao invés de DATPPT)
        if data_inicio and data_fim:
            query += " AND DATA_AJUSTADA BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        elif data_inicio:
            query += " AND DATA_AJUSTADA >= %s"
            params.append(data_inicio)

        query += " ORDER BY DATPPT DESC"

        results = db.execute_query(query, tuple(params) if params else None)

        # Processa resultados aplicando cálculos
        contas_processadas = []
        for row in results:
            valor_calculado = calcular_valor_receber(
                row.get('VLRABE', 0),
                row.get('RECDEC', 0),
                row.get('VLRORI', 0)
            )

            conta = {
                'codemp': row.get('CODEMP'),
                'codfil': row.get('CODFIL'),
                'codcli': row.get('CODCLI'),
                'nomcli': row.get('NOMCLI'),
                'cidcli': row.get('CIDCLI'),
                'baicli': row.get('BAICLI'),
                'tipcli': row.get('TIPCLI'),
                'numtit': row.get('NUMTIT'),
                'sittit': row.get('SITTIT'),
                'codtpt': row.get('CODTPT'),
                'vlrabe': row.get('VLRABE'),
                'vlrori': row.get('VLRORI'),
                'recdec': row.get('RECDEC'),
                'vctpro': row.get('VCTPRO'),
                'vctori': row.get('VCTORI'),
                'datppt': row.get('DATPPT'),
                'datemi': row.get('DATEMI'),
                'destns': row.get('DESTNS'),
                'codccu': row.get('CODCCU'),
                'ctafin': row.get('CTAFIN'),
                'ultpgt': row.get('ULTPGT'),
                'valor_calculado': valor_calculado
            }
            contas_processadas.append(conta)

        return contas_processadas

    @staticmethod
    def calcular_total_receitas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None, filiais: Optional[List[str]] = None) -> float:
        """
        Calcula o total de receitas no período usando a tabela local
        Filtra pela DATA AJUSTADA (dias úteis)
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                VLRABE,
                VLRORI,
                RECDEC,
                CODFIL,
                -- Calcula a data ajustada (move finais de semana para terça-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)  -- Sexta → +3 = Segunda
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)  -- Sábado → +3 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)  -- Domingo → +2 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)  -- Segunda → +1 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)  -- Terça → +1 = Quarta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)  -- Quarta → +1 = Quinta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)  -- Quinta → +1 = Sexta
                    ELSE DATPPT
                END as DATA_AJUSTADA
            FROM contas_receber
        )
        SELECT
            CAST(SUM(
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END
            ) AS DECIMAL(18,2)) AS total_receitas
        FROM contas_ajustadas
        WHERE 1=1
        """

        params = []

        if data_inicio and data_fim:
            query += " AND DATA_AJUSTADA BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        elif data_inicio:
            query += " AND DATA_AJUSTADA >= %s"
            params.append(data_inicio)

        if filiais:
            placeholders = ','.join(['%s'] * len(filiais))
            query += f" AND CODFIL IN ({placeholders})"
            params.extend(filiais)

        results = db.execute_query(query, tuple(params) if params else None)

        total = results[0]['total_receitas'] if results and results[0]['total_receitas'] else 0
        return max(total, 0)

    @staticmethod
    def calcular_total_periodo_anterior(data_inicio: str, data_fim: str, filiais: Optional[List[str]] = None) -> float:
        """Calcula total do período anterior para comparação"""
        # Converte strings para datas
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')

        # Calcula duração do período
        duracao = (fim - inicio).days

        # Calcula período anterior
        inicio_anterior = inicio - timedelta(days=duracao + 1)
        fim_anterior = inicio - timedelta(days=1)

        return ContasReceberLocalService.calcular_total_receitas(
            inicio_anterior.strftime('%Y-%m-%d'),
            fim_anterior.strftime('%Y-%m-%d'),
            filiais
        )

    @staticmethod
    def obter_dados_mensais(data_inicio: str, data_fim: str) -> List[dict]:
        """
        Obtém dados agrupados por mês para gráficos
        Filtra pela DATA AJUSTADA (dias úteis)
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                VLRABE,
                VLRORI,
                RECDEC,
                -- Calcula a data ajustada (move finais de semana para terça-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)  -- Sexta → +3 = Segunda
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)  -- Sábado → +3 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)  -- Domingo → +2 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)  -- Segunda → +1 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)  -- Terça → +1 = Quarta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)  -- Quarta → +1 = Quinta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)  -- Quinta → +1 = Sexta
                    ELSE DATPPT
                END as DATA_AJUSTADA
            FROM contas_receber
        )
        SELECT
            FORMAT(DATA_AJUSTADA, 'MMM', 'pt-BR') as mes,
            MONTH(DATA_AJUSTADA) as mes_numero,
            CAST(SUM(
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END
            ) AS DECIMAL(18,2)) AS total
        FROM contas_ajustadas
        WHERE DATA_AJUSTADA BETWEEN %s AND %s
        GROUP BY FORMAT(DATA_AJUSTADA, 'MMM', 'pt-BR'), MONTH(DATA_AJUSTADA)
        ORDER BY MONTH(DATA_AJUSTADA)
        """

        results = db.execute_query(query, (data_inicio, data_fim))
        return results if results else []

    @staticmethod
    def obter_dados_diarios(data_inicio: str, data_fim: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Obtém dados agrupados por dia para gráficos
        Aplica ajuste de dia da semana (move finais de semana para dias úteis)
        Filtra pela DATA AJUSTADA (dias úteis)
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                DATPPT,
                VLRABE,
                VLRORI,
                RECDEC,
                CODFIL,
                -- Calcula a data ajustada (move finais de semana para terça-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)  -- Sexta → +3 = Segunda
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)  -- Sábado → +3 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)  -- Domingo → +2 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)  -- Segunda → +1 = Terça
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)  -- Terça → +1 = Quarta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)  -- Quarta → +1 = Quinta
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)  -- Quinta → +1 = Sexta
                    ELSE DATPPT
                END as DATA_AJUSTADA
            FROM contas_receber
        )
        SELECT
            CONVERT(VARCHAR(10), DATA_AJUSTADA, 23) as data,
            CAST(SUM(
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END
            ) AS DECIMAL(18,2)) AS total
        FROM contas_ajustadas
        WHERE DATA_AJUSTADA BETWEEN %s AND %s
        """

        params = [data_inicio, data_fim]

        if filiais:
            placeholders = ','.join(['%s'] * len(filiais))
            query += f" AND CODFIL IN ({placeholders})"
            params.extend(filiais)

        query += """
        GROUP BY CONVERT(VARCHAR(10), DATA_AJUSTADA, 23)
        ORDER BY CONVERT(VARCHAR(10), DATA_AJUSTADA, 23)
        """

        results = db.execute_query(query, tuple(params))
        return results if results else []

    @staticmethod
    def obter_dados_diarios_projetados(data_inicio: str, data_fim: str) -> List[dict]:
        """
        Obtém dados agrupados por dia com projeção baseada em média dos últimos 3 meses
        Lógica:
        - Para cada CTAFIN, calcula média dos últimos 3 meses
        - Se valor do mês vigente > média: usa valor lançado
        - Se valor do mês vigente <= média OU = 0: usa média
        - Quando usa média sem data, replica a data do último lançamento do mês anterior
        """
        from datetime import datetime, timedelta, date

        # Converte strings para objetos date
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        # Calcula os 3 meses anteriores usando apenas datetime/timedelta
        # Mês anterior 1
        if inicio.month == 1:
            mes_anterior_1_inicio = date(inicio.year - 1, 12, 1)
            mes_anterior_1_fim = date(inicio.year - 1, 12, 31)
        else:
            mes_anterior_1_inicio = date(inicio.year, inicio.month - 1, 1)
            mes_anterior_1_fim = inicio - timedelta(days=1)

        # Mês anterior 2
        if mes_anterior_1_inicio.month == 1:
            mes_anterior_2_inicio = date(mes_anterior_1_inicio.year - 1, 12, 1)
            mes_anterior_2_fim = date(mes_anterior_1_inicio.year - 1, 12, 31)
        else:
            mes_anterior_2_inicio = date(mes_anterior_1_inicio.year, mes_anterior_1_inicio.month - 1, 1)
            mes_anterior_2_fim = mes_anterior_1_inicio - timedelta(days=1)

        # Mês anterior 3
        if mes_anterior_2_inicio.month == 1:
            mes_anterior_3_inicio = date(mes_anterior_2_inicio.year - 1, 12, 1)
            mes_anterior_3_fim = date(mes_anterior_2_inicio.year - 1, 12, 31)
        else:
            mes_anterior_3_inicio = date(mes_anterior_2_inicio.year, mes_anterior_2_inicio.month - 1, 1)
            mes_anterior_3_fim = mes_anterior_2_inicio - timedelta(days=1)

        # Query para buscar dados dos últimos 3 meses + mês vigente, agrupados por CTAFIN
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CTAFIN,
                VLRABE,
                VLRORI,
                RECDEC,
                DATPPT,
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)
                    ELSE DATPPT
                END as DATA_AJUSTADA,
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END as VALOR_CALCULADO
            FROM contas_receber
        ),
        -- Dados do mês anterior 1
        mes_ant_1 AS (
            SELECT
                CTAFIN,
                SUM(VALOR_CALCULADO) as total_mes,
                MAX(DATA_AJUSTADA) as ultima_data
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        -- Dados do mês anterior 2
        mes_ant_2 AS (
            SELECT
                CTAFIN,
                SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        -- Dados do mês anterior 3
        mes_ant_3 AS (
            SELECT
                CTAFIN,
                SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        -- Calcula média dos 3 meses
        medias AS (
            SELECT
                COALESCE(m1.CTAFIN, m2.CTAFIN, m3.CTAFIN) as CTAFIN,
                (COALESCE(m1.total_mes, 0) + COALESCE(m2.total_mes, 0) + COALESCE(m3.total_mes, 0)) / 3.0 as media,
                m1.ultima_data
            FROM mes_ant_1 m1
            FULL OUTER JOIN mes_ant_2 m2 ON m1.CTAFIN = m2.CTAFIN
            FULL OUTER JOIN mes_ant_3 m3 ON COALESCE(m1.CTAFIN, m2.CTAFIN) = m3.CTAFIN
        ),
        -- Dados do mês vigente
        mes_vigente AS (
            SELECT
                CTAFIN,
                DATA_AJUSTADA,
                SUM(VALOR_CALCULADO) as total_dia
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN, DATA_AJUSTADA
        ),
        -- Aplica regra de projeção
        projecao AS (
            SELECT
                mv.CTAFIN,
                mv.DATA_AJUSTADA,
                mv.total_dia,
                m.media,
                m.ultima_data,
                CASE
                    -- Se valor lançado > média, usa valor lançado
                    WHEN mv.total_dia > m.media THEN mv.DATA_AJUSTADA
                    -- Se não, usa a data do último lançamento do mês anterior
                    ELSE m.ultima_data
                END as data_final,
                CASE
                    -- Se valor lançado > média, usa valor lançado
                    WHEN mv.total_dia > m.media THEN mv.total_dia
                    -- Se não, usa a média
                    ELSE m.media
                END as valor_final
            FROM mes_vigente mv
            LEFT JOIN medias m ON mv.CTAFIN = m.CTAFIN

            UNION ALL

            -- Adiciona CTAFINs que não têm lançamento no mês vigente (valor = 0)
            -- mas têm média dos meses anteriores
            SELECT
                m.CTAFIN,
                NULL as DATA_AJUSTADA,
                0 as total_dia,
                m.media,
                m.ultima_data,
                m.ultima_data as data_final,
                m.media as valor_final
            FROM medias m
            WHERE m.CTAFIN NOT IN (SELECT CTAFIN FROM mes_vigente)
            AND m.media > 0
        )
        SELECT
            CONVERT(VARCHAR(10), data_final, 23) as data,
            CAST(SUM(valor_final) AS DECIMAL(18,2)) AS total
        FROM projecao
        WHERE data_final IS NOT NULL
        AND data_final BETWEEN %s AND %s
        GROUP BY CONVERT(VARCHAR(10), data_final, 23)
        ORDER BY CONVERT(VARCHAR(10), data_final, 23)
        """

        results = db.execute_query(query, (
            mes_anterior_1_inicio.strftime('%Y-%m-%d'), mes_anterior_1_fim.strftime('%Y-%m-%d'),
            mes_anterior_2_inicio.strftime('%Y-%m-%d'), mes_anterior_2_fim.strftime('%Y-%m-%d'),
            mes_anterior_3_inicio.strftime('%Y-%m-%d'), mes_anterior_3_fim.strftime('%Y-%m-%d'),
            data_inicio, data_fim,
            data_inicio, data_fim
        ))
        return results if results else []

    @staticmethod
    def obter_top_receitas(data_inicio: str, data_fim: str, limit: int = 10, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Obtém as maiores receitas por conta reduzida (CTAFIN) no período
        usando a tabela plano_financeiro para categorização
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                cr.CTAFIN,
                cr.VLRABE,
                cr.VLRORI,
                cr.RECDEC,
                cr.CODFIL,
                -- Calcula a data ajustada (move finais de semana para dias úteis)
                CASE
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 6 THEN DATEADD(DAY, 3, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 7 THEN DATEADD(DAY, 3, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 1 THEN DATEADD(DAY, 2, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 2 THEN DATEADD(DAY, 1, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 3 THEN DATEADD(DAY, 1, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 4 THEN DATEADD(DAY, 1, cr.DATPPT)
                    WHEN DATEPART(WEEKDAY, cr.DATPPT) = 5 THEN DATEADD(DAY, 1, cr.DATPPT)
                    ELSE cr.DATPPT
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra de receita/despesa
                CASE
                    WHEN cr.VLRABE != 0 AND cr.RECDEC = 2 THEN -cr.VLRABE
                    WHEN cr.VLRABE = 0 AND cr.RECDEC = 2 THEN -cr.VLRORI
                    WHEN cr.VLRABE != 0 AND cr.RECDEC = 1 THEN cr.VLRABE
                    ELSE cr.VLRORI
                END as VALOR_CALCULADO
            FROM contas_receber cr
        )
        SELECT TOP %s
            -- Formata CTARED com 4 dígitos + concatena com DESCTA
            RIGHT('0000' + CAST(ca.CTAFIN AS VARCHAR), 4) + ' - ' + pf.DESCTA as nome,
            CAST(SUM(ca.VALOR_CALCULADO) AS DECIMAL(18,2)) AS total,
            pf.NIVCTA as nivel,
            -- Cria coluna RECDEP
            CASE
                WHEN pf.NATCTA = 'C' THEN 'RECEITA'
                WHEN pf.NATCTA = 'D' THEN 'DESPESA'
                ELSE NULL
            END as recdep
        FROM contas_ajustadas ca
        INNER JOIN plano_financeiro pf ON ca.CTAFIN = CAST(pf.CTARED AS INT)
        WHERE ca.DATA_AJUSTADA BETWEEN %s AND %s
        """

        params = [limit, data_inicio, data_fim]

        if filiais:
            placeholders = ','.join(['%s'] * len(filiais))
            query += f" AND ca.CODFIL IN ({placeholders})"
            params.extend(filiais)

        query += """
        AND pf.NATCTA = 'C'  -- Apenas receitas
        AND pf.NIVCTA = 6  -- Apenas nível 6
        GROUP BY ca.CTAFIN, pf.DESCTA, pf.NIVCTA, pf.NATCTA
        ORDER BY total DESC
        """

        results = db.execute_query(query, tuple(params))
        return results if results else []

    @staticmethod
    def obter_top_clientes(data_inicio: str, data_fim: str, limit: int = 10) -> List[dict]:
        """
        Obtém os maiores clientes por valor de receita no período
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CODCLI,
                NOMCLI,
                VLRABE,
                VLRORI,
                RECDEC,
                -- Calcula a data ajustada
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)
                    ELSE DATPPT
                END as DATA_AJUSTADA,
                -- Calcula o valor
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END as VALOR_CALCULADO
            FROM contas_receber
        )
        SELECT TOP %s
            NOMCLI as nome,
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total
        FROM contas_ajustadas
        WHERE DATA_AJUSTADA BETWEEN %s AND %s
        GROUP BY CODCLI, NOMCLI
        ORDER BY total DESC
        """

        results = db.execute_query(query, (limit, data_inicio, data_fim))
        return results if results else []
