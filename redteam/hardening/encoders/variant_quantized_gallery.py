#!/usr/bin/env python3
"""More precise gallery quantization using the unused base-1024 digit capacity.

Per template, round scaled coordinates to integers (clip at 6); reduce scale
if L1 would exceed 1023. Query codes and compressed codes stay ternary. Thus
680 additions and five templates per 50-bit slot still suffice in the full
experiment. No benchmark identities, batch statistics or objective search.
"""
import argparse
import numpy as np
p=argparse.ArgumentParser()
p.add_argument('--role',required=True);p.add_argument('--input',required=True);p.add_argument('--output',required=True)
p.add_argument('--beta',type=int,default=341)
a=p.parse_args();x=np.load(a.input,allow_pickle=False)['templates'].astype(np.float64)
if a.role=='gallery' and a.beta==341:
    low=np.zeros(len(x));high=np.full(len(x),52.)
    for _ in range(24):
        mid=(low+high)/2
        z=np.clip(np.rint(x*mid[:,None]),-6,6)
        ok=np.abs(z).sum(axis=1)<=1023
        low=np.where(ok,mid,low);high=np.where(ok,high,mid)
    z=np.clip(np.rint(x*low[:,None]),-6,6).astype(np.int8)
else:
    k=341 if a.role=='gallery' else a.beta
    i=np.argpartition(abs(x),-k,axis=1)[:,-k:];r=np.arange(len(x))[:,None]
    z=np.zeros(x.shape,dtype=np.int8);z[r,i]=np.where(x[r,i]>=0,1,-1)
np.savez(a.output,codes=z)
