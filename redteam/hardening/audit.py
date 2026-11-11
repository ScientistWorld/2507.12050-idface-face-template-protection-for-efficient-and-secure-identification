#!/usr/bin/env python3
"""Hardening audit: run variants and shortcuts through the hidden test evaluator.

Usage (inside the gym container, from the workspace root):
    python redteam/hardening/audit.py

Steps
1. install every case as a method directory under checkpoints/ (a scanned root);
2. plant a forged scoring/scores_test.json and an empty scoring/scores_train.json
   (direct-score-write and empty-manifest shortcuts), then run the hidden test
   evaluator exactly as scripts/evaluate_test.sh does (no arguments) and check
   that it overwrote the forged file and scored every method directory on disk;
3. run the train evaluator on every method (train/test gap check);
4. rerun the reference and honest variants on three further test draws
   (--data-seed) to measure seed noise and paired differences;
5. remove the cases, restore the scoring files, and write summary.json/summary.md.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
RESULTS = HERE / "results"
CASES_ROOT = WORKSPACE / "checkpoints"
REFERENCE = "idface"
AUDIT_SEEDS = (101, 202, 303)
HONEST = ("idface", "hv_multilevel_gallery", "hv_alpha277", "hv_weaker_127", "sign_random_subset")
SHORTCUT_ENC = "redteam/hardening/encoders/shortcut_encoders.py"
VARIANT_ENC = "redteam/hardening/encoders/variant_multilevel_gallery.py"
EXP_FULL = "synthetic_identification"
EXP_COMP = "synthetic_identification_compressed"


def spec(command: list[str], full: list[str], compressed: list[str]) -> dict:
    return {"command": command, "experiments": {EXP_FULL: {"args": full}, EXP_COMP: {"args": compressed}}}


def shortcut(kind: str) -> dict:
    return {"encoder.json": spec(["python", SHORTCUT_ENC, "--kind", kind],
                                 ["--alpha", "341", "--beta", "341"], ["--alpha", "341", "--beta", "63"])}


CASES: dict[str, dict] = {
    # Honest variants (the reference itself is method/outputs/idface).
    "hv_multilevel_gallery": {"encoder.json": spec(["python", VARIANT_ENC],
                                                   ["--alpha", "341", "--beta", "341", "--levels", "3"],
                                                   ["--alpha", "341", "--beta", "63", "--levels", "1"])},
    "hv_alpha277": {"encoder.json": spec(["python", "method/encode_idface.py"],
                                         ["--alpha", "277", "--beta", "277"], ["--alpha", "277", "--beta", "63"])},
    "hv_weaker_127": {"encoder.json": spec(["python", "method/encode_idface.py"],
                                           ["--alpha", "127", "--beta", "127"], ["--alpha", "63", "--beta", "63"])},
    "hv_full_sign_512": {"encoder.json": spec(["python", "method/encode_idface.py"],
                                              ["--alpha", "512", "--beta", "512"], ["--alpha", "512", "--beta", "63"])},
    # Shortcuts from REDTEAM.md re-expressed through the new interface, plus new attacks.
    "sc_visible_lookup": shortcut("visible_lookup"),
    "sc_constant_codes": shortcut("constant"),
    "sc_unprotected_float": shortcut("float_quantized"),
    "sc_scaled_codes": shortcut("scaled"),
    "sc_nan_codes": shortcut("nan_float"),
    "sc_empty_codes": shortcut("empty"),
    "sc_zero_codes": shortcut("zero"),
    "sc_stateful_query_lookup": shortcut("stateful_query"),
    "sc_stateful_gallery_fold": shortcut("stateful_gallery"),
    "sc_batch_center": shortcut("batch_center"),
    "sc_forged_metadata": {
        "encoder.json": spec(["python", "method/encode_idface.py"],
                             ["--alpha", "341", "--beta", "341"], ["--alpha", "341", "--beta", "63"]),
        "metadata.json": {"operation_counts": {"ciphertext_additions_per_query": 0, "decryptions_per_query": 0,
                                               "pack": 1e12, "protected_template_storage": 1e12}},
    },
    "sc_cached_predictions": {
        "metadata.json": {"operation_counts": {"ciphertext_additions_per_query": 0, "pack": 1e12}},
        "predictions.npz": None,
    },
}


def run(cmd: list[str], log: Path) -> int:
    print("+", " ".join(cmd), flush=True)
    with log.open("a") as fh:
        fh.write("+ " + " ".join(cmd) + "\n")
        fh.flush()
        proc = subprocess.run(cmd, cwd=WORKSPACE, stdout=fh, stderr=subprocess.STDOUT)
    return proc.returncode


def install_cases() -> None:
    for name, files in CASES.items():
        d = CASES_ROOT / name
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        for fname, content in files.items():
            if fname.endswith(".json"):
                (d / fname).write_text(json.dumps(content, indent=2) + "\n")
            elif fname == "predictions.npz":
                n = 64
                rng = np.random.default_rng(0)
                np.savez_compressed(d / fname, genuine_scores=rng.normal(size=(n, n)), impostor_scores=rng.normal(size=(n, n)),
                                    genuine_labels=np.arange(n), gallery_labels=np.arange(n))


def remove_cases() -> None:
    for name in CASES:
        shutil.rmtree(CASES_ROOT / name, ignore_errors=True)
    shutil.rmtree(HERE / "state", ignore_errors=True)


# ── Rank arithmetic (as specified for the gym) ───────────────────────────────


def load_reference() -> dict:
    return json.loads((WORKSPACE / "scoring" / "reference.json").read_text())


def rank_deltas(scores: dict, cohort_scores: dict, reference: str = REFERENCE) -> dict[str, float]:
    """delta = sum_e w_e sum_m |c_m| * dir_m * (x_m - ref_m) / sd_m, sd over the cohort rows."""
    ref = load_reference()["experiments"]
    deltas: dict[str, float] = {}
    for exp, exp_def in ref.items():
        if exp not in scores:
            continue
        rows = scores[exp]
        cohort = cohort_scores[exp]
        for metric, mdef in exp_def["metrics"].items():
            coef = abs(float(mdef["coefficient"]))
            if coef == 0:
                continue
            direction = 1.0 if mdef["higher_is_better"] else -1.0
            values = [r[metric] for r in cohort.values() if metric in r and np.isfinite(r[metric])]
            sd = float(np.std(values)) if len(values) > 1 else 0.0
            sd = sd if sd > 0 else 1.0
            for name, row in rows.items():
                if metric not in row or reference not in rows:
                    continue
                gain = direction * (row[metric] - rows[reference][metric]) / sd
                deltas[name] = deltas.get(name, 0.0) + float(exp_def["weight"]) * coef * gain
    return deltas


def results_of(path: Path) -> dict:
    data = json.loads(path.read_text())
    return {exp: v["results"] for exp, v in data["experiments"].items()}


def paired_bootstrap(dump_dir: Path, exp: str, a: str, b: str, fpir: float, reps: int = 400) -> tuple[float, float]:
    """TPIR(a) - TPIR(b) at fpir and its bootstrap SE, resampling probes jointly."""
    da = np.load(dump_dir / f"{exp}__{a}.npz")
    db = np.load(dump_dir / f"{exp}__{b}.npz")

    def tpir(d, gi, ii):
        imp = np.sort(d["impostor_max"][ii])[::-1]
        k = int(np.floor(fpir * len(imp) + 1e-9))
        thr = imp[k] if k < len(imp) else -np.inf
        return float(np.mean(d["correct"][gi] & (d["true"][gi] > thr)))

    n_g, n_i = len(da["true"]), len(da["impostor_max"])
    full_g, full_i = np.arange(n_g), np.arange(n_i)
    point = tpir(da, full_g, full_i) - tpir(db, full_g, full_i)
    rng = np.random.default_rng(0)
    diffs = []
    for _ in range(reps):
        gi = rng.integers(0, n_g, n_g)
        ii = rng.integers(0, n_i, n_i)
        diffs.append(tpir(da, gi, ii) - tpir(db, gi, ii))
    return point, float(np.std(diffs))


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    log = RESULTS / "audit.log"
    log.write_text("")
    scoring = WORKSPACE / "scoring"
    backup = {f: (scoring / f).read_text() for f in ("scores_train.json", "scores_test.json") if (scoring / f).exists()}
    remove_cases()
    install_cases()
    try:
        # Direct-score-write and empty-manifest shortcuts, then the no-argument hidden test.
        (scoring / "scores_test.json").write_text(json.dumps({"experiments": {EXP_FULL: {"results": {"sc_direct_write": {"tpir_at_fpir_0.01": 1e9}}}}}))
        (scoring / "scores_train.json").write_text(json.dumps({"experiments": {}}))
        rc = run(["bash", "scripts/evaluate_test.sh"], log)
        planted = json.loads((scoring / "scores_test.json").read_text())
        shutil.copy(scoring / "scores_test.json", RESULTS / "test_secret_all.json")
        checks = {
            "evaluate_test_exit_code": rc,
            "forged_scores_overwritten": "sc_direct_write" not in planted["experiments"][EXP_FULL]["results"],
            "methods_scored_with_empty_train_manifest": sorted(planted["experiments"][EXP_FULL]["results"]),
        }
        # Per-probe dumps of the honest rows on the hidden draw, for paired statistics.
        run([sys.executable, "eval/test/evaluate.py", "--methods", ",".join(HONEST),
             "--dump-dir", str(RESULTS / "dump_secret"), "--out", str(RESULTS / "test_secret_honest.json")], log)
        # Train evaluation of everything (train/test gap).
        run([sys.executable, "eval/train/evaluate.py", "--out", str(RESULTS / "train_all.json")], log)
        # Seed noise and paired differences on further test draws.
        for seed in AUDIT_SEEDS:
            run([sys.executable, "eval/test/evaluate.py", "--data-seed", str(seed), "--methods", ",".join(HONEST),
                 "--dump-dir", str(RESULTS / f"dump_seed_{seed}"), "--out", str(RESULTS / f"test_seed_{seed}.json")], log)
    finally:
        remove_cases()
        for f, text in backup.items():
            (scoring / f).write_text(text)

    summarize(checks)


def summarize(checks: dict) -> None:
    secret = results_of(RESULTS / "test_secret_all.json")
    train = results_of(RESULTS / "train_all.json")
    diag = {exp: v["_diagnostics"] for exp, v in json.loads((RESULTS / "test_secret_all.json").read_text())["experiments"].items()}
    honest_names = set(HONEST) | {"random_codes"}
    calibration = {exp: {k: v for k, v in rows.items() if k in honest_names} for exp, rows in secret.items()}
    summary: dict = {"checks": checks, "cohorts": {
        "complete": sorted(secret[EXP_FULL]), "calibration": sorted(calibration[EXP_FULL])}}
    summary["rank_delta_complete"] = rank_deltas(secret, secret)
    summary["rank_delta_calibration"] = rank_deltas(secret, calibration)
    summary["test_secret"] = secret
    summary["train"] = train
    summary["diagnostics_secret"] = diag

    seeds = {"secret": RESULTS / "test_secret_honest.json"}
    seeds.update({str(s): RESULTS / f"test_seed_{s}.json" for s in AUDIT_SEEDS})
    per_seed = {}
    for label, path in seeds.items():
        rows = results_of(path)
        per_seed[label] = {"results": rows, "rank_delta_calibration_scale": rank_deltas(rows, calibration)}
    summary["seeds"] = per_seed
    # Unpaired seed spread of the reference's own scores and its rank relative to the secret-draw reference.
    ref_tpir = {lab: per_seed[lab]["results"][EXP_FULL][REFERENCE]["tpir_at_fpir_0.01"] for lab in per_seed}
    summary["reference_tpir_0.01_by_seed"] = ref_tpir
    ref_rank = {}
    for lab in per_seed:
        merged = {exp: {"ref_secret": per_seed["secret"]["results"][exp][REFERENCE],
                        "ref_seed": per_seed[lab]["results"][exp][REFERENCE]} for exp in per_seed[lab]["results"]}
        ref_rank[lab] = rank_deltas(merged, calibration, reference="ref_secret")["ref_seed"]
    summary["reference_rank_by_seed_vs_secret_reference"] = ref_rank

    paired = {}
    dump_dirs = {"secret": RESULTS / "dump_secret"}
    dump_dirs.update({str(s): RESULTS / f"dump_seed_{s}" for s in AUDIT_SEEDS})
    for lab, ddir in dump_dirs.items():
        for exp in (EXP_FULL, EXP_COMP):
            for name in HONEST:
                if name == REFERENCE or not (ddir / f"{exp}__{name}.npz").exists():
                    continue
                for fpir in (0.01, 0.001):
                    d, se = paired_bootstrap(ddir, exp, name, REFERENCE, fpir)
                    paired.setdefault(f"{exp}:{name}:tpir@{fpir:g}", {})[lab] = {"diff": d, "se": se}
    summary["paired_vs_reference"] = paired
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    lines = ["# Hardening audit summary", "", f"checks: {json.dumps(checks)}", ""]
    lines.append("| method | status full | status compressed | TPIR@1e-2 full | TPIR@1e-2 compr. | rank Δ complete | rank Δ calibration |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    for name in sorted(secret[EXP_FULL]):
        sf = diag[EXP_FULL][name]["status"]
        sc = diag[EXP_COMP][name]["status"]
        lines.append(f"| {name} | {sf} | {sc} | {secret[EXP_FULL][name]['tpir_at_fpir_0.01']:.4f} | "
                     f"{secret[EXP_COMP][name]['tpir_at_fpir_0.01']:.4f} | {summary['rank_delta_complete'].get(name, float('nan')):+.4f} | "
                     f"{summary['rank_delta_calibration'].get(name, float('nan')):+.4f} |")
    lines += ["", "## Failure reasons"]
    for exp in (EXP_FULL, EXP_COMP):
        for name, d in diag[exp].items():
            if d["status"] != "ok":
                lines.append(f"- {exp} / {name}: {d['reason']}")
    lines += ["", "## Seeds (rank Δ vs same-draw reference, calibration scales)"]
    for lab, v in per_seed.items():
        lines.append(f"- {lab}: " + ", ".join(f"{k}={x:+.4f}" for k, x in sorted(v["rank_delta_calibration_scale"].items())))
    lines.append(f"- reference TPIR@1e-2 by draw: {ref_tpir}")
    lines.append(f"- reference rank vs secret-draw reference: {ref_rank}")
    lines += ["", "## Paired TPIR differences vs reference (bootstrap SE)"]
    for key, v in paired.items():
        lines.append(f"- {key}: " + ", ".join(f"{lab} {x['diff']:+.4f}±{x['se']:.4f}" for lab, x in v.items()))
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "summarize":
        summarize(json.loads((RESULTS / "summary.json").read_text())["checks"])
    else:
        main()
