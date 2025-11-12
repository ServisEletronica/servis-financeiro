"""
Script de teste para verificar dados de contas a receber
"""
from database import db
from datetime import datetime

def test_contas_receber():
    print("=" * 80)
    print("TESTE: Verificação de Contas a Receber")
    print("=" * 80)

    # 1. Verificar se a tabela existe e tem dados
    print("\n1. Contando registros na tabela contas_receber...")
    query_count = "SELECT COUNT(*) as total FROM contas_receber"
    try:
        result = db.execute_single(query_count)
        total_registros = result['total'] if result else 0
        print(f"   Total de registros: {total_registros}")
    except Exception as e:
        print(f"   ERRO ao contar registros: {e}")
        return

    if total_registros == 0:
        print("   ⚠️  PROBLEMA: Tabela vazia! Execute a sincronização primeiro.")
        return

    # 2. Verificar registros com DATPPT preenchido
    print("\n2. Verificando registros com DATPPT preenchido...")
    query_datppt = """
        SELECT
            COUNT(*) as total,
            MIN(DATPPT) as data_min,
            MAX(DATPPT) as data_max
        FROM contas_receber
        WHERE DATPPT IS NOT NULL
    """
    try:
        result = db.execute_single(query_datppt)
        print(f"   Registros com DATPPT: {result['total']}")
        print(f"   Data mínima: {result['data_min']}")
        print(f"   Data máxima: {result['data_max']}")
    except Exception as e:
        print(f"   ERRO: {e}")

    # 3. Verificar registros de Outubro/2025
    print("\n3. Verificando registros de Outubro/2025...")
    data_inicio = "2025-10-01"
    data_fim = "2025-10-31"

    query_outubro = """
        SELECT COUNT(*) as total
        FROM contas_receber
        WHERE DATPPT BETWEEN %s AND %s
    """
    try:
        result = db.execute_single(query_outubro, (data_inicio, data_fim))
        print(f"   Registros em Outubro/2025: {result['total']}")
    except Exception as e:
        print(f"   ERRO: {e}")

    # 4. Testar a query de cálculo de receitas
    print("\n4. Testando cálculo de receitas para Outubro/2025...")
    query_receitas = """
        SELECT
            CAST(SUM(
                CASE
                    WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                    WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                    WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                    ELSE VLRORI
                END
            ) AS DECIMAL(18,2)) AS total_receitas
        FROM contas_receber
        WHERE DATPPT BETWEEN %s AND %s
    """
    try:
        result = db.execute_single(query_receitas, (data_inicio, data_fim))
        total = result['total_receitas'] if result and result['total_receitas'] else 0
        print(f"   Total de receitas: R$ {total:,.2f}")
    except Exception as e:
        print(f"   ERRO: {e}")

    # 5. Mostrar amostra de dados
    print("\n5. Amostra de 5 registros com DATPPT em Outubro/2025...")
    query_sample = """
        SELECT TOP 5
            NOMCLI, NUMTIT, VLRABE, VLRORI, RECDEC, DATPPT,
            CASE
                WHEN VLRABE != 0 AND RECDEC = 2 THEN -VLRABE
                WHEN VLRABE = 0 AND RECDEC = 2 THEN -VLRORI
                WHEN VLRABE != 0 AND RECDEC = 1 THEN VLRABE
                ELSE VLRORI
            END as valor_calculado
        FROM contas_receber
        WHERE DATPPT BETWEEN %s AND %s
        ORDER BY DATPPT
    """
    try:
        results = db.execute_query(query_sample, (data_inicio, data_fim))
        for row in results:
            print(f"   - {row['NOMCLI'][:30]:<30} | Título: {row['NUMTIT']:<15} | "
                  f"VLRABE: {row['VLRABE']:>10.2f} | VLRORI: {row['VLRORI']:>10.2f} | "
                  f"RECDEC: {row['RECDEC']} | Calculado: R$ {row['valor_calculado']:>10.2f} | "
                  f"Data: {row['DATPPT']}")
    except Exception as e:
        print(f"   ERRO: {e}")

    # 6. Verificar distribuição por RECDEC
    print("\n6. Distribuição de registros por RECDEC (Outubro/2025)...")
    query_recdec = """
        SELECT
            RECDEC,
            COUNT(*) as qtd,
            SUM(VLRABE) as sum_vlrabe,
            SUM(VLRORI) as sum_vlrori
        FROM contas_receber
        WHERE DATPPT BETWEEN %s AND %s
        GROUP BY RECDEC
        ORDER BY RECDEC
    """
    try:
        results = db.execute_query(query_recdec, (data_inicio, data_fim))
        for row in results:
            print(f"   RECDEC {row['RECDEC']}: {row['qtd']} registros | "
                  f"VLRABE: R$ {row['sum_vlrabe']:,.2f} | "
                  f"VLRORI: R$ {row['sum_vlrori']:,.2f}")
    except Exception as e:
        print(f"   ERRO: {e}")

    print("\n" + "=" * 80)
    print("FIM DO TESTE")
    print("=" * 80)


if __name__ == "__main__":
    test_contas_receber()
