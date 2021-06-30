#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.." || return

pytest --cov=src --cov-report=html "$@"
echo "pytest passes..."
