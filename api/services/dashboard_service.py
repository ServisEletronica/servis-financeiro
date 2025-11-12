from datetime import date, datetime, timedelta
from typing import List, Dict
from services.contas_receber_local_service import ContasReceberLocalService
from services.contas_pagar_local_service import ContasPagarLocalService
from utils.calculos import calcular_percentual_mudanca
import pytz
from config import settings


class DashboardService:
    """Service para operações do Dashboard"""

    @staticmethod
    def get_timezone():
        """Retorna o timezone configurado (Fortaleza)"""
        return pytz.timezone(settings.TIMEZONE)

    @staticmethod
    def obter_periodo_datas(periodo: str) -> tuple[str, str]:
        """
        Converte string de período em datas de início e fim

        Períodos suportados:
        - mes-atual
        - mes-anterior
        - trimestre
        - ano
        - YYYY-MM (ex: 2025-01 para Janeiro de 2025)
        """
        tz = DashboardService.get_timezone()
        hoje = datetime.now(tz).date()

        # Verifica se é um mês específico no formato YYYY-MM
        if len(periodo) == 7 and periodo[4] == '-':
            try:
                ano, mes = periodo.split('-')
                ano = int(ano)
                mes = int(mes)

                # Valida mês
                if 1 <= mes <= 12:
                    inicio = date(ano, mes, 1)
                    # Último dia do mês
                    if mes == 12:
                        fim = date(ano, 12, 31)
                    else:
                        fim = date(ano, mes + 1, 1) - timedelta(days=1)

                    return (inicio.strftime('%Y-%m-%d'), fim.strftime('%Y-%m-%d'))
            except (ValueError, IndexError):
                pass  # Se falhar, continua para os outros casos

        if periodo == "mes-atual":
            inicio = date(hoje.year, hoje.month, 1)
            # Último dia do mês
            if hoje.month == 12:
                fim = date(hoje.year, 12, 31)
            else:
                fim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)

        elif periodo == "mes-anterior":
            # Primeiro dia do mês anterior
            if hoje.month == 1:
                inicio = date(hoje.year - 1, 12, 1)
                fim = date(hoje.year - 1, 12, 31)
            else:
                inicio = date(hoje.year, hoje.month - 1, 1)
                fim = date(hoje.year, hoje.month, 1) - timedelta(days=1)

        elif periodo == "trimestre":
            # Últimos 3 meses
            inicio = hoje - timedelta(days=90)
            fim = hoje

        elif periodo == "ano":
            # Ano atual
            inicio = date(hoje.year, 1, 1)
            fim = date(hoje.year, 12, 31)

        else:
            # Default: mês atual
            inicio = date(hoje.year, hoje.month, 1)
            if hoje.month == 12:
                fim = date(hoje.year, 12, 31)
            else:
                fim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)

        return (inicio.strftime('%Y-%m-%d'), fim.strftime('%Y-%m-%d'))

    @staticmethod
    def obter_resumo_financeiro(periodo: str = "mes-atual", filiais: List[str] = None) -> Dict:
        """Obtém resumo financeiro consolidado"""

        # Converte período em datas
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)

        # Converte strings para objetos date
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()

        # Obtém data atual
        tz = DashboardService.get_timezone()
        hoje = datetime.now(tz).date()
        mes_atual_inicio = date(hoje.year, hoje.month, 1)

        # Define se usa projeção para despesas (mês atual ou futuro)
        usar_projecao_despesas = inicio >= mes_atual_inicio

        # Busca totais do período atual
        receitas_total = ContasReceberLocalService.calcular_total_receitas(data_inicio, data_fim, filiais)

        # Despesas: usa projeção com média dos últimos 3 meses se for mês atual ou futuro
        if usar_projecao_despesas:
            despesas_total = ContasPagarLocalService.calcular_total_despesas_projetado(data_inicio, data_fim, filiais)
        else:
            despesas_total = ContasPagarLocalService.calcular_total_despesas(data_inicio, data_fim, filiais)

        saldo_atual = receitas_total - despesas_total

        # Busca totais do período anterior para comparação
        receitas_anterior = ContasReceberLocalService.calcular_total_periodo_anterior(data_inicio, data_fim, filiais)
        despesas_anterior = ContasPagarLocalService.calcular_total_periodo_anterior(data_inicio, data_fim, filiais)
        saldo_anterior = receitas_anterior - despesas_anterior

        # Calcula percentuais de mudança
        percentual_saldo = calcular_percentual_mudanca(saldo_atual, saldo_anterior)
        percentual_receita = calcular_percentual_mudanca(receitas_total, receitas_anterior)
        percentual_despesa = calcular_percentual_mudanca(despesas_total, despesas_anterior)

        return {
            'saldo_atual': round(saldo_atual, 2),
            'receitas_total': round(receitas_total, 2),
            'despesas_total': round(despesas_total, 2),
            'saldo_mes': round(saldo_atual, 2),
            'periodo_inicio': data_inicio,
            'periodo_fim': data_fim,
            'percentual_mudanca_saldo': round(percentual_saldo, 1),
            'percentual_mudanca_receita': round(percentual_receita, 1),
            'percentual_mudanca_despesa': round(percentual_despesa, 1)
        }

    @staticmethod
    def obter_dados_grafico_mensal(periodo: str = "mes-atual", filiais: List[str] = None) -> List[Dict]:
        """
        Obtém dados agrupados por dia para gráficos do mês selecionado
        Retorna todos os dias do mês especificado
        Aplica projeção baseada em média dos últimos 3 meses APENAS para mês atual e futuros
        """
        # Converte período em datas
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)

        # Converte strings para objetos date
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        # Obtém data atual
        tz = DashboardService.get_timezone()
        hoje = datetime.now(tz).date()
        mes_atual_inicio = date(hoje.year, hoje.month, 1)

        # IMPORTANTE: Sempre usa dados reais, sem projeção
        # A projeção foi removida porque estava descartando dados reais
        # Se precisar de projeção no futuro, deve ser implementada em um endpoint separado

        # Contas a Receber: dados reais
        receitas_diarias = ContasReceberLocalService.obter_dados_diarios(data_inicio, data_fim, filiais)

        # Contas a Pagar: dados reais (sem projeção)
        despesas_diarias = ContasPagarLocalService.obter_dados_diarios(data_inicio, data_fim, filiais)

        # Converte para dicionário para fácil acesso (chave: data)
        receitas_dict = {r['data']: r['total'] for r in receitas_diarias}
        despesas_dict = {d['data']: d['total'] for d in despesas_diarias}

        # Gera dados para todos os dias do período
        dados = []
        data_atual = inicio

        while data_atual <= fim:
            data_str = data_atual.strftime('%Y-%m-%d')
            dia = data_atual.day

            # Busca valores do dicionário
            receitas = receitas_dict.get(data_str, 0)
            despesas = despesas_dict.get(data_str, 0)

            dados.append({
                'mes': f'{dia:02d}',  # Usa o dia como label (01, 02, 03, etc)
                'data_completa': data_str,  # Data completa para filtros (YYYY-MM-DD)
                'receitas': round(receitas if receitas else 0, 2),
                'despesas': round(despesas if despesas else 0, 2),
                'saldo': round((receitas if receitas else 0) - (despesas if despesas else 0), 2)
            })

            data_atual += timedelta(days=1)

        return dados

    @staticmethod
    def obter_transacoes(periodo: str = "mes-atual", tipo: str = "todos") -> List[Dict]:
        """
        Obtém lista de transações (receitas e despesas) consolidadas (usando tabelas locais)
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)

        transacoes = []
        id_counter = 1

        # Busca receitas (usando tabelas locais)
        if tipo in ["todos", "receita"]:
            contas_receber = ContasReceberLocalService.buscar_contas(data_inicio, data_fim)
            for conta in contas_receber[:50]:  # Limita a 50 registros
                # Trata data
                data_formatada = ''
                if conta.get('datppt'):
                    try:
                        data_formatada = conta['datppt'].strftime('%Y-%m-%d') if hasattr(conta['datppt'], 'strftime') else str(conta['datppt'])
                    except:
                        data_formatada = str(conta['datppt'])

                transacoes.append({
                    'id': id_counter,
                    'date': data_formatada,
                    'description': f"{conta.get('nomcli', 'Cliente')} - {conta.get('numtit', '')}",
                    'category': conta.get('destns') or 'Receita',
                    'type': 'receita',
                    'value': abs(conta.get('valor_calculado', 0))
                })
                id_counter += 1

        # Busca despesas (usando tabelas locais)
        if tipo in ["todos", "despesa"]:
            contas_pagar = ContasPagarLocalService.buscar_contas(data_inicio, data_fim)
            for conta in contas_pagar[:50]:  # Limita a 50 registros
                # Trata data
                data_formatada = ''
                if conta.get('vctpro'):
                    try:
                        data_formatada = conta['vctpro'].strftime('%Y-%m-%d') if hasattr(conta['vctpro'], 'strftime') else str(conta['vctpro'])
                    except:
                        data_formatada = str(conta['vctpro'])

                transacoes.append({
                    'id': id_counter,
                    'date': data_formatada,
                    'description': f"{conta.get('nomfor', 'Fornecedor')} - {conta.get('numtit', '')}",
                    'category': 'Despesa',
                    'type': 'despesa',
                    'value': conta.get('valor_calculado', 0)
                })
                id_counter += 1

        # Ordena por data (mais recente primeiro)
        transacoes.sort(key=lambda x: x['date'], reverse=True)

        return transacoes

    @staticmethod
    def obter_top_despesas(periodo: str = "mes-atual", limit: int = 10, filiais: List[str] = None) -> List[Dict]:
        """
        Obtém as maiores despesas por conta reduzida (CTARED) usando plano_financeiro
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)
        return ContasPagarLocalService.obter_top_despesas(data_inicio, data_fim, limit, filiais)

    @staticmethod
    def obter_top_fornecedores(periodo: str = "mes-atual", limit: int = 10) -> List[Dict]:
        """
        Obtém os maiores fornecedores por valor de despesa
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)
        return ContasPagarLocalService.obter_top_fornecedores(data_inicio, data_fim, limit)

    @staticmethod
    def obter_top_receitas(periodo: str = "mes-atual", limit: int = 10, filiais: List[str] = None) -> List[Dict]:
        """
        Obtém as maiores receitas por conta reduzida (CTAFIN) usando plano_financeiro
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)
        return ContasReceberLocalService.obter_top_receitas(data_inicio, data_fim, limit, filiais)

    @staticmethod
    def obter_top_clientes(periodo: str = "mes-atual", limit: int = 10) -> List[Dict]:
        """
        Obtém os maiores clientes por valor de receita
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)
        return ContasReceberLocalService.obter_top_clientes(data_inicio, data_fim, limit)

    @staticmethod
    def obter_despesas_por_centro_custo(periodo: str = "mes-atual") -> List[Dict]:
        """
        Obtém despesas agrupadas por centro de custo
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)
        return ContasPagarLocalService.obter_despesas_por_centro_custo(data_inicio, data_fim)

    @staticmethod
    def obter_fluxo_caixa_projetado(periodo: str = "mes-atual", filiais: List[str] = None) -> List[Dict]:
        """
        Obtém o fluxo de caixa projetado (saldo acumulado dia a dia)
        """
        data_inicio, data_fim = DashboardService.obter_periodo_datas(periodo)

        # Obtém dados diários
        receitas_diarias = ContasReceberLocalService.obter_dados_diarios(data_inicio, data_fim, filiais)
        despesas_diarias = ContasPagarLocalService.obter_dados_diarios(data_inicio, data_fim, filiais)

        # Converte para dicionário para fácil acesso
        receitas_dict = {r['data']: r['total'] for r in receitas_diarias}
        despesas_dict = {d['data']: d['total'] for d in despesas_diarias}

        # Gera dados para todos os dias do período
        dados = []
        saldo_acumulado = 0

        inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        data_atual = inicio

        while data_atual <= fim:
            data_str = data_atual.strftime('%Y-%m-%d')
            dia = data_atual.day

            # Busca valores do dicionário
            receitas = receitas_dict.get(data_str, 0)
            despesas = despesas_dict.get(data_str, 0)

            # Calcula saldo do dia
            saldo_dia = (receitas if receitas else 0) - (despesas if despesas else 0)
            saldo_acumulado += saldo_dia

            dados.append({
                'data': f'{dia:02d}',
                'saldo': round(saldo_acumulado, 2),
                'receitas': round(receitas if receitas else 0, 2),
                'despesas': round(despesas if despesas else 0, 2)
            })

            data_atual += timedelta(days=1)

        return dados
