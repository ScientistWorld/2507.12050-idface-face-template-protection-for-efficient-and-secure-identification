#!/usr/bin/env python3
"""Prepare identity-disjoint real face banks. All partition secrets stay here.

The input is the public AdaFace extraction cache, not an evaluation protocol.
The output files, including identities, are committed; inference needs no torch.
"""
from pathlib import Path
import json
import hashlib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PARTITION_SEED = 714395881204


def main():
    embeddings, identities, keys, sources = [], [], [], []
    for name in ('lfw', 'xqlfw', 'cplfw'):
        p = ROOT / 'data/downloads/embeddings' / f'{name}_adaface_ir101.npz'
        with np.load(p, allow_pickle=False) as d:
            x = d['embeddings'].astype(np.float32)
            assert x.shape[1] == 512 and np.isfinite(x).all()
            norms = np.linalg.norm(x.astype(np.float64), axis=1)
            assert (norms > 0).all()
            embeddings.append((x / norms[:, None]).astype(np.float32))
            identities.append(d['identities'])
            keys.append(d['keys'])
            sources.append(np.full(len(x), name))
    x = np.concatenate(embeddings)
    ids, key, source = map(np.concatenate, (identities, keys, sources))
    names = np.unique(ids)
    order = np.random.default_rng(PARTITION_SEED).permutation(names)
    dev_names = order[:len(order)//2]
    dev = np.isin(ids, dev_names)
    summary = {'extractor': 'AdaFace IR-101 / WebFace12M (CVLFace)', 'sources': ['lfw', 'xqlfw', 'cplfw']}
    for name, mask, path in (
        ('train', dev, ROOT / 'data/face_embeddings_dev.npz'),
        ('test', ~dev, ROOT / 'eval/test/face_embeddings_test.npz'),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, embeddings=x[mask], identities=ids[mask], keys=key[mask], sources=source[mask])
        summary[name] = {'identities': len(np.unique(ids[mask])), 'images': int(mask.sum()),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert not set(ids[dev]) & set(ids[~dev])
    (ROOT / 'eval/test/data_provenance.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
