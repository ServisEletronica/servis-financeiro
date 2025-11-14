# 🔐 Setup de Autenticação - Financeiro Servis

## 📋 Pré-requisitos

- SQL Server configurado e rodando
- Python 3.11+ com dependências instaladas
- Banco de dados criado

## 🚀 Passo a Passo para Configurar Autenticação

### 1️⃣ Executar as Migrations

Execute os scripts SQL na ordem:

```bash
# No SQL Server Management Studio ou Azure Data Studio

# 1. Criar tabela de roles
api/database/migrations/004_create_user_roles.sql

# 2. Criar tabela de usuários
api/database/migrations/005_create_users.sql

# 3. Inserir usuário Super Admin de teste
api/database/migrations/006_insert_test_users.sql
```

### 2️⃣ Configurar JWT Secret Key

Edite o arquivo `.env` e adicione uma chave secreta forte:

```env
JWT_SECRET_KEY=sua-chave-super-secreta-aqui-use-algo-aleatorio-e-longo
```

**💡 Dica:** Gere uma chave aleatória segura:

```python
import secrets
print(secrets.token_urlsafe(64))
```

### 3️⃣ Testar o Login

**Usuário de Teste Criado:**
- **Email:** `admin@servis.com`
- **Senha:** `admin123`
- **Role:** Super Admin (roleId: 0)
- **2FA:** Desabilitado (para facilitar testes)

**Características do Super Admin:**
- ✅ Acessa todos os clientes (multitenancy)
- ✅ Vê o botão "Sincronizar" na página Projetado
- ✅ Tem todas as permissões do sistema

### 4️⃣ Criar Mais Usuários

#### Opção A: Usar o Script Python (Recomendado)

```bash
cd api
./venv/Scripts/python.exe scripts/generate_password_hash.py
```

Digite a senha desejada e copie o hash gerado.

#### Opção B: Gerar hash diretamente no Python

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash_senha = pwd_context.hash("sua_senha_aqui")
print(hash_senha)
```

#### Opção C: Usar INSERT SQL

Edite o arquivo `006_insert_test_users.sql` e descomente os blocos de INSERT dos outros usuários (Admin, Gestor, Usuário).

**⚠️ IMPORTANTE:** Substitua `'SUBSTITUA-PELO-UUID-DO-CLIENTE'` pelo UUID real do cliente!

```sql
-- Para obter UUIDs de clientes (se houver tabela de clientes):
SELECT id, nome FROM dbo.clientes;

-- Ou gere um novo UUID:
SELECT NEWID() AS novo_uuid;
```

## 🔑 Hierarquia de Roles

| ID | Nome | Level | Permissões | client_id |
|----|------|-------|-----------|-----------|
| 0 | Super Admin | 0 | Acesso total a todos os clientes | NULL |
| 1 | Admin | 1 | Gerencia tudo dentro do seu cliente | NOT NULL |
| 2 | Gestor | 2 | Gerencia equipe e relatórios | NOT NULL |
| 3 | Usuário | 3 | Realiza tarefas básicas | NOT NULL |

**Regra importante:** Quanto MENOR o level, MAIOR o poder!

## 🔐 Autenticação 2FA (Opcional)

### Habilitar 2FA para um usuário:

```sql
UPDATE dbo.users
SET two_factor_enabled = 1,
    whatsapp = '5585999999999',  -- Formato: DDI + DDD + Número
    whatsapp_verified = 1
