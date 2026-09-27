FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

CMD ["sh", "-c", "uv run python manage.py migrate && uv run gunicorn src.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
