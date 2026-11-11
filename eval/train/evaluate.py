#!/usr/bin/env python3
"""Train (development) evaluator for protected biometric identification.

Scores every method directory on the visible development benchmark
``data/synthetic_embeddings.npz`` (produced by ``data/generate_synthetic.py``),
with the same interface, protocol, budgets and metrics as the hidden test:

* every method is a directory holding ``encoder.json``; the evaluator runs the
  method's encoder separately on gallery templates and on probe templates
  (genuine and impostor probes shuffled together, unlabeled) and receives one
  integer code vector per template;
* the evaluator computes every match score itself as the cosine of the
  integer codes and every metric from the benchmark's labels;
* the encrypted-computation cost of the codes (ciphertext additions per probe,
  templates packed per 50-bit plaintext slot) is computed from the codes and
  must fit the experiment's fixed budget;
* an encoder whose codes depend on call order or batch composition, a crash,
  a timeout, malformed or non-integer codes, or a budget violation fails the
  run, which then receives the worst value of every scored metric.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

import numpy as np

SLICE = "train"
WORKSPACE = Path(__file__).resolve().parents[2]

DEFAULT_DATA = Path("data/synthetic_embeddings.npz")
PROTOCOL_SEED = 0

PLAINTEXT_BITS = 50
MAX_CODE_DIM = 512
MAX_ABS_CODE = 1 << 20
ENCODER_TIMEOUT_SECONDS = 600
CONSISTENCY_FRACTION = 0.1
FPIRS = (0.1, 0.01, 0.001)

EXPERIMENTS = {
    "synthetic_identification": {"max_mean_additions": 680.0, "min_pack": 5},
    "synthetic_identification_compressed": {"max_mean_additions": 124.0, "min_pack": 8},
}
SCORED_METRICS = (
    "top1_identification",
    "mean_reciprocal_rank",
    "tpir_at_fpir_0.1",
    "tpir_at_fpir_0.01",
    "tpir_at_fpir_0.001",
    "open_set_score_auc",
)
WORST_VALUES = {name: 0.0 for name in SCORED_METRICS}
DEFAULT_ROOTS = ("method/outputs", "baseline/outputs", "checkpoints")


# ── Visible development benchmark ────────────────────────────────────────────


def load_benchmark(path: Path) -> dict[str, np.ndarray]:
    path = path if path.is_absolute() else WORKSPACE / path
    if not path.is_file():
        raise SystemExit(f"missing {path}; run: python data/generate_synthetic.py")
    with np.load(path, allow_pickle=False) as data:
        gallery_labels = data["gallery_labels"]
        if not np.array_equal(gallery_labels, np.arange(len(gallery_labels))):
            raise SystemExit("gallery_labels must be 0..N-1 in gallery order")
        return {
            "gallery": data["gallery"].astype(np.float32),
            "genuine": data["genuine_queries"].astype(np.float32),
            "genuine_labels": data["genuine_labels"].astype(np.int64),
            "impostor": data["impostor_queries"].astype(np.float32),
        }


# ── Metrics ──────────────────────────────────────────────────────────────────


def _auc(positive: np.ndarray, negative: np.ndarray) -> float:
    scores = np.concatenate([positive, negative])
    _, inverse, counts = np.unique(scores, return_inverse=True, return_counts=True)
    upper = np.cumsum(counts)
    mid_rank = upper - (counts - 1) / 2.0
    ranks = mid_rank[inverse]
    n_pos, n_neg = len(positive), len(negative)
    return float((ranks[:n_pos].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def _match_statistics(gallery, genuine, labels, impostor, gallery_inv_norm=None, chunk: int = 2048):
    """Return per-probe true score, strict top-1 correctness, pessimistic rank and impostor maxima.

    ``gallery`` and probes are float32 matrices. Scores are cosine similarities;
    rows with zero norm score 0 against everything. Ties never count as a
    correct identification.
    """
    g32 = gallery.astype(np.float32)
    if gallery_inv_norm is None:
        norms = np.linalg.norm(gallery.astype(np.float64), axis=1)
        gallery_inv_norm = np.where(norms > 0, 1.0 / np.where(norms > 0, norms, 1.0), 0.0)

    def cosine(block: np.ndarray) -> np.ndarray:
        ip = (block.astype(np.float32) @ g32.T).astype(np.float64)
        norms = np.linalg.norm(block.astype(np.float64), axis=1)
        inv = np.where(norms > 0, 1.0 / np.where(norms > 0, norms, 1.0), 0.0)
        return ip * inv[:, None] * gallery_inv_norm[None, :]

    true_scores = np.empty(len(genuine))
    correct = np.empty(len(genuine), dtype=bool)
    ranks = np.empty(len(genuine))
    for start in range(0, len(genuine), chunk):
        stop = min(start + chunk, len(genuine))
        scores = cosine(genuine[start:stop])
        rows = np.arange(stop - start)
        true = scores[rows, labels[start:stop]].copy()
        scores[rows, labels[start:stop]] = -np.inf
        true_scores[start:stop] = true
        correct[start:stop] = true > scores.max(axis=1)
        ranks[start:stop] = 1 + np.sum(scores >= true[:, None], axis=1)
    impostor_max = np.empty(len(impostor))
    for start in range(0, len(impostor), chunk):
        stop = min(start + chunk, len(impostor))
        impostor_max[start:stop] = cosine(impostor[start:stop]).max(axis=1)
    return true_scores, correct, ranks, impostor_max


def identification_metrics(true_scores, correct, ranks, impostor_max) -> dict[str, float]:
    metrics = {
        "top1_identification": float(np.mean(correct)),
        "mean_reciprocal_rank": float(np.mean(1.0 / ranks)),
        "open_set_score_auc": _auc(true_scores, impostor_max),
    }
    descending = np.sort(impostor_max)[::-1]
    for fpir in FPIRS:
        k = int(math.floor(fpir * len(descending) + 1e-9))
        threshold = descending[k] if k < len(descending) else -np.inf
        metrics[f"tpir_at_fpir_{fpir:g}"] = float(np.mean(correct & (true_scores > threshold)))
    return {name: metrics[name] for name in SCORED_METRICS}


# ── Method discovery and encoder protocol ────────────────────────────────────


class RunFailure(Exception):
    pass


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    return cleaned.strip("._-") or "method"


def discover_methods(extra_roots: list[Path]) -> dict[str, Path]:
    roots = [WORKSPACE / root for root in DEFAULT_ROOTS] + [Path(r).resolve() for r in extra_roots]
    methods: dict[str, Path] = {}
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir() or root in seen:
            continue
        seen.add(root)
        try:
            tag = root.relative_to(WORKSPACE).parts[0]
        except ValueError:
            tag = root.name
        for directory in sorted(p for p in root.iterdir() if p.is_dir()):
            if not any((directory / marker).is_file() for marker in ("encoder.json", "predictions.npz", "metadata.json")):
                continue
            name = _safe_name(directory.name)
            if name in methods and methods[name].resolve() != directory.resolve():
                name = _safe_name(f"{tag}_{directory.name}")
            methods.setdefault(name, directory)
    return dict(sorted(methods.items()))


def _encoder_command(method_dir: Path, experiment: str) -> list[str]:
    spec_file = method_dir / "encoder.json"
    if not spec_file.is_file():
        raise RunFailure("no encoder.json: the method provides no encoder the evaluator can run")
    try:
        spec = json.loads(spec_file.read_text())
        command = spec["command"]
        entry = spec.get("experiments", {})[experiment]
        args = entry.get("args", []) if isinstance(entry, dict) else []
    except KeyError as exc:
        raise RunFailure(f"encoder.json has no entry {exc} for experiment {experiment}") from None
    except Exception as exc:  # malformed JSON or schema
        raise RunFailure(f"unreadable encoder.json: {exc}") from None
    if not (isinstance(command, list) and command and all(isinstance(c, str) for c in command)):
        raise RunFailure("encoder.json 'command' must be a non-empty list of strings")
    if not (isinstance(args, list) and all(isinstance(a, str) for a in args)):
        raise RunFailure("encoder.json experiment 'args' must be a list of strings")
    command = list(command)
    if command[0] in ("python", "python3"):
        command[0] = sys.executable
    return command + args


def _run_encoder(command: list[str], role: str, templates: np.ndarray, workdir: Path) -> np.ndarray:
    call_dir = Path(tempfile.mkdtemp(prefix="call_", dir=workdir))
    try:
        in_file = call_dir / "templates.npz"
        out_file = call_dir / "codes.npz"
        np.savez(in_file, templates=templates.astype(np.float32))
        scratch = call_dir / "tmp"
        scratch.mkdir()
        env = dict(os.environ, TMPDIR=str(scratch))
        full = command + ["--role", role, "--input", str(in_file), "--output", str(out_file)]
        try:
            proc = subprocess.run(
                full, cwd=WORKSPACE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=ENCODER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            raise RunFailure(f"{role} encoder exceeded {ENCODER_TIMEOUT_SECONDS}s") from None
        except OSError as exc:
            raise RunFailure(f"{role} encoder could not start: {exc}") from None
        if proc.returncode != 0:
            tail = proc.stderr.decode(errors="replace").strip().splitlines()[-3:]
            raise RunFailure(f"{role} encoder exited {proc.returncode}: {' | '.join(tail)}")
        if not out_file.is_file():
            raise RunFailure(f"{role} encoder wrote no codes file")
        try:
            with np.load(out_file, allow_pickle=False) as payload:
                codes = np.asarray(payload["codes"])
        except Exception as exc:
            raise RunFailure(f"{role} codes unreadable: {exc}") from None
    finally:
        shutil.rmtree(call_dir, ignore_errors=True)

    if codes.ndim != 2 or codes.shape[0] != len(templates):
        raise RunFailure(f"{role} codes have shape {codes.shape}, expected ({len(templates)}, D)")
    if not 1 <= codes.shape[1] <= MAX_CODE_DIM:
        raise RunFailure(f"{role} code dimension {codes.shape[1]} outside [1, {MAX_CODE_DIM}]")
    if codes.dtype == np.bool_:
        codes = codes.astype(np.int64)
    if not np.issubdtype(codes.dtype, np.integer):
        raise RunFailure(f"{role} codes must be integers, got dtype {codes.dtype}")
    if codes.size and float(np.abs(codes.astype(np.float64)).max()) > MAX_ABS_CODE:
        raise RunFailure(f"{role} code magnitude exceeds {MAX_ABS_CODE}")
    return codes.astype(np.int64)


def encode_with_protocol(command: list[str], gallery: np.ndarray, probes: np.ndarray, rng, workdir: Path):
    """Run the encoder four times and require per-template, order-independent codes.

    1. a random 10% gallery subset, before any probe has been seen;
    2. all probes, shuffled (genuine and impostor mixed, unlabeled);
    3. the full gallery, shuffled, after the probes have been seen;
    4. a random 10% probe subset, after the full gallery has been seen.
    Codes from (1) must equal the same rows of (3) and codes from (4) the same
    rows of (2); otherwise the encoder used information beyond the template.
    """
    n_g, n_p = len(gallery), len(probes)
    gallery_subset = rng.choice(n_g, size=max(1, int(CONSISTENCY_FRACTION * n_g)), replace=False)
    probe_subset = rng.choice(n_p, size=max(1, int(CONSISTENCY_FRACTION * n_p)), replace=False)
    probe_order = rng.permutation(n_p)
    gallery_order = rng.permutation(n_g)

    first_gallery = _run_encoder(command, "gallery", gallery[gallery_subset], workdir)
    shuffled = _run_encoder(command, "query", probes[probe_order], workdir)
    probe_codes = np.empty_like(shuffled)
    probe_codes[probe_order] = shuffled
    shuffled = _run_encoder(command, "gallery", gallery[gallery_order], workdir)
    gallery_codes = np.empty_like(shuffled)
    gallery_codes[gallery_order] = shuffled
    last_probes = _run_encoder(command, "query", probes[probe_subset], workdir)

    dims = {first_gallery.shape[1], probe_codes.shape[1], gallery_codes.shape[1], last_probes.shape[1]}
    if len(dims) != 1:
        raise RunFailure(f"gallery and query codes have different dimensions {sorted(dims)}")
    if not np.array_equal(gallery_codes[gallery_subset], first_gallery):
        raise RunFailure("gallery codes changed between calls (depend on batch or on previously seen probes)")
    if not np.array_equal(probe_codes[probe_subset], last_probes):
        raise RunFailure("query codes changed between calls (depend on batch or on previously seen gallery)")
    return gallery_codes, probe_codes


def encrypted_cost(gallery_codes: np.ndarray, probe_codes: np.ndarray) -> dict[str, float]:
    """Cost of additive-HE matching with sign-split, base-p packed gallery codes.

    Each probe coordinate of magnitude k adds the corresponding encrypted
    gallery column k times into each of the two (same-sign / opposite-sign)
    accumulators, so a probe costs 2 * (||q||_1 - 1) ciphertext additions.
    Every decoded digit is bounded by
    B = min(max ||g||_1 * max |q|, max ||q||_1 * max |g|), so the packing base
    is p = B + 1 and a 50-bit slot holds the largest m with p^m <= 2^50
    templates (the paper's floor(n / log2 p)).
    """
    l1_probe = np.abs(probe_codes).sum(axis=1)
    l1_gallery = np.abs(gallery_codes).sum(axis=1)
    max_probe = int(np.abs(probe_codes).max()) if probe_codes.size else 0
    max_gallery = int(np.abs(gallery_codes).max()) if gallery_codes.size else 0
    bound = min(int(l1_gallery.max()) * max_probe, int(l1_probe.max()) * max_gallery)
    pack = 0
    while pack < PLAINTEXT_BITS and (bound + 1) ** (pack + 1) <= 2**PLAINTEXT_BITS:
        pack += 1
    return {
        "ciphertext_additions_per_query": float(np.mean(2 * np.maximum(l1_probe - 1, 0))),
        "max_query_l1": float(l1_probe.max()),
        "digit_bound": float(bound),
        "bits_per_template": float(math.log2(bound + 1)),
        "templates_per_slot": float(pack),
        "code_dim": float(gallery_codes.shape[1]),
        "ciphertext_multiplications_per_query": 0.0,
        "decryptions_per_block": 2.0,
    }


def evaluate_method(method_dir: Path, experiment: str, bench: dict, rng, workdir: Path, dump_dir: Path | None, name: str):
    budget = EXPERIMENTS[experiment]
    command = _encoder_command(method_dir, experiment)
    probes = np.concatenate([bench["genuine"], bench["impostor"]], axis=0)
    gallery_codes, probe_codes = encode_with_protocol(command, bench["gallery"], probes, rng, workdir)
    cost = encrypted_cost(gallery_codes, probe_codes)
    if cost["ciphertext_additions_per_query"] > budget["max_mean_additions"] + 1e-9:
        raise RunFailure(
            f"budget exceeded: {cost['ciphertext_additions_per_query']:.1f} ciphertext additions per query "
            f"> {budget['max_mean_additions']:.0f}"
        )
    if cost["templates_per_slot"] < budget["min_pack"]:
        raise RunFailure(
            f"budget exceeded: digit bound {int(cost['digit_bound'])} packs {int(cost['templates_per_slot'])} "
            f"templates per {PLAINTEXT_BITS}-bit slot < {budget['min_pack']}"
        )
    n_gen = len(bench["genuine"])
    stats = _match_statistics(gallery_codes, probe_codes[:n_gen], bench["genuine_labels"], probe_codes[n_gen:])
    if dump_dir is not None:
        dump_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(dump_dir / f"{experiment}__{name}.npz", true=stats[0], correct=stats[1], rank=stats[2], impostor_max=stats[3])
    return identification_metrics(*stats), cost


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="*", type=Path, help="Extra roots whose subdirectories are method directories.")
    parser.add_argument("--out", type=Path, default=Path("scoring/scores_train.json"))
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--methods", default=None, help="Audit only: comma-separated subset of method names.")
    parser.add_argument("--dump-dir", type=Path, default=None, help="Audit only: save per-probe outcomes.")
    args = parser.parse_args()

    seed = PROTOCOL_SEED
    bench = load_benchmark(args.data)
    methods = discover_methods(args.roots)
    if args.methods:
        wanted = set(args.methods.split(","))
        methods = {k: v for k, v in methods.items() if k in wanted}

    plain = identification_metrics(*_match_statistics(bench["gallery"], bench["genuine"], bench["genuine_labels"], bench["impostor"]))
    output: dict = {"experiments": {}}
    workdir = Path(tempfile.mkdtemp(prefix="idface_eval_"))
    try:
        for experiment, budget in EXPERIMENTS.items():
            results, diagnostics = {}, {}
            for name, method_dir in methods.items():
                rng = np.random.default_rng([seed, zlib.crc32(name.encode()), zlib.crc32(experiment.encode())])
                try:
                    metrics, cost = evaluate_method(method_dir, experiment, bench, rng, workdir, args.dump_dir, name)
                    diagnostics[name] = {"status": "ok", **cost}
                except RunFailure as exc:
                    metrics = dict(WORST_VALUES)
                    diagnostics[name] = {"status": "failed", "reason": str(exc)}
                results[name] = metrics
                print(f"[{SLICE}] {experiment} {name}: {diagnostics[name]['status']} {metrics}", flush=True)
            output["experiments"][experiment] = {
                "slice": SLICE,
                "budget": {**budget, "plaintext_bits": PLAINTEXT_BITS, "max_code_dim": MAX_CODE_DIM},
                "results": results,
                "_diagnostics": diagnostics,
                "_context": {"unprotected_float_cosine": plain},
            }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    out = args.out if args.out.is_absolute() else WORKSPACE / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
