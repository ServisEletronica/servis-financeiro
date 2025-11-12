"""
Service para consultas de Contas a Pagar usando o banco LOCAL (sincronizado)
Substitui as consultas complexas ao banco Senior por consultas simples ao banco local
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from database import db


class ContasPagarLocalService:
    """Service para operações de Contas a Pagar no banco LOCAL"""

    @staticmethod
    def buscar_contas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
        """
        Busca contas a pagar da tabela local sincronizada
        Filtra pela DATA AJUSTADA (dias úteis) ao invés da data original
        Aplica os mesmos filtros do BI
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CODEMP, CODFIL, NUMTIT, CODFOR, NOMFOR, SEQMOV,
                CODTNS, DATMOV, CODFPG, CODTPT, SITTIT, OBSTCP,
                VLRORI, DATEMI, ULTPGT, VCTPRO, VLRRAT, CTAFIN,
                CODCCU, CTARED, VLRABE,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)  -- Sábado → +2 = Segunda
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)  -- Domingo → +1 = Segunda
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'  -- Exclui cancelados
            AND SEQMOV = 1  -- Apenas sequência 1
            AND VLRABE >= 0  -- Valor em aberto >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)  -- Exclui contas específicas
        )
        SELECT
            CODEMP, CODFIL, NUMTIT, CODFOR, NOMFOR, SEQMOV,
            CODTNS, DATMOV, CODFPG, CODTPT, SITTIT, OBSTCP,
            VLRORI, DATEMI, ULTPGT, VCTPRO, VLRRAT, CTAFIN,
            CODCCU, CTARED, VLRABE, VALOR_CALCULADO
        FROM contas_ajustadas
        WHERE 1=1
        """

        params = []

        # Filtro de data (usando DATA_AJUSTADA ao invés de VCTPRO)
        if data_inicio and data_fim:
            query += " AND DATA_AJUSTADA BETWEEN %s AND %s"
            params.extend([data_inicio, data_fim])
        elif data_inicio:
            query += " AND DATA_AJUSTADA >= %s"
            params.append(data_inicio)

        query += " ORDER BY VCTPRO DESC"

        results = db.execute_query(query, tuple(params) if params else None)

        # Processa resultados
        contas_processadas = []
        for row in results:
            conta = {
                'codemp': row.get('CODEMP'),
                'codfil': row.get('CODFIL'),
                'numtit': row.get('NUMTIT'),
                'codfor': row.get('CODFOR'),
                'nomfor': row.get('NOMFOR'),
                'seqmov': row.get('SEQMOV'),
                'codtns': row.get('CODTNS'),
                'sittit': row.get('SITTIT'),
                'vlrori': row.get('VLRORI'),
                'vlrabe': row.get('VLRABE'),
                'vlrrat': row.get('VLRRAT'),
                'vctpro': row.get('VCTPRO'),
                'datemi': row.get('DATEMI'),
                'ctafin': row.get('CTAFIN'),
                'codccu': row.get('CODCCU'),
                'valor_calculado': row.get('VALOR_CALCULADO', 0)  # Usa VALOR_CALCULADO conforme regra do BI
            }
            contas_processadas.append(conta)

        return contas_processadas

    @staticmethod
    def calcular_total_despesas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None, filiais: Optional[List[str]] = None) -> float:
        """
        Calcula o total de despesas no período usando a tabela local
        Filtra pela DATA AJUSTADA (dias úteis) e usa os mesmos filtros do BI
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                VLRABE,
                VLRRAT,
                CODFIL,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)  -- Sábado → +2 = Segunda
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)  -- Domingo → +1 = Segunda
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'  -- Exclui cancelados
            AND SEQMOV = 1  -- Apenas sequência 1
            AND VLRABE >= 0  -- Valor em aberto >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)  -- Exclui contas específicas
        )
        SELECT
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total_despesas
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

        total = results[0]['total_despesas'] if results and results[0]['total_despesas'] else 0
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

        return ContasPagarLocalService.calcular_total_despesas(
            inicio_anterior.strftime('%Y-%m-%d'),
            fim_anterior.strftime('%Y-%m-%d'),
            filiais
        )

    @staticmethod
    def obter_dados_mensais(data_inicio: str, data_fim: str) -> List[dict]:
        """
        Obtém dados agrupados por mês para gráficos
        Filtra pela DATA AJUSTADA (dias úteis) e usa os mesmos filtros do BI
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                VLRABE,
                VLRRAT,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)  -- Sábado → +2 = Segunda
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)  -- Domingo → +1 = Segunda
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'  -- Exclui cancelados
            AND SEQMOV = 1  -- Apenas sequência 1
            AND VLRABE >= 0  -- Valor em aberto >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)  -- Exclui contas específicas
        )
        SELECT
            FORMAT(DATA_AJUSTADA, 'MMM', 'pt-BR') as mes,
            MONTH(DATA_AJUSTADA) as mes_numero,
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total
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
        Aplica ajuste de dia da semana (move finais de semana para segunda-feira)
        Filtra pela DATA AJUSTADA (dias úteis) e usa os mesmos filtros do BI
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                VCTPRO,
                VLRABE,
                VLRRAT,
                CODFIL,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)  -- Sábado → +2 = Segunda
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)  -- Domingo → +1 = Segunda
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'  -- Exclui cancelados
            AND SEQMOV = 1  -- Apenas sequência 1
            AND VLRABE >= 0  -- Valor em aberto >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)  -- Exclui contas específicas
        )
        SELECT
            CONVERT(VARCHAR(10), DATA_AJUSTADA, 23) as data,
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total
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
    def obter_dados_diarios_projetados(data_inicio: str, data_fim: str, filiais: Optional[List[str]] = None) -> List[dict]:
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

        # Prepara filtro de filiais se fornecido
        filtro_filiais = ""
        if filiais:
            placeholders = ','.join(['%s'] * len(filiais))
            filtro_filiais = f" AND CODFIL IN ({placeholders})"

        # Query para buscar dados dos últimos 3 meses + mês vigente, agrupados por CTAFIN
        query = f"""
        WITH contas_ajustadas AS (
            SELECT
                CTAFIN,
                VLRABE,
                VLRRAT,
                VCTPRO,
                CODFIL,
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'
            AND SEQMOV = 1
            AND VLRABE >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)
            {filtro_filiais}
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

        # Monta os parâmetros na ordem correta
        # Primeiro, se houver filiais (usadas na CTE contas_ajustadas)
        params = []
        if filiais:
            params.extend(filiais)

        # Depois os parâmetros de data na ordem que aparecem na query
        params.extend([
            mes_anterior_1_inicio.strftime('%Y-%m-%d'), mes_anterior_1_fim.strftime('%Y-%m-%d'),
            mes_anterior_2_inicio.strftime('%Y-%m-%d'), mes_anterior_2_fim.strftime('%Y-%m-%d'),
            mes_anterior_3_inicio.strftime('%Y-%m-%d'), mes_anterior_3_fim.strftime('%Y-%m-%d'),
            data_inicio, data_fim,
            data_inicio, data_fim
        ])

        results = db.execute_query(query, tuple(params))
        return results if results else []

    @staticmethod
    def calcular_total_despesas_projetado(data_inicio: str, data_fim: str, filiais: Optional[List[str]] = None) -> float:
        """
        Calcula o total de despesas com projeção baseada em média dos últimos 3 meses por CTAFIN
        Usa a mesma lógica do obter_dados_diarios_projetados mas retorna apenas o total
        """
        from datetime import datetime, timedelta, date

        # Converte strings para objetos date
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        # Calcula os 3 meses anteriores
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

        # Prepara filtro de filiais
        filtro_filiais = ""
        if filiais:
            placeholders = ','.join(['%s'] * len(filiais))
            filtro_filiais = f" AND CODFIL IN ({placeholders})"

        # Query simplificada que retorna apenas o total
        query = f"""
        WITH contas_ajustadas AS (
            SELECT
                CTAFIN,
                VLRABE,
                VLRRAT,
                VCTPRO,
                CODFIL,
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'
            AND SEQMOV = 1
            AND VLRABE >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)
            {filtro_filiais}
        ),
        -- Dados dos 3 meses anteriores
        mes_ant_1 AS (
            SELECT CTAFIN, SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        mes_ant_2 AS (
            SELECT CTAFIN, SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        mes_ant_3 AS (
            SELECT CTAFIN, SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        -- Calcula média dos 3 meses por CTAFIN
        medias AS (
            SELECT
                COALESCE(m1.CTAFIN, m2.CTAFIN, m3.CTAFIN) as CTAFIN,
                (COALESCE(m1.total_mes, 0) + COALESCE(m2.total_mes, 0) + COALESCE(m3.total_mes, 0)) / 3.0 as media
            FROM mes_ant_1 m1
            FULL OUTER JOIN mes_ant_2 m2 ON m1.CTAFIN = m2.CTAFIN
            FULL OUTER JOIN mes_ant_3 m3 ON COALESCE(m1.CTAFIN, m2.CTAFIN) = m3.CTAFIN
        ),
        -- Total do mês vigente por CTAFIN
        mes_vigente AS (
            SELECT
                CTAFIN,
                SUM(VALOR_CALCULADO) as total_mes
            FROM contas_ajustadas
            WHERE DATA_AJUSTADA BETWEEN %s AND %s
            GROUP BY CTAFIN
        ),
        -- Aplica regra: se valor lançado > média usa lançado, senão usa média
        projecao AS (
            SELECT
                COALESCE(mv.CTAFIN, m.CTAFIN) as CTAFIN,
                CASE
                    WHEN COALESCE(mv.total_mes, 0) > COALESCE(m.media, 0) THEN COALESCE(mv.total_mes, 0)
                    ELSE COALESCE(m.media, 0)
                END as valor_final
            FROM mes_vigente mv
            FULL OUTER JOIN medias m ON mv.CTAFIN = m.CTAFIN
            WHERE COALESCE(mv.total_mes, 0) > 0 OR COALESCE(m.media, 0) > 0
        )
        SELECT CAST(SUM(valor_final) AS DECIMAL(18,2)) as total_projetado
        FROM projecao
        """

        # Monta os parâmetros
        params = []
        if filiais:
            params.extend(filiais)

        params.extend([
            mes_anterior_1_inicio.strftime('%Y-%m-%d'), mes_anterior_1_fim.strftime('%Y-%m-%d'),
            mes_anterior_2_inicio.strftime('%Y-%m-%d'), mes_anterior_2_fim.strftime('%Y-%m-%d'),
            mes_anterior_3_inicio.strftime('%Y-%m-%d'), mes_anterior_3_fim.strftime('%Y-%m-%d'),
            data_inicio, data_fim
        ])

        results = db.execute_query(query, tuple(params))
        total = results[0]['total_projetado'] if results and results[0]['total_projetado'] else 0
        return max(total, 0)

    @staticmethod
    def obter_top_despesas(data_inicio: str, data_fim: str, limit: int = 10, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Obtém as maiores despesas por conta reduzida (CTARED) no período
        usando a tabela plano_financeiro para categorização
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                cp.CTAFIN,
                cp.VLRABE,
                cp.VLRRAT,
                cp.CODFIL,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, cp.VCTPRO) = 7 THEN DATEADD(DAY, 2, cp.VCTPRO)
                    WHEN DATEPART(WEEKDAY, cp.VCTPRO) = 1 THEN DATEADD(DAY, 1, cp.VCTPRO)
                    ELSE cp.VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN cp.VLRABE > cp.VLRRAT THEN cp.VLRRAT
                    WHEN cp.VLRABE = 0 THEN cp.VLRRAT
                    ELSE cp.VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar cp
            WHERE cp.SITTIT <> 'CA'  -- Exclui cancelados
            AND cp.SEQMOV = 1  -- Apenas sequência 1
            AND cp.VLRABE >= 0  -- Valor em aberto >= 0
            AND cp.CTAFIN NOT IN (407,408,409,410,411,412,501)  -- Exclui contas específicas
        )
        SELECT TOP %s
            -- Formata CTAFIN com 4 dígitos + concatena com DESCTA
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
        AND pf.NATCTA = 'D'  -- Apenas despesas
        AND pf.NIVCTA = 6  -- Apenas nível 6
        GROUP BY ca.CTAFIN, pf.DESCTA, pf.NIVCTA, pf.NATCTA
        ORDER BY total DESC
        """

        results = db.execute_query(query, tuple(params))
        return results if results else []

    @staticmethod
    def obter_top_fornecedores(data_inicio: str, data_fim: str, limit: int = 10) -> List[dict]:
        """
        Obtém os maiores fornecedores por valor de despesa no período
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CODFOR,
                NOMFOR,
                VLRABE,
                VLRRAT,
                -- Calcula a data ajustada (move finais de semana para segunda-feira)
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'
            AND SEQMOV = 1
            AND VLRABE >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)
        )
        SELECT TOP %s
            NOMFOR as nome,
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total
        FROM contas_ajustadas
        WHERE DATA_AJUSTADA BETWEEN %s AND %s
        GROUP BY CODFOR, NOMFOR
        ORDER BY total DESC
        """

        results = db.execute_query(query, (limit, data_inicio, data_fim))
        return results if results else []

    @staticmethod
    def obter_despesas_por_centro_custo(data_inicio: str, data_fim: str) -> List[dict]:
        """
        Obtém despesas agrupadas por centro de custo
        """
        query = """
        WITH contas_ajustadas AS (
            SELECT
                CODCCU,
                VLRABE,
                VLRRAT,
                -- Calcula a data ajustada
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 2, VCTPRO)
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 1 THEN DATEADD(DAY, 1, VCTPRO)
                    ELSE VCTPRO
                END as DATA_AJUSTADA,
                -- Calcula o valor conforme regra do BI
                CASE
                    WHEN VLRABE > VLRRAT THEN VLRRAT
                    WHEN VLRABE = 0 THEN VLRRAT
                    ELSE VLRABE
                END as VALOR_CALCULADO
            FROM contas_pagar
            WHERE SITTIT <> 'CA'
            AND SEQMOV = 1
            AND VLRABE >= 0
            AND CTAFIN NOT IN (407,408,409,410,411,412,501)
        )
        SELECT
            COALESCE(CAST(CODCCU AS VARCHAR), 'Sem Centro de Custo') as centro_custo,
            CAST(SUM(VALOR_CALCULADO) AS DECIMAL(18,2)) AS total
        FROM contas_ajustadas
        WHERE DATA_AJUSTADA BETWEEN %s AND %s
        GROUP BY CODCCU
        ORDER BY total DESC
        """

        results = db.execute_query(query, (data_inicio, data_fim))
        return results if results else []
