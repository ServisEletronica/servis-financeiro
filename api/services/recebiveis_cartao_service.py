"""
Serviço para gerenciar recebíveis de cartão
Responsável por CRUD de dados de recebíveis extraídos via OCR
"""

from typing import List, Dict, Optional
from database import db
from services.openai_service import OpenAIService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RecebiveisCartaoService:
    """Serviço para operações com recebíveis de cartão"""

    @staticmethod
    def processar_upload(images_bytes_list: List[bytes], status: str = "projetado", usuario: str = "sistema") -> Dict:
        """
        Processa upload de imagens de calendários Cielo

        Args:
            images_bytes_list: Lista de bytes de imagens
            status: Status dos recebíveis ('projetado' ou 'recebido')
            usuario: Usuário que está fazendo o upload

        Returns:
            Dict com resumo do processamento:
            {
                "sucesso": bool,
                "total_imagens": int,
                "total_registros_inseridos": int,
                "erros": list,
                "detalhes": list
            }
        """
        try:
            openai_service = OpenAIService()

            # Extrai dados de todas as imagens
            resultados = openai_service.extrair_multiplos_calendarios(images_bytes_list)

            total_registros = 0
            erros = []
            detalhes = []

            # Processa cada resultado
            for resultado in resultados:
                if not resultado.get("sucesso"):
                    erros.append({
                        "imagem": resultado.get("indice", -1),
                        "erro": resultado.get("erro", "Erro desconhecido")
                    })
                    continue

                dados = resultado["dados"]
                mes_referencia = dados["mes_referencia"]
                estabelecimento = dados["estabelecimento"]

                # Limpa dados existentes deste estabelecimento e mês
                RecebiveisCartaoService.limpar_dados_mes(mes_referencia, estabelecimento)

                # Insere novos dados
                registros_inseridos = 0
                for recebivel in dados["recebiveis"]:
                    try:
                        RecebiveisCartaoService.inserir_recebivel(
                            data_recebimento=recebivel["data"],
                            valor=recebivel["valor"],
                            estabelecimento=estabelecimento,
                            mes_referencia=mes_referencia,
                            status=status,
                            usuario_upload=usuario
                        )
                        registros_inseridos += 1
                        total_registros += 1
                    except Exception as e:
                        logger.error(f"Erro ao inserir recebível {recebivel}: {e}")
                        erros.append({
                            "estabelecimento": estabelecimento,
                            "data": recebivel.get("data"),
                            "erro": str(e)
                        })

                detalhes.append({
                    "estabelecimento": estabelecimento,
                    "mes_referencia": mes_referencia,
                    "registros_inseridos": registros_inseridos
                })

            return {
                "sucesso": len(erros) == 0 or total_registros > 0,
                "total_imagens": len(images_bytes_list),
                "total_registros_inseridos": total_registros,
                "erros": erros,
                "detalhes": detalhes
            }

        except Exception as e:
            logger.error(f"Erro ao processar upload: {e}")
            return {
                "sucesso": False,
                "total_imagens": len(images_bytes_list),
                "total_registros_inseridos": 0,
                "erros": [{"erro": str(e)}],
                "detalhes": []
            }

    @staticmethod
    def inserir_recebivel(
        data_recebimento: str,
        valor: float,
        estabelecimento: str,
        mes_referencia: str,
        status: str = "projetado",
        usuario_upload: str = "sistema"
    ) -> bool:
        """
        Insere um novo recebível no banco de dados

        Args:
            data_recebimento: Data do recebimento (YYYY-MM-DD)
            valor: Valor do recebimento
            estabelecimento: Código do estabelecimento
            mes_referencia: Mês de referência (YYYY-MM)
            status: Status do recebível ('projetado' ou 'recebido')
            usuario_upload: Usuário que fez o upload

        Returns:
            True se inserido com sucesso
        """
        query = """
        INSERT INTO recebiveis_cartao
            (data_recebimento, valor, estabelecimento, mes_referencia, status, usuario_upload, data_upload)
        VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
        """

        # Usa contexto de conexão diretamente para INSERT
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (data_recebimento, valor, estabelecimento, mes_referencia, status, usuario_upload))
            conn.commit()
            cursor.close()

        return True

    @staticmethod
    def upsert_recebivel(
        data_recebimento: str,
        valor: float,
        estabelecimento: str,
        mes_referencia: str,
        status: str = "recebido",
        usuario_upload: str = "manual"
    ) -> bool:
        """
        Insere ou atualiza um recebível no banco de dados (UPSERT)
        Se já existir um registro com mesma data, estabelecimento e status, atualiza o valor
        Senão, insere um novo registro

        Args:
            data_recebimento: Data do recebimento (YYYY-MM-DD)
            valor: Valor do recebimento
            estabelecimento: Código do estabelecimento
            mes_referencia: Mês de referência (YYYY-MM)
            status: Status do recebível ('projetado' ou 'recebido')
            usuario_upload: Usuário que fez o upload

        Returns:
            True se inserido/atualizado com sucesso
        """
        # MERGE não existe em todas as versões do SQL Server acessíveis via pymssql
        # Vamos usar a abordagem UPDATE + INSERT se não afetar linhas

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Primeiro tenta atualizar
            update_query = """
            UPDATE recebiveis_cartao
            SET valor = %s,
                usuario_upload = %s,
                data_upload = GETDATE()
            WHERE data_recebimento = %s
              AND estabelecimento = %s
              AND mes_referencia = %s
              AND status = %s
            """
            cursor.execute(update_query, (valor, usuario_upload, data_recebimento, estabelecimento, mes_referencia, status))

            # Se não atualizou nenhuma linha, insere
            if cursor.rowcount == 0:
                insert_query = """
                INSERT INTO recebiveis_cartao
                    (data_recebimento, valor, estabelecimento, mes_referencia, status, usuario_upload, data_upload)
                VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
                """
                cursor.execute(insert_query, (data_recebimento, valor, estabelecimento, mes_referencia, status, usuario_upload))

            conn.commit()
            cursor.close()

        return True

    @staticmethod
    def obter_recebiveis_por_periodo(
        data_inicio: str,
        data_fim: str,
        estabelecimentos: Optional[List[str]] = None,
        status: str = 'projetado'
    ) -> List[Dict]:
        """
        Obtém recebíveis agrupados por data em um período

        Args:
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            estabelecimentos: Lista de códigos de estabelecimento (opcional)
            status: Status dos recebíveis ('projetado' ou 'recebido')

        Returns:
            Lista de dicionários [{data: str, total: float}]
        """
        if estabelecimentos and len(estabelecimentos) > 0:
            # Filtra por estabelecimentos específicos
            placeholders = ','.join(['%s'] * len(estabelecimentos))
            query = f"""
            SELECT
                CONVERT(VARCHAR(10), data_recebimento, 23) as data,
                CAST(SUM(valor) AS DECIMAL(18,2)) as total
            FROM recebiveis_cartao
            WHERE data_recebimento BETWEEN %s AND %s
              AND estabelecimento IN ({placeholders})
              AND status = %s
            GROUP BY CONVERT(VARCHAR(10), data_recebimento, 23)
            ORDER BY CONVERT(VARCHAR(10), data_recebimento, 23)
            """
            params = (data_inicio, data_fim) + tuple(estabelecimentos) + (status,)
        else:
            # Retorna todos os estabelecimentos
            query = """
            SELECT
                CONVERT(VARCHAR(10), data_recebimento, 23) as data,
                CAST(SUM(valor) AS DECIMAL(18,2)) as total
            FROM recebiveis_cartao
            WHERE data_recebimento BETWEEN %s AND %s
              AND status = %s
            GROUP BY CONVERT(VARCHAR(10), data_recebimento, 23)
            ORDER BY CONVERT(VARCHAR(10), data_recebimento, 23)
            """
            params = (data_inicio, data_fim, status)

        results = db.execute_query(query, params)
        return results if results else []

    @staticmethod
    def limpar_dados_mes(mes_referencia: str, estabelecimento: Optional[str] = None) -> int:
        """
        Remove dados de um mês específico

        Args:
            mes_referencia: Mês no formato YYYY-MM
            estabelecimento: Código do estabelecimento (opcional)

        Returns:
            Número de registros deletados
        """
        if estabelecimento:
            query = """
            DELETE FROM recebiveis_cartao
            WHERE mes_referencia = %s
            AND estabelecimento = %s
            """
            params = (mes_referencia, estabelecimento)
        else:
            query = """
            DELETE FROM recebiveis_cartao
            WHERE mes_referencia = %s
            """
            params = (mes_referencia,)

        try:
            # Usa contexto de conexão diretamente para DELETE
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rowcount = cursor.rowcount
                conn.commit()
                cursor.close()
                logger.info(f"Dados do mês {mes_referencia} removidos com sucesso ({rowcount} registros)")
                return rowcount
        except Exception as e:
            logger.error(f"Erro ao limpar dados do mês {mes_referencia}: {e}")
            return 0

    @staticmethod
    def obter_recebiveis_detalhados(mes_referencia: str) -> List[Dict]:
        """
        Obtém todos os recebíveis de um mês com detalhes

        Args:
            mes_referencia: Mês no formato YYYY-MM

        Returns:
            Lista de recebíveis com todos os campos
        """
        query = """
        SELECT
            id,
            CONVERT(VARCHAR(10), data_recebimento, 23) as data_recebimento,
            valor,
            estabelecimento,
            mes_referencia,
            usuario_upload,
            data_upload
        FROM recebiveis_cartao
        WHERE mes_referencia = %s
        ORDER BY data_recebimento, estabelecimento
        """

        results = db.execute_query(query, (mes_referencia,))
        return results if results else []

    @staticmethod
    def obter_estatisticas_mes(mes_referencia: str) -> Dict:
        """
        Obtém estatísticas dos recebíveis de um mês

        Args:
            mes_referencia: Mês no formato YYYY-MM

        Returns:
            Dict com estatísticas
        """
        query = """
        SELECT
            COUNT(*) as total_registros,
            COUNT(DISTINCT estabelecimento) as total_estabelecimentos,
            CAST(SUM(valor) AS DECIMAL(18,2)) as valor_total,
            CAST(AVG(valor) AS DECIMAL(18,2)) as valor_medio,
            MIN(data_upload) as primeira_carga,
            MAX(data_upload) as ultima_carga
        FROM recebiveis_cartao
        WHERE mes_referencia = %s
        """

        results = db.execute_query(query, (mes_referencia,))

        if results and len(results) > 0:
            return results[0]

        return {
            "total_registros": 0,
            "total_estabelecimentos": 0,
            "valor_total": 0,
            "valor_medio": 0,
            "primeira_carga": None,
            "ultima_carga": None
        }
