#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.." || return

pytest "$@"
echo "pytest passes..."
