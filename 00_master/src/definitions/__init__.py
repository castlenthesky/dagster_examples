# src/dagster_definitions

from dagster import Definitions, load_assets_from_modules

from . import assets

all_assets = load_assets_from_modules([assets])

defs = Definitions(
  assets=all_assets,
  schedules=[],
  sensors=[],
  jobs=[],
  executor=None,
  asset_checks=[],
  resources={},
  loggers={},
  metadata={},
)
