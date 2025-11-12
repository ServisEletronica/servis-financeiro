"""
Service para sincronização da tabela plano_financeiro
"""

from database import db, senior_db
import uuid
import logging

logger = logging.getLogger(__name__)


class PlanoFinanceiroService:
    """Service para sincronização do Plano Financeiro"""

    @staticmethod
    def sincronizar():
        """
        Sincroniza dados do plano financeiro do banco Senior para o banco local
        """
        logger.info("Iniciando sincronização de Plano Financeiro...")

        # Query no banco Senior
        query_senior = """
        SELECT
            E043PCM.CODMPC,
            E043PCM.CTARED,
            E043PCM.MSKGCC,
            E043PCM.DEFGRU,
            E043PCM.CLACTA,
            E043PCM.NIVCTA,
            E043PCM.DESCTA,
            E043PCM.ANASIN,
            E043PCM.NATCTA,
            E043PCM.MODCTB,
            E043PCM.CTACTB,
            E043PCM.CODCCU,
            E043PCM.TIPCCU
        FROM E043PCM
        WHERE E043PCM.CODMPC = 601
        ORDER BY E043PCM.CLACTA, E043PCM.NIVCTA, E043PCM.CTARED, UPPER(E043PCM.DESCTA)
        """

        try:
            # Busca dados do Senior
            logger.info("Buscando dados do banco Senior...")
            dados_senior = senior_db.execute_query(query_senior)
            qtd_registros = len(dados_senior)
            logger.info(f"Encontrados {qtd_registros} registros no Senior")

            if qtd_registros == 0:
                logger.warning("Nenhum registro encontrado no Senior")
                return {
                    'success': True,
                    'registros_sincronizados': 0,
                    'mensagem': 'Nenhum registro encontrado'
                }

            # Limpa tabela local
            logger.info("Limpando tabela plano_financeiro...")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE plano_financeiro")
                conn.commit()

            # Prepara dados para inserção em massa
            logger.info(f"Preparando {qtd_registros} registros para inserção em massa...")
            dados_inserir = []
            for row in dados_senior:
                dados_inserir.append((
                    str(uuid.uuid4()),
                    row.get('CODMPC'),
                    row.get('CTARED'),
                    row.get('MSKGCC'),
                    row.get('DEFGRU'),
                    row.get('CLACTA'),
                    row.get('NIVCTA'),
                    row.get('DESCTA'),
                    row.get('ANASIN'),
                    row.get('NATCTA'),
                    row.get('MODCTB'),
                    row.get('CTACTB'),
                    row.get('CODCCU'),
                    row.get('TIPCCU')
                ))

            # Query de inserção
            insert_query = """
            INSERT INTO plano_financeiro (
                id, CODMPC, CTARED, MSKGCC, DEFGRU, CLACTA, NIVCTA, DESCTA,
                ANASIN, NATCTA, MODCTB, CTACTB, CODCCU, TIPCCU
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            # Insere em batches
            logger.info(f"Inserindo {qtd_registros} registros em massa (batches)...")
            batch_size = 5000
            total_inseridos = 0

            with db.get_connection() as conn:
                cursor = conn.cursor()
                for i in range(0, len(dados_inserir), batch_size):
                    batch = dados_inserir[i:i + batch_size]
                    cursor.executemany(insert_query, batch)
                    total_inseridos += len(batch)
                    logger.info(f"Inseridos {total_inseridos}/{qtd_registros} registros...")
                conn.commit()

            logger.info(f"Total de {total_inseridos} registros inseridos com sucesso.")

            return {
                'success': True,
                'registros_sincronizados': total_inseridos,
                'mensagem': f'{total_inseridos} registros sincronizados com sucesso'
            }

        except Exception as e:
            logger.error(f"Erro ao sincronizar plano financeiro: {str(e)}")
            raise
