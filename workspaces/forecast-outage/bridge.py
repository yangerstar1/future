"""E1: horizon-aligned forecasting across a trailing outage; no fitted wrapper."""
from __future__ import annotations
import argparse, inspect, json, os, platform, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd
from experiment import infer, digest

BASE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--e0',type=Path,required=True)
    args=ap.parse_args()
    cfg=json.loads((BASE/'protocol-E0.json').read_text());ext=json.loads((BASE/'protocol-E1.json').read_text())
    spec=cfg['models'][args.model];L,H=cfg['context'],cfg['horizon']
    cases=pd.read_csv(args.e0/'cases.csv.gz')
    cases=cases[cases.split.eq('test')&cases.family.eq('tail')].copy()
    cases['e0_index']=cases.index
    cases=cases.reset_index(drop=True)
    archive=np.load(args.e0/'selected-series.npz',allow_pickle=False)
    mapping=json.loads(str(archive['mapping_json']))
    arrays={(str(m['dataset']),str(m['series'])):archive[m['key']] for m in mapping}
    out=BASE/'evidence'/'E1'/args.model;out.mkdir(parents=True,exist_ok=True)
    (out/'protocol-E1.json').write_text(json.dumps(ext,indent=2))
    (out/'pip-freeze.txt').write_text(subprocess.check_output(['python','-m','pip','freeze'],text=True))
    # Index-only unit test: a forecast starts at the first missing sample, not the outer origin.
    for k in [42,84,168]:
        outer=1000;predicted_times=np.arange(outer-k,outer+H)
        assert np.array_equal(predicted_times[k:k+H],np.arange(outer,outer+H))
    import torch
    from chronos import BaseChronosPipeline
    torch.set_num_threads(4);torch.manual_seed(cfg['seed'])
    assert not torch.cuda.is_available()
    start=time.perf_counter()
    pipe=BaseChronosPipeline.from_pretrained(spec['id'],revision=spec['revision'],device_map='cpu',torch_dtype=torch.float32)
    runtime={'model':spec,'class':type(pipe).__name__,'run_id':os.getenv('GITHUB_RUN_ID'),
             'commit':os.getenv('GITHUB_SHA'),'source_run':ext['source_run'],'python':platform.python_version(),
             'torch':torch.__version__,'cpus':os.cpu_count(),'cuda':False,'load_seconds':time.perf_counter()-start,
             'code_sha256':digest(Path(__file__).read_bytes()),'helper_sha256':digest((BASE/'experiment.py').read_bytes()),
             'source_cases_sha256':digest((args.e0/'cases.csv.gz').read_bytes()),
             'source_selected_series_sha256':digest((args.e0/'selected-series.npz').read_bytes()),'by_gap':[]}
    (out/'installed-predict-quantiles.py').write_text(inspect.getsource(type(pipe).predict_quantiles))
    (out/'installed-predict.py').write_text(inspect.getsource(type(pipe).predict))
    n=len(cases);qb=np.empty((n,H,3),np.float32);qc=qb.copy();truth=np.empty((n,H),np.float32)
    cases['input_sha256']='';cases['input_end_exclusive']=0;cases['bridge_horizon']=0
    for rate,group in cases.groupby('rate',sort=True):
        k=round(float(rate)*L);xs=[];ys=[]
        for i,row in group.iterrows():
            values=arrays[(str(row.dataset),str(row.series))];origin=int(row.origin)
            x=values[origin-L:origin-k].copy()
            assert len(x)==L-k and np.isfinite(x).all()
            xs.append(x);ys.append(values[origin:origin+H])
            cases.loc[i,'input_sha256']=digest(x.tobytes())
            cases.loc[i,'input_end_exclusive']=origin-k
            cases.loc[i,'bridge_horizon']=k+H
        X=np.asarray(xs,dtype=np.float32)
        t=time.perf_counter();full=infer(pipe,X,k+H,ext['budget']['batch_size']);bridge_seconds=time.perf_counter()-t
        assert full.shape==(len(group),k+H,3)
        qb[group.index]=full[:,k:k+H]
        np.savez_compressed(out/f'full-bridge-gap-{k}.npz',quantiles=full,case_id=group.case_id.to_numpy(dtype='U24'),gap=k)
        t=time.perf_counter();qc[group.index]=infer(pipe,X,H,ext['budget']['batch_size']);blind_seconds=time.perf_counter()-t
        truth[group.index]=np.asarray(ys)
        runtime['by_gap'].append({'gap':k,'input_length':L-k,'full_forecast_length':k+H,'cases':len(group),
                                  'bridge_seconds':bridge_seconds,'clock_blind_seconds':blind_seconds})
    scale=cases.scale.to_numpy()
    for name,q in [('bridge',qb),('clock_blind_control',qc)]:
        cases['mase_'+name]=np.abs(q[:,:,1]-truth).mean(1)/scale
        cases['coverage80_'+name]=((truth>=q[:,:,0])&(truth<=q[:,:,2])).mean(1)
        cases['width80_scaled_'+name]=(q[:,:,2]-q[:,:,0]).mean(1)/scale
    np.savez_compressed(out/'predictions.npz',bridge=qb,clock_blind_control=qc,targets=truth,case_id=cases.case_id.to_numpy(dtype='U24'))
    cases.to_csv(out/'scores.csv.gz',index=False)
    metrics=[c for c in cases if c.startswith(('mase_','coverage80_','width80_scaled_'))]
    ds=cases.groupby(['domain','dataset','series','rate'])[metrics].mean().groupby(['domain','dataset','rate']).mean().groupby(['domain','dataset']).mean()
    ds.reset_index().to_csv(out/'dataset-metrics.csv',index=False)
    macro=ds.groupby('domain').mean().mean()
    summary={'scope':'E1 exploratory extension; reused E0 test origins; not confirmatory','cases':n,
             'method_is_novel':False,'no_hidden_outage_values_in_inputs':True,'no_extended_history':True,
             'macro':{k:float(v) for k,v in macro.items()}}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    runtime['total_seconds']=time.perf_counter()-start
    (out/'runtime.json').write_text(json.dumps(runtime,indent=2))
    hashes={p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.name not in ['SHA256.json','run.log']}
    (out/'SHA256.json').write_text(json.dumps(hashes,indent=2))
    print('SUMMARY',json.dumps(summary,indent=2));print('RUNTIME',json.dumps(runtime,indent=2))

if __name__=='__main__':main()
