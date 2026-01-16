# src/definitions

import sys

from dagster import Definitions, asset


@asset()
def validate_executable_location():
  # Print the name of the executable running the asset to verify the virtual environment is being used
  python_executable = sys.executable
  print(f"Executable running asset: {python_executable}")


defs = Definitions(
  assets=[validate_executable_location],
  schedules=[],
  sensors=[],
  jobs=[],
  executor=None,
  asset_checks=[],
  resources={},
  loggers={},
  metadata={},
)
