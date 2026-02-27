# 🎌 Anime Manager API

API RESTful para gerenciamento de animes com autenticação JWT, sistema social e integração com MyAnimeList via Jikan.

## 🚀 Features
- Arquitetura em camadas (Router -> Service -> Repository)
- JWT com `iss`/`aud`
- RBAC (`admin`/`user`)
- Rate limiting (Redis + fallback in-memory)
- Feed social
- Reviews e comentários
- Estatísticas por usuário e globais
- Integração externa com Jikan
- Cache de dados externos
- Alembic migrations
- Dockerized
- CI com GitHub Actions
- Metrics Prometheus (`/metrics`)

## 🧱 Arquitetura
```text
Client (Web/Mobile)
        |
     FastAPI Routers
        |
      Services
        |
    Repositories
        |
   SQLAlchemy Models
        |
 PostgreSQL / SQLite

External Catalog (Jikan API)
        |
 External Client + Mapper
        |
 AnimeImportService
        |
 Internal Anime Catalog
```

## 📁 Estrutura
```text
app/
  core/          # auth, config, cache, logging, permissions, rate limit
  external/      # cliente da API externa
  events/        # event bus + handlers
  jobs/          # jobs periódicos
  repositories/  # acesso a dados
  routers/       # endpoints HTTP
  services/      # regras de negócio
  tests/         # testes unitários/integrados
alembic/         # migrations
```

## 🔐 Variáveis de ambiente
Use `.env.example` como base.

```env
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
JIKAN_BASE_URL=https://api.jikan.moe/v4
JWT_ISSUER=anime-manager
JWT_AUDIENCE=anime-manager-users
```

## 🐳 Rodar localmente
```bash
docker compose up --build
```

## ☁ Deploy
- Railway (app + PostgreSQL + Redis)
- Start command em produção:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📊 Observabilidade
- `GET /health`
- `GET /metrics`
- Logs estruturados JSON

## 🧪 Testes
```bash
pytest -q -p no:cacheprovider
```

## 🔄 Migrações
```bash
alembic upgrade head
```

## 👤 Autor
Erik Sant
- GitHub: https://github.com/Erik02T
