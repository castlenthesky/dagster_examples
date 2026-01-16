# src/definitions/assets.py
"""Example asset for testing gRPC orchestration."""

from dagster import asset


@asset(name="example_gRPC")
def example_gRPC_asset():
  print("This asset is running in a remote docker container and orchestrated via gRPC.")
