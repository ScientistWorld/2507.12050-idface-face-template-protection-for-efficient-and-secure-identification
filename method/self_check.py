"""Lightweight consistency checks for the IDFace arithmetic."""

from __future__ import annotations

import numpy as np

from idface import IDFaceDatabase, decode, encode, split_pm, transform


def main() -> None:
    rng = np.random.default_rng(7)

    x = rng.normal(size=(4, 12))
    z = transform(x, alpha=5)
    if not np.all(np.sum(z != 0, axis=1) == 5):
        raise AssertionError("T_alpha did not produce exactly alpha non-zero entries")

    block = transform(rng.normal(size=(4, 16)), alpha=6)
    p = 7
    pos, neg = encode(block, p)
    q = transform(rng.normal(size=16), alpha=6)
    q_pos, q_neg = split_pm(q)
    packed_pos = pos @ q_pos + neg @ q_neg
    packed_neg = pos @ q_neg + neg @ q_pos
    decoded = decode(np.array([packed_pos]), np.array([packed_neg]), p=p, m=block.shape[0]).reshape(-1)
    direct = block @ q
    if not np.array_equal(decoded, direct):
        raise AssertionError("encode/decode result differs from direct ternary dot product")

    gallery = rng.normal(size=(11, 32))
    queries = rng.normal(size=(3, 32))
    labels = np.arange(len(gallery))
    db = IDFaceDatabase.enroll(gallery, labels, alpha=9, beta=4, plaintext_bits=18)
    expected_pack = int(np.floor(18 / np.log2(5)))
    if db.p != 5 or db.pack != expected_pack:
        raise AssertionError(f"unexpected compressed packing: p={db.p}, pack={db.pack}")
    actual = db.batch_scores(queries)
    direct_scores = transform(queries, 4).astype(np.int64) @ transform(gallery, 9).astype(np.int64).T
    direct_scores = direct_scores.astype(np.float64) / np.sqrt(9 * 4)
    if not np.allclose(actual, direct_scores):
        raise AssertionError("IDFaceDatabase scores differ from direct transformed scores")

    # The evaluator scores integer inner products of the encoder's codes. Check
    # that the packed, sign-split homomorphic computation decodes to exactly
    # those inner products for the paper's operating points.
    gallery = rng.normal(size=(40, 512))
    queries = rng.normal(size=(6, 512))
    for alpha, beta in ((341, 341), (341, 63)):
        db = IDFaceDatabase.enroll(gallery, np.arange(len(gallery)), alpha=alpha, beta=beta, plaintext_bits=50)
        packed = db.batch_scores(queries) * np.sqrt(alpha * beta)
        codes_ip = transform(queries, beta).astype(np.int64) @ transform(gallery, alpha).astype(np.int64).T
        if not np.allclose(packed, codes_ip):
            raise AssertionError(f"packed computation differs from code inner products at ({alpha},{beta})")
        expected = {341: 5, 63: 8}[beta]
        if db.pack != expected:
            raise AssertionError(f"unexpected pack {db.pack} at ({alpha},{beta}), expected {expected}")

    print("IDFace self-check passed")


if __name__ == "__main__":
    main()
