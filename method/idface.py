"""IDFace core computation.

This module implements the paper's algorithmic steps without depending on a
particular homomorphic encryption library. The encrypted database operations are
represented by additive ciphertext arrays, so the computation preserves the
same data flow: encode enrolled templates, perform additive-only database inner
products, decrypt/decode packed scores, then identify.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def transform(x: np.ndarray, alpha: int) -> np.ndarray:
    """Top-alpha ternary transformation T_alpha from the paper."""
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[None, :]
        squeeze = True
    else:
        squeeze = False
    if not 1 <= alpha <= x.shape[1]:
        raise ValueError(f"alpha must be in [1, {x.shape[1]}], got {alpha}")
    idx = np.argpartition(np.abs(x), -alpha, axis=1)[:, -alpha:]
    z = np.zeros_like(x, dtype=np.int16)
    rows = np.arange(x.shape[0])[:, None]
    z[rows, idx] = np.where(x[rows, idx] >= 0, 1, -1).astype(np.int16)
    return z[0] if squeeze else z


def split_pm(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.asarray(z, dtype=np.int64)
    return ((np.abs(z) + z) // 2, (np.abs(z) - z) // 2)


def encode(z_block: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    """Pack m ternary templates into positive and negative integer vectors."""
    z_pos, z_neg = split_pm(z_block)
    powers = (p ** np.arange(z_block.shape[0], dtype=np.int64)).reshape(-1, 1)
    return (
        np.sum(z_pos.astype(np.int64) * powers, axis=0),
        np.sum(z_neg.astype(np.int64) * powers, axis=0),
    )


def decode(pos: np.ndarray, neg: np.ndarray, p: int, m: int) -> np.ndarray:
    """Decode packed positive/negative inner-product accumulators."""
    pos_work = np.array(pos, dtype=np.int64, copy=True)
    neg_work = np.array(neg, dtype=np.int64, copy=True)
    scores = []
    for _ in range(m):
        s_pos = pos_work % p
        s_neg = neg_work % p
        scores.append(s_pos - s_neg)
        pos_work = (pos_work - s_pos) // p
        neg_work = (neg_work - s_neg) // p
    return np.stack(scores, axis=0)


@dataclass
class IDFaceDatabase:
    labels: np.ndarray
    alpha: int
    beta: int
    p: int
    pack: int
    enc_pos: np.ndarray
    enc_neg: np.ndarray
    original_size: int

    @classmethod
    def enroll(cls, gallery: np.ndarray, labels: np.ndarray, alpha: int, beta: int, plaintext_bits: int = 50) -> "IDFaceDatabase":
        p = max(alpha, beta) + 1
        pack = max(1, int(plaintext_bits // np.ceil(np.log2(p))))
        pad = (-len(gallery)) % pack
        if pad:
            gallery = np.concatenate([gallery, np.zeros((pad, gallery.shape[1]), dtype=gallery.dtype)], axis=0)
            labels = np.concatenate([labels, np.full(pad, -1, dtype=labels.dtype)], axis=0)
        z = transform(gallery, alpha)
        blocks = z.reshape(-1, pack, z.shape[1])
        enc_pos, enc_neg = [], []
        for block in blocks:
            pos, neg = encode(block, p)
            enc_pos.append(pos)
            enc_neg.append(neg)
        return cls(labels, alpha, beta, p, pack, np.array(enc_pos, dtype=np.int64), np.array(enc_neg, dtype=np.int64), len(labels) - pad)

    def query_scores(self, query: np.ndarray) -> np.ndarray:
        zq = transform(query, self.beta)
        q_pos, q_neg = split_pm(zq)
        packed_pos = self.enc_pos @ q_pos + self.enc_neg @ q_neg
        packed_neg = self.enc_pos @ q_neg + self.enc_neg @ q_pos
        decoded = decode(packed_pos, packed_neg, self.p, self.pack).T.reshape(-1)
        return decoded[: self.original_size].astype(np.float64) / np.sqrt(self.alpha * self.beta)

    def batch_scores(self, queries: np.ndarray) -> np.ndarray:
        return np.stack([self.query_scores(q) for q in queries], axis=0)

    def operation_counts(self, identities: int | None = None) -> dict[str, int]:
        n = self.original_size if identities is None else identities
        blocks = int(np.ceil(n / self.pack))
        # The paper reports HE operations for the packed query computation.
        # Local block splitting changes array bookkeeping, not the algorithmic
        # count of two encrypted aggregate scores per query.
        return {
            "ciphertext_additions_per_query": int(2 * (self.beta - 1)),
            "ciphertext_multiplications_per_query": 0,
            "ciphertext_rotations_per_query": 0,
            "decryptions_per_query": 2,
            "ciphertexts_per_block": 2,
            "local_blocks": blocks,
            "pack": int(self.pack),
        }
