-- =====================================================
-- TABELA: centro_custo
-- Armazena os centros de custo do sistema
-- Relaciona com contas_pagar e contas_receber via CODCCU
-- =====================================================

-- Remove a tabela se existir
IF OBJECT_ID('dbo.centro_custo', 'U') IS NOT NULL
    DROP TABLE dbo.centro_custo;
GO

-- Cria a tabela
CREATE TABLE dbo.centro_custo (
    -- Chave primária (UUID)
    id UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,

    -- Campos da tabela E043PCM
    CODMPC INT NOT NULL,
    CTARED INT NOT NULL,
    CLACTA VARCHAR(50),
    DESCTA VARCHAR(255),
    ANASIN VARCHAR(10),
    NATCTA VARCHAR(10),
    NIVCTA INT,
    CODCCU INT NOT NULL,
    TIPCCU VARCHAR(10),

    -- Metadados de controle
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),

    -- Índices
    INDEX IX_centro_custo_codccu (CODCCU),
    INDEX IX_centro_custo_clacta (CLACTA),
    INDEX IX_centro_custo_nivcta (NIVCTA)
);
GO

-- Comentários da tabela
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Tabela de centros de custo sincronizada do Senior (E043PCM)',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'centro_custo';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Código do centro de custo - Relaciona com contas_pagar e contas_receber',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'centro_custo',
    @level2type = N'COLUMN', @level2name = N'CODCCU';
GO

PRINT 'Tabela centro_custo criada com sucesso!'
GO
