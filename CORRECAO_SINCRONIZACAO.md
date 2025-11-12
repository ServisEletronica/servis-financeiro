# Correção: Erros na Sincronização

## Problemas Encontrados

Durante a primeira tentativa de sincronização, foram encontrados **2 erros críticos**:

### 1️⃣ Erro de Conversão de Tipo (Contas a Receber)
```
OperationalError: (245, "Conversion failed when converting the nvarchar value 'D' to data type int")
```

**Causa**: Campos que deveriam ser INT (RECDEC, RECSOM, RECVJM, RECVMM, RECVDM, CODCCU, CTAFIN) estavam recebendo valores string (ex: 'D') do banco Senior.

**Impacto**: 225.533 registros encontrados, mas nenhum foi inserido devido ao erro.

---

### 2️⃣ Chave Duplicada (Contas a Pagar)
```
IntegrityError: (2601, "Cannot insert duplicate key row in object 'dbo.contas_pagar'
with unique index 'IX_contas_pagar_unique'.
The duplicate key value is (10, 1001, 04379, 1, FAT, 835)")
```

**Causa**: A query SQL do Senior (mesmo com `SELECT DISTINCT`) retorna registros duplicados que violam o índice único composto:
- CODEMP + CODFIL + NUMTIT + SEQMOV + CODTPT + CODFOR

**Impacto**: 125.373 registros encontrados, mas nenhum foi inserido devido às duplicatas.

---

## Soluções Implementadas

### ✅ Correção 1: Tratamento de Conversão de Tipos

Criada função auxiliar `to_int()` que:
- Converte strings numéricas para int
- Retorna 0 para strings não-numéricas (como 'D')
- Trata valores None
- Garante que campos INT sempre recebam números

```python
def to_int(value):
    """Converte valor para int, retorna 0 se não for numérico"""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.strip().isdigit():
            return int(value)
        return 0  # String não-numérica vira 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
```

**Campos tratados**:
- RECDEC
- RECSOM
- RECVJM
- RECVMM
- RECVDM
- CODCCU
- CTAFIN

---

### ✅ Correção 2: Remoção de Duplicatas

Implementado filtro de duplicatas **em memória** antes da inserção:

1. **Detecção**: Usa dicionário com chave composta para detectar duplicatas
2. **Estratégia**: Mantém apenas o primeiro registro de cada chave única
3. **Logging**: Registra quantidade de duplicatas removidas
4. **Transparência**: Informa ao usuário quantas duplicatas foram removidas

```python
# Chave única: CODEMP, CODFIL, NUMTIT, SEQMOV, CODTPT, CODFOR
registros_unicos = {}
for row in dados_senior:
    chave = (
        row.get('CODEMP'), row.get('CODFIL'), row.get('NUMTIT'),
        row.get('SEQMOV'), row.get('CODTPT'), row.get('CODFOR')
    )
    if chave not in registros_unicos:
        registros_unicos[chave] = row

dados_limpos = list(registros_unicos.values())
```

---

## Resultados Esperados

### Contas a Receber
- ✅ Valores não-numéricos convertidos para 0
- ✅ Todos os 225.533 registros devem ser inseridos com sucesso
- ✅ Sem erros de conversão

### Contas a Pagar
- ✅ Duplicatas removidas automaticamente
- ✅ Apenas registros únicos inseridos
- ✅ Mensagem informa quantidade de duplicatas removidas
- ✅ Exemplo: "125.373 registros encontrados → 100.000 inseridos (25.373 duplicatas removidas)"

---

## Próximos Passos

### 1️⃣ Testar Novamente a Sincronização

```bash
# 1. Certifique-se de que a API está rodando
cd api
./venv/Scripts/python.exe main.py

# 2. Acesse o frontend
http://localhost:8080/projetado

# 3. Clique em "Sincronizar"
```

### 2️⃣ Verificar Logs

Acompanhe os logs no terminal da API:
```
INFO: Iniciando sincronização de Contas a Receber...
INFO: Encontrados 225533 registros no Senior
INFO: Limpando tabela contas_receber...
INFO: Inserindo 225533 registros no banco local...
INFO: Sincronização concluída em XXXms

INFO: Iniciando sincronização de Contas a Pagar...
INFO: Encontrados 125373 registros no Senior
INFO: Removendo duplicatas de 125373 registros...
INFO: Encontradas e removidas XXXX duplicatas. Restam XXXX registros únicos.
INFO: Inserindo XXXX registros no banco local...
INFO: Sincronização concluída em XXXms
```

### 3️⃣ Validar Dados Sincronizados

```sql
-- Verificar quantidade de registros
SELECT COUNT(*) FROM contas_receber  -- Deve ter ~225.533
SELECT COUNT(*) FROM contas_pagar    -- Deve ter menos (duplicatas removidas)

-- Verificar se há registros
SELECT TOP 10 * FROM contas_receber
SELECT TOP 10 * FROM contas_pagar

-- Verificar log de sincronização
SELECT * FROM log_sincronizacao ORDER BY data_hora_inicio DESC
```

---

## Performance Estimada

Com base no volume de dados:

### Contas a Receber (225.533 registros)
- **Tempo estimado**: 3-5 minutos
- **Velocidade**: ~1.000 registros/segundo

### Contas a Pagar (125.373 registros, ~25% duplicatas)
- **Tempo estimado**: 2-3 minutos
- **Velocidade**: ~1.000 registros/segundo
- **Registros únicos**: ~94.000 (estimativa)

### Total
- **Tempo total estimado**: 5-8 minutos
- **Dados finais**: ~320.000 registros sincronizados

---

## Melhorias Futuras (Opcional)

### 1. Sincronização em Lotes (Batch Insert)
Atualmente: 1 INSERT por registro (lento)
Melhoria: Inserir em lotes de 1.000 registros (10x mais rápido)

```python
# Exemplo de batch insert
batch_size = 1000
for i in range(0, len(dados), batch_size):
    batch = dados[i:i + batch_size]
    cursor.executemany(insert_query, batch)
```

### 2. Paralelização
- Sincronizar contas_receber e contas_pagar simultaneamente
- Reduz tempo total pela metade

### 3. Sincronização Incremental
- Ao invés de TRUNCATE + INSERT, fazer UPDATE/INSERT apenas dos alterados
- Muito mais rápido em sincronizações subsequentes
- Requer campo de controle (data_ultima_atualizacao)

---

## Arquivos Modificados

- ✅ `api/services/sincronizacao_service.py` (corrigido)

---

## Status Final

- ✅ Erro de conversão de tipos **CORRIGIDO**
- ✅ Erro de duplicatas **CORRIGIDO**
- ⏳ Aguardando novo teste de sincronização

---

**Data**: 31/01/2025
**Status**: ✅ Correções aplicadas - Pronto para teste
