#!/usr/bin/env bash

set -e

mkdir -p /app/_logs

echo "********  PYTHONPATH 1 : $PYTHONPATH"
export PYTHONPATH=$(pwd):$PYTHONPATH
echo "********  PYTHONPATH 2 : $PYTHONPATH"

source "$VIRTUAL_ENV"/bin/activate
alembic upgrade head
python platform_registry/initial_data.py

uvicorn platform_registry.main:app --host 0.0.0.0 --port 8000
