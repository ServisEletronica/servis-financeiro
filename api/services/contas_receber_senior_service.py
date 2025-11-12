from database import senior_db
from datetime import datetime, timedelta
from typing import Optional, List
import calendar


class ContasReceberSeniorService:
    """Serviço para buscar dados de Contas a Receber diretamente do Senior"""

    @staticmethod
    def ajustar_dia_semana(data: datetime) -> datetime:
        """
        Ajusta a data conforme o dia da semana:
        - Sexta (4) -> +3 dias (Segunda)
        - Sábado (5) -> +3 dias (Terça)
        - Domingo (6) -> +2 dias (Terça)
        - Segunda (0) -> +1 dia (Terça)
        - Terça (1) -> +1 dia (Quarta)
        - Quarta (2) -> +1 dia (Quinta)
        - Quinta (3) -> +1 dia (Sexta)
        """
        dia_semana = data.weekday()  # 0=Segunda, 6=Domingo

        if dia_semana == 4:  # Sexta
            return data + timedelta(days=3)
        elif dia_semana == 5:  # Sábado
            return data + timedelta(days=3)
        elif dia_semana == 6:  # Domingo
            return data + timedelta(days=2)
        elif dia_semana == 0:  # Segunda
            return data + timedelta(days=1)
        elif dia_semana == 1:  # Terça
            return data + timedelta(days=1)
        elif dia_semana == 2:  # Quarta
            return data + timedelta(days=1)
        elif dia_semana == 3:  # Quinta
            return data + timedelta(days=1)

        return data

    @staticmethod
    def calcular_valor_cr(vlrabe: float, vlrori: float, recdec: int) -> float:
        """
        Calcula o valor da conta a receber:
        - Se VLRABE <> 0 e RECDEC=2 então -VLRABE
        - Se VLRABE = 0 e RECDEC=2 então -VLRORI
        - Se VLRABE <> 0 e RECDEC=1 então VLRABE
        - Senão VLRORI
        """
        if vlrabe != 0 and recdec == 2:
            return -vlrabe
        elif vlrabe == 0 and recdec == 2:
            return -vlrori
        elif vlrabe != 0 and recdec == 1:
            return vlrabe
        else:
            return vlrori

    @staticmethod
    def obter_primeiro_ultimo_dia_mes(periodo: str) -> tuple:
        """
        Retorna o primeiro e último dia do mês baseado no período YYYY-MM
        Considera sexta-feira do mês anterior como parte do mês seguinte
        """
        ano, mes = map(int, periodo.split('-'))

        # Primeiro dia do mês
        primeiro_dia = datetime(ano, mes, 1)

        # Último dia do mês
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        ultimo_dia = datetime(ano, mes, ultimo_dia_mes)

        # Buscar dias do mês anterior que sejam sexta-feira e precisam ser incluídos
        # Vamos começar alguns dias antes do primeiro dia do mês
        data_inicial = primeiro_dia - timedelta(days=10)

        # Encontrar sextas-feiras do mês anterior que, quando ajustadas, caem no mês atual
        while data_inicial < primeiro_dia:
            dia_semana = data_inicial.weekday()
            if dia_semana == 4:  # Sexta
                data_ajustada = ContasReceberSeniorService.ajustar_dia_semana(data_inicial)
                if data_ajustada.month == mes and data_ajustada.year == ano:
                    data_inicial = data_inicial
                    break
            data_inicial += timedelta(days=1)
        else:
            data_inicial = primeiro_dia

        return data_inicial, ultimo_dia

    @staticmethod
    def obter_contas_receber_do_senior(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Busca contas a receber do Senior para o período especificado
        """
        try:
            # Obtém primeiro e último dia do mês
            data_inicio, data_fim = ContasReceberSeniorService.obter_primeiro_ultimo_dia_mes(periodo)

            # Formata datas para SQL
            data_inicio_str = data_inicio.strftime('%Y%m%d')
            data_fim_str = data_fim.strftime('%Y%m%d')

            # Monta filtro de filiais
            filiais_filter = ""
            if filiais and len(filiais) > 0:
                # Remove espaços e converte para string
                filiais_str = ','.join([f"'{f.strip()}'" for f in filiais])
                filiais_filter = f"AND E301TCR.CODFIL IN ({filiais_str})"
            else:
                # Se não especificou filiais, usa as padrão (todas exceto 2002)
                filiais_filter = "AND E301TCR.CODFIL IN ('1001','1002','1003','3001','3002','3003')"

            # Query SQL
            query = f"""
            SELECT E301TCR.CODEMP, E301TCR.CODFIL, E301TCR.CODCLI, E085CLI.NOMCLI,
                E085CLI.CIDCLI, E085CLI.BAICLI, E085CLI.TIPCLI, E301TCR.DATEMI,
                E301TCR.NUMTIT, E301TCR.SITTIT, E301TCR.CODTPT, E301TCR.VLRABE, E301TCR.VLRORI,
                E001TNS.RECDEC, E301TCR.VCTPRO, E301TCR.VCTORI, E301TCR.PERMUL, E301TCR.TOLMUL,
                E301TCR.DATPPT, E002TPT.RECSOM, E070FIL.RECVJM, E070FIL.RECVMM, E070FIL.RECVDM,
                E301TCR.PERDSC, E301TCR.VLRDSC, E301TCR.TOLJRS, E301TCR.TIPJRS, E301TCR.PERJRS,
                E301TCR.JRSDIA, E301TCR.CODTNS, E001TNS.DESTNS, E301TCR.OBSTCR, E301TCR.CODREP,
                E301TCR.NUMCTR, E301TCR.CODSNF, E301TCR.NUMNFV, E301TCR.CODFPG, E085CLI.USU_UNICLI,
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
                          ), 0) AS CTAFIN
            FROM E301TCR, E085CLI, E085HCL, E039POR, E001TNS, E002TPT, E070FIL, E070EMP
            WHERE E085HCL.CODCLI = E301TCR.CODCLI
                AND E085HCL.CODEMP = E301TCR.CODEMP
                AND E085HCL.CODFIL = E301TCR.CODFIL
                AND E301TCR.CODEMP IN (10,20,30)
                AND E301TCR.SITTIT IN ('AB','LQ')
                AND E301TCR.CODEMP = E001TNS.CODEMP
                AND E301TCR.CODTNS = E001TNS.CODTNS
                AND E301TCR.CODEMP = E039POR.CODEMP
                AND E301TCR.CODPOR = E039POR.CODPOR
                AND E301TCR.CODEMP = E070EMP.CODEMP
                AND E301TCR.CODEMP = E070FIL.CODEMP
                AND E301TCR.CODFIL = E070FIL.CODFIL
                AND E301TCR.CODCLI = E085CLI.CODCLI
                AND E085HCL.CODCLI = E301TCR.CODCLI
                AND E085HCL.CODEMP = E301TCR.CODEMP
                AND E085HCL.CODFIL = E301TCR.CODFIL
                AND E301TCR.CODTPT = E002TPT.CODTPT
                AND E301TCR.VLRABE >= 0
                AND E001TNS.CODEMP = E301TCR.CODEMP
                AND E001TNS.CODTNS = E301TCR.CODTNS
                AND E001TNS.LISMOD = 'CRE'
                AND E301TCR.VCTORI >= '20250101'
                AND E301TCR.CODTPT NOT IN ('MCM', 'MCR', 'MEM', 'MER', 'SUB')
                AND E301TCR.CODCLI NOT IN (250,251,304,445,446,448,72473,74207)
                AND E301TCR.DATPPT >= '{data_inicio_str}'
                AND E301TCR.DATPPT <= '{data_fim_str}'
                {filiais_filter}
            """

            # Executa query
            resultados = senior_db.execute_query(query)

            # Processa resultados e aplica ajustes
            registros_processados = []
            for registro in resultados:
                # Ajusta data com base no dia da semana
                datppt = registro.get('DATPPT')
                if datppt:
                    data_ajustada = ContasReceberSeniorService.ajustar_dia_semana(datppt)
                    registro['DATA_AJUSTADA'] = data_ajustada
                    registro['DATA_AJUSTADA_STR'] = data_ajustada.strftime('%Y-%m-%d')
                else:
                    registro['DATA_AJUSTADA'] = None
                    registro['DATA_AJUSTADA_STR'] = None

                # Calcula valor CR
                vlrabe = registro.get('VLRABE', 0) or 0
                vlrori = registro.get('VLRORI', 0) or 0
                recdec_raw = registro.get('RECDEC', 1)
                # Converte RECDEC para int (pode vir como string do banco)
                recdec = int(recdec_raw) if recdec_raw else 1

                valor_cr = ContasReceberSeniorService.calcular_valor_cr(vlrabe, vlrori, recdec)
                registro['VALOR_CR'] = valor_cr

                registros_processados.append(registro)

            return registros_processados

        except Exception as e:
            print(f"Erro ao buscar contas a receber do Senior: {str(e)}")
            raise Exception(f"Erro ao buscar contas a receber do Senior: {str(e)}")

    @staticmethod
    def obter_resumo_por_dia(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Retorna resumo de contas a receber agrupado por dia
        Filtra apenas datas ajustadas que sejam dias úteis do mês solicitado
        """
        try:
            # Busca contas do Senior
            contas = ContasReceberSeniorService.obter_contas_receber_do_senior(periodo, filiais)

            # Agrupa por data ajustada
            resumo_por_dia = {}
            for conta in contas:
                data_str = conta.get('DATA_AJUSTADA_STR')
                if not data_str:
                    continue

                # Filtra apenas datas ajustadas que pertencem ao período solicitado
                # e que sejam dias úteis (segunda a sexta)
                ano_mes_data = data_str[:7]  # YYYY-MM
                if ano_mes_data != periodo:
                    continue

                # Verifica se é dia útil (segunda a sexta)
                data_obj = conta.get('DATA_AJUSTADA')
                if data_obj and data_obj.weekday() > 4:  # 5=sábado, 6=domingo
                    continue

                if data_str not in resumo_por_dia:
                    resumo_por_dia[data_str] = {
                        'data': data_str,
                        'total': 0,
                        'quantidade': 0
                    }

                resumo_por_dia[data_str]['total'] += conta.get('VALOR_CR', 0)
                resumo_por_dia[data_str]['quantidade'] += 1

            # Converte para lista e ordena por data
            resultado = sorted(resumo_por_dia.values(), key=lambda x: x['data'])

            return resultado

        except Exception as e:
            print(f"Erro ao obter resumo por dia: {str(e)}")
            raise Exception(f"Erro ao obter resumo por dia: {str(e)}")

    @staticmethod
    def obter_resumo_por_dia_liquidado(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Retorna resumo de contas a receber LIQUIDADAS agrupado por dia
        Filtra apenas títulos com SITTIT = 'LQ'
        Usa ULTPGT (data de último pagamento) DIRETA, sem ajustes
        Filtra apenas dias úteis do mês solicitado
        """
        try:
            # Busca contas liquidadas do Senior
            contas = ContasReceberSeniorService.obter_contas_receber_liquidadas_do_senior(periodo, filiais)

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
    def obter_contas_receber_liquidadas_do_senior(periodo: str, filiais: Optional[List[str]] = None) -> List[dict]:
        """
        Busca contas a receber LIQUIDADAS do Senior para o período especificado
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
                filiais_filter = f"AND E301TCR.CODFIL IN ({filiais_str})"
            else:
                filiais_filter = "AND E301TCR.CODFIL IN ('1001','1002','1003','3001','3002','3003')"

            # Query SQL - APENAS TÍTULOS LIQUIDADOS (SITTIT = 'LQ')
            # Filtra por ULTPGT (data de último pagamento) ao invés de DATPPT
            query = f"""
            SELECT E301TCR.CODEMP, E301TCR.CODFIL, E301TCR.CODCLI, E085CLI.NOMCLI,
                E085CLI.CIDCLI, E085CLI.BAICLI, E085CLI.TIPCLI, E301TCR.DATEMI,
                E301TCR.NUMTIT, E301TCR.SITTIT, E301TCR.CODTPT, E301TCR.VLRABE, E301TCR.VLRORI,
                E001TNS.RECDEC, E301TCR.VCTPRO, E301TCR.VCTORI, E301TCR.PERMUL, E301TCR.TOLMUL,
                E301TCR.DATPPT, E002TPT.RECSOM, E070FIL.RECVJM, E070FIL.RECVMM, E070FIL.RECVDM,
                E301TCR.PERDSC, E301TCR.VLRDSC, E301TCR.TOLJRS, E301TCR.TIPJRS, E301TCR.PERJRS,
                E301TCR.JRSDIA, E301TCR.CODTNS, E001TNS.DESTNS, E301TCR.OBSTCR, E301TCR.CODREP,
                E301TCR.NUMCTR, E301TCR.CODSNF, E301TCR.NUMNFV, E301TCR.CODFPG, E085CLI.USU_UNICLI,
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
                          ), 0) AS CTAFIN
            FROM E301TCR, E085CLI, E085HCL, E039POR, E001TNS, E002TPT, E070FIL, E070EMP
            WHERE E085HCL.CODCLI = E301TCR.CODCLI
                AND E085HCL.CODEMP = E301TCR.CODEMP
                AND E085HCL.CODFIL = E301TCR.CODFIL
                AND E301TCR.CODEMP IN (10,20,30)
                AND E301TCR.SITTIT = 'LQ'
                AND E301TCR.CODEMP = E001TNS.CODEMP
                AND E301TCR.CODTNS = E001TNS.CODTNS
                AND E301TCR.CODEMP = E039POR.CODEMP
                AND E301TCR.CODPOR = E039POR.CODPOR
                AND E301TCR.CODEMP = E070EMP.CODEMP
                AND E301TCR.CODEMP = E070FIL.CODEMP
                AND E301TCR.CODFIL = E070FIL.CODFIL
                AND E301TCR.CODCLI = E085CLI.CODCLI
                AND E085HCL.CODCLI = E301TCR.CODCLI
                AND E085HCL.CODEMP = E301TCR.CODEMP
                AND E085HCL.CODFIL = E301TCR.CODFIL
                AND E301TCR.CODTPT = E002TPT.CODTPT
                AND E301TCR.VLRABE >= 0
                AND E001TNS.CODEMP = E301TCR.CODEMP
                AND E001TNS.CODTNS = E301TCR.CODTNS
                AND E001TNS.LISMOD = 'CRE'
                AND E301TCR.VCTORI >= '20250101'
                AND E301TCR.CODTPT NOT IN ('MCM', 'MCR', 'MEM', 'MER', 'SUB')
                AND E301TCR.CODCLI NOT IN (250,251,304,445,446,448,72473,74207)
                AND E301TCR.ULTPGT >= '{data_inicio_str}'
                AND E301TCR.ULTPGT <= '{data_fim_str}'
                AND YEAR(E301TCR.ULTPGT) != 1900
                {filiais_filter}
            """

            # Executa query
            resultados = senior_db.execute_query(query)

            # Processa resultados SEM ajustes de data ou valor
            registros_processados = []
            for registro in resultados:
                # Usa ULTPGT DIRETO, sem ajustes
                ultpgt = registro.get('ULTPGT')

                # Converte ULTPGT de string para datetime se necessário
                if isinstance(ultpgt, str) and ultpgt:
                    # Formato: DD/MM/YYYY
                    try:
                        ultpgt = datetime.strptime(ultpgt, '%d/%m/%Y')
                    except:
                        ultpgt = None

                # Armazena ULTPGT direto, SEM ajustar dia da semana
                if ultpgt:
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

    @staticmethod
    def obter_total_periodo(periodo: str, filiais: Optional[List[str]] = None) -> dict:
        """
        Retorna o total de contas a receber para o período
        """
        try:
            contas = ContasReceberSeniorService.obter_contas_receber_do_senior(periodo, filiais)

            total = sum(conta.get('VALOR_CR', 0) for conta in contas)
            quantidade = len(contas)

            return {
                'total': total,
                'quantidade': quantidade,
                'periodo': periodo
            }

        except Exception as e:
            print(f"Erro ao obter total do período: {str(e)}")
            raise Exception(f"Erro ao obter total do período: {str(e)}")
