# ---- builder ----
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# build deps (only in builder)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY ../requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---- runner ----
FROM python:3.13-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# non-root user
RUN adduser --disabled-password --gecos "" appuser

# install deps
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# copy app
COPY ../src ./src
COPY ../alembic ./alembic
COPY ../alembic.ini ./alembic.ini

USER appuser

# Cloud Run sets PORT. Locally default 8000.
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8080"]
