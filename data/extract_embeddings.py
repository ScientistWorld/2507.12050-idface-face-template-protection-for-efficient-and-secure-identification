#!/usr/bin/env python3
"""Extract 512-D AdaFace-IR101 (WebFace12M) embeddings from aligned 112x112 faces.

This is a data-preparation step run by ``scripts/prepare_data.sh`` (it needs
torch; ``scripts/download.sh --with-extraction-deps`` installs extraction
dependencies into .pylib/ for the container's Python 3.11). The network definition below is the IR-101
backbone of the CVLFace library (https://github.com/mk-minchul/CVLface), the
feature extractor used by the paper; weights come from the public Hugging Face
repository ``minchul/cvlface_adaface_ir101_webface12m``.

Input: webdataset tar shards whose members are ``<key>.jpg`` (aligned
112x112 RGB face) and ``<key>.cls``. Output: an ``.npz`` with the raw
(unnormalised) embeddings as float32, the image keys, and the identity names
parsed from the LFW-style keys (``First_Last_0001`` -> ``First_Last``).
"""

from __future__ import annotations

import argparse
import io
import os
import re
import tarfile
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from safetensors.torch import load_file
from torch import nn


# ── IR-101 backbone (CVLFace models/iresnet/model.py, inference subset) ──────


class BasicBlockIR(nn.Module):
    def __init__(self, in_channel: int, depth: int, stride: int):
        super().__init__()
        if in_channel == depth:
            self.shortcut_layer = nn.MaxPool2d(1, stride)
        else:
            self.shortcut_layer = nn.Sequential(nn.Conv2d(in_channel, depth, (1, 1), stride, bias=False), nn.BatchNorm2d(depth))
        self.res_layer = nn.Sequential(
            nn.BatchNorm2d(in_channel),
            nn.Conv2d(in_channel, depth, (3, 3), (1, 1), 1, bias=False),
            nn.BatchNorm2d(depth),
            nn.PReLU(depth),
            nn.Conv2d(depth, depth, (3, 3), stride, 1, bias=False),
            nn.BatchNorm2d(depth),
        )

    def forward(self, x):
        return self.res_layer(x) + self.shortcut_layer(x)


class Flatten(nn.Module):
    def forward(self, x):
        return x.reshape(x.size(0), -1)


class IR101(nn.Module):
    def __init__(self, output_dim: int = 512):
        super().__init__()
        self.input_layer = nn.Sequential(nn.Conv2d(3, 64, (3, 3), 1, 1, bias=False), nn.BatchNorm2d(64), nn.PReLU(64))
        stages = [(64, 64, 3), (64, 128, 13), (128, 256, 30), (256, 512, 3)]
        modules = []
        for in_c, depth, units in stages:
            modules.append(BasicBlockIR(in_c, depth, 2))
            modules.extend(BasicBlockIR(depth, depth, 1) for _ in range(units - 1))
        self.body = nn.Sequential(*modules)
        self.output_layer = nn.Sequential(
            nn.BatchNorm2d(512), nn.Dropout(0.4), Flatten(), nn.Linear(512 * 7 * 7, output_dim),
            nn.BatchNorm1d(output_dim, affine=False),
        )

    def forward(self, x):
        return self.output_layer(self.body(self.input_layer(x)))


def load_model(weights: Path) -> nn.Module:
    model = IR101()
    state = load_file(str(weights))
    prefix = "model.net."
    state = {k[len(prefix):]: v for k, v in state.items() if k.startswith(prefix)}
    model.load_state_dict(state, strict=True)
    model.eval()
    return model


# ── Data ─────────────────────────────────────────────────────────────────────


def iter_shards(shards: list[Path]):
    for shard in shards:
        with tarfile.open(shard) as tar:
            for member in tar:
                if member.isfile() and member.name.endswith(".jpg"):
                    key = member.name[: -len(".jpg")]
                    yield key, tar.extractfile(member).read()


def to_tensor(jpeg: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(jpeg)).convert("RGB")
    if image.size != (112, 112):
        image = image.resize((112, 112), Image.BILINEAR)
    array = np.asarray(image, dtype=np.float32) / 255.0
    return np.ascontiguousarray(((array - 0.5) / 0.5).transpose(2, 0, 1))


def identity_of(key: str) -> str:
    """LFW-style keys: ``First_Last_0001`` (LFW, XQLFW) or ``First_Last_1`` (CPLFW)."""
    return re.sub(r"_\d+$", "", Path(key).name)


def extract(model: nn.Module, shards: list[Path], out: Path, device: str, batch_size: int, limit: int = 0) -> None:
    keys, feats, batch_keys, batch = [], [], [], []
    start = time.time()

    def flush():
        with torch.inference_mode():
            emb = model(torch.from_numpy(np.stack(batch)).to(device))
        feats.append(emb.float().cpu().numpy())
        keys.extend(batch_keys)
        batch.clear()
        batch_keys.clear()
        if len(keys) % (batch_size * 20) == 0:
            print(f"  {out.name}: {len(keys)} images, {len(keys) / (time.time() - start):.1f} img/s", flush=True)

    for key, jpeg in iter_shards(shards):
        batch_keys.append(Path(key).name)
        batch.append(to_tensor(jpeg))
        if len(batch) == batch_size:
            flush()
        if limit and len(keys) + len(batch) >= limit:
            break
    if batch:
        flush()
    emb = np.concatenate(feats, axis=0)
    order = np.argsort(np.array(keys))
    keys_sorted = np.array(keys)[order]
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part.npz")
    np.savez(tmp, embeddings=emb[order], keys=keys_sorted, identities=np.array([identity_of(k) for k in keys_sorted]))
    tmp.replace(out)
    print(f"wrote {out}: {len(keys_sorted)} embeddings in {time.time() - start:.0f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=Path, default=Path("data/downloads/adaface_ir101_webface12m/model.safetensors"))
    parser.add_argument("--downloads", type=Path, default=Path("data/downloads"))
    parser.add_argument("--datasets", nargs="+", default=["lfw", "xqlfw", "cplfw"])
    parser.add_argument("--out-dir", type=Path, default=Path("data/downloads/embeddings"))
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--limit", type=int, default=0, help="debug: stop after this many images per dataset")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(max(1, len(os.sched_getaffinity(0))))
    print(f"device={device} torch={torch.__version__} threads={torch.get_num_threads()}", flush=True)
    model = load_model(args.weights).to(device)
    for name in args.datasets:
        out = args.out_dir / f"{name}_adaface_ir101.npz"
        if out.exists() and not args.limit:
            print(f"skip {out} (exists)")
            continue
        shards = sorted((args.downloads / name).glob("shard-*.tar"))
        if not shards:
            raise SystemExit(f"no shards for {name} under {args.downloads}; run scripts/download.sh")
        extract(model, shards, out, device, args.batch if device == "cuda" else 32, args.limit)


if __name__ == "__main__":
    main()
