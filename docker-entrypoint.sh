#!/usr/bin/env bash

set -e

mkdir -p /app/_logs

export PYTHONPATH=$(pwd):$PYTHONPATH

source "$VIRTUAL_ENV"/bin/activate
alembic upgrade head
python platform_registry/initial_data.py

uvicorn platform_registry.main:app --host 0.0.0.0 --port 8000
