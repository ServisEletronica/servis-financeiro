#!/usr/bin/env python3
"""
Script de teste para validar os ajustes de data
"""
from datetime import datetime
from utils.date_adjustments import ajustar_data_contas_pagar, ajustar_data_contas_receber


def test_ajuste_contas_pagar():
    """Testa ajustes de data para contas a pagar"""
    print("=" * 60)
    print("TESTE: AJUSTES DE DATA - CONTAS A PAGAR")
    print("=" * 60)
    print("Regra: Sabado/Domingo -> Segunda-feira\n")

    testes = [
        # (data, dia_semana_esperado, descricao)
        (datetime(2025, 1, 27), "Segunda", "Segunda permanece Segunda"),
        (datetime(2025, 1, 28), "Terca", "Terca permanece Terca"),
        (datetime(2025, 1, 29), "Quarta", "Quarta permanece Quarta"),
        (datetime(2025, 1, 30), "Quinta", "Quinta permanece Quinta"),
        (datetime(2025, 1, 31), "Sexta", "Sexta permanece Sexta"),
        (datetime(2025, 2, 1), "Sabado -> Segunda", "Sabado move para Segunda (03/02)"),
        (datetime(2025, 2, 2), "Domingo -> Segunda", "Domingo move para Segunda (03/02)"),
    ]

    dias_semana = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]

    for data_original, dia_esperado, descricao in testes:
        data_ajustada = ajustar_data_contas_pagar(data_original)
        dia_original = dias_semana[data_original.weekday()]
        dia_ajustado = dias_semana[data_ajustada.weekday()]

        print(f"[OK] {descricao}")
        print(f"  Original: {data_original.strftime('%d/%m/%Y')} ({dia_original})")
        print(f"  Ajustada: {data_ajustada.strftime('%d/%m/%Y')} ({dia_ajustado})")
        print()


def test_ajuste_contas_receber():
    """Testa ajustes de data para contas a receber"""
    print("\n" + "=" * 60)
    print("TESTE: AJUSTES DE DATA - CONTAS A RECEBER")
    print("=" * 60)
    print("Regra: Avança conforme o dia da semana\n")

    testes = [
        (datetime(2025, 1, 27), "Segunda -> Terca"),
        (datetime(2025, 1, 28), "Terca -> Quarta"),
        (datetime(2025, 1, 29), "Quarta -> Quinta"),
        (datetime(2025, 1, 30), "Quinta -> Sexta"),
        (datetime(2025, 1, 31), "Sexta -> Segunda (pula fim de semana)"),
        (datetime(2025, 2, 1), "Sabado -> Terca"),
        (datetime(2025, 2, 2), "Domingo -> Terca"),
    ]

    dias_semana = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]

    for data_original, descricao in testes:
        data_ajustada = ajustar_data_contas_receber(data_original)
        dia_original = dias_semana[data_original.weekday()]
        dia_ajustado = dias_semana[data_ajustada.weekday()]

        print(f"[OK] {descricao}")
        print(f"  Original: {data_original.strftime('%d/%m/%Y')} ({dia_original})")
        print(f"  Ajustada: {data_ajustada.strftime('%d/%m/%Y')} ({dia_ajustado})")
        print()


if __name__ == "__main__":
    test_ajuste_contas_pagar()
    test_ajuste_contas_receber()
    print("=" * 60)
    print("TESTES CONCLUÍDOS!")
    print("=" * 60)
