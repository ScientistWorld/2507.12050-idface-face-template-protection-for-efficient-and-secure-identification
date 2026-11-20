#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  uv pip install --system numpy==2.2.6
else
  python -m pip install numpy==2.2.6
fi
