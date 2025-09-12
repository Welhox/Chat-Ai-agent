# ----- Base (shared) -----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*
# Copy only requirement spec first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt

# ----- Dev image (autoreload, mounts code) -----
FROM base AS dev
# In dev we don’t copy source; compose will mount it
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ----- Prod image (copy code, non-root, gunicorn) -----
FROM base AS prod
# Add a non-root user
RUN useradd -m appuser
COPY . /app
# Optional: verify app imports at build time
RUN python -m py_compile main.py || true
USER appuser
EXPOSE 8000
# gunicorn with uvicorn workers is robust for prod
# tweak workers/threads for your target CPU
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
