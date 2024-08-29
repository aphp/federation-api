#!/usr/bin/env bash

set -e

source "$VIRTUAL_ENV"/bin/activate

coverage run --source=platform_registry -m pytest -x --disable-warnings
coverage xml -o coverage/coverage.xml