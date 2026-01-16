# muninn_dagster/src/example/assets.py
import requests
from pathlib import Path
from dagster import asset


@asset
def example_request_taxi_data():
  month_to_fetch = "2023-03"
  output_path = ".data/assets/examples/taxi.parquet"
  Path(output_path).parent.mkdir(parents=True, exist_ok=True)
  raw_trips = requests.get(
    f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
  )
  with open(output_path, "wb") as output_file:
    output_file.write(raw_trips.content)


@asset(deps=["example_request_taxi_data"])
def example_request_taxi_zone_data():
  output_path = ".data/assets/examples/taxi_zones.csv"
  Path(output_path).parent.mkdir(parents=True, exist_ok=True)
  raw_zones = requests.get(
    "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
  )
  with open(output_path, "wb") as output_file:
    output_file.write(raw_zones.content)


@asset(deps=["example_request_taxi_data", "example_request_taxi_zone_data"])
def example_transform_taxi_data():
  # do your transformation here
  pass
