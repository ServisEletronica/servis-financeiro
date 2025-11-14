# 🚀 Deploy do Sistema Financeiro com Traefik

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Traefik configurado e rodando
- Rede `ocorrenciasapp_ocorrencias-net` criada
- DNS `financeiro.serviseletronica.com.br` apontando para o servidor

## 🔧 Configuração

### 1. Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# Banco de Dados SQL Server
DB_SERVER=seu-servidor.database.windows.net
DB_PORT=1433
DB_USER=seu-usuario
DB_PASSWORD=sua-senha
DB_NAME=servis_financeiro

# Segurança
SECRET_KEY=sua-chave-secreta-jwt-aqui

# OpenAI (para OCR dos calendários)
OPENAI_API_KEY=sk-...
```

### 2. Pull das Imagens Docker

```bash
# Autenticar no GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull das imagens
docker pull ghcr.io/serviseletronica/servis-financeiro-api:latest
docker pull ghcr.io/serviseletronica/servis-financeiro-frontend:latest
```

### 3. Deploy

```bash
# Iniciar os serviços
docker stack deploy -c docker-compose.yml financeiro

# Ou com docker compose (modo standalone)
docker compose up -d
```

## 🌐 Roteamento com Traefik

### Frontend
- **URL**: `https://financeiro.serviseletronica.com.br`
- **Porta**: 6009
- **Rotas**: Todas exceto `/api/*`
- **SSL**: Cloudflare (certresolver=cloudflareResolver)

### Backend
- **URL**: `https://financeiro.serviseletronica.com.br/api/*`
- **Porta**: 3006
- **Rotas**: Apenas `/api/*`
- **SSL**: Cloudflare (certresolver=cloudflareResolver)

### Redirecionamento HTTP → HTTPS
Ambos os serviços estão configurados para redirecionar automaticamente HTTP para HTTPS.

## 📊 Verificar Status

```bash
# Ver logs
docker service logs financeiro_frontend
docker service logs financeiro_backend

# Ver serviços rodando
docker service ls

# Ver tasks dos serviços
docker service ps financeiro_frontend
docker service ps financeiro_backend
```

## 🔍 Healthchecks

### Frontend
```bash
curl http://localhost:6009/
```

### Backend
```bash
curl http://localhost:3006/health
```

## 🔄 Atualizar Deploy

```bash
# Pull das novas imagens
docker pull ghcr.io/serviseletronica/servis-financeiro-api:latest
docker pull ghcr.io/serviseletronica/servis-financeiro-frontend:latest

# Atualizar serviços
docker service update --image ghcr.io/serviseletronica/servis-financeiro-api:latest financeiro_backend
docker service update --image ghcr.io/serviseletronica/servis-financeiro-frontend:latest financeiro_frontend
```

## 🐛 Troubleshooting

### Verificar se o Traefik está detectando os serviços

```bash
# Ver labels do container
docker service inspect financeiro_frontend --pretty
docker service inspect financeiro_backend --pretty
```

### Verificar network

```bash
# Listar networks
docker network ls

# Verificar se a network existe
docker network inspect ocorrenciasapp_ocorrencias-net
```

### Logs do Traefik

```bash
docker service logs traefik
```

### Reiniciar serviços

```bash
docker service update --force financeiro_frontend
docker service update --force financeiro_backend
```

## 📝 Estrutura de Portas

| Serviço | Porta Interna | Porta Externa | Descrição |
|---------|---------------|---------------|-----------|
| Frontend | 6009 | 6009 | React App (Nginx) |
| Backend | 3006 | 3006 | FastAPI |

## 🔐 Certificados SSL

Os certificados são gerenciados automaticamente pelo Traefik usando o resolver `cloudflareResolver`.

Certifique-se de que o Traefik está configurado com:
- DNS challenge da Cloudflare
- Email para Let's Encrypt
- Storage para os certificados

## 📚 Documentação Adicional

- [DEPLOY.md](./DEPLOY.md) - Deploy básico com Docker
- [README.md](./README.md) - Visão geral do projeto
- [RECEBIVEIS_CARTAO.md](./RECEBIVEIS_CARTAO.md) - Sistema de recebíveis

---

**Data da última atualização:** 2025-01-14
