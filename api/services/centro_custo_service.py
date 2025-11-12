from typing import List, Dict
from database import db, senior_db


class CentroCustoService:
    """Service para sincronização de Centro de Custo"""

    @staticmethod
    def sincronizar_centro_custo() -> Dict:
        """
        Sincroniza dados de centro de custo do Senior para o banco local

        Returns:
            Dict com informações da sincronização
        """

        try:
            # Query do Senior
            query_senior = """
                SELECT
                    E043PCM.CODMPC,
                    E043PCM.CTARED,
                    E043PCM.CLACTA,
                    E043PCM.DESCTA,
                    E043PCM.ANASIN,
                    E043PCM.NATCTA,
                    E043PCM.NIVCTA,
                    E043PCM.CODCCU,
                    E043PCM.TIPCCU
                FROM E043PCM
                WHERE E043PCM.CODMPC = 602
                ORDER BY E043PCM.CLACTA, E043PCM.NIVCTA, E043PCM.CTARED, UPPER(E043PCM.DESCTA)
            """

            # Busca dados do Senior
            print("Buscando dados de centro de custo do Senior...")
            dados_senior = senior_db.execute_query(query_senior)

            if not dados_senior or len(dados_senior) == 0:
                return {
                    'success': True,
                    'message': 'Nenhum centro de custo encontrado no Senior',
                    'registros_inseridos': 0
                }

            print(f"Encontrados {len(dados_senior)} centros de custo no Senior")

            # Limpa tabela local
            print("Limpando tabela centro_custo...")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE centro_custo")
                conn.commit()
                cursor.close()

            # Prepara query de inserção em lote
            insert_query = """
                INSERT INTO centro_custo (
                    CODMPC, CTARED, CLACTA, DESCTA, ANASIN, NATCTA,
                    NIVCTA, CODCCU, TIPCCU
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Prepara dados para inserção
            dados_para_inserir = []
            for row in dados_senior:
                dados_para_inserir.append((
                    row.get('CODMPC'),
                    row.get('CTARED'),
                    row.get('CLACTA'),
                    row.get('DESCTA'),
                    row.get('ANASIN'),
                    row.get('NATCTA'),
                    row.get('NIVCTA'),
                    row.get('CODCCU'),
                    row.get('TIPCCU')
                ))

            # Insere em lote
            print(f"Inserindo {len(dados_para_inserir)} centros de custo...")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(insert_query, dados_para_inserir)
                conn.commit()
                cursor.close()

            print(f"✓ Sincronização de centro de custo concluída: {len(dados_para_inserir)} registros")

            return {
                'success': True,
                'message': f'Centro de custo sincronizado com sucesso',
                'registros_inseridos': len(dados_para_inserir)
            }

        except Exception as e:
            print(f"Erro ao sincronizar centro de custo: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Erro ao sincronizar centro de custo: {str(e)}',
                'registros_inseridos': 0
            }

    @staticmethod
    def buscar_centro_custo_por_codigo(codccu: int) -> Dict:
        """
        Busca um centro de custo por código

        Args:
            codccu: Código do centro de custo

        Returns:
            Dict com os dados do centro de custo
        """
        query = """
            SELECT
                CODMPC, CTARED, CLACTA, DESCTA, ANASIN, NATCTA,
                NIVCTA, CODCCU, TIPCCU, created_at, updated_at
            FROM centro_custo
            WHERE CODCCU = %s
        """

        resultado = db.execute_query(query, (codccu,))

        if resultado and len(resultado) > 0:
            return resultado[0]

        return None

    @staticmethod
    def listar_centros_custo() -> List[Dict]:
        """
        Lista todos os centros de custo

        Returns:
            Lista de dicts com os centros de custo
        """
        query = """
            SELECT
                CODMPC, CTARED, CLACTA, DESCTA, ANASIN, NATCTA,
                NIVCTA, CODCCU, TIPCCU, created_at, updated_at
            FROM centro_custo
            ORDER BY CLACTA, NIVCTA, CTARED, DESCTA
        """

        return db.execute_query(query)
