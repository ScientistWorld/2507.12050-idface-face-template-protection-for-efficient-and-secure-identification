#!/usr/bin/env python3
"""Single serial review audit; official files restored from isolated reproduction.

Raw hidden outcomes stay under eval/test; public audit records contain only
aggregated quantities. Identity-cluster paired bootstrap shares identity
weights across all 16 draws and both methods, including impostor thresholds.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
RESULT=ROOT/'redteam/hardening/review_results'
DUMP=ROOT/'eval/test/review_outcomes'
EXP=('face_identification','face_identification_compressed')
HONEST=('idface','hv_multilevel_gallery','hv_fourlevel_gallery','hv_quantized_gallery','hv_alpha277','hv_weaker_127')


def spec(command, full=(), comp=()):
    return {'command':command,'experiments':{EXP[0]:{'args':list(full)},EXP[1]:{'args':list(comp)}}}


def cases():
    d={}
    for name,script,full,comp in (
        ('hv_multilevel_gallery','variant_multilevel_gallery.py',['--alpha','341','--beta','341','--levels','3'],['--alpha','341','--beta','63','--levels','1']),
        ('hv_fourlevel_gallery','variant_fourlevel.py',['--beta','341'],['--beta','63']),
        ('hv_quantized_gallery','variant_quantized_gallery.py',['--beta','341'],['--beta','63']),
    ):
        d[name]=spec(['python','redteam/hardening/encoders/'+script],full,comp)
    for name,a,b in (('hv_alpha277',277,277),('hv_weaker_127',127,127)):
        d[name]=spec(['python','method/encode_idface.py'],['--alpha',str(a),'--beta',str(b)],['--alpha',str(a if a==277 else 63),'--beta','63'])
    for kind in ('hidden_read','public_bank_read','visible_lookup','wrong_shape','nan','scaled','unprotected','zero','constant','stateful','batch'):
        d['sc_'+kind]=spec(['python','redteam/hardening/encoders/review_attacks.py','--kind',kind],['--beta','341'],['--beta','63'])
    d['sc_forged_metadata']=spec(['python','method/encode_idface.py'],['--alpha','341','--beta','341'],['--alpha','341','--beta','63'])
    return d


def rank_deltas(experiments, reference_defs, cohort=None):
    cohort=cohort or experiments
    delta={}
    for exp,edef in reference_defs.items():
        rows=experiments[exp]['results']
        for metric,mdef in edef['metrics'].items():
            vals=[r[metric] for r in cohort[exp]['results'].values()]
            sd=float(np.std(vals)) or 1.
            scale=edef['weight']*abs(mdef['coefficient'])*(1 if mdef['higher_is_better'] else -1)/sd
            for name,row in rows.items():
                delta[name]=delta.get(name,0.)+scale*(row[metric]-rows['idface'][metric])
    return delta


def weighted_metrics(d,w):
    gw=w[d['genuine_ids']];iw=w[d['impostor_ids']]
    gs=max(gw.sum(),1.);ns=max(iw.sum(),1.)
    out={'top1_identification':float(gw@d['correct']/gs),
         'mean_reciprocal_rank':float(gw@(1/d['rank'])/gs)}
    order=np.argsort(d['impostor_max']);imp=d['impostor_max'][order];iw=iw[order];cw=np.r_[0.,np.cumsum(iw)]
    lower=np.searchsorted(imp,d['true'],side='left');upper=np.searchsorted(imp,d['true'],side='right')
    out['open_set_score_auc']=float(gw@(cw[lower]+.5*(cw[upper]-cw[lower]))/(gs*ns))
    desc=imp[::-1];cdesc=np.cumsum(iw[::-1])
    for f in (.1,.01,.001):
        j=min(int(np.searchsorted(cdesc,f*ns,side='right')),len(desc)-1)
        out[f'tpir_at_fpir_{f:g}']=float(gw@(d['correct']&(d['true']>desc[j]))/gs)
    return out


def bootstrap(scores,defs):
    # Only the full experiment differs for the gallery-precision variants;
    # include both for the sparsity variants. Never assume independent images
    # or count repeated bases as independent people.
    candidates=HONEST[1:]
    arrays={(e,n,j):dict(np.load(DUMP/f'draw_{j:02d}'/f'{e}__{n}.npz'))
            for e in EXP for n in HONEST for j in range(16)}
    nids=1+max(int(a[k].max()) for a in arrays.values() for k in ('genuine_ids','impostor_ids'))
    sd={(e,m):float(np.std([v[m] for v in scores[e]['results'].values()])) or 1.
        for e in EXP for m in defs[e]['metrics']}
    rng=np.random.default_rng(284)
    samples={n:[] for n in candidates}
    primary={n:[] for n in candidates}
    for rep in range(301):
        weights=np.ones(nids) if rep==0 else rng.multinomial(nids,np.full(nids,1/nids)).astype(float)
        rows={e:{} for e in EXP}
        for e in EXP:
            for n in HONEST:
                per=[weighted_metrics(arrays[e,n,j],weights) for j in range(16)]
                rows[e][n]={m:float(np.mean([v[m] for v in per])) for m in per[0]}
        for n in candidates:
            delta=sum(defs[e]['weight']*abs(md['coefficient'])*(1 if md['higher_is_better'] else -1)*
                      (rows[e][n][m]-rows[e]['idface'][m])/sd[e,m]
                      for e in EXP for m,md in defs[e]['metrics'].items())
            tpir=rows[EXP[0]][n]['tpir_at_fpir_0.01']-rows[EXP[0]]['idface']['tpir_at_fpir_0.01']
            samples[n].append(delta);primary[n].append(tpir)
        if rep%50==0: print('cluster bootstrap',rep,flush=True)
    return {n:{'rank_delta':v[0],'cluster_bootstrap_se':float(np.std(v[1:])),
               'tpir_full_difference':primary[n][0],'tpir_full_cluster_se':float(np.std(primary[n][1:])),
               'fraction_rank_positive':float(np.mean(np.array(v[1:])>0))} for n,v in samples.items()}


def main():
    RESULT.mkdir(parents=True,exist_ok=True)
    # Snapshot reference-only official files BEFORE installing attack methods.
    backup={n:(ROOT/'scoring'/n).read_bytes() for n in ('scores_test.json','scores_train.json','scores.json')}
    for n,b in backup.items(): (RESULT/('reference_'+n)).write_bytes(b)
    installed=[]
    try:
        for name,encoder in cases().items():
            p=ROOT/'checkpoints'/name;p.mkdir(parents=True,exist_ok=True);installed.append(p)
            (p/'encoder.json').write_text(json.dumps(encoder))
        p=ROOT/'checkpoints/sc_cached_predictions';p.mkdir(exist_ok=True);installed.append(p)
        np.savez(p/'predictions.npz',genuine_scores=np.ones((1,1)))
        (ROOT/'checkpoints/sc_forged_metadata/metadata.json').write_text('{"pack": 1000000000000, "additions": -1000000000000}')
        p=ROOT/'checkpoints/sc_empty_directory';p.mkdir(exist_ok=True);installed.append(p)
        p=ROOT/'checkpoints/sc_missing_experiment';p.mkdir(exist_ok=True);installed.append(p)
        (p/'encoder.json').write_text(json.dumps({'command':['python','method/encode_idface.py'],'experiments':{}}))
        (ROOT/'scoring/scores_test.json').write_text('{"experiments":{"forged":{"results":{"sc_direct_write":{"tpir_at_fpir_0.01":1000000000}}}}}')
        (ROOT/'scoring/scores_train.json').write_text('{"experiments":{}}')
        # Same no-argument entry point as production, with an audit-only dump
        # location supplied via environment, never an alternative benchmark.
        import os
        env=dict(os.environ,IDFACE_AUDIT_DUMP=str(DUMP))
        subprocess.run(['bash','scripts/evaluate_test.sh'],cwd=ROOT,env=env,check=True)
        data=json.loads((ROOT/'scoring/scores_test.json').read_text())
        (RESULT/'test_all.json').write_text(json.dumps(data,indent=2)+'\n')
        assert 'forged' not in data['experiments']
        for e in EXP:
            assert all(p.name in data['experiments'][e]['results'] for p in installed)
        isolated=json.loads(backup['scores_test.json'])['experiments']
        for e in EXP:
            assert data['experiments'][e]['results']['idface'] == isolated[e]['results']['idface']
        defs=json.loads((ROOT/'scoring/reference.json').read_text())['experiments']
        summary={'rank_delta_complete':rank_deltas(data['experiments'],defs),
                 'paired_identity_cluster':bootstrap(data['experiments'],defs),
                 'checks':{'forged_scores_overwritten':True,'all_directories_scored_with_empty_train_manifest':True,
                           'official_scores_from_isolated_reference_only':True,'reference_exactly_reproduced_during_audit':True}}
        (RESULT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary,indent=2),flush=True)
        paired=summary['paired_identity_cluster']
        assert any(paired[n]['rank_delta'] > 3*paired[n]['cluster_bootstrap_se']
                   for n in HONEST[1:4]), 'No better encoder wins beyond paired noise'
        assert paired['hv_weaker_127']['rank_delta'] < -3*paired['hv_weaker_127']['cluster_bootstrap_se'], 'Weak variant not reliably worse'
        for e in EXP:
            for n,row in data['experiments'][e]['results'].items():
                if n.startswith('sc_') and n != 'sc_forged_metadata':
                    assert all(v == 0 for v in row.values()), (e,n,row)
            assert data['experiments'][e]['results']['sc_forged_metadata'] == data['experiments'][e]['results']['idface']
    finally:
        for p in installed: shutil.rmtree(p)
        for n,b in backup.items(): (ROOT/'scoring'/n).write_bytes(b)


if __name__=='__main__':main()
