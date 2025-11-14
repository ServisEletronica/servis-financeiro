-- =====================================================
-- Adiciona coluna de status na tabela recebiveis_cartao
-- Para diferenciar entre valores projetados e recebidos
-- =====================================================

-- Adiciona coluna status
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.recebiveis_cartao')
    AND name = 'status'
)
BEGIN
    ALTER TABLE dbo.recebiveis_cartao
    ADD status VARCHAR(20) NOT NULL DEFAULT 'projetado';

    PRINT 'Coluna status adicionada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Coluna status já existe.';
END
GO

-- Adiciona check constraint para validar valores permitidos
IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'CK_recebiveis_cartao_status'
)
BEGIN
    ALTER TABLE dbo.recebiveis_cartao
    ADD CONSTRAINT CK_recebiveis_cartao_status
    CHECK (status IN ('projetado', 'recebido'));

    PRINT 'Constraint CK_recebiveis_cartao_status criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Constraint CK_recebiveis_cartao_status já existe.';
END
GO

-- Cria índice para melhorar performance de consultas por status
IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_recebiveis_cartao_status'
    AND object_id = OBJECT_ID('dbo.recebiveis_cartao')
)
BEGIN
    CREATE INDEX IX_recebiveis_cartao_status
    ON dbo.recebiveis_cartao(status);

    PRINT 'Índice IX_recebiveis_cartao_status criado com sucesso!';
END
ELSE
BEGIN
    PRINT 'Índice IX_recebiveis_cartao_status já existe.';
END
GO

-- Adiciona comentário na coluna
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Status do recebível: projetado (a receber) ou recebido (realizado)',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'recebiveis_cartao',
    @level2type = N'COLUMN', @level2name = N'status';
GO

PRINT '';
PRINT '=================================================';
PRINT 'Migração concluída!';
PRINT 'Valores permitidos: projetado, recebido';
PRINT 'Todos os registros existentes: status = projetado';
PRINT '=================================================';
GO
