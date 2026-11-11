#!/usr/bin/env python3
"""Compute the user-specified rank with explicit, reproducible attempt cohorts."""
import json
from pathlib import Path
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "redteam"
EXP = "synthetic_identification"
reference_file = json.loads((AUDIT / "original_scores_test.json").read_text())
original = reference_file["experiments"][EXP]["results"]
anchor = original["idface_341_341"]
spec = json.loads((ROOT / "scoring/reference.json").read_text())["experiments"][EXP]
metrics = {k: v for k, v in spec["metrics"].items() if abs(v["coefficient"]) > 0}
names = json.loads((AUDIT / "cases.json").read_text())
rows = {}
statuses = {}
for name in names:
    status = json.loads((AUDIT / name / "status.json").read_text())
    statuses[name] = status
    scores = json.loads((AUDIT / name / "scores_test.json").read_text())
    result = scores["experiments"][EXP]["results"]
    rows[name] = result.get(status["candidate_name"], {}) if status["test"]["exit_code"] == 0 else None

finite = {k: v for k, v in rows.items() if v is not None and all(math.isfinite(x) for x in v.values())}
honest = {k: v for k, v in finite.items() if not k.startswith("shortcut_") or k == "shortcut_bruteforce_cosine"}
cohorts = {"all_finite_attempts": {**original, **finite}, "honest_attempts": {**original, **honest}}
scales = {}
for cohort, attempts in cohorts.items():
    scales[cohort] = {}
    for metric in metrics:
        values = [r[metric] for r in attempts.values() if metric in r and math.isfinite(r[metric])]
        std = float(statistics.pstdev(values))
        scales[cohort][metric] = std if std > 0 else 1.0


def rank(row, scale):
    if row is None or any(not math.isfinite(x) for x in row.values()):
        return None
    return sum(spec["weight"] * abs(m["coefficient"]) * (1 if m["higher_is_better"] else -1)
               * (row[k] - anchor[k]) / scale[k]
               for k, m in metrics.items() if k in row and k in anchor)


summary = {"reference": anchor, "coefficients": metrics, "experiment_weight": spec["weight"],
           "cohorts": {k: list(v) for k, v in cohorts.items()}, "standard_deviations": scales,
           "rows": {}, "original_baselines": {}}
for name, row in rows.items():
    summary["rows"][name] = {
        "raw_test_metrics": row,
        "delta_rank": {cohort: rank(row, scale) for cohort, scale in scales.items()},
        "test_exit": statuses[name]["test"]["exit_code"],
        "train_exit": statuses[name]["train"]["exit_code"],
        "shapes": statuses[name]["artifact_shapes"],
        "test_seconds": statuses[name]["test"]["seconds"],
        "method_seconds": statuses[name].get("method_run", {}).get("seconds"),
    }
for name, row in original.items():
    summary["original_baselines"][name] = {"raw_test_metrics": row,
        "delta_rank": {cohort: rank(row, scale) for cohort, scale in scales.items()}}

for cohort, scale in scales.items():
    seed_names = [f"reference_seed_{seed}" for seed in (20260712, 20260713, 20260714)]
    values = [rank(rows[name], scale) for name in seed_names]
    summary.setdefault("reference_seed_rank_spread", {})[cohort] = {
        "values": values, "range": float(max(values) - min(values)), "std": float(statistics.pstdev(values))}
summary["reference_seed_metric_spread"] = {
    k: {"values": [rows[f"reference_seed_{s}"][k] for s in (20260712, 20260713, 20260714)],
        "range": float(max(rows[f"reference_seed_{s}"][k] for s in (20260712, 20260713, 20260714)) - min(rows[f"reference_seed_{s}"][k] for s in (20260712, 20260713, 20260714)))}
    for k in metrics}
summary["deterministic_reference_repeats"] = {
    name: rows[name] == anchor for name in names if name.startswith("reference_repeat_")}
(AUDIT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print("case | TPIR .01 | delta rank (all attempts) | delta rank (honest scale) | test exit")
for name, result in summary["rows"].items():
    print(name, "|", (result["raw_test_metrics"] or {}).get("tpir_at_fpir_0.01"), "|",
          result["delta_rank"]["all_finite_attempts"], "|", result["delta_rank"]["honest_attempts"], "|", result["test_exit"])
print("seed spread", summary["reference_seed_rank_spread"], flush=True)
