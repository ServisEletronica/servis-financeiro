"""
Serviço de Sincronização
Responsável por sincronizar dados do banco Senior para o banco local
"""

import logging
from datetime import datetime
from typing import Dict, Any
import traceback
import uuid

from database import db, senior_db
from services.plano_financeiro_service import PlanoFinanceiroService
from services.centro_custo_service import CentroCustoService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================================================
# QUERIES SQL DO SISTEMA SENIOR
# ================================================

QUERY_CONTAS_RECEBER = """
SELECT E301TCR.CODEMP,E301TCR.CODFIL,E301TCR.CODCLI ,E085CLI.NOMCLI,
E085CLI.CIDCLI, E085CLI.BAICLI, E085CLI.TIPCLI, E301TCR.DATEMI
,E301TCR.NUMTIT,E301TCR.SITTIT,E301TCR.CODTPT,E301TCR.VLRABE,E301TCR.VLRORI
,E001TNS.RECDEC,E301TCR.VCTPRO,E301TCR.VCTORI,E301TCR.PERMUL,E301TCR.TOLMUL
,E301TCR.DATPPT,E002TPT.RECSOM,E070FIL.RECVJM,E070FIL.RECVMM,E070FIL.RECVDM
,E301TCR.PERDSC,E301TCR.VLRDSC,E301TCR.TOLJRS,E301TCR.TIPJRS,E301TCR.PERJRS
,E301TCR.JRSDIA,E301TCR.CODTNS,E001TNS.DESTNS,E301TCR.OBSTCR,E301TCR.CODREP
,E301TCR.NUMCTR,E301TCR.CODSNF,E301TCR.NUMNFV,E301TCR.CODFPG,E085CLI.USU_UNICLI
,CASE WHEN YEAR(E301TCR.ULTPGT) = 1900 THEN ''
ELSE CONVERT(VARCHAR(10), E301TCR.ULTPGT, 103)
END AS ULTPGT
,ISNULL((SELECT TOP 1 E301RAT.CODCCU FROM E301RAT
                 WHERE E301RAT.CODEMP = E301TCR.CODEMP
                        AND E301RAT.CODFIL = E301TCR.CODFIL
                        AND E301RAT.NUMTIT = E301TCR.NUMTIT
                        AND E301RAT.CODTPT = E301TCR.CODTPT
                      ), 0) AS CODCCU
,ISNULL((SELECT TOP 1 E301RAT.CTAFIN FROM E301RAT
                 WHERE E301RAT.CODEMP = E301TCR.CODEMP
                        AND E301RAT.CODFIL = E301TCR.CODFIL
                        AND E301RAT.NUMTIT = E301TCR.NUMTIT
                        AND E301RAT.CODTPT = E301TCR.CODTPT
                      ), 0) AS CTAFIN
FROM E301TCR,E085CLI,E085HCL,E039POR,E001TNS,E002TPT,E070FIL,E070EMP
WHERE E085HCL.CODCLI = E301TCR.CODCLI
AND E085HCL.CODEMP = E301TCR.CODEMP
AND E085HCL.CODFIL = E301TCR.CODFIL
AND E301TCR.CODEMP IN (10,20,30)
AND E301TCR.SITTIT IN ('AB','LQ')
AND E301TCR.CODEMP = E001TNS.CODEMP
AND E301TCR.CODTNS = E001TNS.CODTNS
AND E301TCR.CODEMP = E039POR.CODEMP
AND E301TCR.CODPOR = E039POR.CODPOR
AND E301TCR.CODEMP = E070EMP.CODEMP
AND E301TCR.CODEMP = E070FIL.CODEMP
AND E301TCR.CODFIL = E070FIL.CODFIL
AND E301TCR.CODCLI = E085CLI.CODCLI
AND E085HCL.CODCLI = E301TCR.CODCLI
AND E085HCL.CODEMP = E301TCR.CODEMP
AND E085HCL.CODFIL = E301TCR.CODFIL
AND E301TCR.CODTPT = E002TPT.CODTPT
AND E301TCR.VLRABE >= 0
AND E001TNS.CODEMP = E301TCR.CODEMP
AND E001TNS.CODTNS = E301TCR.CODTNS
AND E001TNS.LISMOD = 'CRE'
AND E301TCR.VCTORI >= '20250101'
"""

