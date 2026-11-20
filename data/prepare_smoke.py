"""Visible real-template input for the independent Paillier correctness check."""
import numpy as np
with np.load('data/face_embeddings_dev.npz',allow_pickle=False) as d:
    x,names,keys=d['embeddings'],d['identities'],d['keys']
ids=np.unique(names)
gallery=[];probes=[]
for name in ids:
    rows=np.flatnonzero(names==name)
    if len(np.unique(keys[rows]))>=2:
        gallery.append(rows[0]);probes.append(rows[keys[rows]!=keys[rows[0]]][0])
    if len(gallery)==8:break
impostor=np.flatnonzero(~np.isin(names,names[gallery]))[:4]
np.savez('data/paillier_dev.npz',gallery=x[gallery],gallery_labels=np.arange(8),
         genuine_queries=x[probes],genuine_labels=np.arange(8),impostor_queries=x[impostor])
