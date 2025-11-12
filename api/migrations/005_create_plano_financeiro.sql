-- ================================================
-- Migration: 005_create_plano_financeiro
-- Descrição: Cria tabela plano_financeiro no banco local
-- Data: 2025-10-31
-- ================================================

-- Cria tabela se não existir
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[plano_financeiro]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[plano_financeiro] (
        -- Identificador único gerado pela aplicação
        [id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),

        -- Dados do plano de contas
        [CODMPC] INT NOT NULL,
        [CTARED] VARCHAR(30) NOT NULL,
        [MSKGCC] VARCHAR(50) NULL,
        [DEFGRU] VARCHAR(100) NULL,
        [CLACTA] INT NULL,
        [NIVCTA] INT NULL,
        [DESCTA] VARCHAR(255) NULL,
        [ANASIN] VARCHAR(10) NULL,
        [NATCTA] VARCHAR(10) NULL,
        [MODCTB] VARCHAR(10) NULL,
        [CTACTB] VARCHAR(30) NULL,
        [CODCCU] VARCHAR(30) NULL,
        [TIPCCU] VARCHAR(10) NULL,

        -- Controle de auditoria
        [created_at] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [updated_at] DATETIME2 NOT NULL DEFAULT GETDATE()
    );

    -- Cria índices para melhor performance
    CREATE INDEX [IX_plano_financeiro_ctared] ON [dbo].[plano_financeiro] ([CTARED]);
    CREATE INDEX [IX_plano_financeiro_codmpc] ON [dbo].[plano_financeiro] ([CODMPC]);
    CREATE INDEX [IX_plano_financeiro_clacta] ON [dbo].[plano_financeiro] ([CLACTA]);
    CREATE INDEX [IX_plano_financeiro_nivcta] ON [dbo].[plano_financeiro] ([NIVCTA]);

    -- Cria índice composto para chave única
    CREATE UNIQUE INDEX [IX_plano_financeiro_unique] ON [dbo].[plano_financeiro]
        ([CODMPC], [CTARED]);

    PRINT 'Tabela plano_financeiro criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela plano_financeiro já existe.';
END
GO
