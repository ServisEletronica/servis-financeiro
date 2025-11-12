-- ================================================
-- Fix: Remover índice único e criar índice regular
-- Permite inserir registros duplicados em contas_pagar
-- ================================================

-- 1. Dropar o índice único existente (se existir)
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_contas_pagar_unique' AND object_id = OBJECT_ID('dbo.contas_pagar'))
BEGIN
    DROP INDEX [IX_contas_pagar_unique] ON [dbo].[contas_pagar];
    PRINT 'Índice único IX_contas_pagar_unique removido com sucesso.';
END
ELSE
BEGIN
    PRINT 'Índice IX_contas_pagar_unique não existe.';
END
GO

-- 2. Criar índice regular (não-único) para performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_contas_pagar_composite' AND object_id = OBJECT_ID('dbo.contas_pagar'))
BEGIN
    CREATE INDEX [IX_contas_pagar_composite] ON [dbo].[contas_pagar]
        ([CODEMP], [CODFIL], [NUMTIT], [SEQMOV], [CODTPT], [CODFOR]);
    PRINT 'Índice regular IX_contas_pagar_composite criado com sucesso.';
END
ELSE
BEGIN
    PRINT 'Índice IX_contas_pagar_composite já existe.';
END
GO

PRINT 'Migração concluída! Agora você pode executar a sincronização novamente.';
GO
