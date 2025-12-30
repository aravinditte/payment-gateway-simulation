# -------------------------------------------------
# Base Image
# -------------------------------------------------
FROM python:3.11-slim AS runtime

# -------------------------------------------------
# Environment
# -------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# -------------------------------------------------
# System Dependencies
# -------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# Python Dependencies
# -------------------------------------------------
# Copy only dependency metadata first for better caching
COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install .

# -------------------------------------------------
# Application Code
# -------------------------------------------------
COPY app ./app

# -------------------------------------------------
# Runtime User (Security Best Practice)
# -------------------------------------------------
RUN useradd -m appuser
USER appuser

# -------------------------------------------------
# Expose & Run
# -------------------------------------------------
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
