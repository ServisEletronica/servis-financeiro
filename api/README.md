# API Financeiro Servis

API Python/FastAPI para gestão de contas a pagar e receber integrada com SQL Server.

## 🚀 Instalação

### 1. Criar ambiente virtual

```bash
cd api
python -m venv venv
```

### 2. Ativar ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Certifique-se de que o arquivo `.env` na raiz do projeto contém:

```env
DB_SERVER=seu_servidor
DB_PORT=1433
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

## ▶️ Executar API

```bash
python main.py
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📋 Endpoints Principais

### Dashboard
- `GET /api/dashboard/resumo?periodo=mes-atual` - Resumo financeiro (cards)
- `GET /api/dashboard/grafico-receitas-despesas` - Dados para gráfico de barras
- `GET /api/dashboard/grafico-evolucao` - Dados para gráfico de linha
- `GET /api/dashboard/transacoes?tipo=todos&periodo=mes-atual` - Lista de transações

### Contas
- `GET /api/contas/receber` - Lista contas a receber
- `GET /api/contas/pagar` - Lista contas a pagar
- `GET /api/contas/receber/total` - Total de receitas
- `GET /api/contas/pagar/total` - Total de despesas

## 🔧 Parâmetros de Período

- `mes-atual` - Mês corrente
- `mes-anterior` - Mês passado
- `trimestre` - Últimos 3 meses
- `ano` - Ano atual

## 🕐 Timezone

Configurado para: **America/Fortaleza (UTC-3)**

## 🏗️ Estrutura

```
api/
├── main.py              # Entry point
├── config.py            # Configurações
├── database.py          # Conexão SQL Server
├── models.py            # Modelos Pydantic
├── routes/              # Endpoints
│   ├── dashboard.py
│   └── contas.py
├── services/            # Lógica de negócio
│   ├── dashboard_service.py
│   ├── contas_receber_service.py
│   └── contas_pagar_service.py
└── utils/               # Utilitários
    └── calculos.py      # Cálculos financeiros
```

## 🔒 Segurança

- CORS configurado para aceitar requests do frontend
- Conexões com SQL Server via pool gerenciado
- Queries parametrizadas para prevenir SQL Injection

## 📊 Lógica de Cálculo

### Contas a Receber
```python
if VLRABE != 0 and RECDEC == 2:
    valor = -VLRABE
elif VLRABE == 0 and RECDEC == 2:
    valor = -VLRORI
elif VLRABE != 0 and RECDEC == 1:
    valor = VLRABE
else:
    valor = VLRORI
```

### Contas a Pagar
```python
if VLRABE > VLRRAT:
    valor = VLRRAT
elif VLRABE == 0:
    valor = VLRRAT
else:
    valor = VLRABE
```
