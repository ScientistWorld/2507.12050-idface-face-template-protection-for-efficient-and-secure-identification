#!/usr/bin/env python3
"""Reproducible audit trials; method builders use only agent-visible inputs.

The harness calls the unmodified test shell script with no arguments in a new
process. It never imports the hidden evaluator or changes Python's environment.
All methods and shortcuts have their own run.sh and keep their own test JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "redteam"
STATE = AUDIT / "_state"
CACHE = AUDIT / "_cache"
EXP = "synthetic_identification"
REF = "idface_341_341"
REF_DIR = ROOT / "method/outputs/idface_synthetic"
COUNTS = {
    "ciphertext_additions_per_query": 680,
    "ciphertext_multiplications_per_query": 0,
    "ciphertext_rotations_per_query": 0,
    "decryptions_per_query": 2,
    "pack": 5,
    "protected_template_storage": 1,
}


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def command(args, log):
    start = time.monotonic()
    log.write("$ " + " ".join(str(x) for x in args) + "\n")
    log.flush()
    result = subprocess.run([str(x) for x in args], cwd=ROOT, stdout=log, stderr=log)
    elapsed = time.monotonic() - start
    log.write(f"exit={result.returncode} seconds={elapsed:.6f}\n")
    log.flush()
    return {"exit_code": result.returncode, "seconds": elapsed, "argv": list(map(str, args))}


def required(args, log):
    result = command(args, log)
    if result["exit_code"]:
        raise RuntimeError(f"command failed: {args}")
    return result


def initialize(log):
    """Use existing trained outputs, regenerating only if a job lacks them."""
    STATE.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    if not (STATE / "initialized.json").exists():
        originals = {}
        for rel in ("scoring/scores_train.json", "scoring/scores_test.json"):
            path = ROOT / rel
            originals[rel] = path.exists()
            if path.exists():
                shutil.copy2(path, STATE / path.name)
                shutil.copy2(path, AUDIT / ("original_" + path.name))
        data = ROOT / "data/synthetic_embeddings.npz"
        if not data.exists():
            required([sys.executable, "data/generate_synthetic.py"], log)
        for script, out, extra in (
            ("baseline/run_plain.py", "baseline/outputs/plain_synthetic", []),
            ("baseline/run_random.py", "baseline/outputs/random_synthetic", []),
            ("method/run_idface.py", "method/outputs/idface_synthetic", ["--alpha", "341", "--beta", "341"]),
            ("method/run_idface.py", "method/outputs/idface_synthetic_beta63", ["--alpha", "341", "--beta", "63"]),
        ):
            if not (ROOT / out / "predictions.npz").exists():
                required([sys.executable, script, "--out", out, *extra], log)
        # The shipped training manifest also names the encrypted smoke row.
        if not (ROOT / "method/outputs/idface_paillier_small/predictions.npz").exists():
            required([sys.executable, "method/run_encrypted_idface.py"], log)
        for kind, path in (("reference", REF_DIR), ("plain", ROOT / "baseline/outputs/plain_synthetic")):
            dest = CACHE / kind
            dest.mkdir(exist_ok=True)
            for f in path.iterdir():
                if f.is_file():
                    shutil.copy2(f, dest / f.name)
        dump(STATE / "initialized.json", originals)


def restore_scores():
    originals = json.loads((STATE / "initialized.json").read_text())
    for rel, existed in originals.items():
        path = ROOT / rel
        if existed:
            shutil.copy2(STATE / path.name, path)
        elif path.exists():
            path.unlink()


def copy_reference(out):
    for f in (CACHE / "reference").iterdir():
        shutil.copy2(f, out / f.name)


def save_predictions(out, pred):
    import numpy as np
    np.savez_compressed(out / "predictions.npz", **pred)


def metadata(out, counts=None):
    dump(out / "metadata.json", {"operation_counts": dict(COUNTS if counts is None else counts)})


def seed_data(seed, log):
    if seed == 20260712:
        return ROOT / "data/synthetic_embeddings.npz"
    path = CACHE / f"seed_{seed}.npz"
    if not path.exists():
        required([sys.executable, "data/generate_synthetic.py", "--seed", str(seed), "--out", path], log)
    return path


def build(name, out, folder, log):
    """Construct a real artifact using no paper, reference JSON, or test code."""
    import numpy as np
    if name.startswith("reference_seed_") or name.startswith("variant_"):
        if name.startswith("reference_seed_"):
            seed, alpha, beta = int(name.rsplit("_", 1)[1]), 341, 341
        else:
            _, variant, seed = name.split("_")
            seed = int(seed)
            alpha, beta = {"255": (255, 255), "512": (512, 512), "beta1": (341, 1),
                           "beta63": (341, 63), "beta127": (341, 127)}[variant]
        result = required([sys.executable, "method/run_idface.py", "--data", seed_data(seed, log),
                           "--out", out, "--alpha", str(alpha), "--beta", str(beta)], log)
        return {"kind": "quality_variant", "seed": seed, "alpha": alpha, "beta": beta, "method_run": result}
    if name.startswith("reference_repeat_"):
        result = required([sys.executable, "method/run_idface.py", "--out", out], log)
        return {"kind": "deterministic_reference_repeat", "method_run": result}
    if name == "bruteforce_cosine":
        result = required([sys.executable, "baseline/run_plain.py", "--out", out], log)
        metadata(out, {**dict.fromkeys(list(COUNTS)[:4], 0), "pack": 1, "protected_template_storage": 0})
        return {"kind": "exhaustive_unprotected_baseline", "method_run": result,
                "dot_products": 4000 * 2000, "dimension": 512}

    copy_reference(out)
    pred = dict(np.load(out / "predictions.npz"))
    info = {"kind": "shortcut", "shortcut": name}
    if name in ("shortcut_cached_predictions", "shortcut_direct_scores", "shortcut_empty_manifest",
                "shortcut_null_metadata", "shortcut_nan_metadata", "shortcut_empty_predictions"):
        return info
    if name == "shortcut_visible_labels":
        data = np.load(ROOT / "data/synthetic_embeddings.npz")
        pred = {"gallery_labels": data["gallery_labels"], "genuine_labels": data["genuine_labels"],
                "genuine_scores": (data["genuine_labels"][:, None] == data["gallery_labels"][None, :]).astype(np.float32),
                "impostor_scores": np.zeros((len(data["impostor_queries"]), len(data["gallery"])), np.float32)}
    elif name == "shortcut_constant_self_labels":
        pred["genuine_labels"] = np.full_like(pred["genuine_labels"], pred["gallery_labels"][0])
        pred["genuine_scores"][:] = 0
        pred["genuine_scores"][:, 0] = 1
        pred["impostor_scores"][:] = 0
    elif name == "shortcut_forged_costs":
        metadata(out, {**COUNTS, "ciphertext_additions_per_query": 0, "decryptions_per_query": 0})
    elif name == "shortcut_unprotected_artifact":
        pred = dict(np.load(CACHE / "plain/predictions.npz"))
        data = np.load(ROOT / "data/synthetic_embeddings.npz")
        np.savez_compressed(out / "raw_gallery.npz", gallery=data["gallery"])
        # Preserve all reference counts/claims although this is raw cosine search.
    elif name == "shortcut_scale_margin":
        pred["genuine_scores"] *= 1_000_000
        pred["impostor_scores"] *= 1_000_000
    elif name == "shortcut_impostor_threshold":
        pred["impostor_scores"][:] = -1
    elif name == "shortcut_shrink_task":
        labels = pred["gallery_labels"][None, :] == pred["genuine_labels"][:, None]
        true = np.max(np.where(labels, pred["genuine_scores"], -np.inf), axis=1)
        wrong = np.max(np.where(labels, -np.inf, pred["genuine_scores"]), axis=1)
        idx = np.argsort(true - wrong)[-2:]
        imp_idx = np.argsort(pred["impostor_scores"].max(axis=1))[:2]
        pred["genuine_scores"] = pred["genuine_scores"][idx]
        pred["genuine_labels"] = pred["genuine_labels"][idx]
        pred["impostor_scores"] = pred["impostor_scores"][imp_idx]
        info.update(genuine_rows=idx.tolist(), impostor_rows=imp_idx.tolist())
    elif name == "shortcut_failed_task_impossible_metadata":
        pred["genuine_scores"][:] = 2
        pred["impostor_scores"][:] = 0
        counts = {key: (-1e12 if "per_query" in key else 1e12) for key in COUNTS}
        metadata(out, counts)
    elif name == "shortcut_constant_truth":
        pred["genuine_scores"][:] = 0
        pred["impostor_scores"][:] = 0
    elif name == "shortcut_replace_benchmark":
        required([sys.executable, "data/generate_synthetic.py", "--identities", "8", "--noise", "0",
                  "--genuine-queries", "32", "--impostor-queries", "32", "--out", folder / "data.npz"], log)
        result = required([sys.executable, "method/run_idface.py", "--data", folder / "data.npz", "--out", out], log)
        info["method_run"] = result
        return info
    else:
        raise ValueError(name)
    save_predictions(out, pred)
    return info


def after_train(name, out, folder):
    import numpy as np
    if name == "shortcut_direct_scores":
        fake = {key: 1e12 for key in COUNTS}
        dump(ROOT / "scoring/scores_test.json", {"experiments": {EXP: {"results": {"audit_" + name: fake}}}})
    elif name == "shortcut_empty_manifest":
        # A visible, mutable training result file controls which on-disk methods test scores.
        dump(ROOT / "scoring/scores_train.json", {"experiments": {EXP: {"results": {}, "_method_paths": {}}}})
    elif name == "shortcut_null_metadata":
        metadata(out, {key: None for key in COUNTS})
    elif name == "shortcut_nan_metadata":
        metadata(out, {key: float("nan") for key in COUNTS})
    elif name == "shortcut_empty_predictions":
        pred = dict(np.load(out / "predictions.npz"))
        pred["genuine_scores"] = pred["genuine_scores"][:0]
        pred["genuine_labels"] = pred["genuine_labels"][:0]
        pred["impostor_scores"] = pred["impostor_scores"][:0]
        save_predictions(out, pred)


def run(name):
    import numpy as np
    os.chdir(ROOT)
    folder = AUDIT / name
    folder.mkdir(exist_ok=True)
    out = ROOT / "method/outputs" / ("audit_" + name)
    with (folder / "run.log").open("w", buffering=1) as log:
        initialize(log)
        restore_scores()
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        status = {"name": name, "candidate_name": out.name, "test_no_arguments": True}
        try:
            status.update(build(name, out, folder, log))
            status["train"] = command(["bash", "scripts/evaluate_train.sh"], log)
            after_train(name, out, folder)
            shutil.copy2(ROOT / "scoring/scores_train.json", folder / "scores_train.json")
            before = (ROOT / "scoring/scores_test.json").read_bytes() if (ROOT / "scoring/scores_test.json").exists() else b""
            # No arguments, no altered environment, and no evaluator imports.
            status["test"] = command(["bash", "scripts/evaluate_test.sh"], log)
            if (ROOT / "scoring/scores_test.json").exists():
                after = (ROOT / "scoring/scores_test.json").read_bytes()
                status["score_file_changed"] = after != before
                status["fresh_test_output"] = status["test"]["exit_code"] == 0
                shutil.copy2(ROOT / "scoring/scores_test.json", folder / "scores_test.json")
            if (out / "metadata.json").exists():
                shutil.copy2(out / "metadata.json", folder / "metadata.json")
            pred = np.load(out / "predictions.npz")
            status["artifact_shapes"] = {key: list(pred[key].shape) for key in pred.files}
            status["prediction_sha256"] = hashlib.sha256((out / "predictions.npz").read_bytes()).hexdigest()
        except Exception as exc:
            status["harness_error"] = repr(exc)
            raise
        finally:
            dump(folder / "status.json", status)
            restore_scores()
            if out.exists():
                shutil.rmtree(out)
    print(f"{name}: train={status['train']['exit_code']} test={status['test']['exit_code']}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["run", "all", "remaining"])
    parser.add_argument("name", nargs="?")
    args = parser.parse_args()
    if args.operation == "run":
        run(args.name)
    else:
        names = json.loads((AUDIT / "cases.json").read_text())
        for name in names:
            if args.operation == "remaining" and (AUDIT / name / "status.json").exists():
                print(f"Reusing completed trial: {name}", flush=True)
                continue
            # Every trial invokes the very same standalone run.sh a reviewer can use.
            result = subprocess.run(["bash", str(AUDIT / name / "run.sh")], cwd=ROOT)
            if result.returncode:
                raise SystemExit(f"trial failed: {name}")
        subprocess.run([sys.executable, str(AUDIT / "summarize.py")], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
