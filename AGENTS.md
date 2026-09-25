# Query Agent

AI-powered data agent for exploring and analyzing PostgreSQL databases using natural language.

## Project overview

- Frontend: Next.js, TypeScript, pnpm
- Backend: Django, Django REST Framework, Python, uv
- Database: PostgreSQL
- Infrastructure: Docker Compose

## Project structure

- `frontend` - Next.js application
- `backend` - Django/DRF application
- `backend/apps` - Django domain applications
- `backend/src` - Django project configuration

## Backend conventions

Django apps live under `backend/apps/`.

Current apps:

- `catalog` — categories and products
- `customers` — customer domain
- `orders` — orders, order items, payments and refunds
- `agent` — AI agent orchestration and tools

Prefer domain-oriented Django apps.

Do not create a separate Django app for every model.

Use Django migrations for all database schema changes.

Use PostgreSQL as the application database.

Use `uv` for Python dependency management.

Do not add `requirements.txt` or Pipenv.

## Frontend conventions

Use:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- pnpm

Follow a lightweight FSD-inspired structure:

- `src/app/` — routing and composition
- `src/features/` — feature-specific logic and UI
- `src/shared/` — reusable UI, API helpers, and utilities

Do not introduce full Feature-Sliced Design layers unless the project complexity requires them.

Use shadcn/ui for reusable interface primitives when appropriate.

Prefer existing shadcn/ui components over implementing equivalent primitives from scratch.

Do not add a new UI abstraction or wrapper around shadcn/ui unless it provides clear project-specific value.

Keep feature-specific UI inside its feature.

Keep generic reusable UI components under `src/shared/ui`.

Prefer Server Components unless client-side behavior is required.
Keep client components as small as practical.

## Docker

The application should be runnable using Docker Compose.

Services:

- `frontend` - Next.js application
- `backend` - Django/DRF application
- `postgres` - primary PostgreSQL database

The `postgres` service is the main application database.

Inside Docker Compose, services communicate using service names.

- backend → PostgreSQL: `postgres:5432`
- frontend server → backend: `backend:8000`

Do not use `localhost` for container-to-container communication.

## Development

Backend commands should generally be run through:

```bash
docker compose run --rm backend uv run ...
```

Examples:

```bash
docker compose run --rm backend uv run python manage.py migrate
docker compose run --rm backend uv run python manage.py makemigrations
docker compose run --rm backend uv run python manage.py test
```

Frontend dependencies are managed with pnpm.

## Database

PostgreSQL is the primary and only application database for this project.

Do not introduce SQLite for development, tests, or local fallback unless explicitly requested.

Django database configuration should use the PostgreSQL service from Docker Compose.

Inside containers, the database host is: `postgres`

## Code quality

Prefer:

- clear typing
- small focused functions
- explicit names
- domain-oriented structure
- minimal unnecessary abstraction

Do not overengineer early-stage features.

Run relevant checks/tests after changes.

## AI agent architecture

The application agent should use explicit tools rather than giving unrestricted database access to the model.

Database access for the AI agent must eventually be read-only.

Do not rely only on prompting for database safety.

Destructive SQL operations must be prevented at the tool/database permission level.

Keep agent orchestration separate from HTTP/DRF views.

DRF views should delegate business logic to services.