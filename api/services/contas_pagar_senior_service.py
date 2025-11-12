from database import senior_db
from datetime import datetime, timedelta
from typing import Optional, List
import calendar
from dateutil.relativedelta import relativedelta


class ContasPagarSeniorService:
    """Serviço para buscar dados de Contas a Pagar diretamente do Senior"""

    @staticmethod
    def ajustar_dia_semana(data: datetime) -> datetime:
        """
        Ajusta a data conforme o dia da semana:
        - Sábado (5) -> +2 dias (Segunda)
        - Domingo (6) -> +1 dia (Segunda)
        - Outros dias -> mantém
        """
        dia_semana = data.weekday()  # 0=Segunda, 6=Domingo

        if dia_semana == 5:  # Sábado
            return data + timedelta(days=2)
        elif dia_semana == 6:  # Domingo
            return data + timedelta(days=1)

        return data

    @staticmethod
    def calcular_valor_cp(vlrabe: float, vlrrat: float) -> float:
        """
        Calcula o valor da conta a pagar:
        - Se VLRABE > VLRRAT então VALOR_CP = VLRRAT
        - Senão Se VLRABE = 0 então VALOR_CP = VLRRAT
        - Senão VALOR_CP = VLRABE
        """
        if vlrabe > vlrrat:
            return vlrrat
        elif vlrabe == 0:
            return vlrrat
        else:
            return vlrabe

    @staticmethod
    def obter_periodo_4_meses(periodo: str) -> tuple:
        """
        Retorna data_inicio e data_fim para buscar 4 meses (vigente + 3 anteriores)
        Considera até dia 28 do mês vigente para evitar que ajustes caiam no mês seguinte
        """
        ano, mes = map(int, periodo.split('-'))

        # Mês vigente - até dia 28
        data_fim = datetime(ano, mes, 28)

        # 3 meses atrás
        data_inicio = datetime(ano, mes, 1) - relativedelta(months=3)

        return data_inicio, data_fim

    @staticmethod
    def obter_contas_pagar_do_senior(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Busca contas a pagar do Senior para o período especificado (4 meses)
        """
        try:
            # Obtém período de 4 meses (vigente + 3 anteriores)
            data_inicio, data_fim = ContasPagarSeniorService.obter_periodo_4_meses(periodo)

            # Formata datas para SQL
            data_inicio_str = data_inicio.strftime('%Y%m%d')
            data_fim_str = data_fim.strftime('%Y%m%d')

            # Monta filtro de filiais
            filiais_filter = ""
            if filiais and len(filiais) > 0:
                filiais_str = ','.join([f"'{f.strip()}'" for f in filiais])
                filiais_filter = f"AND E501MCP.CODFIL IN ({filiais_str})"
            else:
                # Se não especificou filiais, usa as padrão (todas exceto 2002)
                filiais_filter = "AND E501MCP.CODFIL IN ('1001','1002','1003','3001','3002','3003')"

            # Query SQL
            query = f"""
            SELECT DISTINCT E501MCP.CODEMP,E501MCP.CODFIL,E501MCP.NUMTIT,E501MCP.CODFOR
            ,E095FOR.NOMFOR,E501MCP.SEQMOV,E501MCP.CODTNS,E501MCP.DATMOV,E501MCP.CODFPG
            ,E501TCP.CODTPT,E501TCP.SITTIT,E501TCP.OBSTCP,E501TCP.VLRORI,E501TCP.DATEMI,E501TCP.ULTPGT
            ,E501MCP.VCTPRO,E501RAT.VLRRAT,E501RAT.CTAFIN,E501RAT.CODCCU,E501RAT.CTARED,E501TCP.VLRABE
            FROM E501MCP,E501TCP,E001TNS,E002TPT,E095FOR,E501RAT
            WHERE E501MCP.CODEMP IN (10,20,30)
            AND E501MCP.CODEMP = E501TCP.CODEMP
            AND E501MCP.CODFIL = E501TCP.CODFIL
            AND E501MCP.NUMTIT = E501TCP.NUMTIT
            AND E501MCP.CODTPT = E501TCP.CODTPT
            AND E501MCP.CODFOR = E501TCP.CODFOR
            AND E501TCP.CODEMP = E001TNS.CODEMP
            AND E501TCP.CODTNS = E001TNS.CODTNS
            AND E501MCP.CODTPT = E002TPT.CODTPT
            AND E501MCP.CODFOR = E095FOR.CODFOR
            AND E501MCP.CODEMP = E501RAT.CODEMP
            AND E501MCP.CODFIL = E501RAT.CODFIL
            AND E501MCP.CODFOR = E501RAT.CODFOR
            AND E501MCP.NUMTIT = E501RAT.NUMTIT
            AND E501MCP.SEQMOV = E501RAT.SEQMOV
            AND E501MCP.CODTPT = E501RAT.CODTPT
            AND E501TCP.SITTIT <> 'CA'
            AND E501MCP.SEQMOV = 1
            AND E501TCP.VLRABE >= 0
            AND E001TNS.LISMOD = 'CPE'
            AND E501RAT.CTAFIN NOT IN (407,408,409,410,411,412,501)
            AND E501MCP.VCTPRO >= '{data_inicio_str}'
            AND E501MCP.VCTPRO <= '{data_fim_str}'
            {filiais_filter}
            """

            # Executa query
            resultados = senior_db.execute_query(query)

            # Processa resultados e aplica ajustes
            registros_processados = []
            for registro in resultados:
                # Ajusta data com base no dia da semana
                vctpro = registro.get('VCTPRO')
                if vctpro:
                    data_ajustada = ContasPagarSeniorService.ajustar_dia_semana(vctpro)
                    registro['DATA_AJUSTADA'] = data_ajustada
                    registro['DATA_AJUSTADA_STR'] = data_ajustada.strftime('%Y-%m-%d')
                else:
                    registro['DATA_AJUSTADA'] = None
                    registro['DATA_AJUSTADA_STR'] = None

                # Calcula valor CP
                vlrabe = registro.get('VLRABE', 0) or 0
                vlrrat = registro.get('VLRRAT', 0) or 0

                valor_cp = ContasPagarSeniorService.calcular_valor_cp(vlrabe, vlrrat)
                registro['VALOR_CP'] = valor_cp

                registros_processados.append(registro)

            return registros_processados

        except Exception as e:
            print(f"Erro ao buscar contas a pagar do Senior: {str(e)}")
            raise Exception(f"Erro ao buscar contas a pagar do Senior: {str(e)}")

    @staticmethod
    def aplicar_projecao_media(registros: List[dict], periodo_vigente: str) -> List[dict]:
        """
        Aplica lógica de projeção com média dos últimos 3 meses
        IMPORTANTE: SEMPRE mantém os registros dos 3 meses anteriores intactos
        Para o mês vigente:
        - Se valor do mês vigente > média: usa valor lançado
        - Se valor do mês vigente <= média ou = 0: adiciona registro projetado com a média
        """
        ano_vigente, mes_vigente = map(int, periodo_vigente.split('-'))

        # Calcula meses anteriores
        mes1_anterior = (datetime(ano_vigente, mes_vigente, 1) - relativedelta(months=1)).strftime('%Y-%m')
        mes2_anterior = (datetime(ano_vigente, mes_vigente, 1) - relativedelta(months=2)).strftime('%Y-%m')
        mes3_anterior = (datetime(ano_vigente, mes_vigente, 1) - relativedelta(months=3)).strftime('%Y-%m')

        # Separa registros por mês
        registros_mes_anterior_1 = [r for r in registros if r.get('DATA_AJUSTADA') and r['DATA_AJUSTADA'].strftime('%Y-%m') == mes1_anterior]
        registros_mes_anterior_2 = [r for r in registros if r.get('DATA_AJUSTADA') and r['DATA_AJUSTADA'].strftime('%Y-%m') == mes2_anterior]
        registros_mes_anterior_3 = [r for r in registros if r.get('DATA_AJUSTADA') and r['DATA_AJUSTADA'].strftime('%Y-%m') == mes3_anterior]
        registros_vigente = [r for r in registros if r.get('DATA_AJUSTADA') and r['DATA_AJUSTADA'].strftime('%Y-%m') == periodo_vigente]

        # Agrupa registros do mês vigente por CTAFIN
        vigente_por_ctafin = {}
        for reg in registros_vigente:
            ctafin = reg.get('CTAFIN')
            if ctafin not in vigente_por_ctafin:
                vigente_por_ctafin[ctafin] = []
            vigente_por_ctafin[ctafin].append(reg)

        # Agrupa registros dos 3 meses anteriores por CTAFIN
        anterior_por_ctafin = {}
        for reg in registros_mes_anterior_1 + registros_mes_anterior_2 + registros_mes_anterior_3:
            ctafin = reg.get('CTAFIN')
            if ctafin not in anterior_por_ctafin:
                anterior_por_ctafin[ctafin] = {
                    'mes1': [],
                    'mes2': [],
                    'mes3': []
                }

            ano_mes = reg['DATA_AJUSTADA'].strftime('%Y-%m')
            if ano_mes == mes1_anterior:
                anterior_por_ctafin[ctafin]['mes1'].append(reg)
            elif ano_mes == mes2_anterior:
                anterior_por_ctafin[ctafin]['mes2'].append(reg)
            elif ano_mes == mes3_anterior:
                anterior_por_ctafin[ctafin]['mes3'].append(reg)

        # SEMPRE inclui TODOS os registros dos 3 meses anteriores
        registros_finais = registros_mes_anterior_1 + registros_mes_anterior_2 + registros_mes_anterior_3

        # Para o mês vigente, aplica a lógica de projeção POR CTAFIN
        ctafins_processados = set()

        for ctafin in set(list(vigente_por_ctafin.keys()) + list(anterior_por_ctafin.keys())):
            regs_vigente = vigente_por_ctafin.get(ctafin, [])
            total_vigente = sum(float(r['VALOR_CP']) for r in regs_vigente)

            # Calcula média dos 3 meses anteriores para este CTAFIN
            anterior = anterior_por_ctafin.get(ctafin, {'mes1': [], 'mes2': [], 'mes3': []})
            total_mes1 = sum(float(r['VALOR_CP']) for r in anterior['mes1'])
            total_mes2 = sum(float(r['VALOR_CP']) for r in anterior['mes2'])
            total_mes3 = sum(float(r['VALOR_CP']) for r in anterior['mes3'])
            media = (total_mes1 + total_mes2 + total_mes3) / 3.0

            if total_vigente > media:
                # Usa registros lançados
                registros_finais.extend(regs_vigente)
            elif media > 0:
                # Usa média - cria registro projetado
                # Pega última data do mês anterior para este CTAFIN
                if anterior['mes1']:
                    ultimo_reg = max(anterior['mes1'], key=lambda x: x.get('DATA_AJUSTADA', datetime.min))

                    reg_projetado = ultimo_reg.copy()
                    reg_projetado['VALOR_CP'] = media

                    # Ajusta data para mês vigente
                    data_anterior = ultimo_reg.get('DATA_AJUSTADA')
                    if data_anterior:
                        dia = data_anterior.day
                        try:
                            nova_data = datetime(ano_vigente, mes_vigente, dia)
                        except ValueError:
                            ultimo_dia = calendar.monthrange(ano_vigente, mes_vigente)[1]
                            nova_data = datetime(ano_vigente, mes_vigente, ultimo_dia)

                        reg_projetado['DATA_AJUSTADA'] = nova_data
                        reg_projetado['DATA_AJUSTADA_STR'] = nova_data.strftime('%Y-%m-%d')
                        reg_projetado['VCTPRO'] = nova_data

                    registros_finais.append(reg_projetado)
                elif regs_vigente:
                    # Se não tem histórico mas tem vigente, usa vigente
                    registros_finais.extend(regs_vigente)
            elif regs_vigente:
                # Se média é 0 mas tem registros vigentes, usa vigente
                registros_finais.extend(regs_vigente)

            ctafins_processados.add(ctafin)

        return registros_finais

    @staticmethod
    def obter_resumo_por_dia_liquidado(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Retorna resumo de contas a pagar LIQUIDADAS agrupado por dia
        Filtra apenas títulos com SITTIT = 'LQ'
        Usa ULTPGT (data de último pagamento) DIRETA, sem ajustes
        Filtra apenas dias úteis do mês solicitado
        """
        try:
            # Busca contas liquidadas do Senior
            contas = ContasPagarSeniorService.obter_contas_pagar_liquidadas_do_senior(periodo, filiais)

            # Agrupa por ULTPGT (SEM ajustes)
            resumo_por_dia = {}
            for conta in contas:
                data_str = conta.get('ULTPGT_STR')
                if not data_str:
                    continue

                # Filtra apenas datas que pertencem ao período solicitado
                # e que sejam dias úteis (segunda a sexta)
                ano_mes_data = data_str[:7]  # YYYY-MM
                if ano_mes_data != periodo:
                    continue

                # Verifica se é dia útil (segunda a sexta)
                data_obj = conta.get('ULTPGT')
                if data_obj and data_obj.weekday() > 4:  # 5=sábado, 6=domingo
                    continue

                if data_str not in resumo_por_dia:
                    resumo_por_dia[data_str] = {
                        'data': data_str,
                        'total': 0,
                        'quantidade': 0
                    }

                # Usa VLRORI (valor original) direto
                resumo_por_dia[data_str]['total'] += conta.get('VLRORI', 0)
                resumo_por_dia[data_str]['quantidade'] += 1

            # Converte para lista e ordena por data
            resultado = sorted(resumo_por_dia.values(), key=lambda x: x['data'])

            return resultado

        except Exception as e:
            print(f"Erro ao obter resumo liquidado por dia: {str(e)}")
            raise Exception(f"Erro ao obter resumo liquidado por dia: {str(e)}")

    @staticmethod
    def obter_contas_pagar_liquidadas_do_senior(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Busca contas a pagar LIQUIDADAS do Senior para o período especificado
        Filtra apenas títulos com SITTIT = 'LQ'
        Usa ULTPGT (data de último pagamento) DIRETA, sem ajustes de data ou valor
        """
        try:
            # Obtém primeiro e último dia do mês
            ano, mes = map(int, periodo.split('-'))
            ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
            data_inicio = datetime(ano, mes, 1)
            data_fim = datetime(ano, mes, ultimo_dia_mes)

            # Formata datas para SQL
            data_inicio_str = data_inicio.strftime('%Y%m%d')
            data_fim_str = data_fim.strftime('%Y%m%d')

            # Monta filtro de filiais
            filiais_filter = ""
            if filiais and len(filiais) > 0:
                filiais_str = ','.join([f"'{f.strip()}'" for f in filiais])
                filiais_filter = f"AND E501MCP.CODFIL IN ({filiais_str})"
            else:
                # Se não especificou filiais, usa as padrão (todas exceto 2002)
                filiais_filter = "AND E501MCP.CODFIL IN ('1001','1002','1003','3001','3002','3003')"

            # Query SQL - APENAS TÍTULOS LIQUIDADOS (SITTIT = 'LQ')
            # Filtra por ULTPGT (data de último pagamento) ao invés de VCTPRO
            query = f"""
            SELECT DISTINCT E501MCP.CODEMP,E501MCP.CODFIL,E501MCP.NUMTIT,E501MCP.CODFOR
            ,E095FOR.NOMFOR,E501MCP.SEQMOV,E501MCP.CODTNS,E501MCP.DATMOV,E501MCP.CODFPG
            ,E501TCP.CODTPT,E501TCP.SITTIT,E501TCP.OBSTCP,E501TCP.VLRORI,E501TCP.DATEMI,E501TCP.ULTPGT
            ,E501MCP.VCTPRO,E501RAT.VLRRAT,E501RAT.CTAFIN,E501RAT.CODCCU,E501RAT.CTARED,E501TCP.VLRABE
            FROM E501MCP,E501TCP,E001TNS,E002TPT,E095FOR,E501RAT
            WHERE E501MCP.CODEMP IN (10,20,30)
            AND E501MCP.CODEMP = E501TCP.CODEMP
            AND E501MCP.CODFIL = E501TCP.CODFIL
            AND E501MCP.NUMTIT = E501TCP.NUMTIT
            AND E501MCP.CODTPT = E501TCP.CODTPT
            AND E501MCP.CODFOR = E501TCP.CODFOR
            AND E501TCP.CODEMP = E001TNS.CODEMP
            AND E501TCP.CODTNS = E001TNS.CODTNS
            AND E501MCP.CODTPT = E002TPT.CODTPT
            AND E501MCP.CODFOR = E095FOR.CODFOR
            AND E501MCP.CODEMP = E501RAT.CODEMP
            AND E501MCP.CODFIL = E501RAT.CODFIL
            AND E501MCP.CODFOR = E501RAT.CODFOR
            AND E501MCP.NUMTIT = E501RAT.NUMTIT
            AND E501MCP.SEQMOV = E501RAT.SEQMOV
            AND E501MCP.CODTPT = E501RAT.CODTPT
            AND E501TCP.SITTIT = 'LQ'
            AND E501MCP.SEQMOV = 1
            AND E501TCP.VLRABE >= 0
            AND E001TNS.LISMOD = 'CPE'
            AND E501RAT.CTAFIN NOT IN (407,408,409,410,411,412,501)
            AND E501TCP.ULTPGT >= '{data_inicio_str}'
            AND E501TCP.ULTPGT <= '{data_fim_str}'
            AND YEAR(E501TCP.ULTPGT) != 1900
            {filiais_filter}
            """

            # Executa query
            resultados = senior_db.execute_query(query)

            # Processa resultados SEM ajustes de data ou valor
            registros_processados = []
            for registro in resultados:
                # Usa ULTPGT DIRETO, sem ajustes
                ultpgt = registro.get('ULTPGT')

                # Armazena ULTPGT direto, SEM ajustar dia da semana
                if ultpgt and isinstance(ultpgt, datetime):
                    registro['ULTPGT'] = ultpgt
                    registro['ULTPGT_STR'] = ultpgt.strftime('%Y-%m-%d')
                else:
                    registro['ULTPGT'] = None
                    registro['ULTPGT_STR'] = None

                # NÃO calcula valor - usa VLRABE direto
                # O valor será usado diretamente no método obter_resumo_por_dia_liquidado

                registros_processados.append(registro)

            return registros_processados

        except Exception as e:
            print(f"Erro ao buscar contas liquidadas do Senior: {str(e)}")
            raise Exception(f"Erro ao buscar contas liquidadas do Senior: {str(e)}")
