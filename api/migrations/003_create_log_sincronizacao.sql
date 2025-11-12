-- ================================================
-- Migration: 003_create_log_sincronizacao
-- Descrição: Cria tabela para log de sincronizações
-- Data: 2025-01-31
-- ================================================

-- Cria tabela se não existir
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[log_sincronizacao]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[log_sincronizacao] (
        -- Identificador único
        [id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT NEWID(),

        -- Tipo de sincronização
        [tipo] VARCHAR(20) NOT NULL, -- 'contas_receber', 'contas_pagar', 'ambas'

        -- Data e hora
        [data_hora_inicio] DATETIME2 NOT NULL DEFAULT GETDATE(),
        [data_hora_fim] DATETIME2 NULL,

        -- Resultado
        [status] VARCHAR(20) NOT NULL, -- 'sucesso', 'erro', 'em_andamento'
        [registros_inseridos] INT NULL DEFAULT 0,
        [tempo_execucao_ms] INT NULL, -- Tempo em milissegundos

        -- Informações de erro (se houver)
        [mensagem_erro] VARCHAR(MAX) NULL,
        [stack_trace] VARCHAR(MAX) NULL,

        -- Usuário/Sistema que executou
        [executado_por] VARCHAR(100) NULL,

        -- Metadados adicionais
        [observacoes] VARCHAR(MAX) NULL
    );

    -- Cria índices
    CREATE INDEX [IX_log_sincronizacao_tipo] ON [dbo].[log_sincronizacao] ([tipo]);
    CREATE INDEX [IX_log_sincronizacao_data] ON [dbo].[log_sincronizacao] ([data_hora_inicio]);
    CREATE INDEX [IX_log_sincronizacao_status] ON [dbo].[log_sincronizacao] ([status]);

    PRINT 'Tabela log_sincronizacao criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'Tabela log_sincronizacao já existe.';
END
GO
