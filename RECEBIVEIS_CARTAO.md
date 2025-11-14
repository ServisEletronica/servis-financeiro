# 💳 Sistema de Recebíveis de Cartão

## 📋 Visão Geral

O sistema de recebíveis de cartão permite gerenciar valores projetados (a receber) e valores já recebidos (realizados) separadamente.

## 🗄️ Estrutura do Banco de Dados

### Tabela: `recebiveis_cartao`

```sql
CREATE TABLE recebiveis_cartao (
    id UNIQUEIDENTIFIER PRIMARY KEY,
    data_recebimento DATE NOT NULL,
    valor DECIMAL(18,2) NOT NULL,
    estabelecimento VARCHAR(20) NOT NULL,
    mes_referencia VARCHAR(7) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'projetado', -- ← NOVA COLUNA
    usuario_upload VARCHAR(100),
    data_upload DATETIME2

    CONSTRAINT CK_recebiveis_cartao_status
    CHECK (status IN ('projetado', 'recebido'))
);
```

### Valores Permitidos para `status`:
- **`'projetado'`** - Valores a receber (futuro/planejado)
- **`'recebido'`** - Valores já recebidos (realizado/efetivado)

## 🔄 Como Funciona

### 1️⃣ Upload de Calendário Cielo

Quando você faz upload de um calendário Cielo:
- Todos os registros são inseridos com `status = 'projetado'`
- Aparecem na linha **"A RECEBER CARTÕES"** (bloco Projetado)

```sql
INSERT INTO recebiveis_cartao
    (data_recebimento, valor, estabelecimento, mes_referencia, status)
VALUES
    ('2025-01-15', 1500.00, '1028859080', '2025-01', 'projetado');
```

### 2️⃣ Marcar Como Recebido

Para marcar valores como recebidos, você precisa:

**Opção A: Atualizar registros existentes**
```sql
UPDATE recebiveis_cartao
SET status = 'recebido'
WHERE data_recebimento = '2025-01-15'
  AND estabelecimento = '1028859080';
```

**Opção B: Inserir diretamente como recebido**
```sql
INSERT INTO recebiveis_cartao
    (data_recebimento, valor, estabelecimento, mes_referencia, status)
VALUES
    ('2025-01-15', 1500.00, '1028859080', '2025-01', 'recebido');
```

### 3️⃣ Visualização no Frontend

#### Caixa Diário Projetado
- **A RECEBER CARTÕES**: Mostra valores com `status = 'projetado'`
- Cor: #a0bbe3 (azul claro)

#### Caixa Diário Realizado
- **RECEBIDO CARTÕES**: Mostra valores com `status = 'recebido'`
- Cor: #a0bbe3 (azul claro)

## 📡 API Endpoints

### GET `/api/recebiveis-cartao`

Busca recebíveis por período e status.

**Parâmetros:**
```
data_inicio: string (YYYY-MM-DD) - obrigatório
data_fim: string (YYYY-MM-DD) - obrigatório
estabelecimentos: string (opcional) - códigos separados por vírgula
status: string (opcional) - 'projetado' ou 'recebido' (default: 'projetado')
```

**Exemplos:**

```bash
# Buscar valores a receber (projetado)
GET /api/recebiveis-cartao?data_inicio=2025-01-01&data_fim=2025-01-31&status=projetado

# Buscar valores já recebidos (realizado)
GET /api/recebiveis-cartao?data_inicio=2025-01-01&data_fim=2025-01-31&status=recebido

# Buscar por estabelecimento específico
GET /api/recebiveis-cartao?data_inicio=2025-01-01&data_fim=2025-01-31&estabelecimentos=1028859080&status=recebido
```

**Resposta:**
```json
[
  {
    "data": "2025-01-15",
    "total": 1500.00
  },
  {
    "data": "2025-01-16",
    "total": 2300.50
  }
]
```

## 🏢 Mapeamento de Estabelecimentos por Filial

| Filial | Nome | Estabelecimento |
|--------|------|-----------------|
| 1001 | Servis Eletrônica Ceará | 1028859080 |
| 1002 | Servis Eletrônica Amazonas | (sem cartões) |
| 1003 | Servis Eletrônica Maranhão | 1060654811 |
| 2002 | Servis Gerenciamento de Risco | (sem cartões) |
| 3001 | Secopi Serviços Teresina | 1071167917 |
| 3002 | Secopi Serviços Picos | 1071167917 |
| 3003 | Secopi Serviços Paraíba | 1071167917 |

## 🔧 Migrações

Execute as migrations na ordem:

```sql
-- 1. Adicionar coluna status
api/database/migrations/008_add_status_recebiveis_cartao.sql
```

## 💡 Casos de Uso

### Cenário 1: Importar calendário Cielo
1. Upload do arquivo → Registros criados com `status = 'projetado'`
2. Valores aparecem em "A RECEBER CARTÕES"

### Cenário 2: Receber pagamento de cartão
Quando o valor cai na conta:

```sql
-- Marcar como recebido
UPDATE recebiveis_cartao
SET status = 'recebido'
WHERE data_recebimento = '2025-01-15'
  AND estabelecimento = '1028859080'
  AND status = 'projetado';
```

Agora o valor:
- ❌ **NÃO** aparece mais em "A RECEBER CARTÕES"
- ✅ **APARECE** em "RECEBIDO CARTÕES" (Realizado)

### Cenário 3: Reconciliação Bancária
```sql
-- Buscar valores que já deveriam ter sido recebidos
SELECT
    data_recebimento,
    estabelecimento,
    SUM(valor) as total
FROM recebiveis_cartao
WHERE data_recebimento < GETDATE()
  AND status = 'projetado' -- Ainda não marcado como recebido!
GROUP BY data_recebimento, estabelecimento;
```

## 📊 Consultas Úteis

### Ver todos os projetados do mês
```sql
SELECT
    data_recebimento,
    estabelecimento,
    valor
FROM recebiveis_cartao
WHERE mes_referencia = '2025-01'
  AND status = 'projetado'
ORDER BY data_recebimento;
```

### Ver todos os recebidos do mês
```sql
SELECT
    data_recebimento,
    estabelecimento,
    valor
FROM recebiveis_cartao
WHERE mes_referencia = '2025-01'
  AND status = 'recebido'
ORDER BY data_recebimento;
```

### Comparar projetado vs realizado
```sql
SELECT
    data_recebimento,
    SUM(CASE WHEN status = 'projetado' THEN valor ELSE 0 END) as projetado,
    SUM(CASE WHEN status = 'recebido' THEN valor ELSE 0 END) as recebido,
    SUM(CASE WHEN status = 'projetado' THEN valor ELSE 0 END) -
    SUM(CASE WHEN status = 'recebido' THEN valor ELSE 0 END) as diferenca
FROM recebiveis_cartao
WHERE mes_referencia = '2025-01'
GROUP BY data_recebimento
ORDER BY data_recebimento;
```

## 🚀 Próximos Passos (Futuro)

1. **Automatizar marcação como recebido**
   - Integração com extrato bancário
   - Marcar automaticamente quando o valor cair na conta

2. **Dashboard de Reconciliação**
   - Comparar projetado vs recebido
   - Identificar divergências

3. **Notificações**
   - Alertar quando valor projetado não foi recebido
   - Alerta de valores em atraso

4. **Relatório de Performance**
   - Taxa de realização (recebido/projetado)
   - Dias de atraso médio

---

**Data da última atualização:** 2025-01-14
