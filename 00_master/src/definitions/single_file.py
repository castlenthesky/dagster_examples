from dagster import Definitions, asset


@asset
def example_single_file_asset():
  print("This asset is defined in a single file to demonstrate workspace.yaml configuration.")


defs = Definitions(
  assets=[example_single_file_asset],
  schedules=[],
  sensors=[],
  jobs=[],
  executor=None,
  asset_checks=[],
  resources={},
  loggers={},
  metadata={},
)
