## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.13-bookworm AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential && \
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

RUN useradd --create-home appuser
USER appuser

WORKDIR /app

COPY src ./src
COPY --from=builder /app/.venv .venv

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

# Expose the gRPC server port
EXPOSE 4000

# Start the Dagster gRPC server
CMD ["dagster", "code-server", "start", "--host", "0.0.0.0", "--port", "4000", "--module-name", "src.definitions", "--attribute", "defs"]