from fastapi import APIRouter, Query
from typing import Optional
from services.contas_receber_service import ContasReceberService
from services.contas_pagar_service import ContasPagarService

router = APIRouter(prefix="/api/contas", tags=["Contas"])


@router.get("/receber")
async def listar_contas_receber(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """
    Lista todas as contas a receber com filtro de data opcional
    """
    return ContasReceberService.buscar_contas(data_inicio, data_fim)


@router.get("/pagar")
async def listar_contas_pagar(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """
    Lista todas as contas a pagar com filtro de data opcional
    """
    return ContasPagarService.buscar_contas(data_inicio, data_fim)


@router.get("/receber/total")
async def total_contas_receber(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """
    Retorna o total de contas a receber no período
    """
    total = ContasReceberService.calcular_total_receitas(data_inicio, data_fim)
    return {"total": round(total, 2)}


@router.get("/pagar/total")
async def total_contas_pagar(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)")
):
    """
    Retorna o total de contas a pagar no período
    """
    total = ContasPagarService.calcular_total_despesas(data_inicio, data_fim)
    return {"total": round(total, 2)}
