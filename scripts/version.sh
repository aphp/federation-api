#!/usr/bin/env bash

set -e

source "$VIRTUAL_ENV"/bin/activate

VERSION=$(python -c "from platform_registry.core.config import settings; print(settings.VERSION)")
echo "$VERSION"