QUERY_CONTAS_PAGAR = """
SELECT DISTINCT E501MCP.CODEMP,E501MCP.CODFIL,E501MCP.NUMTIT,E501MCP.CODFOR
,E095FOR.NOMFOR,E501MCP.SEQMOV,E501MCP.CODTNS,E501MCP.DATMOV,E501MCP.CODFPG
,E501TCP.CODTPT,E501TCP.SITTIT,E501TCP.OBSTCP,E501TCP.VLRORI,E501TCP.DATEMI,E501TCP.ULTPGT
,E501MCP.VCTPRO,E501RAT.VLRRAT,E501RAT.CTAFIN,E501RAT.CODCCU,E501RAT.CTARED,E501TCP.VLRABE
FROM E501MCP,E501TCP,E001TNS,E002TPT,E095FOR,E501RAT
WHERE E501MCP.CODEMP IN (10,20,30)
AND E501MCP.CODEMP = E501TCP.CODEMP
AND E501MCP.CODFIL = E501TCP.CODFIL
AND E501MCP.NUMTIT = E501TCP.NUMTIT
AND E501MCP.CODTPT = E501TCP.CODTPT
AND E501MCP.CODFOR = E501TCP.CODFOR
AND E501TCP.CODEMP = E001TNS.CODEMP
AND E501TCP.CODTNS = E001TNS.CODTNS
AND E501MCP.CODTPT = E002TPT.CODTPT
AND E501MCP.CODFOR = E095FOR.CODFOR
AND E501MCP.CODEMP = E501RAT.CODEMP
AND E501MCP.CODFIL = E501RAT.CODFIL
AND E501MCP.CODFOR = E501RAT.CODFOR
AND E501MCP.NUMTIT = E501RAT.NUMTIT
AND E501MCP.SEQMOV = E501RAT.SEQMOV
AND E501MCP.CODTPT = E501RAT.CODTPT
AND E501TCP.SITTIT <> 'CA'
AND E501MCP.SEQMOV = 1
AND E501TCP.VLRABE >= 0
AND 0 = 0
AND E001TNS.LISMOD = 'CPE'
AND E501RAT.CTAFIN NOT IN (407,408,409,410,411,412,501)
"""


