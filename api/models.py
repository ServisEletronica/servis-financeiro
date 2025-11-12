from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


# ========================================
# Modelos para Banco Local (Sincronização)
# ========================================

class ContasReceberDB(BaseModel):
    """Modelo para tabela contas_receber no banco local"""
    id: Optional[UUID] = None
    CODEMP: int
    CODFIL: int
    CODCLI: int
    NOMCLI: Optional[str] = None
    CIDCLI: Optional[str] = None
    BAICLI: Optional[str] = None
    TIPCLI: Optional[str] = None
    DATEMI: Optional[date] = None
    NUMTIT: str
    SITTIT: Optional[str] = None
    CODTPT: Optional[str] = None
    VLRABE: Optional[float] = 0
    VLRORI: Optional[float] = 0
    RECDEC: Optional[int] = 0
    VCTPRO: Optional[date] = None
    VCTORI: Optional[date] = None
    PERMUL: Optional[float] = 0
    TOLMUL: Optional[float] = 0
    DATPPT: Optional[date] = None
    RECSOM: Optional[int] = 0
    RECVJM: Optional[int] = 0
    RECVMM: Optional[int] = 0
    RECVDM: Optional[int] = 0
    PERDSC: Optional[float] = 0
    VLRDSC: Optional[float] = 0
    TOLJRS: Optional[float] = 0
    TIPJRS: Optional[str] = None
    PERJRS: Optional[float] = 0
    JRSDIA: Optional[float] = 0
    CODTNS: Optional[str] = None
    DESTNS: Optional[str] = None
    OBSTCR: Optional[str] = None
    CODREP: Optional[str] = None
    NUMCTR: Optional[str] = None
    CODSNF: Optional[str] = None
    NUMNFV: Optional[str] = None
    CODFPG: Optional[str] = None
    USU_UNICLI: Optional[str] = None
    ULTPGT: Optional[str] = None
    CODCCU: Optional[int] = 0
    CTAFIN: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContasPagarDB(BaseModel):
    """Modelo para tabela contas_pagar no banco local"""
    id: Optional[UUID] = None
    CODEMP: int
    CODFIL: int
    NUMTIT: str
    CODFOR: int
    NOMFOR: Optional[str] = None
    SEQMOV: int
    CODTNS: Optional[str] = None
    DATMOV: Optional[date] = None
    CODFPG: Optional[str] = None
    CODTPT: Optional[str] = None
    SITTIT: Optional[str] = None
    OBSTCP: Optional[str] = None
    VLRORI: Optional[float] = 0
    DATEMI: Optional[date] = None
    ULTPGT: Optional[date] = None
    VCTPRO: Optional[date] = None
    VLRRAT: Optional[float] = 0
    CTAFIN: Optional[int] = 0
    CODCCU: Optional[int] = 0
    CTARED: Optional[int] = 0
    VLRABE: Optional[float] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CentroCustoDB(BaseModel):
    """Modelo para tabela centro_custo no banco local"""
    id: Optional[UUID] = None
    CODMPC: int
    CTARED: int
    CLACTA: Optional[str] = None
    DESCTA: Optional[str] = None
    ANASIN: Optional[str] = None
    NATCTA: Optional[str] = None
    NIVCTA: Optional[int] = None
    CODCCU: int
    TIPCCU: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogSincronizacao(BaseModel):
    """Modelo para tabela log_sincronizacao"""
    id: Optional[UUID] = None
    tipo: str  # 'contas_receber', 'contas_pagar', 'ambas'
    data_hora_inicio: datetime
    data_hora_fim: Optional[datetime] = None
    status: str  # 'sucesso', 'erro', 'em_andamento'
    registros_inseridos: Optional[int] = 0
    tempo_execucao_ms: Optional[int] = None
    mensagem_erro: Optional[str] = None
    stack_trace: Optional[str] = None
    executado_por: Optional[str] = None
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True


# ========================================
# Modelos Antigos (Mantidos para compatibilidade)
# ========================================

class ContaReceber(BaseModel):
    codemp: int
    codfil: int
    codcli: int
    nomcli: str
    numtit: str
    sittit: str
    codtpt: str
    vlrabe: float
    vlrori: float
    recdec: int
    vctpro: Optional[date]
    vctori: Optional[date]
    datemi: Optional[date]
    destns: Optional[str]
    valor_calculado: float


class ContaPagar(BaseModel):
    codemp: int
    codfil: int
    numtit: str
    codfor: int
    nomfor: str
    seqmov: int
    codtns: str
    sittit: str
    vlrori: float
    vlrabe: float
    vlrrat: float
    vctpro: Optional[date]
    datemi: Optional[date]
    ctafin: Optional[int]
    codccu: Optional[int]
    valor_calculado: float


class ResumoFinanceiro(BaseModel):
    saldo_atual: float
    receitas_total: float
    despesas_total: float
    saldo_mes: float
    periodo_inicio: date
    periodo_fim: date
    percentual_mudanca_saldo: float
    percentual_mudanca_receita: float
    percentual_mudanca_despesa: float


class DadosGrafico(BaseModel):
    mes: str
    receitas: float
    despesas: float
    saldo: float


class Transacao(BaseModel):
    id: int
    date: str
    description: str
    category: str
    type: str  # 'receita' ou 'despesa'
    value: float


# ========================================
# Modelos de Resposta da API
# ========================================

class SincronizacaoResponse(BaseModel):
    """Resposta da sincronização"""
    success: bool
    tipo: str
    registros_inseridos: int
    tempo_execucao_ms: int
    mensagem: str
    log_id: Optional[UUID] = None


class StatusSincronizacaoResponse(BaseModel):
    """Status da última sincronização"""
    ultima_sincronizacao: Optional[datetime] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    registros_inseridos: Optional[int] = None
    tempo_execucao_ms: Optional[int] = None
    mensagem_erro: Optional[str] = None
