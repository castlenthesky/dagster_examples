## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.13-bookworm AS builder

# Install system packages required for compiling psycopg2 and general operations
# libpq-dev: Postgres headers for compiling psycopg2
# gcc: C Compiler
# python3-dev: Python headers for extensions
# git: Often required for installing dependencies from repositories
RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
        gcc \
        python3-dev \
        git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download the latest installer, install it and then remove it
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.13-slim-bookworm AS production

# Install runtime dependencies for Postgres connectivity
# libpq5: Shared runtime libraries for Postgres connection
RUN apt-get update && apt-get install --no-install-recommends -y \
        libpq5 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up environment variables for production
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Ensures stdout/stderr are flushed immediately (vital for Docker logs)
# DAGSTER_HOME: Sets the location for the instance configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/opt/dagster/dagster_home \
    PATH="/app/.venv/bin:$PATH"

# Create the DAGSTER_HOME directory and /app directory
RUN mkdir -p $DAGSTER_HOME /app

# Copy the Dagster Instance Configuration (as root, then we'll set ownership)
# This file MUST exist and contain the Postgres config
COPY docker/dagster.yaml $DAGSTER_HOME/dagster.yaml

# Create appuser and set ownership of directories
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app $DAGSTER_HOME

USER appuser

WORKDIR /app

# Copy application code and virtual environment
COPY --chown=appuser:appuser src ./src
COPY --from=builder --chown=appuser:appuser /app/.venv .venv

# Expose the gRPC server port
EXPOSE 4000

# Healthcheck ensures the gRPC server is responsive before the Host attempts to use it
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD dagster api grpc-health-check -p 4000 || exit 1

# Start the Dagster gRPC Code Server
# -h 0.0.0.0 binds to all interfaces (required for Docker)
# -p 4000 sets the port
# -m specifies the python module to load
CMD ["dagster", "code-server", "start", "--host", "0.0.0.0", "--port", "4000", "--module-name", "src.definitions", "--attribute", "defs"]