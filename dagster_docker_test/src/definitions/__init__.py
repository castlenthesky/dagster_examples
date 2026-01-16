# src/dagster_definitions

import os
from dagster import Definitions, FilesystemIOManager, asset


@asset(name="example_gRPC")
def example_gRPC_asset():
  print("This asset is running in a remote docker container and orchestrated via gRPC.")
  return "Asset executed successfully"


defs = Definitions(
  assets=[example_gRPC_asset],
  resources={
    # Configure I/O manager to write to a location accessible in the container
    # This path will be used for storing asset outputs
    "io_manager": FilesystemIOManager(
      base_dir=os.getenv("DAGSTER_STORAGE_DIR", "/opt/dagster/dagster_home/storage")
    ),
  },
  schedules=[],
  sensors=[],
  jobs=[],
  executor=None,
  asset_checks=[],
  loggers={},
  metadata={},
)
