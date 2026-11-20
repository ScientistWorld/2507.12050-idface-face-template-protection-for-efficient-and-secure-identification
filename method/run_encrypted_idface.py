#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from idface import IDFaceDatabase, decode, split_pm, transform
from paillier import generate_keypair


def encrypted_scores(db: IDFaceDatabase, queries: np.ndarray, key_bits: int) -> tuple[np.ndarray, dict[str, float]]:
    public, private = generate_keypair(key_bits)

    enc_pos = np.empty(db.enc_pos.shape, dtype=object)
    enc_neg = np.empty(db.enc_neg.shape, dtype=object)
    for index in np.ndindex(db.enc_pos.shape):
        enc_pos[index] = public.encrypt(int(db.enc_pos[index]))
        enc_neg[index] = public.encrypt(int(db.enc_neg[index]))

    zero = public.encrypt(0)
    all_scores = []
    encrypted_additions = 0
    encrypted_plain_mults = 0
    decryptions = 0
    for query in queries:
        zq = transform(query, db.beta)
        q_pos, q_neg = split_pm(zq)
        packed_pos = []
        packed_neg = []
        active_dims = np.flatnonzero((q_pos + q_neg) > 0)
        for block in range(db.enc_pos.shape[0]):
            # T_beta is ternary: select columns, then add from the first
            # selected ciphertext. This is the paper's 2*(beta-1) schedule.
            acc_pos = acc_neg = None
            for dim in active_dims:
                pp = int(q_pos[dim])
                left = enc_pos[block, dim] if pp else enc_neg[block, dim]
                right = enc_neg[block, dim] if pp else enc_pos[block, dim]
                if acc_pos is None:
                    acc_pos, acc_neg = left, right
                else:
                    acc_pos = public.add(acc_pos, left)
                    acc_neg = public.add(acc_neg, right)
                    encrypted_additions += 2
            if acc_pos is None:
                acc_pos = acc_neg = zero
            packed_pos.append(private.decrypt(acc_pos))
            packed_neg.append(private.decrypt(acc_neg))
            decryptions += 2
        decoded = decode(np.array(packed_pos, dtype=object), np.array(packed_neg, dtype=object), db.p, db.pack)
        all_scores.append(decoded.T.reshape(-1)[: db.original_size].astype(np.float64) / np.sqrt(db.alpha * db.beta))

    metadata = {
        "encrypted_ciphertexts": float(enc_pos.size + enc_neg.size),
        "paillier_key_bits": float(key_bits),
        "actual_homomorphic_additions": float(encrypted_additions),
        "actual_plaintext_scalar_multiplications": float(encrypted_plain_mults),
        "actual_decryptions": float(decryptions),
    }
    return np.stack(all_scores, axis=0), metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/paillier_dev.npz"))
    parser.add_argument("--out", type=Path, default=Path("method/smoke/paillier_small"))
    parser.add_argument("--identities", type=int, default=64)
    parser.add_argument("--genuine-queries", type=int, default=32)
    parser.add_argument("--impostor-queries", type=int, default=32)
    parser.add_argument("--alpha", type=int, default=341)
    parser.add_argument("--beta", type=int, default=63)
    parser.add_argument("--plaintext-bits", type=int, default=50)
    parser.add_argument("--key-bits", type=int, default=2048)
    args = parser.parse_args()

    data = np.load(args.data)
    gallery = data["gallery"][: args.identities]
    gallery_labels = data["gallery_labels"][: args.identities]

    genuine_mask = data["genuine_labels"] < args.identities
    genuine_idx = np.flatnonzero(genuine_mask)[: args.genuine_queries]
    if len(genuine_idx) < args.genuine_queries:
        raise ValueError("not enough genuine queries for encrypted smoke test")
    genuine = data["genuine_queries"][genuine_idx]
    genuine_labels = data["genuine_labels"][genuine_idx]
    impostor = data["impostor_queries"][: args.impostor_queries]

    db = IDFaceDatabase.enroll(gallery, gallery_labels, args.alpha, args.beta, args.plaintext_bits)
    genuine_scores, genuine_meta = encrypted_scores(db, genuine, args.key_bits)
    impostor_scores, impostor_meta = encrypted_scores(db, impostor, args.key_bits)

    plain_genuine = db.batch_scores(genuine)
    plain_impostor = db.batch_scores(impostor)
    max_error = max(
        float(np.max(np.abs(genuine_scores - plain_genuine))),
        float(np.max(np.abs(impostor_scores - plain_impostor))),
    )
    if max_error > 1e-12:
        raise AssertionError(f"encrypted IDFace scores differ from plaintext packed arithmetic: {max_error}")

    args.out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out / "predictions.npz",
        genuine_scores=genuine_scores.astype(np.float32),
        impostor_scores=impostor_scores.astype(np.float32),
        genuine_labels=genuine_labels,
        gallery_labels=gallery_labels,
    )
    n_queries = len(genuine) + len(impostor)
    total_additions = genuine_meta["actual_homomorphic_additions"] + impostor_meta["actual_homomorphic_additions"]
    total_mults = genuine_meta["actual_plaintext_scalar_multiplications"] + impostor_meta["actual_plaintext_scalar_multiplications"]
    total_decryptions = genuine_meta["actual_decryptions"] + impostor_meta["actual_decryptions"]
    metadata = {
        "method": "idface_paillier_smoke_check",
        "note": (
            "Correctness check only (not scored): decrypted Paillier scores equal the packed plaintext "
            "IDFace arithmetic. This pure-Python Paillier run adds one encrypted column per active probe "
            "coordinate and per packed block, so its measured counts scale with the number of blocks; "
            "the paper's 2(beta-1) additions / 2 decryptions are per packed SIMD block."
        ),
        "alpha": args.alpha,
        "beta": args.beta,
        "plaintext_bits": args.plaintext_bits,
        "paillier_key_bits": args.key_bits,
        "identities": args.identities,
        "genuine_queries": len(genuine),
        "impostor_queries": len(impostor),
        "packed_blocks": int(db.enc_pos.shape[0]),
        "templates_per_block": int(db.pack),
        "encrypted_ciphertexts": genuine_meta["encrypted_ciphertexts"],
        "measured_homomorphic_additions_per_query": total_additions / n_queries,
        "measured_plaintext_scalar_multiplications_per_query": total_mults / n_queries,
        "measured_decryptions_per_query": total_decryptions / n_queries,
        "algorithmic_counts_per_block": {k: v for k, v in db.operation_counts().items() if k != "local_blocks"},
        "max_plain_encrypted_score_error": max_error,
    }
    (args.out / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
