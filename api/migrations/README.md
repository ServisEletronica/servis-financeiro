# Migrations do Banco de Dados

Este diretório contém os scripts de migração (migrations) para o banco de dados local do sistema financeiro.

## Execução Manual

Para executar as migrations, conecte-se ao banco de dados **Financeiro** no servidor **192.168.0.230** e execute os scripts SQL na ordem:

### Ordem de execução:

1. **001_create_contas_receber.sql** - Cria a tabela `contas_receber`
2. **002_create_contas_pagar.sql** - Cria a tabela `contas_pagar`
3. **003_create_log_sincronizacao.sql** - Cria a tabela `log_sincronizacao`

### Como executar:

#### Via SQL Server Management Studio (SSMS):
1. Conecte-se ao servidor: `192.168.0.230`
2. Selecione o banco de dados: `Financeiro`
3. Abra cada arquivo `.sql` em sequência
4. Execute (F5) cada script

#### Via sqlcmd (linha de comando):
```bash
sqlcmd -S 192.168.0.230 -d Financeiro -U sa -P kks8G8d9Fk32 -i 001_create_contas_receber.sql
sqlcmd -S 192.168.0.230 -d Financeiro -U sa -P kks8G8d9Fk32 -i 002_create_contas_pagar.sql
sqlcmd -S 192.168.0.230 -d Financeiro -U sa -P kks8G8d9Fk32 -i 003_create_log_sincronizacao.sql
```

## Estrutura das Tabelas

### contas_receber
Armazena os dados sincronizados de contas a receber do sistema Senior.

**Campos principais:**
- `id` (UNIQUEIDENTIFIER) - Chave primária
- `CODEMP`, `CODFIL` - Empresa e filial
- `CODCLI`, `NOMCLI` - Código e nome do cliente
- `NUMTIT` - Número do título
- `VLRABE`, `VLRORI` - Valores
- `VCTPRO` - Data de vencimento projetada
- Timestamps: `created_at`, `updated_at`

### contas_pagar
Armazena os dados sincronizados de contas a pagar do sistema Senior.

**Campos principais:**
- `id` (UNIQUEIDENTIFIER) - Chave primária
- `CODEMP`, `CODFIL` - Empresa e filial
- `CODFOR`, `NOMFOR` - Código e nome do fornecedor
- `NUMTIT`, `SEQMOV` - Número do título e sequência
- `VLRABE`, `VLRORI`, `VLRRAT` - Valores
- `VCTPRO` - Data de vencimento projetada
- Timestamps: `created_at`, `updated_at`

### log_sincronizacao
Registra todas as operações de sincronização executadas.

**Campos principais:**
- `id` (UNIQUEIDENTIFIER) - Chave primária
- `tipo` - Tipo de sincronização (contas_receber, contas_pagar, ambas)
- `data_hora_inicio`, `data_hora_fim` - Timestamps
- `status` - Status da operação (sucesso, erro, em_andamento)
- `registros_inseridos` - Quantidade de registros sincronizados
- `tempo_execucao_ms` - Tempo de execução em milissegundos

## Notas Importantes

- As tabelas possuem **índices únicos compostos** para evitar duplicatas
- Todos os scripts verificam se a tabela já existe antes de criar
- Os scripts são **idempotentes** (podem ser executados múltiplas vezes)
- As tabelas incluem campos de auditoria (`created_at`, `updated_at`)

## Rollback

Para remover as tabelas criadas (USE COM CUIDADO!):

```sql
DROP TABLE IF EXISTS [dbo].[contas_receber];
DROP TABLE IF EXISTS [dbo].[contas_pagar];
DROP TABLE IF EXISTS [dbo].[log_sincronizacao];
```
