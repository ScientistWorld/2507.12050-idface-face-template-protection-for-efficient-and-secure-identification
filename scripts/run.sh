#!/usr/bin/env bash
set -euo pipefail

scripts/evaluate.sh
python validate.py --compare
