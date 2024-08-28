#!/usr/bin/env bash

set -e

source "$VIRTUAL_ENV"/bin/activate

coverage run --source=platform_registry -m pytest -x --disable-warnings
coverage report --show-missing
coverage xml -o coverage/coverage.xml
coverage html -d coverage/htmlcov