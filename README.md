# Project Overview

[Dagster](https://dagster.io/) is a highly-configurable and powerful code orchestration platform (like Airflow [but with different design decisions](https://dagster.io/blog/dagster-airflow)). This project serves as an overview of how to self-host the dagster UI in a way that allows for orchestration of many smaller dagster deployments - from easy to complex, from local to distributed - all without a headache.

**With this guide, you can have a distributed, and resilliant data orchestration platform with minimal effort and maximum understanding.**

*Why Dagster?*

 Organizations have a growing set of interests across a growing variety of priorities that requires a growing number of systems to be linked together. Dagster is an orchestration platform that helps wrangle and make sense of that chaos. It provides a centralized hub where data teams and executives can inspect, and interogate their data pipelines to make sure everything is running smoothly. In short - it let's you Manage and Observe your data pipelines.

# Overview of Dagster Features:
## 1. Pipeline Health Summary

Get a global overview of your data's health in a single view!

![run_history](assets/run_history.png)
![overview](assets/overview.png)

## 2. Data Lineage View

Easily trace where your data is coming from, where it is going, and how healthy those flows are.

![lineage](assets/lineage.png)

## 3. Lineage Health

Individual assets and their links help track issues when your data pipeline isn't running as you'd expect.

![example_dag](assets/example_dag.png)

## 4. Data Quality Checks

Test your data along the way. Simply business rule validation throughout your pipeline helps ensure the quality of the data being output.

![quality_checks](assets/quality_checks.png)

## 5. Automated Alerting

Receive automated alerts via slack, MS Teams, discord, telegra, etc. whenever an individual asset or entire jobs fails.

![alert](assets/alert.png)

## And more!!!
- Partitioning
- Scheduling
- Dynamic Job Triggering
- Automatic Retry Policies
- Freshness Warnings
- Metadata Capture

## Consider the Dagster cloud offering "Dagster+" for even more features!


# Dagster Multi-Code-Location Orchestration Guide

This repository demonstrates how to configure a single Dagster webserver and daemon to orchestrate code across various types of code locations and configuration methods. This is essential for managing complex data pipelines where code lives in separate repositories, containers, or environments.

These patterns allow your organization to deploy many smaller data pipelines without having to create a monolithic system. Sales' data pipeline doesn't need to live in the same environment to the ML Ops pipeline.

## Project Structure

```sh
.
├── 00_master/                    # Central Webserver and Daemon
│   ├── src/definitions/          # Local definitions (module and single-file examples)
│   │   ├── __init__.py           # Module-level code location example
│   │   ├── assets.py             # Assets loaded by module code location
│   │   └── single_file.py        # Single-file code location example
│   ├── .env                      # Environment variables (database connection, etc.)
│   ├── .env.EXAMPLE              # Template for environment variables
│   ├── workspace.yaml            # Defines all code locations (local and remote)
│   └── dagster.yaml              # Global Dagster configuration (run storage, logging)
│
├── dagster_remote_test/          # Remote Package Code Location Example
│   └── src/definitions/          # Definitions loaded as remote package
│       └── __init__.py           # Validates executable location (custom .venv)
│
└── dagster_docker_test/          # Remote gRPC Code Server Example
    ├── src/definitions/          # Definitions served via gRPC
    │   ├── __init__.py           # Module loader
    │   └── assets.py             # Example gRPC-served assets
    └── docker/
        ├── Dockerfile            # Builds Dagster gRPC server container
        └── compose.yml           # Docker Compose configuration
```

## Quick Start

### 1. Set Up Environment Variables

Copy the example environment file and configure your database connection:

```bash
cd 00_master
cp .env.EXAMPLE .env
# Optionally: Edit .env and set DAGSTER_DATABASE_URL
# Database can be postgres or sqlite
# Data will not persist after you close dagster without the .env
```

### 2. Start Remote Code Server (Optional - for gRPC example)

If you want to test the remote gRPC code location:

```bash
cd dagster_docker_test/docker
docker compose up -d
```

This builds a docker container, launches a Dagster instance, and exposes the gRPC server on `localhost:4556`. The core service defined in `00_master` will look for the code in this example folder via that gRPC server.

### 3. Start the Central Webserver and Daemon

From the `00_master` directory:

```bash
dagster dev -h 0.0.0.0 -p 4550 -w workspace.yaml
# -h 0.0.0.0 listens from all hosts
# -p 4550 specifys port 4550
# -w workspace.yaml tells dagster which workspace file to load
```

This starts:
- **Webserver**: UI at `http://localhost:4550`
- **Daemon**: Background process that executes runs

The webserver reads `workspace.yaml` to discover all code locations and `dagster.yaml` for run configuration.

---

## Local Code-Base Development: Use `[tool.dg]` in `pyproject.toml`

For local development of individual code locations, you can configure Dagster directly in your `pyproject.toml` file using the `[tool.dg.project]` section. This eliminates the need for a `workspace.yaml` file when working on a single project, making development faster and simpler.

### When to Use This Pattern

- **Single Project Development**: Working on one code location at a time
- **Rapid Iteration**: No need to maintain `workspace.yaml` during development
- **Team Autonomy**: Each project can define its own code location independently
- **CI/CD**: Automated discovery of code locations in monorepos

### Configuration

Add a `[tool.dg.project]` section to your `pyproject.toml`:

```toml
[tool.dg.project]
code_location_name = "dagster_local_dev"
root_module = "src"
# Optional: defaults to <root_module>.definitions if omitted
# code_location_target_module = "src.definitions"
```

### Key Parameters

- **`code_location_name`**: Unique identifier for this code location (appears in the Dagster UI)
- **`root_module`**: The base package name of your project (e.g., `"src"` if your code is in `src/`)
- **`code_location_target_module`**: (Optional) The specific module containing your `Definitions` object. Defaults to `<root_module>.definitions` if omitted.

### Example: `dagster_remote_test/pyproject.toml`

```toml
[tool.dg.project]
code_location_name = "dagster_local_dev"
# Required: The root module of your project (base package name).
# If your definitions are in src.dagster_definitions, this could be "src" if src is the package root.
root_module = "src"
# Optional: The submodule where the top-level Definitions object is located for loading as a code location.
# This is the equivalent to pointing to your module in the old load_from syntax.
# Defaults to <root_module>.definitions if omitted.
# code_location_target_module = "src.definitions"
```

### Running Without `workspace.yaml`

With `[tool.dg.project]` configured, you can run Dagster directly from any project directory:

```bash
cd dagster_remote_test
dagster dev -h 0.0.0.0 -p 4550
```

Dagster will:
1. Automatically detect the `[tool.dg.project]` configuration in `pyproject.toml`
2. Load the code location from the specified module
3. Start the webserver and daemon with just that code location

### How It Works

When you run `dagster dev` without a `workspace.yaml` file, Dagster:
1. Scans the current directory for `pyproject.toml`
2. Reads the `[tool.dg.project]` section
3. Constructs a code location using:
   - `code_location_name` as the location identifier
   - `root_module` (or `code_location_target_module` if specified) to find the `Definitions` object
4. Loads the definitions and makes them available in the UI

### File Structure Requirements

Your project structure must match the configuration:

```
dagster_remote_test/
├── pyproject.toml              # Contains [tool.dg.project]
├── src/
│   └── definitions/
│       └── __init__.py          # Contains: defs = Definitions(...)
```

If `root_module = "src"` and `code_location_target_module` is omitted, Dagster will look for `src.definitions` and expect a `defs` variable in `src/definitions/__init__.py`.

### Custom Definitions Variable Name

If your `Definitions` object has a different name (not `defs`), you can specify it:

```toml
[tool.dg.project]
code_location_name = "my_project"
root_module = "src"
code_location_target_module = "src.my_definitions"
# Then in src/my_definitions/__init__.py: my_defs = Definitions(...)
```

However, note that `[tool.dg.project]` doesn't directly support custom attribute names. For custom attribute names, you'll need to use `workspace.yaml` with the `attribute` parameter.

### Benefits Over `workspace.yaml` for Local Development

1. **Simpler Setup**: No need to maintain a separate YAML file
2. **Version Control**: Configuration lives with your code in `pyproject.toml`
3. **Auto-Discovery**: Dagster automatically finds and loads your code location
4. **Project Portability**: Each project is self-contained and can be developed independently

### When to Use `workspace.yaml` Instead

Use `workspace.yaml` when:
- **Multi-Location Orchestration**: You need to orchestrate multiple code locations from one webserver
- **Remote Locations**: Loading code from separate projects, containers, or gRPC servers
- **Production Deployment**: Centralized configuration for production environments
- **Custom Attributes**: Your `Definitions` object has a non-standard name

### Combining Both Approaches

You can use both patterns:
- **Local Development**: Use `[tool.dg.project]` in each project's `pyproject.toml` for individual development
- **Central Orchestration**: Use `workspace.yaml` in `00_master/` to orchestrate all locations together

This gives you the best of both worlds: simple local development and powerful multi-location orchestration.

---

## Deep Dive: `dagster.yaml` - Run Configuration

The `dagster.yaml` file in `00_master/` defines global configuration for how Dagster stores run metadata, events, and schedules. This is where you configure persistent storage and logging.

### Location
`00_master/dagster.yaml`

### Key Concepts

**Run Storage**: Where Dagster stores information about pipeline runs (status, timestamps, configuration).

**Event Log Storage**: Where Dagster logs all events during run execution (asset materializations, logs, errors).

**Schedule Storage**: Where Dagster stores schedule definitions and their execution history.

### Database-Backed Storage

This example uses PostgreSQL for all storage backends, reading the connection string from environment variables:

```yaml
run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_url:
      env: DAGSTER_DATABASE_URL

event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_url:
      env: DAGSTER_DATABASE_URL

schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_url:
      env: DAGSTER_DATABASE_URL
```

### Environment Variable Configuration

The `env: DAGSTER_DATABASE_URL` syntax tells Dagster to read the value from an environment variable. This keeps sensitive credentials out of version control.

**Example `.env` file:**
```bash
DAGSTER_DATABASE_URL=postgresql://user:password@localhost:5432/dagster
```

### Why This Matters

- **Persistence**: Without database storage, run history is lost when the daemon restarts
- **Observability**: Event logs enable debugging, monitoring, and audit trails
- **Collaboration**: Multiple team members can view the same run history
- **Production Ready**: File-based storage (default) doesn't scale for production

### Alternative Storage Backends

You can also use:
- **SQLite**: For development (`dagster_sqlite`)
- **Cloud Storage**: AWS S3, GCS, Azure Blob for event logs
- **Custom**: Implement your own storage classes

---

## Deep Dive: `workspace.yaml` - Code Locations

The `workspace.yaml` file defines where Dagster should look for code to execute. This is the heart of multi-location orchestration - it allows a single webserver to discover and execute code from multiple sources.

### Location
`00_master/workspace.yaml`

### Code Location Types

Dagster supports four primary code location patterns, each suited for different deployment scenarios:

1. **Single File** (`python_file`): Load definitions from a standalone Python file
2. **Module** (`python_module`): Load definitions from a Python module/package
3. **Remote Package** (`python_package`): Load definitions from a separate project with its own virtual environment
4. **Remote gRPC Server** (`grpc_server`): Load definitions from a running Dagster code server (often containerized)

---

### 1. Single File Code Location

**Use Case**: Quick prototyping, simple scripts, or when you want to isolate a single definition file.

**Configuration:**
```yaml
load_from:
  - python_file:
      location_name: example_local_file
      relative_path: src/definitions/single_file.py
      working_directory: /home/bmoney/projects/integrations/00_master
      executable_path: /home/bmoney/projects/integrations/00_master/.venv/bin/python
```

**Key Parameters:**
- `location_name`: Unique identifier for this code location (appears in UI)
- `relative_path`: Path to the Python file relative to `working_directory`
- `working_directory`: Project root where the file lives
- `executable_path`: Python interpreter to use (ensures correct dependencies)

**Example File Structure:**
```
00_master/
  └── src/definitions/
      └── single_file.py          # Contains: defs = Definitions(assets=[...])
```

**When to Use:**
- Testing new assets quickly
- Sharing a single file between projects
- Minimal dependencies or standalone scripts

---

### 2. Module-Level Code Location

**Use Case**: Standard Python package structure where definitions are organized across multiple files.

**Configuration:**
```yaml
load_from:
  - python_module:
      location_name: example_local_module
      module_name: src.definitions
      # working_directory and executable_path are optional when in same project
```

**Key Parameters:**
- `module_name`: Dot-separated Python module path (e.g., `src.definitions`)
- `working_directory`: Optional if loading from the same project as the webserver
- `executable_path`: Optional if using the same Python environment

**Example File Structure:**
```
00_master/
  └── src/
      └── definitions/
          ├── __init__.py         # Contains: defs = Definitions(...)
          └── assets.py           # Imported by __init__.py
```

**When to Use:**
- Standard project organization
- Code is in the same repository as the webserver
- Multiple files need to be organized together

**Note**: The module must have a top-level `defs` variable (or specify `attribute: my_defs` if using a different name).

---

### 3. Remote Package Code Location

**Use Case**: Code lives in a separate project/repository with its own dependencies and virtual environment. This is essential for microservices architectures or when different teams own different code locations.

**Configuration:**
```yaml
load_from:
  - python_package:
      location_name: example_remote_package
      package_name: src.definitions
      working_directory: /home/bmoney/projects/integrations/dagster_remote_test/
      executable_path: /home/bmoney/projects/integrations/dagster_remote_test/.venv/bin/python
```

**Key Parameters:**
- `package_name`: Dot-separated package path within the remote project
- `working_directory`: **Absolute path** to the remote project root
- `executable_path`: **Absolute path** to the Python interpreter in the remote project's virtual environment

**Example File Structure:**
```
dagster_remote_test/              # Separate project
  ├── .venv/                      # Has its own virtual environment
  │   └── bin/python
  └── src/
      └── definitions/
          └── __init__.py         # Contains: defs = Definitions(...)
```

**Why This Matters:**
- **Dependency Isolation**: Each code location can have different package versions
- **Team Autonomy**: Teams can deploy their code independently
- **Environment Separation**: Different Python versions or system dependencies per location

**Important**: The remote project must have its virtual environment set up and dependencies installed. The `executable_path` ensures Dagster uses the correct environment.

---

### 4. Remote gRPC Code Server

**Use Case**: Code runs in a separate process (often containerized) and communicates via gRPC. This is the most production-ready pattern for distributed orchestration.

**Configuration:**
```yaml
load_from:
  - grpc_server:
      location_name: remote_grpc_server
      host: localhost
      port: 4556
```

**Key Parameters:**
- `host`: Hostname or IP address of the gRPC server
- `port`: Port the gRPC server is listening on

**How It Works:**
1. A separate Dagster process runs as a code server: `dagster code-server start`
2. The code server loads definitions from its own codebase
3. The central webserver connects via gRPC to discover and execute code
4. Code execution happens in the remote server's environment

**Example Setup (Docker):**

**Dockerfile** (`dagster_docker_test/docker/Dockerfile`):
```dockerfile
# Builds a container with Dagster code server
CMD ["dagster", "code-server", "start", 
     "--host", "0.0.0.0", 
     "--port", "4000", 
     "--module-name", "src.definitions", 
     "--attribute", "defs"]
```

**Docker Compose** (`dagster_docker_test/docker/compose.yml`):
```yaml
services:
  dagster:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "4556:4000"  # Map host port 4556 to container port 4000
```

**Starting the Server:**
```bash
cd dagster_docker_test/docker
docker compose up -d
```

**When to Use:**
- **Production Deployments**: Isolated execution environments
- **Scalability**: Each code location can scale independently
- **Security**: Code runs in sandboxed containers
- **Resource Management**: Different memory/CPU limits per location
- **Multi-Cloud**: Code locations can run in different regions/clouds

**Benefits Over Remote Package:**
- Complete process isolation
- No shared filesystem requirements
- Can run on different machines/networks
- Better for Kubernetes deployments

---

## Code Location Details

### `00_master/` - Central Orchestration Hub

This directory contains:
- The central Dagster webserver and daemon
- Configuration files (`dagster.yaml`, `workspace.yaml`)
- Example local code locations (single file and module)

**Local Code Locations:**
- `example_local_file`: Loads from `src/definitions/single_file.py`
- `example_local_module`: Loads from `src.definitions` module

**Purpose**: Demonstrates how to organize code in the same project as the webserver.

---

### `dagster_remote_test/` - Remote Package Example

This directory simulates a separate project that's orchestrated remotely.

**Key Features:**
- Has its own `pyproject.toml` and dependencies
- Uses its own virtual environment (`.venv`)
- Contains an asset that validates the executable path to prove isolation

**Code Location**: `example_remote_package` in `workspace.yaml`

**Purpose**: Demonstrates how to orchestrate code from a separate project with different dependencies.

---

### `dagster_docker_test/` - Remote gRPC Server Example

This directory contains code that runs in a Docker container and is accessed via gRPC.

**Key Features:**
- Dockerized Dagster code server
- Serves definitions via gRPC on port 4556
- Complete process isolation

**Code Location**: `remote_grpc_server` in `workspace.yaml`

**Purpose**: Demonstrates production-ready distributed orchestration pattern.

**To Use:**
1. Build and start the container: `cd dagster_docker_test/docker && docker compose up -d`
2. The central webserver will discover it automatically via `workspace.yaml`

---

## Running the Orchestration

### Starting the Central Server

From `00_master/`:

```bash
dagster dev -h 0.0.0.0 -p 4550
```

This command:
1. Reads `dagster.yaml` for storage configuration
2. Reads `workspace.yaml` to discover all code locations
3. Starts the webserver (UI) on port 4550
4. Starts the daemon (execution engine)

### Viewing Code Locations

In the Dagster UI (`http://localhost:4550`):
- Navigate to **Deployment** → **Code Locations**
- You should see all four code locations:
  - `example_local_file`
  - `example_local_module`
  - `example_remote_package`
  - `remote_grpc_server`

### Executing Assets

1. Go to **Assets** in the UI
2. You'll see assets from all code locations
3. Materialize assets to verify they execute in their respective environments

### Verifying Isolation

The `dagster_remote_test` location includes an asset (`validate_executable_location`) that prints the Python executable path. When you materialize it, you should see the path to `dagster_remote_test/.venv/bin/python`, proving it's using the remote environment.

---

## Configuration Best Practices

### Environment Variables

- **Never commit `.env` files**: Use `.env.EXAMPLE` as a template
- **Use absolute paths**: For remote code locations, always use absolute paths
- **Validate paths exist**: Ensure `working_directory` and `executable_path` exist before starting

### Code Location Naming

- Use descriptive `location_name` values
- Match naming to team/project ownership
- Consider prefixing with environment (e.g., `prod_data_team`, `dev_ml_team`)

### Virtual Environments

- Each remote package location should have its own `.venv`
- Install dependencies: `cd <project> && uv sync` (or `pip install -r requirements.txt`)
- Verify `executable_path` points to the correct Python

### gRPC Servers

- Use Docker Compose for local development
- Use Kubernetes for production
- Monitor server health (Dagster UI shows connection status)
- Configure appropriate resource limits per container

---

## Troubleshooting

### Code Location Not Appearing

1. **Check `workspace.yaml` syntax**: YAML indentation matters
2. **Verify paths exist**: All `working_directory` and `executable_path` must exist and be full file paths (no `~` shorthand or relative paths)
3. **Check Python environment**: Remote locations need dependencies installed
4. **Review logs**: `dagster dev` output shows code location loading errors

### gRPC Server Connection Issues

1. **Verify container is running**: `docker ps` should show the container
2. **Check port mapping**: Ensure host port matches `workspace.yaml`
3. **Test connectivity**: `curl localhost:4556` or check container logs
4. **Firewall**: Ensure ports aren't blocked

### Database Connection Errors

1. **Check `.env` file**: Verify `DAGSTER_DATABASE_URL` is set
2. **Database exists**: Create the database if it doesn't exist
3. **Permissions**: Ensure database user has CREATE TABLE permissions
4. **Network**: Verify database is reachable from where Dagster runs

### Asset Execution Failures

1. **Check code location logs**: Each location has separate logs in the UI
2. **Verify dependencies**: Remote locations need all packages installed
3. **Check executable path**: Wrong Python version can cause import errors
4. **Review asset code**: Check for syntax errors or missing imports

---

## Next Steps

- **Add Schedules**: Configure schedules in your definitions to automate runs
- **Add Sensors**: Set up sensors to trigger on external events
- **Configure Resources**: Use resources for database connections, API clients, etc.
- **Set Up CI/CD**: Automate deployment of code locations
- **Monitor Production**: Set up alerting and monitoring for production deployments

---

## Summary

This repository demonstrates how a single Dagster instance can orchestrate code from multiple locations:

- **Local code** (single file and module) for rapid development
- **Remote packages** for separate projects with isolated dependencies
- **gRPC servers** for production-ready distributed execution

The key configuration files are:
- `dagster.yaml`: Defines how runs are stored and logged (database-backed)
- `workspace.yaml`: Defines where code lives and how to load it

By mastering these patterns, you can build scalable, maintainable data orchestration systems that support team autonomy and production requirements.
