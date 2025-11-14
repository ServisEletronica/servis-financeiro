-- =====================================================
-- SCRIPT: Inserir usuários de teste
-- Cria usuários de exemplo para cada role do sistema
-- =====================================================

-- Super Admin (acesso total a todos os clientes)
-- Email: admin@servis.com | Senha: admin123
INSERT INTO dbo.users (
    role_id,
    client_id,
    first_name,
    full_name,
    phone,
    email,
    cpf,
    password_hash,
    is_active,
    two_factor_enabled,
    whatsapp,
    whatsapp_verified
) VALUES (
    0,                          -- Super Admin
    NULL,                       -- Sem client_id (acessa todos)
    'Admin',
    'Administrador do Sistema',
    '(85) 99999-0000',
    'admin@servis.com',
    '000.000.000-00',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYpNkr0z.HW', -- admin123
    1,                          -- Ativo
    0,                          -- 2FA desabilitado para facilitar testes
    '5585999990000',
    0
);

PRINT 'Usuário Super Admin criado com sucesso!';
PRINT 'Email: admin@servis.com';
PRINT 'Senha: admin123';
PRINT '';

GO

-- Você pode descomentar os exemplos abaixo após criar clientes na tabela
-- Certifique-se de substituir os UUIDs pelos IDs reais dos seus clientes

/*
-- Admin de Cliente
-- Email: admin.cliente@servis.com | Senha: cliente123
INSERT INTO dbo.users (
    role_id,
    client_id,
    first_name,
    full_name,
    phone,
    email,
    cpf,
    password_hash,
    is_active,
    two_factor_enabled,
    whatsapp,
    whatsapp_verified
) VALUES (
    1,                          -- Admin
    'SUBSTITUA-PELO-UUID-DO-CLIENTE',  -- UUID do cliente
    'João',
    'João Silva Santos',
    '(85) 98888-1111',
    'admin.cliente@servis.com',
    '111.111.111-11',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQam1qgdQO24TQDqN0tLu', -- cliente123
    1,                          -- Ativo
    1,                          -- 2FA habilitado
    '5585988881111',
    1
);

PRINT 'Usuário Admin de Cliente criado com sucesso!';
PRINT 'Email: admin.cliente@servis.com';
PRINT 'Senha: cliente123';
PRINT '';
*/

/*
-- Gestor
-- Email: gestor@servis.com | Senha: gestor123
INSERT INTO dbo.users (
    role_id,
    client_id,
    first_name,
    full_name,
    phone,
    email,
    cpf,
    password_hash,
    is_active,
    two_factor_enabled,
    whatsapp,
    whatsapp_verified
) VALUES (
    2,                          -- Gestor
    'SUBSTITUA-PELO-UUID-DO-CLIENTE',  -- UUID do cliente
    'Maria',
    'Maria Oliveira Costa',
    '(85) 97777-2222',
    'gestor@servis.com',
    '222.222.222-22',
    '$2b$12$zx0VfLdH6HqQqZ7fO6RXOOgx5z3QvJ2qKJqzf8LpYHZYpBqX8Wz8m', -- gestor123
    1,                          -- Ativo
    0,                          -- 2FA desabilitado
    '5585977772222',
    0
);

PRINT 'Usuário Gestor criado com sucesso!';
PRINT 'Email: gestor@servis.com';
PRINT 'Senha: gestor123';
PRINT '';
*/

/*
-- Usuário/Atendente
-- Email: usuario@servis.com | Senha: usuario123
INSERT INTO dbo.users (
    role_id,
    client_id,
    first_name,
    full_name,
    phone,
    email,
    cpf,
    password_hash,
    is_active,
    two_factor_enabled,
    whatsapp,
    whatsapp_verified
) VALUES (
    3,                          -- Usuário
    'SUBSTITUA-PELO-UUID-DO-CLIENTE',  -- UUID do cliente
    'Pedro',
    'Pedro Santos Lima',
    '(85) 96666-3333',
    'usuario@servis.com',
    '333.333.333-33',
    '$2b$12$P8pNHj/xF6qB0qLYkqY4lOZG2YKb8m5F5xQqB5qYxB7QxB8QxB9Qx', -- usuario123
    1,                          -- Ativo
    0,                          -- 2FA desabilitado
    '5585966663333',
    0
);

PRINT 'Usuário Atendente criado com sucesso!';
PRINT 'Email: usuario@servis.com';
PRINT 'Senha: usuario123';
PRINT '';
*/

GO

PRINT '=================================================';
PRINT 'IMPORTANTE: Use o script generate_password_hash.py';
PRINT 'para gerar hashes de senhas personalizadas!';
PRINT '=================================================';
GO
