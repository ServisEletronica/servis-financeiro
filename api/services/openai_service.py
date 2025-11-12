"""
Serviço para integração com OpenAI Vision API
Responsável por extrair dados de calendários Cielo usando OCR
"""

import base64
import json
from typing import Dict, List, Optional
from openai import OpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """Serviço para operações com OpenAI"""

    def __init__(self):
        """Inicializa o cliente OpenAI"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Modelo com suporte a visão

    @staticmethod
    def encode_image_to_base64(image_bytes: bytes) -> str:
        """
        Converte bytes de imagem para base64

        Args:
            image_bytes: Bytes da imagem

        Returns:
            String base64 da imagem
        """
        return base64.b64encode(image_bytes).decode('utf-8')

    def extrair_dados_calendario_cielo(self, image_bytes: bytes) -> Dict:
        """
        Extrai dados de um calendário Cielo usando OpenAI Vision

        Args:
            image_bytes: Bytes da imagem do calendário

        Returns:
            Dict com estrutura:
            {
                "mes_referencia": "2025-11",
                "estabelecimento": "1071167917",
                "recebiveis": [
                    {"data": "2025-11-03", "valor": 5830.47},
                    {"data": "2025-11-04", "valor": 1906.52},
                    ...
                ]
            }

        Raises:
            Exception: Se houver erro na extração
        """
        try:
            # Converte imagem para base64
            base64_image = self.encode_image_to_base64(image_bytes)

            # Prompt otimizado para extração de dados do calendário Cielo
            prompt = """
Analise esta imagem de um calendário de recebíveis da Cielo e extraia os dados APENAS dos valores líquidos.

IMPORTANTE:
1. Use a aba "Valores líquidos" mostrada na imagem
2. Extraia APENAS os dias que têm valores maiores que R$ 0,00
3. O número do estabelecimento está no canto direito (exemplo: 1071167917)
4. O mês e ano estão no centro do calendário (exemplo: Novembro • 2025)

Retorne um JSON válido no seguinte formato EXATO (sem explicações ou texto adicional):

{
    "mes_referencia": "YYYY-MM",
    "estabelecimento": "número do estabelecimento",
    "recebiveis": [
        {
            "data": "YYYY-MM-DD",
            "valor": número sem formatação
        }
    ]
}

REGRAS IMPORTANTES:
- Valores devem ser números decimais (use ponto como separador decimal)
- Ignore R$, pontos e vírgulas nos valores
- Exemplo: R$ 5.830,47 deve virar 5830.47
- Ignore dias com R$ 0,00
- A data deve estar no formato YYYY-MM-DD
- Retorne APENAS o JSON, sem markdown, sem ```json, sem explicações
"""

            # Faz a chamada para a API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Baixa temperatura para respostas mais determinísticas
            )

            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content.strip()

            # Remove possíveis marcadores de código se houver
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Parse do JSON
            dados = json.loads(content)

            # Validação básica
            if not all(key in dados for key in ["mes_referencia", "estabelecimento", "recebiveis"]):
                raise ValueError("JSON retornado não contém todas as chaves necessárias")

            if not isinstance(dados["recebiveis"], list):
                raise ValueError("Campo 'recebiveis' deve ser uma lista")

            # Validação de cada recebível
            for rec in dados["recebiveis"]:
                if not all(key in rec for key in ["data", "valor"]):
                    raise ValueError(f"Recebível inválido: {rec}")
                if not isinstance(rec["valor"], (int, float)):
                    raise ValueError(f"Valor inválido: {rec['valor']}")

            logger.info(f"Dados extraídos com sucesso: {len(dados['recebiveis'])} recebíveis encontrados")
            return dados

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON retornado pela OpenAI: {e}")
            logger.error(f"Conteúdo recebido: {content}")
            raise Exception(f"Erro ao interpretar resposta da OpenAI: {str(e)}")

        except Exception as e:
            logger.error(f"Erro ao extrair dados do calendário: {e}")
            raise Exception(f"Erro ao processar imagem: {str(e)}")

    def extrair_multiplos_calendarios(self, images_bytes_list: List[bytes]) -> List[Dict]:
        """
        Extrai dados de múltiplos calendários

        Args:
            images_bytes_list: Lista de bytes de imagens

        Returns:
            Lista de dicionários com dados extraídos
        """
        resultados = []
        erros = []

        for idx, image_bytes in enumerate(images_bytes_list):
            try:
                dados = self.extrair_dados_calendario_cielo(image_bytes)
                resultados.append({
                    "sucesso": True,
                    "dados": dados,
                    "indice": idx
                })
            except Exception as e:
                logger.error(f"Erro ao processar imagem {idx}: {e}")
                erros.append({
                    "sucesso": False,
                    "erro": str(e),
                    "indice": idx
                })

        return resultados + erros
