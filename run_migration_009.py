"""
Script para executar a migration 009
Execute com: venv\Scripts\python run_migration_009.py
"""

import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    print("Conectando ao banco de dados...")
    conn = pymssql.connect(
        server=os.getenv('DB_SERVER'),
        port=int(os.getenv('DB_PORT', 1433)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

    cursor = conn.cursor()

    print("Executando migration 009...")

    # Executa migration
    with open('api/database/migrations/009_fix_unique_constraint_add_status.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    # Separa por ; e executa cada comando
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

    for i, statement in enumerate(statements, 1):
        print(f"  Executando statement {i}/{len(statements)}...")
        cursor.execute(statement)

    conn.commit()
    print("✓ Migration 009 executada com sucesso!")
    print("  - Constraint antiga removida")
    print("  - Nova constraint criada incluindo campo 'status'")
    print("  - Agora é possível ter registros com mesmo dia/estabelecimento mas status diferentes")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"✗ Erro ao executar migration: {e}")
        raise
