"""
Rotas para gerenciamento de recebíveis de cartão
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from services.recebiveis_cartao_service import RecebiveisCartaoService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recebiveis-cartao", tags=["Recebíveis Cartão"])


@router.post("/upload")
async def upload_calendarios(files: List[UploadFile] = File(...)):
    """
    Faz upload e processa calendários Cielo

    Args:
        files: Lista de arquivos de imagem dos calendários

    Returns:
        Resumo do processamento
    """
    try:
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
        resultado = RecebiveisCartaoService.processar_upload(images_bytes)

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
    data_fim: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    """
    Obtém recebíveis agrupados por data em um período

    Args:
        data_inicio: Data inicial no formato YYYY-MM-DD
        data_fim: Data final no formato YYYY-MM-DD

    Returns:
        Lista de recebíveis por data
    """
    try:
        recebiveis = RecebiveisCartaoService.obter_recebiveis_por_periodo(data_inicio, data_fim)
        return recebiveis

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
