# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY src src
COPY alembic alembic
COPY alembic.ini alembic.ini

# Copy .env if present (for docker-compose)
COPY ../.env .env

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
