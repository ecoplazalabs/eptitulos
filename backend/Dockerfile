FROM python:3.12-slim

WORKDIR /app

# Install build deps for asyncpg (C extension)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code and migrations
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini alembic.ini

# Create storage directory
RUN mkdir -p /app/storage

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
