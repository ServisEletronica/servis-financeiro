-- =====================================================
-- TABELA: user_roles
-- Armazena os perfis/papéis de usuários do sistema
-- Hierarquia: Super Admin (0) > Admin (1) > Gestor (2) > Usuário (3)
-- =====================================================

-- Remove a tabela se existir
IF OBJECT_ID('dbo.user_roles', 'U') IS NOT NULL
    DROP TABLE dbo.user_roles;
GO

-- Cria a tabela
CREATE TABLE dbo.user_roles (
    -- Chave primária
    id INT NOT NULL PRIMARY KEY,

    -- Dados do perfil
    name NVARCHAR(50) NOT NULL,
    description NVARCHAR(255) NULL,
    level INT NOT NULL,

    -- Metadados de controle
    created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),

    -- Constraints
    CONSTRAINT UQ_user_roles_name UNIQUE (name),
    CONSTRAINT UQ_user_roles_level UNIQUE (level)
);
GO

-- Inserir roles padrão
INSERT INTO dbo.user_roles (id, name, description, level) VALUES
    (0, 'Super Admin', 'Administrador da plataforma - acesso total a todos os clientes', 0),
    (1, 'Admin', 'Administrador do cliente - gerencia tudo dentro do cliente', 1),
    (2, 'Gestor', 'Gestor de setor - gerencia equipe e visualiza relatórios', 2),
    (3, 'Usuário', 'Atendente - realiza atendimentos e tarefas básicas', 3);
GO

-- Comentários da tabela
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Tabela de perfis/papéis de usuários do sistema com controle hierárquico',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'user_roles';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Nível hierárquico do perfil - quanto menor, maior o nível de acesso',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'user_roles',
    @level2type = N'COLUMN', @level2name = N'level';
GO

PRINT 'Tabela user_roles criada com sucesso!'
GO
