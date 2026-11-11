#!/usr/bin/env bash
# Reproduce the reference end to end. The hardening audit is run separately:
#   python redteam/hardening/audit.py && python redteam/hardening/rank_bootstrap.py
set -euo pipefail

bash scripts/reproduce.sh
