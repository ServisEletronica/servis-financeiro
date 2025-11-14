-- =====================================================
-- Remove constraint de multitenancy
-- Permite que todos os usuários tenham client_id NULL
-- (sistema sem multitenancy)
-- =====================================================

-- Remove a constraint que obriga multitenancy
IF EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'CK_users_client_role'
)
BEGIN
    ALTER TABLE dbo.users DROP CONSTRAINT CK_users_client_role;
    PRINT 'Constraint CK_users_client_role removida com sucesso!';
END
ELSE
BEGIN
    PRINT 'Constraint CK_users_client_role não existe.';
END

GO

PRINT '';
PRINT '=================================================';
PRINT 'Sistema configurado SEM multitenancy';
PRINT 'Todos os usuários podem ter client_id = NULL';
PRINT '=================================================';
GO
