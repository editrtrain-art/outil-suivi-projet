# syntax=docker/dockerfile:1

# ── Build Stage ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a wheels directory
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ── Final Runtime Stage ──────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

# Add a non-root user for security
RUN groupadd -r nexus && useradd -r -g nexus nexus

# Install runtime system dependencies (PostgreSQL client libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application source
COPY . .

# Ensure permissions for migrations and db file if using sqlite in staging
RUN chown -R nexus:nexus /app

USER nexus

# Expose FastAPI port
EXPOSE 8000

# Healthcheck for orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
