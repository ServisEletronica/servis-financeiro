from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.dashboard_service import DashboardService
import traceback

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumo")
async def obter_resumo(
    periodo: str = Query(default="mes-atual", description="Período: mes-atual, mes-anterior, trimestre, ano"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula (ex: 1001,1002)")
):
    """
    Retorna resumo financeiro com cards do dashboard
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = DashboardService.obter_resumo_financeiro(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_resumo: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo: {str(e)}")


@router.get("/grafico-receitas-despesas")
async def obter_grafico_receitas_despesas(
    periodo: str = Query(default="mes-atual", description="Período para agrupamento"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna dados para o gráfico de barras (Receitas vs Despesas)
    Últimos 6 meses
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = DashboardService.obter_dados_grafico_mensal(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_grafico_receitas_despesas: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar gráfico: {str(e)}")


@router.get("/grafico-evolucao")
async def obter_grafico_evolucao(
    periodo: str = Query(default="mes-atual", description="Período para agrupamento")
):
    """
    Retorna dados para o gráfico de linha (Evolução do Saldo)
    Últimos 6 meses
    """
    try:
        resultado = DashboardService.obter_dados_grafico_mensal(periodo)
        return resultado
    except Exception as e:
        print(f"Erro em obter_grafico_evolucao: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar gráfico: {str(e)}")


@router.get("/transacoes")
async def obter_transacoes(
    periodo: str = Query(default="mes-atual", description="Período: mes-atual, mes-anterior, trimestre, ano"),
    tipo: str = Query(default="todos", description="Tipo: todos, receita, despesa")
):
    """
    Retorna lista de transações consolidadas (receitas e despesas)
    """
    try:
        resultado = DashboardService.obter_transacoes(periodo, tipo)
        return resultado
    except Exception as e:
        print(f"Erro em obter_transacoes: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar transações: {str(e)}")


@router.get("/top-despesas")
async def obter_top_despesas(
    periodo: str = Query(default="mes-atual", description="Período"),
    limit: int = Query(default=10, description="Número de despesas"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna as maiores despesas por conta reduzida (CTARED) usando plano_financeiro
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = DashboardService.obter_top_despesas(periodo, limit, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_top_despesas: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top despesas: {str(e)}")


@router.get("/top-fornecedores")
async def obter_top_fornecedores(
    periodo: str = Query(default="mes-atual", description="Período"),
    limit: int = Query(default=10, description="Número de fornecedores")
):
    """
    Retorna os maiores fornecedores por valor de despesa
    """
    try:
        resultado = DashboardService.obter_top_fornecedores(periodo, limit)
        return resultado
    except Exception as e:
        print(f"Erro em obter_top_fornecedores: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top fornecedores: {str(e)}")


@router.get("/top-receitas")
async def obter_top_receitas(
    periodo: str = Query(default="mes-atual", description="Período"),
    limit: int = Query(default=10, description="Número de receitas"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna as maiores receitas por conta reduzida (CTAFIN) usando plano_financeiro
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = DashboardService.obter_top_receitas(periodo, limit, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_top_receitas: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top receitas: {str(e)}")


@router.get("/top-clientes")
async def obter_top_clientes(
    periodo: str = Query(default="mes-atual", description="Período"),
    limit: int = Query(default=10, description="Número de clientes")
):
    """
    Retorna os maiores clientes por valor de receita
    """
    try:
        resultado = DashboardService.obter_top_clientes(periodo, limit)
        return resultado
    except Exception as e:
        print(f"Erro em obter_top_clientes: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top clientes: {str(e)}")


@router.get("/despesas-por-centro-custo")
async def obter_despesas_por_centro_custo(
    periodo: str = Query(default="mes-atual", description="Período")
):
    """
    Retorna despesas agrupadas por centro de custo
    """
    try:
        resultado = DashboardService.obter_despesas_por_centro_custo(periodo)
        return resultado
    except Exception as e:
        print(f"Erro em obter_despesas_por_centro_custo: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar despesas por centro de custo: {str(e)}")


@router.get("/fluxo-caixa")
async def obter_fluxo_caixa(
    periodo: str = Query(default="mes-atual", description="Período"),
    filiais: Optional[str] = Query(default=None, description="Códigos de filiais separados por vírgula")
):
    """
    Retorna o fluxo de caixa projetado (saldo acumulado dia a dia)
    """
    try:
        filiais_list = filiais.split(',') if filiais else None
        resultado = DashboardService.obter_fluxo_caixa_projetado(periodo, filiais_list)
        return resultado
    except Exception as e:
        print(f"Erro em obter_fluxo_caixa: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fluxo de caixa: {str(e)}")
