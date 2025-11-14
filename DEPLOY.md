# 🚀 Deploy do Sistema Financeiro Servis

## 📋 Visão Geral

Este documento explica como fazer o deploy do sistema financeiro usando Docker.

## 🏗️ Arquitetura

- **Frontend**: React + Vite (porta 6009)
- **Backend**: FastAPI + Python (porta 3006)
- **Banco de Dados**: SQL Server (externo)

## 🐳 Deploy com Docker

### Usando Docker Compose (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/ServisEletronica/servis-financeiro.git
cd servis-financeiro
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

3. **Inicie os containers**
```bash
docker-compose up -d
```

4. **Acesse a aplicação**
- Frontend: http://localhost:6009
- API: http://localhost:3006
- Docs da API: http://localhost:3006/docs

### Usando Docker manualmente

#### Backend (API)
```bash
cd api
docker build -t servis-financeiro-api .
docker run -d -p 3006:3006 --env-file ../.env servis-financeiro-api
```

#### Frontend
```bash
docker build -t servis-financeiro-frontend --build-arg VITE_API_URL=http://localhost:3006 .
docker run -d -p 6009:6009 servis-financeiro-frontend
```

## 🔄 CI/CD com GitHub Actions

O projeto está configurado com GitHub Actions para build automático quando houver push na branch `main`.

### Imagens geradas

As imagens Docker são automaticamente publicadas no GitHub Container Registry:

- `ghcr.io/serviseletronica/servis-financeiro-api:latest`
- `ghcr.io/serviseletronica/servis-financeiro-frontend:latest`

### Configurar secrets

No GitHub, vá em **Settings > Secrets and variables > Actions** e adicione:

- `VITE_API_URL`: URL da API em produção (ex: `https://api.servis.com.br`)

### Pull das imagens

```bash
# Autenticar no GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull das imagens
docker pull ghcr.io/serviseletronica/servis-financeiro-api:latest
docker pull ghcr.io/serviseletronica/servis-financeiro-frontend:latest

# Executar
docker run -d -p 3006:3006 --env-file .env ghcr.io/serviseletronica/servis-financeiro-api:latest
docker run -d -p 6009:6009 ghcr.io/serviseletronica/servis-financeiro-frontend:latest
```

## 🔧 Variáveis de Ambiente

### Backend (.env)

```env
# Banco de Dados SQL Server
DB_SERVER=seu-servidor.database.windows.net
DB_PORT=1433
DB_USER=seu-usuario
DB_PASSWORD=sua-senha
DB_NAME=servis_financeiro

# Segurança
SECRET_KEY=sua-chave-secreta-aqui

# OpenAI (para OCR dos calendários)
OPENAI_API_KEY=sk-...
```

### Frontend (build args)

- `VITE_API_URL`: URL da API (default: `http://localhost:3006`)

## 📦 Estrutura de Portas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Frontend | 6009 | Aplicação React |
| Backend | 3006 | API FastAPI |

## 🔄 Atualizar Deploy

### Com Docker Compose
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Com imagens do GitHub
```bash
docker pull ghcr.io/serviseletronica/servis-financeiro-api:latest
docker pull ghcr.io/serviseletronica/servis-financeiro-frontend:latest

# Parar containers antigos
docker stop servis-financeiro-api servis-financeiro-frontend
docker rm servis-financeiro-api servis-financeiro-frontend

# Iniciar novos containers
docker run -d --name servis-financeiro-api -p 3006:3006 --env-file .env ghcr.io/serviseletronica/servis-financeiro-api:latest
docker run -d --name servis-financeiro-frontend -p 6009:6009 ghcr.io/serviseletronica/servis-financeiro-frontend:latest
```

## 🐛 Troubleshooting

### Ver logs dos containers
```bash
docker-compose logs -f
# ou
docker logs servis-financeiro-api
docker logs servis-financeiro-frontend
```

### Acessar shell do container
```bash
docker exec -it servis-financeiro-api sh
```

### Rebuild sem cache
```bash
docker-compose build --no-cache
```

## 📚 Documentação Adicional

- [README.md](./README.md) - Visão geral do projeto
- [RECEBIVEIS_CARTAO.md](./RECEBIVEIS_CARTAO.md) - Sistema de recebíveis de cartão
- [api/AUTH_SETUP.md](./api/AUTH_SETUP.md) - Sistema de autenticação

---

**Data da última atualização:** 2025-01-14
