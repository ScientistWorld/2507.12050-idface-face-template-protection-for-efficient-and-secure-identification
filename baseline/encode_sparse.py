#!/usr/bin/env python3
"""Paper's sparse (63,63) ablation, expressed independently of the reference."""
import argparse
import numpy as np
p=argparse.ArgumentParser()
p.add_argument('--input',required=True);p.add_argument('--output',required=True)
p.add_argument('--role',required=True)
a=p.parse_args()
x=np.load(a.input,allow_pickle=False)['templates']
i=np.argpartition(abs(x),-63,axis=1)[:,-63:]
z=np.zeros(x.shape,dtype=np.int8);r=np.arange(len(x))[:,None]
z[r,i]=np.where(x[r,i]>=0,1,-1)
np.savez(a.output,codes=z)
