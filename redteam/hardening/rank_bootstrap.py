#!/usr/bin/env python3
"""Paired bootstrap of the full rank delta (variant minus reference) per test draw.

Reads the per-probe dumps written by audit.py (results/dump_*), resamples
genuine and impostor probes jointly for both methods, recomputes all six
scored metrics of both experiments, and applies the gym's rank rule with the
calibration-cohort scales of the hidden draw (from results/test_secret_all.json).
Writes results/rank_bootstrap.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
WORKSPACE = HERE.parents[1]
REFERENCE = "idface"
VARIANTS = ("hv_multilevel_gallery", "hv_alpha277", "hv_weaker_127")
CALIBRATION = ("idface", "hv_multilevel_gallery", "hv_alpha277", "hv_weaker_127", "sign_random_subset", "random_codes")
DRAWS = {"secret": "dump_secret", "101": "dump_seed_101", "202": "dump_seed_202", "303": "dump_seed_303"}
REPS = 300


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    scores = np.concatenate([pos, neg])
    _, inverse, counts = np.unique(scores, return_inverse=True, return_counts=True)
    ranks = (np.cumsum(counts) - (counts - 1) / 2.0)[inverse]
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def metrics(d: dict, gi: np.ndarray, ii: np.ndarray) -> dict[str, float]:
    true, correct, rank, imp = d["true"][gi], d["correct"][gi], d["rank"][gi], d["impostor_max"][ii]
    out = {"top1_identification": float(correct.mean()), "mean_reciprocal_rank": float(np.mean(1.0 / rank)),
           "open_set_score_auc": auc(true, imp)}
    desc = np.sort(imp)[::-1]
    for f in (0.1, 0.01, 0.001):
        k = int(math.floor(f * len(desc) + 1e-9))
        out[f"tpir_at_fpir_{f:g}"] = float(np.mean(correct & (true > desc[k])))
    return out


def main() -> None:
    ref = json.loads((WORKSPACE / "scoring" / "reference.json").read_text())["experiments"]
    secret = json.loads((RESULTS / "test_secret_all.json").read_text())["experiments"]
    scales = {}
    for exp, edef in ref.items():
        for m in edef["metrics"]:
            vals = [secret[exp]["results"][n][m] for n in CALIBRATION]
            sd = float(np.std(vals))
            scales[(exp, m)] = sd if sd > 0 else 1.0
    out: dict = {}
    for label, dname in DRAWS.items():
        ddir = RESULTS / dname
        data = {(exp, n): dict(np.load(ddir / f"{exp}__{n}.npz")) for exp in ref for n in (REFERENCE,) + VARIANTS}
        n_g = len(data[(next(iter(ref)), REFERENCE)]["true"])
        n_i = len(data[(next(iter(ref)), REFERENCE)]["impostor_max"])
        rng = np.random.default_rng(1)
        samples = {v: [] for v in VARIANTS}
        point = {v: 0.0 for v in VARIANTS}
        for rep in range(REPS + 1):
            gi = np.arange(n_g) if rep == 0 else rng.integers(0, n_g, n_g)
            ii = np.arange(n_i) if rep == 0 else rng.integers(0, n_i, n_i)
            for v in VARIANTS:
                delta = 0.0
                for exp, edef in ref.items():
                    mr = metrics(data[(exp, REFERENCE)], gi, ii)
                    mv = metrics(data[(exp, v)], gi, ii)
                    for m, mdef in edef["metrics"].items():
                        sign = 1.0 if mdef["higher_is_better"] else -1.0
                        delta += edef["weight"] * abs(mdef["coefficient"]) * sign * (mv[m] - mr[m]) / scales[(exp, m)]
                if rep == 0:
                    point[v] = delta
                else:
                    samples[v].append(delta)
        out[label] = {v: {"rank_delta": point[v], "bootstrap_se": float(np.std(samples[v])),
                          "fraction_positive": float(np.mean(np.array(samples[v]) > 0))} for v in VARIANTS}
        print(label, {v: f"{x['rank_delta']:+.4f}±{x['bootstrap_se']:.4f} (P>0 {x['fraction_positive']:.2f})" for v, x in out[label].items()}, flush=True)
    (RESULTS / "rank_bootstrap.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
