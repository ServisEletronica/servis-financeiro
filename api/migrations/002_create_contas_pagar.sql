-- ================================================
-- Migration: 002_create_contas_pagar
-- Descrição: Cria tabela contas_pagar no banco local
-- Data: 2025-01-31
-- ================================================

-- Cria tabela se não existir
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[contas_pagar]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[contas_pagar] (
        -- Identificador único gerado pela aplicação
        [id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),

        -- Campos da empresa/filial
        [CODEMP] INT NOT NULL,
        [CODFIL] INT NOT NULL,

        -- Dados do título
        [NUMTIT] VARCHAR(20) NOT NULL,
        [SEQMOV] INT NOT NULL,
        [CODTPT] VARCHAR(10) NULL,
        [SITTIT] VARCHAR(2) NULL,

        -- Dados do fornecedor
        [CODFOR] INT NOT NULL,
        [NOMFOR] VARCHAR(100) NULL,

        -- Transação e forma de pagamento
        [CODTNS] VARCHAR(10) NULL,
        [CODFPG] VARCHAR(10) NULL,

        -- Valores
        [VLRORI] DECIMAL(18, 2) NULL DEFAULT 0,
        [VLRABE] DECIMAL(18, 2) NULL DEFAULT 0,
        [VLRRAT] DECIMAL(18, 2) NULL DEFAULT 0,

        -- Datas
        [DATMOV] DATE NULL,
        [DATEMI] DATE NULL,
        [VCTPRO] DATE NULL,
        [ULTPGT] DATE NULL,

        -- Centro de custo e contas
        [CODCCU] INT NULL DEFAULT 0,
        [CTAFIN] INT NULL DEFAULT 0,
        [CTARED] INT NULL DEFAULT 0,

        -- Observações
        [OBSTCP] VARCHAR(MAX) NULL,

        -- Controle de auditoria
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
    );

    -- Cria índices para melhor performance
    CREATE INDEX [IX_contas_pagar_empresa_filial] ON [dbo].[contas_pagar] ([CODEMP], [CODFIL]);
    CREATE INDEX [IX_contas_pagar_fornecedor] ON [dbo].[contas_pagar] ([CODFOR]);
    CREATE INDEX [IX_contas_pagar_numtit] ON [dbo].[contas_pagar] ([NUMTIT]);
    CREATE INDEX [IX_contas_pagar_vctpro] ON [dbo].[contas_pagar] ([VCTPRO]);
    CREATE INDEX [IX_contas_pagar_sittit] ON [dbo].[contas_pagar] ([SITTIT]);

    -- Índice composto NÃO-ÚNICO para performance (permite registros com mesma chave)
    CREATE INDEX [IX_contas_pagar_composite] ON [dbo].[contas_pagar]
        ([CODEMP], [CODFIL], [NUMTIT], [SEQMOV], [CODTPT], [CODFOR]);

    PRINT 'Tabela contas_pagar criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela contas_pagar já existe.';
END
GO
