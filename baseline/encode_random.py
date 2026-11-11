#!/usr/bin/env python3
"""Random-code sanity baseline.

Every template gets a ternary code with ``alpha`` (gallery) or ``beta``
(probe) non-zeros at pseudo-random positions and signs. The code is a
deterministic function of the template bytes (so it is a valid per-template
encoder) but carries no information about the template, so identification
should be at chance level.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=341)
    parser.add_argument("--role", choices=("gallery", "query"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with np.load(args.input, allow_pickle=False) as payload:
        templates = np.ascontiguousarray(payload["templates"], dtype=np.float32)
    k = args.alpha if args.role == "gallery" else args.beta
    codes = np.zeros(templates.shape, dtype=np.int8)
    for row, template in enumerate(templates):
        digest = hashlib.sha256(template.tobytes()).digest()
        rng = np.random.default_rng(int.from_bytes(digest[:8], "little"))
        coords = rng.choice(templates.shape[1], size=k, replace=False)
        codes[row, coords] = rng.choice(np.array([-1, 1], dtype=np.int8), size=k)
    np.savez(args.output, codes=codes)


if __name__ == "__main__":
    main()
