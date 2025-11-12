-- Migration 006: Criar tabela recebiveis_cartao
-- Descrição: Tabela para armazenar dados de recebíveis de cartão extraídos via OCR/OpenAI
-- Data: 2025-11-07

-- Criar tabela se não existir
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[recebiveis_cartao]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[recebiveis_cartao] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [data_recebimento] DATE NOT NULL,
        [valor] DECIMAL(18,2) NOT NULL,
        [estabelecimento] VARCHAR(50) NULL,
        [mes_referencia] VARCHAR(7) NOT NULL,  -- Formato YYYY-MM
        [data_upload] DATETIME NOT NULL DEFAULT GETDATE(),
        [usuario_upload] VARCHAR(100) NULL,

        -- Índice único para evitar duplicatas
        CONSTRAINT UQ_recebiveis_cartao_data_mes_estab
            UNIQUE (data_recebimento, mes_referencia, estabelecimento)
    );

    -- Criar índice em mes_referencia para queries rápidas
    CREATE INDEX IX_recebiveis_cartao_mes_referencia
        ON [dbo].[recebiveis_cartao] (mes_referencia);

    -- Criar índice em data_recebimento para filtros de período
    CREATE INDEX IX_recebiveis_cartao_data_recebimento
        ON [dbo].[recebiveis_cartao] (data_recebimento);

    PRINT 'Tabela recebiveis_cartao criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela recebiveis_cartao já existe.';
END
GO
