set shell := ["bash", "-cu"]

default:
  @just --list

build:
  docker compose build

start:
  docker compose up --build app

ingest:
  docker compose run --rm ingest

stop:
  docker compose down

visualize:
  mkdir -p artifacts
  docker compose run --rm --env ARTIFACTS_DIR=/artifacts --volume "$PWD/artifacts:/artifacts" --volume "$PWD/services/app/scripts:/workspace/scripts" app python scripts/visualize_agents.py
