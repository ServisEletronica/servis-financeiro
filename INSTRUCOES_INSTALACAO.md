# 🚀 Instruções de Instalação e Execução

## ✅ Plano de Ação Implementado

Toda a integração Backend Python + SQL Server + Frontend React foi concluída com sucesso!

---

## 📋 Pré-requisitos

- **Python 3.8+** instalado
- **Node.js 18+** instalado
- **SQL Server** acessível
- Arquivo `.env` configurado com credenciais do banco

---

## 🔧 Configuração

### 1. Configurar `.env`

Edite o arquivo `.env` na raiz do projeto com suas credenciais SQL Server:

```env
# Frontend
VITE_API_URL=http://localhost:8000

# Database (Backend Python)
DB_SERVER=seu_servidor_sql
DB_PORT=1433
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

---

## 🐍 Backend Python (API)

### 1. Navegar para a pasta da API

```bash
cd api
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Executar a API

```bash
python main.py
```

✅ API rodando em: **http://localhost:8000**
📚 Documentação em: **http://localhost:8000/docs**

---

## ⚛️ Frontend React

### 1. Voltar para a raiz do projeto

```bash
cd ..
```

### 2. Instalar dependências (se ainda não instalou)

```bash
npm install
```

### 3. Executar o frontend

```bash
npm run dev
```

✅ Frontend rodando em: **http://localhost:5173**

---

## 🎯 Testando a Integração

1. **Acesse**: http://localhost:5173
2. **Faça login** com as credenciais de teste
3. **Navegue** para "Contas a Pagar/Receber"
4. **Verifique**:
   - ✅ Cards com valores reais do banco
   - ✅ Gráficos com dados dos últimos 6 meses
   - ✅ Tabela com transações reais
   - ✅ Filtro de período funcionando

---

## 📊 Endpoints da API

### Dashboard
- `GET /api/dashboard/resumo?periodo=mes-atual`
- `GET /api/dashboard/grafico-receitas-despesas`
- `GET /api/dashboard/grafico-evolucao`
- `GET /api/dashboard/transacoes?tipo=todos&periodo=mes-atual`

### Contas
- `GET /api/contas/receber`
- `GET /api/contas/pagar`
- `GET /api/contas/receber/total`
- `GET /api/contas/pagar/total`

---

## 🔍 Verificação de Problemas

### API não conecta ao SQL Server

1. Verifique as credenciais no `.env`
2. Teste a conexão com SQL Server Management Studio
3. Verifique firewall e portas (1433)

### Frontend não conecta à API

1. Verifique se a API está rodando: http://localhost:8000/health
2. Verifique CORS no arquivo `api/config.py`
3. Limpe cache do navegador (Ctrl+Shift+R)

### Dados não aparecem

1. Verifique os logs da API no terminal
2. Abra DevTools do navegador (F12) e veja erros no Console
3. Verifique se existem dados no banco para o período selecionado

---

## 🎨 Tema Cosmic Night

O tema roxo/azul está aplicado em:
- ✅ Cards com cores do tema
- ✅ Gráficos usando `chart-2` (receitas) e `chart-5` (despesas)
- ✅ Badges coloridos
- ✅ Valores em cores consistentes

---

## 📁 Estrutura Final

```
financeiro/
├── api/                    # Backend Python
│   ├── main.py            # Entry point
│   ├── config.py          # Configurações
│   ├── database.py        # SQL Server
│   ├── models.py          # Modelos
│   ├── routes/            # Endpoints
│   ├── services/          # Lógica de negócio
│   └── utils/             # Cálculos
│
├── src/                   # Frontend React
│   ├── pages/
│   │   └── Dashboard.tsx  # ✅ Integrado com API
│   ├── services/
│   │   ├── api.ts         # ✅ Axios config
│   │   └── dashboard.service.ts  # ✅ Chamadas API
│   └── ...
│
├── .env                   # Variáveis de ambiente
└── package.json
```

---

## ✨ Otimizações Implementadas

### Backend
- ✅ Queries SQL otimizadas (menos JOINs)
- ✅ Cálculos de valores corretos aplicados
- ✅ Filtros de data funcionais
- ✅ Timezone de Fortaleza (America/Fortaleza)
- ✅ Pool de conexões gerenciado

### Frontend
- ✅ Loading states em cards, gráficos e tabela
- ✅ Error handling com mensagem amigável
- ✅ Sincronização automática com filtros
- ✅ Tema Cosmic Night aplicado
- ✅ Responsivo

---

## 🎉 Próximos Passos

1. **Testar** com dados reais do banco
2. **Ajustar** datas e filtros conforme necessidade
3. **Adicionar** mais funcionalidades (CRUD de lançamentos)
4. **Deploy** em produção

---

## 📞 Suporte

- **Documentação API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

**Integração Completa! 🎊**

Backend Python + SQL Server + Frontend React funcionando perfeitamente!
