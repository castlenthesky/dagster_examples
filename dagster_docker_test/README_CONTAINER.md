# Dagster Docker Container Setup

This document describes the containerized Dagster code location setup based on best practices for distributed Dagster deployments.

## Overview

The container runs a Dagster gRPC code server that can be connected to a main Dagster webserver instance. The container is configured to:
- Connect to a PostgreSQL database (Supabase-compatible) for storage
- Expose a gRPC server on port 4000
- Use environment variables for secure configuration
- Support health checks for container orchestration

## Container Status

✅ **Container is built and running successfully**
- Image: `dagster_docker_test:latest`
- Container: `dagster_docker_example`
- gRPC Port: `4000` (mapped to host port 4000)
- Status: Healthy

## Configuration Files

### 1. Dockerfile (`docker/Dockerfile`)
- Multi-stage build with Python 3.13
- Installs system dependencies (libpq-dev, gcc, python3-dev) for psycopg2 compilation
- Sets up DAGSTER_HOME at `/opt/dagster/dagster_home`
- Copies dagster.yaml configuration
- Runs as non-root user (`appuser`)

### 2. docker-compose.yml (`docker/compose.yml`)
- Service name: `dagster_remote_code`
- Environment variables for Postgres connection
- Network: `dagster_network` (bridge)
- Volume mounts for logs and source code

### 3. dagster.yaml (`docker/dagster.yaml`)
- Uses environment variable interpolation for security
- Configured for Supabase (SSL required)
- Local compute log manager

## Environment Variables

The container expects these environment variables (set in `docker/compose.yml`):

- `DAGSTER_POSTGRES_USER`: Postgres username (default: `postgres`)
- `DAGSTER_POSTGRES_PASSWORD`: Postgres password (from `${SUPABASE_PASSWORD}` or default)
- `DAGSTER_POSTGRES_HOST`: Postgres hostname (from `${SUPABASE_HOST}` or `localhost`)
- `DAGSTER_POSTGRES_DB`: Database name (default: `postgres`)
- `DAGSTER_POSTGRES_PORT`: Postgres port (default: `5432`)
- `DAGSTER_HOME`: Path to Dagster home directory (`/opt/dagster/dagster_home`)
- `DAGSTER_CURRENT_IMAGE`: Image name for Docker run launcher

## Connecting from Main Dagster Instance

To connect your main Dagster webserver to this code location, create or update your `workspace.yaml` file:

```yaml
load_from:
  - grpc_server:
      host: localhost
      port: 4000
      location_name: "docker_remote_code"
```

If your main instance is running in a different container or on a different host, replace `localhost` with the appropriate hostname or IP address.

## Usage

### Start the container:
```bash
cd /home/bmoney/projects/integrations/dagster_docker_test
docker compose -f docker/compose.yml up -d
```

### Stop the container:
```bash
docker compose -f docker/compose.yml down
```

### View logs:
```bash
docker compose -f docker/compose.yml logs -f
```

### Check health:
```bash
docker exec dagster_docker_example dagster api grpc-health-check -p 4000
```

### Rebuild after code changes:
```bash
docker compose -f docker/compose.yml build
docker compose -f docker/compose.yml up -d
```

## Testing

The container includes a test asset (`example_gRPC`) that can be executed via the main Dagster instance. Once connected:

1. Start your main Dagster webserver
2. Ensure it can reach the container on port 4000
3. The code location should appear in the Dagster UI
4. You can materialize the `example_gRPC` asset to test execution

## Troubleshooting

### Container won't start
- Check logs: `docker compose -f docker/compose.yml logs`
- Verify environment variables are set correctly
- Ensure port 4000 is not already in use

### Can't connect from main instance
- Verify the container is running: `docker compose -f docker/compose.yml ps`
- Test gRPC health: `docker exec dagster_docker_example dagster api grpc-health-check -p 4000`
- Check network connectivity between containers/hosts
- Verify workspace.yaml points to the correct host and port

### Postgres connection issues
- Verify environment variables match your Supabase credentials
- Check that `sslmode: require` is set in dagster.yaml (required for Supabase)
- Test Postgres connectivity from within the container:
  ```bash
  docker exec -it dagster_docker_example bash
  # Then test connection with psql or Python
  ```

### Assets not appearing
- Verify the code location is loaded in workspace.yaml
- Check that the module path (`src.definitions`) is correct
- Review container logs for import errors

## Next Steps

1. Update environment variables in `docker/compose.yml` with your actual Supabase credentials
2. Configure your main Dagster instance's `workspace.yaml` to connect to this code location
3. Start your main Dagster webserver and verify the code location appears
4. Test asset materialization through the Dagster UI
