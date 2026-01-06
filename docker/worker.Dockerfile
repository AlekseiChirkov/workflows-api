FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONBUFFERED=1

CMD ["uvicorn", "src.worker.main:app", "--host", "0.0.0.0", "--port=8080"]
