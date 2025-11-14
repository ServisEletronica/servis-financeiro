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
# Remover stack antigo se existir
docker stack rm financeiro 2>/dev/null || true

# Iniciar os serviços com docker-compose
docker-compose up -d

# Ou usando docker compose v2
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
docker-compose logs -f frontend
docker-compose logs -f backend

# Ver containers rodando
docker-compose ps

# Ver logs em tempo real
docker logs -f financeiro-frontend
docker logs -f financeiro-backend
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
docker-compose pull

# Recriar containers com as novas imagens
docker-compose up -d --force-recreate

# Ou manualmente
docker pull ghcr.io/serviseletronica/servis-financeiro-api:latest
docker pull ghcr.io/serviseletronica/servis-financeiro-frontend:latest
docker-compose up -d
```

## 🐛 Troubleshooting

### Verificar se o Traefik está detectando os serviços

```bash
# Ver labels do container
docker inspect financeiro-frontend
docker inspect financeiro-backend
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
docker logs -f traefik
```

### Reiniciar serviços

```bash
docker-compose restart frontend
docker-compose restart backend

# Ou reiniciar tudo
docker-compose restart
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
