#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np


SLICE = "train"
EXPERIMENT = "synthetic_identification"
TRAIN_RESIDUE = 0
SPLIT_MODULUS = 2

DEFAULT_METHODS = {
    "plain": Path("baseline/outputs/plain_synthetic"),
    "random": Path("baseline/outputs/random_synthetic"),
    "idface_341_341": Path("method/outputs/idface_synthetic"),
    "idface_341_63": Path("method/outputs/idface_synthetic_beta63"),
}
KNOWN_PATH_NAMES = {path.as_posix(): name for name, path in DEFAULT_METHODS.items()}


def _load_predictions(path: Path) -> dict[str, np.ndarray]:
    pred_file = path / "predictions.npz"
    if not pred_file.exists():
        raise FileNotFoundError(f"missing predictions file: {pred_file}")
    return dict(np.load(pred_file))


def _split_rows(array: np.ndarray, residue: int) -> np.ndarray:
    mask = np.arange(array.shape[0]) % SPLIT_MODULUS == residue
    return array[mask]


def _slice_predictions(pred: dict[str, np.ndarray], residue: int) -> dict[str, np.ndarray]:
    return {
        "genuine_scores": _split_rows(pred["genuine_scores"], residue),
        "impostor_scores": _split_rows(pred["impostor_scores"], residue),
        "genuine_labels": _split_rows(pred["genuine_labels"], residue),
        "gallery_labels": pred["gallery_labels"],
    }


def _threshold_at_fpir(impostor_scores: np.ndarray, fpir: float) -> float:
    max_impostor = np.max(impostor_scores, axis=1)
    return float(np.quantile(max_impostor, 1.0 - fpir, method="higher"))


def identification_metrics(pred: dict[str, np.ndarray]) -> dict[str, float]:
    genuine_scores = pred["genuine_scores"]
    impostor_scores = pred["impostor_scores"]
    genuine_labels = pred["genuine_labels"]
    gallery_labels = pred["gallery_labels"]

    top_idx = np.argmax(genuine_scores, axis=1)
    top_scores = genuine_scores[np.arange(len(genuine_scores)), top_idx]
    top_labels = gallery_labels[top_idx]
    correct_top1 = top_labels == genuine_labels

    true_gallery = gallery_labels[None, :] == genuine_labels[:, None]
    true_scores = np.max(np.where(true_gallery, genuine_scores, -np.inf), axis=1)
    best_wrong_scores = np.max(np.where(true_gallery, -np.inf, genuine_scores), axis=1)

    metrics = {
        "top1_identification": float(np.mean(correct_top1)),
        "mean_genuine_rank_margin": float(np.mean(true_scores - best_wrong_scores)),
    }
    for fpir in (1e-1, 1e-2):
        threshold = _threshold_at_fpir(impostor_scores, fpir)
        accepted_correct = correct_top1 & (top_scores >= threshold)
        metrics[f"tpir_at_fpir_{fpir:g}"] = float(np.mean(accepted_correct))
    return metrics


def evaluate_method(name: str, path: Path) -> dict[str, float]:
    metrics = identification_metrics(_slice_predictions(_load_predictions(path), TRAIN_RESIDUE))
    metadata_file = path / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
        counts = metadata.get("operation_counts", {})
        for key in (
            "ciphertext_additions_per_query",
            "ciphertext_multiplications_per_query",
            "ciphertext_rotations_per_query",
            "decryptions_per_query",
            "pack",
        ):
            if key in counts:
                metrics[key] = float(counts[key])
        if name == "plain":
            metrics.update(
                {
                    "ciphertext_additions_per_query": 0.0,
                    "ciphertext_multiplications_per_query": 0.0,
                    "ciphertext_rotations_per_query": 0.0,
                    "decryptions_per_query": 0.0,
                    "pack": 1.0,
                }
            )
    return metrics


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    return cleaned.strip("._-") or "method"


def _method_name_for_path(path: Path) -> str:
    normalized = path.as_posix().rstrip("/")
    return KNOWN_PATH_NAMES.get(normalized, _safe_name(path.name))


def _discover_output_dirs() -> dict[str, Path]:
    methods: dict[str, Path] = {}
    for root in (Path("baseline/outputs"), Path("method/outputs"), Path("checkpoints")):
        if not root.exists():
            continue
        for pred_file in sorted(root.glob("*/predictions.npz")):
            method_path = pred_file.parent
            methods.setdefault(_method_name_for_path(method_path), method_path)
    return methods


def _parse_method_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--method values must be NAME=PATH")
    name, raw_path = value.split("=", 1)
    name = _safe_name(name)
    if not name:
        raise argparse.ArgumentTypeError("--method name must not be empty")
    return name, Path(raw_path)


def _collect_methods(args: argparse.Namespace) -> dict[str, Path]:
    methods = _discover_output_dirs()
    for name, path in {
        "plain": args.plain,
        "random": args.random,
        "idface_341_341": args.idface,
        "idface_341_63": args.idface_compressed,
    }.items():
        methods[name] = path
    for name, path in args.method:
        methods[name] = path
    return {
        name: path
        for name, path in sorted(methods.items())
        if (path / "predictions.npz").exists()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plain", type=Path, default=DEFAULT_METHODS["plain"])
    parser.add_argument("--random", type=Path, default=DEFAULT_METHODS["random"])
    parser.add_argument("--idface", type=Path, default=DEFAULT_METHODS["idface_341_341"])
    parser.add_argument("--idface-compressed", type=Path, default=DEFAULT_METHODS["idface_341_63"])
    parser.add_argument("--method", action="append", default=[], type=_parse_method_arg)
    parser.add_argument("--out", type=Path, default=Path("scoring/scores_train.json"))
    args = parser.parse_args()

    methods = _collect_methods(args)
    results = {
        name: evaluate_method(name, path)
        for name, path in methods.items()
    }

    output = {
        "experiments": {
            EXPERIMENT: {
                "slice": SLICE,
                "split": "even query rows from predictions.npz; impostor threshold rows split the same way",
                "_method_paths": {name: path.as_posix() for name, path in methods.items()},
                "results": results,
            }
        }
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
