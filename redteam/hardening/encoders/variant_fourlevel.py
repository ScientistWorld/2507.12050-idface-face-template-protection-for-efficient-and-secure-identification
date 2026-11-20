#!/usr/bin/env python3
"""Use spare gallery digit capacity for four magnitude levels.

Fixed histogram: top 32 -> 4, next 96 -> 3, next 160 -> 2, rest -> 1.
Gallery L1=960; at beta=341 the digit bound is 960, still 5/50-bit slot.
Probe and compressed encoders are the reference transformation.
"""
import argparse
import numpy as np
p=argparse.ArgumentParser()
p.add_argument('--role',required=True);p.add_argument('--input',required=True);p.add_argument('--output',required=True)
p.add_argument('--beta',type=int,default=341)
a=p.parse_args();x=np.load(a.input,allow_pickle=False)['templates']
k=341 if a.role=='gallery' else a.beta
if a.role=='gallery' and a.beta==341:
    order=np.argsort(-abs(x),axis=1,kind='stable')
    levels=np.ones(512,dtype=np.int8);levels[:32]=4;levels[32:128]=3;levels[128:288]=2
    z=np.zeros(x.shape,dtype=np.int8);r=np.arange(len(x))[:,None]
    z[r,order]=np.where(x[r,order]>=0,1,-1)*levels
else:
    i=np.argpartition(abs(x),-k,axis=1)[:,-k:]
    z=np.zeros(x.shape,dtype=np.int8);r=np.arange(len(x))[:,None]
    z[r,i]=np.where(x[r,i]>=0,1,-1)
np.savez(a.output,codes=z)
