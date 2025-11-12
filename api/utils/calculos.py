from typing import Optional


def calcular_valor_receber(vlrabe: float, recdec: int, vlrori: float) -> float:
    """
    Calcula o valor correto para contas a receber

    Regras:
    - Se VLRABE != 0 e RECDEC = 2: retorna -VLRABE
    - Se VLRABE = 0 e RECDEC = 2: retorna -VLRORI
    - Se VLRABE != 0 e RECDEC = 1: retorna VLRABE
    - Caso contrário: retorna VLRORI
    """
    if vlrabe != 0 and recdec == 2:
        return -vlrabe
    elif vlrabe == 0 and recdec == 2:
        return -vlrori
    elif vlrabe != 0 and recdec == 1:
        return vlrabe
    else:
        return vlrori


def calcular_valor_pagar(vlrabe: float, vlrrat: float) -> float:
    """
    Calcula o valor correto para contas a pagar

    Regras:
    - Se VLRABE > VLRRAT: usa VLRRAT
    - Se VLRABE = 0: usa VLRRAT
    - Caso contrário: usa VLRABE
    """
    if vlrabe > vlrrat:
        return vlrrat
    elif vlrabe == 0:
        return vlrrat
    else:
        return vlrabe


def calcular_percentual_mudanca(valor_atual: float, valor_anterior: float) -> float:
    """Calcula o percentual de mudança entre dois valores"""
    if valor_anterior == 0:
        return 0.0
    return ((valor_atual - valor_anterior) / valor_anterior) * 100
