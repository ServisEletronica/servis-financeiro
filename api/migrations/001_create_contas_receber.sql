-- ================================================
-- Migration: 001_create_contas_receber
-- Descrição: Cria tabela contas_receber no banco local
-- Data: 2025-01-31
-- ================================================

-- Cria tabela se não existir
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[contas_receber]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[contas_receber] (
        -- Identificador único gerado pela aplicação
        [id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),

        -- Campos da empresa/filial
        [CODEMP] INT NOT NULL,
        [CODFIL] INT NOT NULL,

        -- Dados do cliente
        [CODCLI] INT NOT NULL,
        [NOMCLI] VARCHAR(150) NULL,
        [CIDCLI] VARCHAR(100) NULL,
        [BAICLI] VARCHAR(100) NULL,
        [TIPCLI] VARCHAR(10) NULL,
        [USU_UNICLI] VARCHAR(50) NULL,

        -- Dados do título
        [NUMTIT] VARCHAR(20) NOT NULL,
        [SITTIT] VARCHAR(2) NULL,
        [CODTPT] VARCHAR(10) NULL,
        [CODTNS] VARCHAR(10) NULL,
        [DESTNS] VARCHAR(100) NULL,

        -- Valores
        [VLRABE] DECIMAL(18, 2) NULL DEFAULT 0,
        [VLRORI] DECIMAL(18, 2) NULL DEFAULT 0,
        [VLRDSC] DECIMAL(18, 2) NULL DEFAULT 0,

        -- Percentuais
        [PERMUL] DECIMAL(5, 2) NULL DEFAULT 0,
        [PERDSC] DECIMAL(5, 2) NULL DEFAULT 0,
        [PERJRS] DECIMAL(5, 2) NULL DEFAULT 0,

        -- Configurações
        [RECDEC] INT NULL DEFAULT 0,
        [RECSOM] INT NULL DEFAULT 0,
        [RECVJM] INT NULL DEFAULT 0,
        [RECVMM] INT NULL DEFAULT 0,
        [RECVDM] INT NULL DEFAULT 0,
        [TOLJRS] DECIMAL(5, 2) NULL DEFAULT 0,
        [TOLMUL] DECIMAL(5, 2) NULL DEFAULT 0,
        [TIPJRS] VARCHAR(1) NULL,
        [JRSDIA] DECIMAL(5, 2) NULL DEFAULT 0,

        -- Datas
        [DATEMI] DATE NULL,
        [VCTPRO] DATE NULL,
        [VCTORI] DATE NULL,
        [DATPPT] DATE NULL,
        [ULTPGT] VARCHAR(10) NULL,

        -- Observações e outros
        [OBSTCR] VARCHAR(MAX) NULL,
        [CODREP] VARCHAR(10) NULL,
        [NUMCTR] VARCHAR(20) NULL,
        [CODSNF] VARCHAR(10) NULL,
        [NUMNFV] VARCHAR(20) NULL,
        [CODFPG] VARCHAR(10) NULL,

        -- Centro de custo e conta financeira
        [CODCCU] INT NULL DEFAULT 0,
        [CTAFIN] INT NULL DEFAULT 0,

        -- Controle de auditoria
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
    );

    -- Cria índices para melhor performance
    CREATE INDEX [IX_contas_receber_empresa_filial] ON [dbo].[contas_receber] ([CODEMP], [CODFIL]);
    CREATE INDEX [IX_contas_receber_cliente] ON [dbo].[contas_receber] ([CODCLI]);
    CREATE INDEX [IX_contas_receber_numtit] ON [dbo].[contas_receber] ([NUMTIT]);
    CREATE INDEX [IX_contas_receber_vctpro] ON [dbo].[contas_receber] ([VCTPRO]);
    CREATE INDEX [IX_contas_receber_sittit] ON [dbo].[contas_receber] ([SITTIT]);

    -- Cria índice composto para chave única (pode ser usado para detectar duplicatas)
    CREATE UNIQUE INDEX [IX_contas_receber_unique] ON [dbo].[contas_receber]
        ([CODEMP], [CODFIL], [NUMTIT], [CODTPT], [CODCLI]);

    PRINT 'Tabela contas_receber criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela contas_receber já existe.';
END
GO
