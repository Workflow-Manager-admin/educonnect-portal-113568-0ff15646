# EduConnect Portal API

## Quickstart

This repo provides a fully automated, dockerized FastAPI + PostgreSQL backend for the EduConnect student portal. No manual DB/ORM setup required.

### 1. One-command start (first time or after pulling changes):

```bash
# Copy and edit env vars if desired
cp .env.example .env

# Launch everything (API + Postgres, with migrations):
docker-compose up --build
```

This exposes:
- API at [http://localhost:8000/docs](http://localhost:8000/docs)
- PostgreSQL at `localhost:5432` (user: `admin`, pass: `password`, db: `eduportal`)

### 2. Directory structure

- `backend_api/src/api/` - FastAPI code, models, endpoints
- `backend_api/alembic/` - Alembic migrations
- `media/` - Uploaded PDF files etc. (mounted to backend container)
- `docker-compose.yml` / `Dockerfile` - Automation and networking

### 3. Main features

- Student & admin authentication (JWT)
- Timetable CRUD (PDF upload/download)
- Scorecard CRUD
- Announcement CRUD
- OpenAPI docs at `/docs`
- Automated DB migrations (no manual SQL, no Alembic commands required)

### 4. Environment/configuration

Edit `.env` to override DB URL, API secret, etc.

### 5. Development
- Code & migrations hot-reloaded in backend container.
- All DB schema changes tracked/migrated via Alembic.

For further detail, see API docs or source code.

---

**You're ready!**
