"""
Rotas para gerenciamento de recebíveis de cartão
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from services.recebiveis_cartao_service import RecebiveisCartaoService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recebiveis-cartao", tags=["Recebíveis Cartão"])


class RecebidoManualRequest(BaseModel):
    data_recebimento: str
    valor: float
    estabelecimento: str
    mes_referencia: str


@router.post("/upload")
async def upload_calendarios(
    files: List[UploadFile] = File(...),
    status: str = Query('projetado', description="Status: projetado ou recebido")
):
    """
    Faz upload e processa calendários Cielo

    Args:
        files: Lista de arquivos de imagem dos calendários
        status: Status dos recebíveis (projetado ou recebido)

    Returns:
        Resumo do processamento
    """
    try:
        # Valida status
        if status not in ['projetado', 'recebido']:
            raise HTTPException(status_code=400, detail="Status deve ser 'projetado' ou 'recebido'")

        # Validações
        if not files:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado")

        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Máximo de 10 arquivos por vez")

        # Validar tipos de arquivo
        allowed_types = ["image/png", "image/jpeg", "image/jpg"]
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de arquivo não permitido: {file.content_type}. Apenas PNG e JPEG são aceitos."
                )

        # Ler bytes das imagens
        images_bytes = []
        for file in files:
            content = await file.read()

            # Validar tamanho (máx 10MB por arquivo)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo {file.filename} muito grande. Máximo: 10MB"
                )

            images_bytes.append(content)

        # Processar upload
        resultado = RecebiveisCartaoService.processar_upload(images_bytes, status=status)

        if not resultado["sucesso"]:
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Erro ao processar imagens",
                    "data": resultado
                }
            )

        return {
            "message": f"{resultado['total_registros_inseridos']} recebíveis processados com sucesso",
            "data": resultado
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em upload_calendarios: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar upload: {str(e)}")


@router.get("")
async def obter_recebiveis(
    data_inicio: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data final (YYYY-MM-DD)"),
    estabelecimentos: Optional[str] = Query(None, description="Códigos de estabelecimento separados por vírgula"),
    status: str = Query('projetado', description="Status: projetado ou recebido")
):
    """
    Obtém recebíveis agrupados por data em um período

    Args:
        data_inicio: Data inicial no formato YYYY-MM-DD
        data_fim: Data final no formato YYYY-MM-DD
        estabelecimentos: Códigos de estabelecimento separados por vírgula (opcional)
        status: Status dos recebíveis (projetado ou recebido)

    Returns:
        Lista de recebíveis por data
    """
    try:
        # Valida status
        if status not in ['projetado', 'recebido']:
            raise HTTPException(status_code=400, detail="Status deve ser 'projetado' ou 'recebido'")

        # Converte string de estabelecimentos em lista
        lista_estabelecimentos = None
        if estabelecimentos:
            lista_estabelecimentos = [e.strip() for e in estabelecimentos.split(',') if e.strip()]

        recebiveis = RecebiveisCartaoService.obter_recebiveis_por_periodo(
            data_inicio,
            data_fim,
            lista_estabelecimentos,
            status
        )
        return recebiveis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em obter_recebiveis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detalhado/{mes_referencia}")
async def obter_recebiveis_detalhados(mes_referencia: str):
    """
    Obtém todos os recebíveis de um mês com detalhes

    Args:
        mes_referencia: Mês no formato YYYY-MM

    Returns:
        Lista de recebíveis com todos os campos
    """
    try:
        recebiveis = RecebiveisCartaoService.obter_recebiveis_detalhados(mes_referencia)
        return recebiveis

    except Exception as e:
        logger.error(f"Erro em obter_recebiveis_detalhados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estatisticas/{mes_referencia}")
async def obter_estatisticas(mes_referencia: str):
    """
    Obtém estatísticas dos recebíveis de um mês

    Args:
        mes_referencia: Mês no formato YYYY-MM

    Returns:
        Estatísticas do mês
    """
    try:
        estatisticas = RecebiveisCartaoService.obter_estatisticas_mes(mes_referencia)
        return estatisticas

    except Exception as e:
        logger.error(f"Erro em obter_estatisticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{mes_referencia}")
async def limpar_dados_mes(
    mes_referencia: str,
    estabelecimento: Optional[str] = Query(None, description="Código do estabelecimento (opcional)")
):
    """
    Remove dados de um mês específico

    Args:
        mes_referencia: Mês no formato YYYY-MM
        estabelecimento: Código do estabelecimento (opcional)

    Returns:
        Confirmação da exclusão
    """
    try:
        count = RecebiveisCartaoService.limpar_dados_mes(mes_referencia, estabelecimento)

        if estabelecimento:
            mensagem = f"Dados do estabelecimento {estabelecimento} do mês {mes_referencia} removidos"
        else:
            mensagem = f"Todos os dados do mês {mes_referencia} removidos"

        return {
            "message": mensagem,
            "registros_removidos": count
        }

    except Exception as e:
        logger.error(f"Erro em limpar_dados_mes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual")
async def inserir_recebido_manual(data: RecebidoManualRequest):
    """
    Insere ou atualiza um recebível de cartão manualmente com status 'recebido'

    Args:
        data: Dados do recebível (data_recebimento, valor, estabelecimento, mes_referencia)

    Returns:
        Confirmação da inserção/atualização
    """
    try:
        RecebiveisCartaoService.upsert_recebivel(
            data_recebimento=data.data_recebimento,
            valor=data.valor,
            estabelecimento=data.estabelecimento,
            mes_referencia=data.mes_referencia,
            status='recebido',
            usuario_upload='manual'
        )

        return {
            "message": "Recebível registrado com sucesso",
            "data": {
                "data_recebimento": data.data_recebimento,
                "valor": data.valor,
                "estabelecimento": data.estabelecimento,
                "status": "recebido"
            }
        }

    except Exception as e:
        logger.error(f"Erro em inserir_recebido_manual: {e}")
        raise HTTPException(status_code=500, detail=str(e))
