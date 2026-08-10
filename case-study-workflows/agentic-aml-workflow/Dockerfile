# Dockerfile
# Agentic AML Compliance Workflow — Pipeline API
#
# Build:  docker build -t aml-pipeline .
# Run:    docker run -p 8000:8000 --env-file .env aml-pipeline

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# (libpq-dev for psycopg2 compilation if using source build instead of binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching — only rebuilds on requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for OFAC local list and other data files
RUN mkdir -p /app/data

# Non-root user for security
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Health check — used by docker compose depends_on
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use uvicorn directly.
# --reload is off in production (ENVIRONMENT=production sets no-reload via main.py).
# For development with auto-reload, override CMD in docker-compose.yml.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