class SincronizacaoService:
    """Serviço para sincronização de dados entre Senior e banco local"""

    @staticmethod
    def criar_log_sincronizacao(tipo: str, executado_por: str = "Sistema") -> str:
        """Cria um registro de log de sincronização e retorna o ID"""
        log_id = str(uuid.uuid4())
        query = """
            INSERT INTO log_sincronizacao
            (id, tipo, data_hora_inicio, status, executado_por)
            VALUES (%s, %s, %s, %s, %s)
        """

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                log_id,
                tipo,
                datetime.now(),
                'em_andamento',
                executado_por
            ))
            conn.commit()
            cursor.close()

        return log_id

    @staticmethod
    def atualizar_log_sincronizacao(
        log_id: str,
        status: str,
        registros_inseridos: int = 0,
        tempo_execucao_ms: int = 0,
        mensagem_erro: str = None,
        stack_trace: str = None
    ):
        """Atualiza o log de sincronização"""
        query = """
            UPDATE log_sincronizacao
            SET data_hora_fim = %s,
                status = %s,
                registros_inseridos = %s,
                tempo_execucao_ms = %s,
                mensagem_erro = %s,
                stack_trace = %s
            WHERE id = %s
        """

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                datetime.now(),
                status,
                registros_inseridos,
                tempo_execucao_ms,
                mensagem_erro,
                stack_trace,
                log_id
            ))
            conn.commit()
            cursor.close()

    @staticmethod
    def sincronizar_contas_receber() -> Dict[str, Any]:
        """
        Sincroniza contas a receber do Senior para o banco local
        Estratégia: Limpa tabela e reinsere todos os registros
        """
        inicio = datetime.now()
        log_id = SincronizacaoService.criar_log_sincronizacao('contas_receber')

        try:
            logger.info("Iniciando sincronização de Contas a Receber...")

            # 1. Buscar dados do Senior
            logger.info("Buscando dados do banco Senior...")
            dados_senior = senior_db.execute_query(QUERY_CONTAS_RECEBER)
            qtd_registros = len(dados_senior)
            logger.info(f"Encontrados {qtd_registros} registros no Senior")

            if qtd_registros == 0:
                tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'sucesso', 0, tempo_ms
                )
                return {
                    'success': True,
                    'registros_inseridos': 0,
                    'tempo_execucao_ms': tempo_ms,
                    'mensagem': 'Nenhum registro encontrado no Senior',
                    'log_id': log_id
                }

            # 2. Limpar tabela local
            logger.info("Limpando tabela contas_receber...")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE contas_receber")
                conn.commit()
                cursor.close()

            # 3. Preparar dados para inserção em massa
            logger.info(f"Preparando {qtd_registros} registros para inserção em massa...")
            insert_query = """
                INSERT INTO contas_receber (
                    id, CODEMP, CODFIL, CODCLI, NOMCLI, CIDCLI, BAICLI, TIPCLI, DATEMI,
                    NUMTIT, SITTIT, CODTPT, VLRABE, VLRORI, RECDEC, VCTPRO, VCTORI,
                    PERMUL, TOLMUL, DATPPT, RECSOM, RECVJM, RECVMM, RECVDM, PERDSC,
                    VLRDSC, TOLJRS, TIPJRS, PERJRS, JRSDIA, CODTNS, DESTNS, OBSTCR,
                    CODREP, NUMCTR, CODSNF, NUMNFV, CODFPG, USU_UNICLI, ULTPGT,
                    CODCCU, CTAFIN
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            # Função para converter valores para int (trata strings não-numéricas como 0)
            def to_int(value):
                if value is None:
                    return 0
                if isinstance(value, int):
                    return value
                if isinstance(value, str):
                    if value.strip().isdigit():
                        return int(value)
                    return 0
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return 0

            # Preparar lista de tuplas para executemany
            dados_inserir = []
            for row in dados_senior:
                dados_inserir.append((
                    str(uuid.uuid4()),
                    row.get('CODEMP'),
                    row.get('CODFIL'),
                    row.get('CODCLI'),
                    row.get('NOMCLI'),
                    row.get('CIDCLI'),
                    row.get('BAICLI'),
                    row.get('TIPCLI'),
                    row.get('DATEMI'),
                    row.get('NUMTIT'),
                    row.get('SITTIT'),
                    row.get('CODTPT'),
                    row.get('VLRABE'),
                    row.get('VLRORI'),
                    to_int(row.get('RECDEC')),
                    row.get('VCTPRO'),
                    row.get('VCTORI'),
                    row.get('PERMUL'),
                    row.get('TOLMUL'),
                    row.get('DATPPT'),
                    to_int(row.get('RECSOM')),
                    to_int(row.get('RECVJM')),
                    to_int(row.get('RECVMM')),
                    to_int(row.get('RECVDM')),
                    row.get('PERDSC'),
                    row.get('VLRDSC'),
                    row.get('TOLJRS'),
                    row.get('TIPJRS'),
                    row.get('PERJRS'),
                    row.get('JRSDIA'),
                    row.get('CODTNS'),
                    row.get('DESTNS'),
                    row.get('OBSTCR'),
                    row.get('CODREP'),
                    row.get('NUMCTR'),
                    row.get('CODSNF'),
                    row.get('NUMNFV'),
                    row.get('CODFPG'),
                    row.get('USU_UNICLI'),
                    row.get('ULTPGT'),
                    to_int(row.get('CODCCU')),
                    to_int(row.get('CTAFIN'))
                ))

            # 4. Inserir dados em massa com executemany (batches de 5000)
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
                cursor.close()
                logger.info(f"Total de {total_inseridos} registros inseridos com sucesso.")

            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            logger.info(f"Sincronização concluída em {tempo_ms}ms")

            # Atualizar log com sucesso
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'sucesso', qtd_registros, tempo_ms
            )

            return {
                'success': True,
                'registros_inseridos': qtd_registros,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Sincronização concluída com sucesso! {qtd_registros} registros inseridos.',
                'log_id': log_id
            }

        except Exception as e:
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            erro_msg = str(e)
            stack = traceback.format_exc()
            logger.error(f"Erro na sincronização: {erro_msg}")
            logger.error(stack)

            # Atualizar log com erro
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'erro', 0, tempo_ms, erro_msg, stack
            )

            return {
                'success': False,
                'registros_inseridos': 0,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Erro na sincronização: {erro_msg}',
                'log_id': log_id
            }

    @staticmethod
    def sincronizar_contas_pagar() -> Dict[str, Any]:
        """
        Sincroniza contas a pagar do Senior para o banco local
        Estratégia: Limpa tabela e reinsere todos os registros
        """
        inicio = datetime.now()
        log_id = SincronizacaoService.criar_log_sincronizacao('contas_pagar')

        try:
            logger.info("Iniciando sincronização de Contas a Pagar...")

            # 1. Buscar dados do Senior
            logger.info("Buscando dados do banco Senior...")
            dados_senior = senior_db.execute_query(QUERY_CONTAS_PAGAR)
            qtd_registros = len(dados_senior)
            logger.info(f"Encontrados {qtd_registros} registros no Senior")

            if qtd_registros == 0:
                tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'sucesso', 0, tempo_ms
                )
                return {
                    'success': True,
                    'registros_inseridos': 0,
                    'tempo_execucao_ms': tempo_ms,
                    'mensagem': 'Nenhum registro encontrado no Senior',
                    'log_id': log_id
                }

            # 2. Limpar tabela local
            logger.info("Limpando tabela contas_pagar...")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("TRUNCATE TABLE contas_pagar")
                conn.commit()
                cursor.close()

            # 3. Preparar dados para inserção em massa (TODOS os registros, sem filtrar duplicatas)
            logger.info(f"Preparando {qtd_registros} registros para inserção em massa...")
            insert_query = """
                INSERT INTO contas_pagar (
                    id, CODEMP, CODFIL, NUMTIT, CODFOR, NOMFOR, SEQMOV, CODTNS,
                    DATMOV, CODFPG, CODTPT, SITTIT, OBSTCP, VLRORI, DATEMI,
                    ULTPGT, VCTPRO, VLRRAT, CTAFIN, CODCCU, CTARED, VLRABE
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
            """

            # Preparar lista de tuplas para executemany
            dados_inserir = []
            for row in dados_senior:
                dados_inserir.append((
                    str(uuid.uuid4()),
                    row.get('CODEMP'),
                    row.get('CODFIL'),
                    row.get('NUMTIT'),
                    row.get('CODFOR'),
                    row.get('NOMFOR'),
                    row.get('SEQMOV'),
                    row.get('CODTNS'),
                    row.get('DATMOV'),
                    row.get('CODFPG'),
                    row.get('CODTPT'),
                    row.get('SITTIT'),
                    row.get('OBSTCP'),
                    row.get('VLRORI'),
                    row.get('DATEMI'),
                    row.get('ULTPGT'),
                    row.get('VCTPRO'),
                    row.get('VLRRAT'),
                    row.get('CTAFIN'),
                    row.get('CODCCU'),
                    row.get('CTARED'),
                    row.get('VLRABE')
                ))

            # 4. Inserir dados em massa com executemany (batches de 5000)
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
                cursor.close()
                logger.info(f"Total de {total_inseridos} registros inseridos com sucesso.")

            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            logger.info(f"Sincronização concluída em {tempo_ms}ms")

            # Atualizar log com sucesso
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'sucesso', qtd_registros, tempo_ms
            )

            return {
                'success': True,
                'registros_inseridos': qtd_registros,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Sincronização concluída com sucesso! {qtd_registros} registros inseridos.',
                'log_id': log_id
            }

        except Exception as e:
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            erro_msg = str(e)
            stack = traceback.format_exc()
            logger.error(f"Erro na sincronização: {erro_msg}")
            logger.error(stack)

            # Atualizar log com erro
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'erro', 0, tempo_ms, erro_msg, stack
            )

            return {
                'success': False,
                'registros_inseridos': 0,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Erro na sincronização: {erro_msg}',
                'log_id': log_id
            }

    @staticmethod
    def sincronizar_tudo() -> Dict[str, Any]:
        """Sincroniza todas as tabelas (contas a receber, contas a pagar, plano financeiro e centro de custo)"""
        inicio = datetime.now()
        log_id = SincronizacaoService.criar_log_sincronizacao('ambas')

        try:
            logger.info("=" * 80)
            logger.info("Iniciando sincronização completa...")
            logger.info("=" * 80)

            # Sincronizar dados gerais (primeiro, pois as outras dependem deles)

            # 1. Sincronizar plano financeiro
            logger.info("PASSO 1/4: Sincronizando Plano Financeiro...")
            try:
                resultado_plano = PlanoFinanceiroService.sincronizar()
                logger.info(f"✓ Plano Financeiro: {resultado_plano.get('mensagem', 'OK')}")
            except Exception as e:
                logger.error(f"✗ ERRO no Plano Financeiro: {str(e)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Falha na sincronização do Plano Financeiro: {str(e)}")

            # 2. Sincronizar centro de custo
            logger.info("PASSO 2/4: Sincronizando Centro de Custo...")
            try:
                resultado_centro_custo = CentroCustoService.sincronizar_centro_custo()
                logger.info(f"✓ Centro de Custo: {resultado_centro_custo.get('message', 'OK')}")
            except Exception as e:
                logger.error(f"✗ ERRO no Centro de Custo: {str(e)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Falha na sincronização do Centro de Custo: {str(e)}")

            # 3. Sincronizar contas a receber
            logger.info("PASSO 3/4: Sincronizando Contas a Receber...")
            try:
                resultado_receber = SincronizacaoService.sincronizar_contas_receber()
                logger.info(f"✓ Contas a Receber: {resultado_receber.get('mensagem', 'OK')}")
            except Exception as e:
                logger.error(f"✗ ERRO no Contas a Receber: {str(e)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Falha na sincronização de Contas a Receber: {str(e)}")

            # 4. Sincronizar contas a pagar
            logger.info("PASSO 4/4: Sincronizando Contas a Pagar...")
            try:
                resultado_pagar = SincronizacaoService.sincronizar_contas_pagar()
                logger.info(f"✓ Contas a Pagar: {resultado_pagar.get('mensagem', 'OK')}")
            except Exception as e:
                logger.error(f"✗ ERRO no Contas a Pagar: {str(e)}")
                logger.error(traceback.format_exc())
                raise Exception(f"Falha na sincronização de Contas a Pagar: {str(e)}")

            # Verificar se todas tiveram sucesso
            success = (resultado_plano.get('success', False) and
                      resultado_centro_custo.get('success', False) and
                      resultado_receber.get('success', False) and
                      resultado_pagar.get('success', False))

            total_registros = (resultado_plano.get('registros_sincronizados', 0) +
                             resultado_centro_custo.get('registros_inseridos', 0) +
                             resultado_receber.get('registros_inseridos', 0) +
                             resultado_pagar.get('registros_inseridos', 0))

            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)

            if success:
                mensagem = f'Sincronização completa concluída! Total de {total_registros} registros inseridos.'
                logger.info("=" * 80)
                logger.info(f"✓ SUCESSO: {mensagem}")
                logger.info("=" * 80)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'sucesso', total_registros, tempo_ms
                )
            else:
                mensagem = 'Sincronização completa com erros. Verifique os logs individuais.'
                logger.warning("=" * 80)
                logger.warning(f"⚠ AVISO: {mensagem}")
                logger.warning("=" * 80)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'erro', total_registros, tempo_ms, mensagem
                )

            return {
                'success': success,
                'registros_inseridos': total_registros,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': mensagem,
                'log_id': log_id,
                'detalhes': {
                    'plano_financeiro': resultado_plano,
                    'centro_custo': resultado_centro_custo,
                    'contas_receber': resultado_receber,
                    'contas_pagar': resultado_pagar
                }
            }

        except Exception as e:
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            erro_msg = str(e)
            stack = traceback.format_exc()
            logger.error("=" * 80)
            logger.error(f"✗ ERRO FATAL na sincronização completa: {erro_msg}")
            logger.error("=" * 80)
            logger.error(stack)

            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'erro', 0, tempo_ms, erro_msg, stack
            )

            return {
                'success': False,
                'registros_inseridos': 0,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Erro na sincronização completa: {erro_msg}',
                'log_id': log_id,
                'stack_trace': stack
            }

    @staticmethod
    def sincronizar_contas_receber_periodo(periodo: str) -> Dict[str, Any]:
        """
        Sincroniza contas a receber de um período específico usando a nova API do Senior
        Estratégia:
        1. Busca dados do Senior com todas as filiais (1001, 1002, 1003, 3001, 3002, 3003)
        2. Deleta registros do banco local do período baseado na DATA_AJUSTADA
        3. Insere os novos registros

        Args:
            periodo: Período no formato YYYY-MM (ex: 2025-11)
        """
        from services.contas_receber_senior_service import ContasReceberSeniorService

        inicio = datetime.now()
        log_id = SincronizacaoService.criar_log_sincronizacao('contas_receber')

        try:
            logger.info(f"=== Iniciando sincronização de Contas a Receber para período {periodo} ===")

            # Filiais fixas (todas exceto 2002)
            filiais = ['1001', '1002', '1003', '3001', '3002', '3003']
            logger.info(f"Filiais: {filiais}")

            # 1. Buscar dados do Senior usando a nova API
            logger.info("Buscando dados do banco Senior...")
            try:
                dados_senior = ContasReceberSeniorService.obter_contas_receber_do_senior(periodo, filiais)
                qtd_registros = len(dados_senior)
                logger.info(f"Encontrados {qtd_registros} registros no Senior")
            except Exception as e:
                logger.error(f"ERRO ao buscar dados do Senior: {str(e)}")
                raise

            if qtd_registros == 0:
                tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'sucesso', 0, tempo_ms
                )
                return {
                    'success': True,
                    'tipo': 'contas_receber',
                    'registros_inseridos': 0,
                    'tempo_execucao_ms': tempo_ms,
                    'mensagem': f'Nenhum registro encontrado no Senior para o período {periodo}',
                    'log_id': log_id
                }

            # 2. Deletar registros do banco local baseado na DATA_AJUSTADA do período
            logger.info(f"Deletando registros do período {periodo}...")
            delete_query = """
            DELETE FROM contas_receber
            WHERE CONVERT(VARCHAR(7),
                CASE
                    WHEN DATEPART(WEEKDAY, DATPPT) = 6 THEN DATEADD(DAY, 3, DATPPT)  -- Sexta → +3
                    WHEN DATEPART(WEEKDAY, DATPPT) = 7 THEN DATEADD(DAY, 3, DATPPT)  -- Sábado → +3
                    WHEN DATEPART(WEEKDAY, DATPPT) = 1 THEN DATEADD(DAY, 2, DATPPT)  -- Domingo → +2
                    WHEN DATEPART(WEEKDAY, DATPPT) = 2 THEN DATEADD(DAY, 1, DATPPT)  -- Segunda → +1
                    WHEN DATEPART(WEEKDAY, DATPPT) = 3 THEN DATEADD(DAY, 1, DATPPT)  -- Terça → +1
                    WHEN DATEPART(WEEKDAY, DATPPT) = 4 THEN DATEADD(DAY, 1, DATPPT)  -- Quarta → +1
                    WHEN DATEPART(WEEKDAY, DATPPT) = 5 THEN DATEADD(DAY, 1, DATPPT)  -- Quinta → +1
                    ELSE DATPPT
                END, 23) = %s
            AND CODFIL IN ('1001', '1002', '1003', '3001', '3002', '3003')
            """

            try:
                logger.info(f"Query DELETE: {delete_query}")
                logger.info(f"Parâmetro: {periodo}")

                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(delete_query, (periodo,))
                    registros_deletados = cursor.rowcount
                    conn.commit()
                    cursor.close()

                logger.info(f"Deletados {registros_deletados} registros do banco local")
            except Exception as e:
                logger.error(f"ERRO ao deletar registros: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                raise

            # 3. Inserir novos registros
            logger.info("Inserindo novos registros...")
            insert_query = """
                INSERT INTO contas_receber (
                    id, CODEMP, CODFIL, CODCLI, NOMCLI, CIDCLI, BAICLI, TIPCLI,
                    NUMTIT, SITTIT, CODTPT, VLRABE, VLRORI, RECDEC, VCTPRO, VCTORI,
                    DATPPT, DATEMI, CODTNS, DESTNS, CODCCU, CTAFIN, USU_UNICLI, ULTPGT,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s
                )
            """

            registros_inseridos = 0
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for registro in dados_senior:
                    try:
                        # Gera ID único
                        registro_id = str(uuid.uuid4())
                        now = datetime.now()

                        cursor.execute(insert_query, (
                            registro_id,
                            registro.get('CODEMP'),
                            registro.get('CODFIL'),
                            registro.get('CODCLI'),
                            registro.get('NOMCLI'),
                            registro.get('CIDCLI'),
                            registro.get('BAICLI'),
                            registro.get('TIPCLI'),
                            registro.get('NUMTIT'),
                            registro.get('SITTIT'),
                            registro.get('CODTPT'),
                            registro.get('VLRABE'),
                            registro.get('VLRORI'),
                            registro.get('RECDEC'),
                            registro.get('VCTPRO'),
                            registro.get('VCTORI'),
                            registro.get('DATPPT'),
                            registro.get('DATEMI'),
                            registro.get('CODTNS'),
                            registro.get('DESTNS'),
                            registro.get('CODCCU'),
                            registro.get('CTAFIN'),
                            registro.get('USU_UNICLI'),
                            registro.get('ULTPGT'),
                            now,
                            now
                        ))
                        registros_inseridos += 1
                    except Exception as e:
                        logger.error(f"Erro ao inserir registro {registro.get('NUMTIT')}: {str(e)}")
                        continue

                conn.commit()
                cursor.close()

            logger.info(f"Inseridos {registros_inseridos} registros no banco local")

            # Finalizar
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'sucesso', registros_inseridos, tempo_ms
            )

            return {
                'success': True,
                'tipo': 'contas_receber',
                'registros_inseridos': registros_inseridos,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Sincronização concluída para {periodo}. {registros_inseridos} registros inseridos, {registros_deletados} deletados.',
                'log_id': log_id
            }

        except Exception as e:
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            erro_msg = str(e)
            stack = traceback.format_exc()

            logger.error(f"Erro ao sincronizar: {erro_msg}")
            logger.error(stack)

            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'erro', 0, tempo_ms, erro_msg, stack
            )

            return {
                'success': False,
                'tipo': 'contas_receber',
                'registros_inseridos': 0,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Erro na sincronização: {erro_msg}',
                'log_id': log_id
            }

    @staticmethod
    def sincronizar_contas_pagar_periodo(periodo: str) -> Dict[str, Any]:
        """
        Sincroniza contas a pagar de um período específico usando a nova API do Senior
        Estratégia:
        1. Busca dados do Senior dos últimos 4 meses (vigente + 3 anteriores) com todas as filiais
        2. Aplica projeção com média dos últimos 3 meses
        3. Deleta registros do banco local dos 4 meses baseado na DATA_AJUSTADA
        4. Insere os novos registros

        Args:
            periodo: Período no formato YYYY-MM (ex: 2025-11)
        """
        from services.contas_pagar_senior_service import ContasPagarSeniorService

        inicio = datetime.now()
        log_id = SincronizacaoService.criar_log_sincronizacao('contas_pagar')

        try:
            logger.info(f"=== Iniciando sincronização de Contas a Pagar para período {periodo} ===")

            # Filiais fixas (todas exceto 2002)
            filiais = ['1001', '1002', '1003', '3001', '3002', '3003']
            logger.info(f"Filiais: {filiais}")

            # 1. Buscar dados do Senior usando a nova API (4 meses)
            logger.info("Buscando dados do banco Senior...")
            try:
                dados_senior = ContasPagarSeniorService.obter_contas_pagar_do_senior(periodo, filiais)
                qtd_registros = len(dados_senior)
                logger.info(f"Encontrados {qtd_registros} registros no Senior")

                # IMPORTANTE: Salvamos TODOS os dados reais, sem projeção
                # A projeção será aplicada apenas na visualização/relatórios se necessário
            except Exception as e:
                logger.error(f"ERRO ao buscar dados do Senior: {str(e)}")
                raise

            if qtd_registros == 0:
                tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
                SincronizacaoService.atualizar_log_sincronizacao(
                    log_id, 'sucesso', 0, tempo_ms
                )
                return {
                    'success': True,
                    'tipo': 'contas_pagar',
                    'registros_inseridos': 0,
                    'tempo_execucao_ms': tempo_ms,
                    'mensagem': f'Nenhum registro encontrado no Senior para o período {periodo}',
                    'log_id': log_id
                }

            # 2. Deletar registros do banco local dos 4 meses baseado na DATA_AJUSTADA
            logger.info(f"Deletando registros dos últimos 4 meses...")

            # Calcula os 4 meses que serão deletados
            from dateutil.relativedelta import relativedelta
            ano, mes = map(int, periodo.split('-'))
            data_inicio_delete = datetime(ano, mes, 1) - relativedelta(months=3)
            data_fim_delete = datetime(ano, mes, 28)  # Até dia 28 do mês vigente

            delete_query = """
            DELETE FROM contas_pagar
            WHERE CONVERT(VARCHAR(10),
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 6 THEN DATEADD(DAY, 2, VCTPRO)  -- Sábado → +2
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 1, VCTPRO)  -- Domingo → +1
                    ELSE VCTPRO
                END, 23) >= %s
            AND CONVERT(VARCHAR(10),
                CASE
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 6 THEN DATEADD(DAY, 2, VCTPRO)
                    WHEN DATEPART(WEEKDAY, VCTPRO) = 7 THEN DATEADD(DAY, 1, VCTPRO)
                    ELSE VCTPRO
                END, 23) <= %s
            AND CODFIL IN ('1001', '1002', '1003', '3001', '3002', '3003')
            """

            try:
                logger.info(f"Deletando de {data_inicio_delete.strftime('%Y-%m-%d')} até {data_fim_delete.strftime('%Y-%m-%d')}")

                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(delete_query, (
                        data_inicio_delete.strftime('%Y-%m-%d'),
                        data_fim_delete.strftime('%Y-%m-%d')
                    ))
                    registros_deletados = cursor.rowcount
                    conn.commit()
                    cursor.close()

                logger.info(f"Deletados {registros_deletados} registros do banco local")
            except Exception as e:
                logger.error(f"ERRO ao deletar registros: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                raise

            # 3. Inserir novos registros
            logger.info("Inserindo novos registros...")
            insert_query = """
                INSERT INTO contas_pagar (
                    id, CODEMP, CODFIL, CODFOR, NOMFOR, NUMTIT, SEQMOV,
                    CODTNS, DATMOV, CODFPG, CODTPT, SITTIT, OBSTCP,
                    VLRORI, DATEMI, ULTPGT, VCTPRO, VLRRAT, CTAFIN,
                    CODCCU, CTARED, VLRABE, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            registros_inseridos = 0
            registros_com_erro = 0
            erros_detalhados = []

            with db.get_connection() as conn:
                cursor = conn.cursor()

                for registro in dados_senior:
                    try:
                        # Gera ID único
                        registro_id = str(uuid.uuid4())
                        now = datetime.now()

                        cursor.execute(insert_query, (
                            registro_id,
                            registro.get('CODEMP'),
                            registro.get('CODFIL'),
                            registro.get('CODFOR'),
                            registro.get('NOMFOR'),
                            registro.get('NUMTIT'),
                            registro.get('SEQMOV'),
                            registro.get('CODTNS'),
                            registro.get('DATMOV'),
                            registro.get('CODFPG'),
                            registro.get('CODTPT'),
                            registro.get('SITTIT'),
                            registro.get('OBSTCP'),
                            registro.get('VLRORI'),
                            registro.get('DATEMI'),
                            registro.get('ULTPGT'),
                            registro.get('VCTPRO'),
                            registro.get('VLRRAT'),
                            registro.get('CTAFIN'),
                            registro.get('CODCCU'),
                            registro.get('CTARED'),
                            registro.get('VLRABE'),
                            now,
                            now
                        ))
                        registros_inseridos += 1
                    except Exception as e:
                        registros_com_erro += 1
                        erro_msg = f"Erro ao inserir registro {registro.get('NUMTIT')} (SEQMOV: {registro.get('SEQMOV')}): {str(e)}"
                        logger.error(erro_msg)
                        if len(erros_detalhados) < 10:  # Guarda apenas os 10 primeiros erros para não lotar o log
                            erros_detalhados.append(erro_msg)
                        continue

                conn.commit()
                cursor.close()

            logger.info(f"Inseridos {registros_inseridos} registros no banco local")
            logger.info(f"Total de registros com erro: {registros_com_erro}")
            if erros_detalhados:
                logger.error(f"Primeiros erros encontrados:")
                for erro in erros_detalhados:
                    logger.error(f"  - {erro}")

            # Finalizar
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'sucesso', registros_inseridos, tempo_ms
            )

            return {
                'success': True,
                'tipo': 'contas_pagar',
                'registros_inseridos': registros_inseridos,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Sincronização concluída para {periodo}. {registros_inseridos} registros inseridos, {registros_deletados} deletados.',
                'log_id': log_id
            }

        except Exception as e:
            tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
            erro_msg = str(e)
            stack = traceback.format_exc()

            logger.error(f"Erro ao sincronizar: {erro_msg}")
            logger.error(stack)

            SincronizacaoService.atualizar_log_sincronizacao(
                log_id, 'erro', 0, tempo_ms, erro_msg, stack
            )

            return {
                'success': False,
                'tipo': 'contas_pagar',
                'registros_inseridos': 0,
                'tempo_execucao_ms': tempo_ms,
                'mensagem': f'Erro na sincronização: {erro_msg}',
                'log_id': log_id
            }

    @staticmethod
    def obter_status_ultima_sincronizacao(tipo: str = None) -> Dict[str, Any]:
        """Obtém status da última sincronização"""
        query = """
            SELECT TOP 1 *
            FROM log_sincronizacao
        """

        if tipo:
            query += " WHERE tipo = %s"
            query += " ORDER BY data_hora_inicio DESC"
            result = db.execute_single(query, (tipo,))
        else:
            query += " ORDER BY data_hora_inicio DESC"
            result = db.execute_single(query)

        if not result:
            return {
                'ultima_sincronizacao': None,
                'tipo': None,
                'status': None,
                'registros_inseridos': None,
                'tempo_execucao_ms': None,
                'mensagem_erro': None
            }

        return {
            'ultima_sincronizacao': result.get('data_hora_inicio'),
            'tipo': result.get('tipo'),
            'status': result.get('status'),
            'registros_inseridos': result.get('registros_inseridos'),
            'tempo_execucao_ms': result.get('tempo_execucao_ms'),
            'mensagem_erro': result.get('mensagem_erro')
        }
