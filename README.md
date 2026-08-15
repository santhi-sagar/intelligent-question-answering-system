## SRM UniChat — University SRM RAG Chatbot (Monorepo)

Production-ready mono-repo for a Retrieval-Augmented Generation chatbot tailored for SRM University. Includes FastAPI backend with pgvector search, React/Vite frontend, and Capacitor Android wrapper.

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 20+

### Quickstart
```bash
# From repo root
cp .env.example .env
cp web/.env.example web/.env
# Edit .env and set OPENAI_API_KEY and POSTGRES_PASSWORD

docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Services:
- Backend (FastAPI): http://localhost:8000 (Docs at /docs)
- Web (Vite dev): http://localhost:5173
- Postgres: localhost:5432 (inside compose network hostname: db)

### Environment
Root `.env`:
```
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=auto
EMBEDDING_MODEL=auto
POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql+psycopg://postgres:${POSTGRES_PASSWORD}@db:5432/srm?sslmode=disable
CORS_ALLOW_ORIGINS=http://localhost:5173
```

Web `.env`:
```
VITE_API_BASE=http://localhost:8000
```

### Database Migration
```bash
docker compose exec backend alembic upgrade head
```

The initial migration creates the `vector` extension and all RAG and canonical tables with indexes.

### Running Tests
```bash
docker compose exec backend pytest -q
```

### Ingestion and Ask
- Upload files via `POST /api/ingest/file` (PDF/DOCX/TXT/CSV/XLSX).
- Ask questions with `POST /api/ask`.

Example request:
```json
{ "question": "Fees for B.Tech CSE 2025–26 at KTR?", "filters": {"campus":"KTR","program":"B.Tech CSE","year":"2025-26"} }
```

### Android (Capacitor)
After building the web app:
```bash
cd web && npm run build
cd ..
npx cap sync android
npx cap open android
```

### Notes
- CORS is restricted to origins set in `CORS_ALLOW_ORIGINS`.
- Do not commit secrets; use `.env` files locally.
- Basic rate limiting placeholder is included.


