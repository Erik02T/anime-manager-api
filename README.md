# Anime Manager API

REST API for anime tracking, social features, rankings, and external catalog sync (Jikan/MAL data).

## Features
- Layered architecture (`Router -> Service -> Repository`)
- JWT authentication with issuer/audience claims
- Role-based authorization (`admin`, `user`)
- Rate limiting (Redis with in-memory fallback)
- Social feed, reviews, comments, and follows
- User and global statistics
- External catalog integration (Jikan API)
- External data caching
- Alembic migrations
- Docker support
- CI with GitHub Actions
- Prometheus metrics endpoint (`/metrics`)

## Architecture
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

## Project Structure
```text
app/
  core/          # auth, config, cache, logging, permissions, rate limit
  external/      # external API client
  events/        # event bus + handlers
  jobs/          # scheduled jobs
  repositories/  # data access layer
  routers/       # HTTP endpoints
  services/      # business logic
  tests/         # unit/integration tests
alembic/         # DB migrations
```

## Environment Variables
Use `.env.example` as a base.

```env
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
JIKAN_BASE_URL=https://api.jikan.moe/v4
JWT_ISSUER=anime-manager
JWT_AUDIENCE=anime-manager-users
ENVIRONMENT=production
ENABLE_RUNTIME_MIGRATIONS=false
REQUIRE_ALEMBIC_IN_PRODUCTION=true
```

## Run Locally
```bash
docker compose up --build
```

## Deploy (Render)
- Runtime: Python
- Root directory: `backend`
- Build command:
```bash
pip install -r requirements.txt
```
- Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Observability
- `GET /health`
- `GET /metrics`
- Structured JSON logs

## Tests
```bash
pytest -q -p no:cacheprovider
```

## Migrations
```bash
alembic upgrade head
```

## Author
Erik Sant  
GitHub: https://github.com/Erik02T
