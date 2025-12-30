# -------------------------------------------------
# Base Image
# -------------------------------------------------
FROM postgres:15-alpine

# -------------------------------------------------
# Environment Defaults (override in docker-compose)
# -------------------------------------------------
ENV POSTGRES_DB=payments \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

# -------------------------------------------------
# Initialization Scripts
# -------------------------------------------------
# Place SQL or shell scripts here if needed
# They will run once on first container startup
COPY init.sql /docker-entrypoint-initdb.d/init.sql
