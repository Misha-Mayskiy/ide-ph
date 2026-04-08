# IDE Builder MVP

MVP конструктора IDE: пользователь вводит текстовый prompt, backend асинхронно генерирует `ide-config`, frontend рендерит персонализированную IDE и позволяет сохранять профили.

## Stack

- Frontend: React + TypeScript + Vite + Monaco
- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic
- DB: PostgreSQL
- Infra: Docker Compose

## Local Run (Docker)

1. Опционально задайте env:
   - `OPENAI_API_KEY` для LLM-интерпретации prompt
   - `VITE_DEMO_JWT` для автоподстановки JWT во фронте
2. Запустите:

```bash
docker compose up --build
```

3. Откройте:
   - Frontend: `http://localhost:5173`
   - Backend docs: `http://localhost:8000/docs`

## JWT

Все `api/v1` ручки требуют Bearer JWT, где claim `sub` содержит `user_id`.

Локальный пример токена:

```bash
python - <<'PY'
from jose import jwt
print(jwt.encode({"sub":"demo-user"}, "dev-secret-change-me", algorithm="HS256"))
PY
```

## API Contract

- `POST /api/v1/generations` -> `{ generationId, status, pollUrl }`
- `GET /api/v1/generations/{id}` -> `{ status, progress, ideConfig?, error? }`
- `POST /api/v1/profiles` -> create profile
- `GET /api/v1/profiles` -> list profiles
- `GET /api/v1/profiles/{id}` -> profile by id
- `PUT /api/v1/profiles/{id}` -> update
- `DELETE /api/v1/profiles/{id}` -> delete

## Backend Dev

```bash
cd backend
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend Dev

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend unit:

```bash
cd frontend
npm run test
```

Frontend e2e:

```bash
cd frontend
npm run e2e
```