WHERE email = 'usuario@servis.com';
```

### Fluxo de Login com 2FA:

1. Usuário envia email/senha para `/api/auth/login`
2. API retorna `requires_2fa: true` e gera código de 6 dígitos
3. Código é salvo no banco e expira em 5 minutos
4. Usuário envia código para `/api/auth/verify-2fa`
5. API valida código e retorna access_token + refresh_token

**⚠️ Nota:** A integração com WhatsApp ainda precisa ser implementada. Por enquanto, o código aparece no console do servidor.

## 📡 Endpoints da API

### POST `/api/auth/login`
Login com email e senha

**Request:**
```json
{
  "email": "admin@servis.com",
  "password": "admin123"
}
```

**Response (sem 2FA):**
```json
{
  "requires_2fa": false,
  "message": "Login realizado com sucesso",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "admin@servis.com",
    "first_name": "Admin",
    "full_name": "Administrador do Sistema",
    "role_id": 0,
    "role_name": "Super Admin",
    "client_id": null
  }
}
```

**Response (com 2FA):**
```json
{
  "requires_2fa": true,
  "message": "Código enviado para seu WhatsApp"
}
```

### POST `/api/auth/verify-2fa`
Valida código 2FA

**Request:**
```json
{
  "email": "admin@servis.com",
  "code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### POST `/api/auth/refresh`
Renova o access token

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### GET `/api/auth/me`
Retorna dados do usuário atual

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response:**
```json
{
  "id": "uuid",
  "email": "admin@servis.com",
  "first_name": "Admin",
  "full_name": "Administrador do Sistema",
  "role_id": 0,
  "role_name": "Super Admin",
  "client_id": null,
  "is_active": true
}
```

## 🎨 Frontend

### AuthContext

Use o hook `useAuth()` em qualquer componente:

```tsx
import { useAuth } from '@/context/auth-context'

function MeuComponente() {
  const { user, token, login, logout } = useAuth()

  // Verificar se é Super Admin
  if (user?.roleId === 0) {
    // Mostrar funcionalidade exclusiva
  }

  return <div>Olá, {user?.firstName}!</div>
}
```

### Controle de Permissões

```tsx
// Mostrar apenas para Super Admin
{user?.roleId === 0 && (
  <Button>Funcionalidade Administrativa</Button>
)}

// Mostrar para Admin ou superior (roleId <= 1)
{user?.roleId !== undefined && user.roleId <= 1 && (
  <Button>Gerenciar Equipe</Button>
)}
```

## 🐛 Troubleshooting

### Erro: "Email ou senha incorretos"
- Verifique se o usuário foi criado no banco
- Confirme que o hash da senha está correto
- Verifique se `is_active = 1`

### Erro: "Token inválido ou expirado"
- Access token expira em 24 horas
- Use o refresh token para obter um novo
- Verifique se JWT_SECRET_KEY está configurada

### Erro: "Constraint CK_users_client_role"
- Super Admin (role_id=0) DEVE ter client_id=NULL
- Outros roles (1,2,3) DEVEM ter client_id NOT NULL

### 2FA: "Código não aparece"
- Código é impresso no console do servidor (procure por `[DEBUG]`)
- Integração com WhatsApp precisa ser implementada
- Código expira em 5 minutos

## 📝 Próximos Passos

1. ✅ Executar migrations e criar usuário de teste
2. ✅ Configurar JWT_SECRET_KEY no .env
3. ✅ Testar login no frontend
4. ⏳ Implementar integração com WhatsApp para 2FA
5. ⏳ Criar tabela de clientes (para multitenancy)
6. ⏳ Adicionar mais controles de permissão nas páginas
7. ⏳ Implementar "Esqueci minha senha"
8. ⏳ Adicionar logs de auditoria

## 🔒 Segurança

- ✅ Senhas com hash bcrypt (custo 12)
- ✅ JWT com expiração (24h access, 7d refresh)
- ✅ 2FA opcional com bloqueio após 5 tentativas
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Multitenancy (isolamento por client_id)
- ⚠️ Lembre-se de usar HTTPS em produção!
- ⚠️ Troque JWT_SECRET_KEY em produção!

---

**Dúvidas?** Consulte os arquivos:
- `api/services/auth_service.py` - Lógica de autenticação
- `api/routes/auth.py` - Endpoints da API
- `src/context/auth-context.tsx` - Context do React
