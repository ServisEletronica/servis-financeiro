from datetime import datetime, timedelta
from typing import Optional


def ajustar_data_contas_pagar(data: datetime) -> datetime:
    """
    Ajusta a data de vencimento para contas a pagar
    Regra: Se cair em sábado ou domingo, empurra para segunda-feira

    Args:
        data: Data a ser ajustada

    Returns:
        Data ajustada

    Lógica DAX equivalente:
        VAR DiaSemana = WEEKDAY(CPs[VCTPRO], 2) -- Segunda=1, Domingo=7
        RETURN SWITCH(
            TRUE(),
            DiaSemana IN {6}, CPs[VCTPRO] + 2,  -- Sábado → Segunda
            DiaSemana IN {7}, CPs[VCTPRO] + 1,  -- Domingo → Segunda
            CPs[VCTPRO]
        )
    """
    if not isinstance(data, datetime):
        return data

    # weekday() em Python: Segunda=0, Domingo=6
    # Converter para formato DAX: Segunda=1, Domingo=7
    dia_semana = data.weekday() + 1  # Segunda=1, Domingo=7

    if dia_semana == 6:  # Sábado
        return data + timedelta(days=2)  # +2 dias → Segunda
    elif dia_semana == 7:  # Domingo
        return data + timedelta(days=1)  # +1 dia → Segunda
    else:
        return data


def ajustar_data_contas_receber(data: datetime) -> datetime:
    """
    Ajusta a data de vencimento para contas a receber
    Regra: Avança a data conforme o dia da semana

    Args:
        data: Data a ser ajustada

    Returns:
        Data ajustada

    Lógica DAX equivalente:
        VAR DiaSemana = WEEKDAY(CaR[DATPPT], 2) -- Segunda=1, Domingo=7
        RETURN SWITCH(
            TRUE(),
            DiaSemana = 5, CaR[DATPPT] + 3,  -- Sexta → Segunda (pula fim de semana)
            DiaSemana = 6, CaR[DATPPT] + 3,  -- Sábado → Terça
            DiaSemana = 7, CaR[DATPPT] + 2,  -- Domingo → Terça
            DiaSemana = 1, CaR[DATPPT] + 1,  -- Segunda → Terça
            DiaSemana = 2, CaR[DATPPT] + 1,  -- Terça → Quarta
            DiaSemana = 3, CaR[DATPPT] + 1,  -- Quarta → Quinta
            DiaSemana = 4, CaR[DATPPT] + 1,  -- Quinta → Sexta
            CaR[DATPPT]
        )
    """
    if not isinstance(data, datetime):
        return data

    # weekday() em Python: Segunda=0, Domingo=6
    # Converter para formato DAX: Segunda=1, Domingo=7
    dia_semana = data.weekday() + 1  # Segunda=1, Domingo=7

    if dia_semana == 5:  # Sexta
        return data + timedelta(days=3)  # +3 dias → Segunda
    elif dia_semana == 6:  # Sábado
        return data + timedelta(days=3)  # +3 dias → Terça
    elif dia_semana == 7:  # Domingo
        return data + timedelta(days=2)  # +2 dias → Terça
    elif dia_semana == 1:  # Segunda
        return data + timedelta(days=1)  # +1 dia → Terça
    elif dia_semana == 2:  # Terça
        return data + timedelta(days=1)  # +1 dia → Quarta
    elif dia_semana == 3:  # Quarta
        return data + timedelta(days=1)  # +1 dia → Quinta
    elif dia_semana == 4:  # Quinta
        return data + timedelta(days=1)  # +1 dia → Sexta
    else:
        return data
