#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


MILESTONES = {"not_possible", "none", "method_runs", "core_claim", "core_claim_plus", "secondary_claims", "majority", "near_complete", "full"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def validate_reference(ref: dict) -> None:
    experiments = ref.get("experiments")
    if not isinstance(experiments, dict) or not experiments:
        raise SystemExit("reference.json must contain non-empty experiments")
    total_weight = sum(float(exp.get("weight", 0.0)) for exp in experiments.values())
    if abs(total_weight - 1.0) > 1e-6:
        raise SystemExit(f"experiment weights must sum to 1, got {total_weight}")
    for exp_name, exp in experiments.items():
        if exp.get("primary_metric") not in exp.get("metrics", {}):
            raise SystemExit(f"{exp_name}: primary_metric missing from metrics")
        for method, vals in exp.get("results", {}).items():
            if vals.get("type") not in {"baseline", "proposed"}:
                raise SystemExit(f"{exp_name}/{method}: type must be baseline or proposed")


def compare(ref: dict, scores: dict) -> None:
    for exp_name, exp in scores.get("experiments", {}).items():
        print(f"[{exp_name}]")
        ref_exp = ref.get("experiments", {}).get(exp_name, {})
        metric_defs = ref_exp.get("metrics", {})
        for method, vals in exp.get("results", {}).items():
            print(f"  {method}")
            ref_vals = ref_exp.get("results", {}).get(method, {})
            for key, value in vals.items():
                if isinstance(value, (int, float)):
                    suffix = ""
                    if key in ref_vals:
                        suffix = f" (paper {ref_vals[key]})"
                    elif key in metric_defs:
                        suffix = " (new run)"
                    print(f"    {key}: {value}{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    ref = load_json(Path("scoring/reference.json"))
    validate_reference(ref)
    if args.compare:
        scores_path = Path("scoring/scores.json")
        if not scores_path.exists():
            raise SystemExit("scoring/scores.json does not exist")
        compare(ref, load_json(scores_path))
    print("validation ok")


if __name__ == "__main__":
    main()
