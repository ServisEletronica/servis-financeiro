-- =====================================================
-- TABELA: users
-- Armazena os usuários do sistema com autenticação e multitenancy
-- Suporta 2FA, reset de senha e controle de acesso por cliente
-- =====================================================

-- Remove a tabela se existir
IF OBJECT_ID('dbo.users', 'U') IS NOT NULL
    DROP TABLE dbo.users;
GO

-- Cria a stored procedure para atualizar updated_at automaticamente
IF OBJECT_ID('dbo.sp_touch_updated_at', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_touch_updated_at;
GO

CREATE PROCEDURE dbo.sp_touch_updated_at
    @table_name NVARCHAR(128),
    @pk_column NVARCHAR(128)
AS
BEGIN
    DECLARE @sql NVARCHAR(MAX);
    DECLARE @trigger_name NVARCHAR(128) = 'TR_' + @table_name + '_UpdatedAt';

    -- Remove o trigger se existir
    SET @sql = N'
    IF EXISTS (SELECT 1 FROM sys.triggers WHERE name = ''' + @trigger_name + ''')
        DROP TRIGGER dbo.' + @trigger_name + ';';
    EXEC sp_executesql @sql;

    -- Cria o trigger
    SET @sql = N'
    CREATE TRIGGER dbo.' + @trigger_name + '
    ON dbo.' + @table_name + '
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE dbo.' + @table_name + '
        SET updated_at = SYSUTCDATETIME()
        FROM dbo.' + @table_name + ' t
        INNER JOIN inserted i ON t.' + @pk_column + ' = i.' + @pk_column + ';
    END';

    EXEC sp_executesql @sql;
END;
GO

-- Cria a tabela
CREATE TABLE dbo.users (
    -- Chave primária
    id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID() PRIMARY KEY,

    -- Relacionamentos
    role_id INT NOT NULL,
    client_id UNIQUEIDENTIFIER NULL, /* MULTITENANCY - NULL apenas para Super Admin (role_id = 0) */

    -- Dados pessoais
    first_name NVARCHAR(100) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    phone NVARCHAR(32) NULL,
    email NVARCHAR(255) NOT NULL,
    cpf NVARCHAR(14) NULL,
    gender NVARCHAR(20) NULL,

    -- Endereço
    address_street NVARCHAR(255) NULL,
    address_number NVARCHAR(32) NULL,
    address_complement NVARCHAR(128) NULL,
    address_district NVARCHAR(128) NULL,
    address_city NVARCHAR(128) NULL,
    address_state NVARCHAR(64) NULL,
    address_zip NVARCHAR(16) NULL,

    -- Autenticação
    password_hash NVARCHAR(255) NOT NULL,
    profile_picture_url NVARCHAR(512) NULL,
    is_active BIT NOT NULL DEFAULT 1,
    last_login_at DATETIME2(3) NULL,

    -- Reset de senha
    reset_password_token NVARCHAR(128) NULL,
    reset_password_expires DATETIME2(3) NULL,

    -- WhatsApp e 2FA
    whatsapp VARCHAR(20) NULL,
    whatsapp_verified BIT NOT NULL DEFAULT 0,
    two_factor_enabled BIT NOT NULL DEFAULT 1,
    two_factor_code VARCHAR(6) NULL,
    two_factor_expires_at DATETIME2(3) NULL,
    two_factor_attempts INT NOT NULL DEFAULT 0,
    two_factor_blocked_until DATETIME2(3) NULL,

    -- Metadados de controle
    created_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),

    -- Constraints
    CONSTRAINT UQ_users_cpf UNIQUE (cpf),
    CONSTRAINT UQ_users_email UNIQUE (email),
    CONSTRAINT UQ_users_whatsapp UNIQUE (whatsapp),

    -- Foreign Key
    CONSTRAINT FK_users_role FOREIGN KEY (role_id) REFERENCES dbo.user_roles(id),

    -- MULTITENANCY - Constraint: Super Admin tem client_id NULL, outros têm NOT NULL
    CONSTRAINT CK_users_client_role CHECK (
        (role_id = 0 AND client_id IS NULL) OR
        (role_id > 0 AND client_id IS NOT NULL)
    )
);
GO

-- Criar índices
CREATE INDEX IX_users_email ON dbo.users(email);
CREATE INDEX IX_users_cpf ON dbo.users(cpf);
CREATE INDEX IX_users_role_id ON dbo.users(role_id);
CREATE INDEX IX_users_client_id ON dbo.users(client_id);
CREATE INDEX IX_users_is_active ON dbo.users(is_active);
GO

-- Adicionar trigger para updated_at
EXEC dbo.sp_touch_updated_at 'users', 'id';
GO

-- Comentários da tabela
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Tabela de usuários do sistema com autenticação, 2FA e multitenancy',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'users';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'ID do cliente (multitenancy) - NULL apenas para Super Admin',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'users',
    @level2type = N'COLUMN', @level2name = N'client_id';
GO

EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Hash da senha usando bcrypt',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE',  @level1name = N'users',
    @level2type = N'COLUMN', @level2name = N'password_hash';
GO

PRINT 'Tabela users criada com sucesso!'
GO
