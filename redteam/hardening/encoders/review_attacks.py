#!/usr/bin/env python3
"""Review attacks: hidden read, public-vector lookup, incomplete & invalid codes."""
import argparse
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--kind',required=True)
p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--role',required=True)
p.add_argument('--beta',type=int,default=341);a=p.parse_args()
x=np.load(a.input,allow_pickle=False)['templates']
k=341 if a.role=='gallery' else a.beta
idx=np.argpartition(abs(x),-k,axis=1)[:,-k:];r=np.arange(len(x))[:,None]
z=np.zeros(x.shape,dtype=np.int8);z[r,idx]=np.where(x[r,idx]>=0,1,-1)
if a.kind=='hidden_read':
    # The original hardened gym explicitly left this major shortcut open.
    with np.load('eval/test/face_embeddings_test.npz',allow_pickle=False) as d:
        names=d['identities']
    z[:]=1
elif a.kind=='visible_lookup':
    # Pure vector lookup, without an honest reference encoder as a fallback.
    d=np.load('data/face_embeddings_dev.npz',allow_pickle=False)
    lookup={row.tobytes():i for i,row in enumerate(d['embeddings'])}
    z[:]=0
    for i,row in enumerate(x):
        if row.tobytes() in lookup:
            j=lookup[row.tobytes()];z[i,j%512]=1
elif a.kind=='public_bank_read':
    # Public labelled held-out embeddings cannot be used during encoding.
    np.load('data/downloads/embeddings/lfw_adaface_ir101.npz',allow_pickle=False)
    z[:]=1
elif a.kind=='wrong_shape': z=z[:0]
elif a.kind=='nan': z=np.full(x.shape,np.nan)
elif a.kind=='scaled': z=z.astype(np.int64)*1000
elif a.kind=='unprotected': z=np.rint(x*4096).astype(np.int64)
elif a.kind=='zero': z[:]=0
elif a.kind=='constant': z[:]=1
elif a.kind=='stateful':
    # Persisting templates to match a later call is denied by the launcher.
    np.save('method/outputs/idface/stolen_gallery.npy',x)
elif a.kind=='batch':
    x=x-x.mean(axis=0,keepdims=True);idx=np.argpartition(abs(x),-k,axis=1)[:,-k:]
    z[:]=0;z[r,idx]=np.where(x[r,idx]>=0,1,-1)
else: raise ValueError(a.kind)
np.savez(a.output,codes=z)
