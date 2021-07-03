#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.." || return

pytest --cov=file_renamer/src --cov-report=html "$@"
echo "pytest passes..."
