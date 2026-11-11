#!/usr/bin/env bash
# Hardening job: reproduce the reference end to end, then run the hardening
# audit (variants, shortcuts, seed noise) through the hidden test evaluator.
set -uo pipefail

bash scripts/reproduce.sh; echo "reproduce rc=$?"
python redteam/hardening/audit.py; echo "audit rc=$?"
python validate.py --post-design; echo "validate rc=$?"
