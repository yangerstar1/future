"""E0: CPU-only, timestamp-preserving outage/fallback experiment.

All methods consume observed histories only. 'oracle' is a labelled diagnostic,
never a deployable predictor. See protocol-E0.json for frozen study parameters.
"""
from __future__ import annotations
import argparse, hashlib, inspect, json, os, platform, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
FEATURES = ['missing_rate','age_fraction','max_gap_fraction','missing_recent24',
            'missing_recent72','observed_cv','seasonal_correlation','trend',
            'native_width','disagreement','recent_level_change']

def digest(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()

def stable_seed(text: str) -> int:
    return int(digest(text.encode())[:8],16)

def missing_mask(n: int, family: str, rate: float, seed: int) -> np.ndarray:
    mask = np.zeros(n,dtype=bool)
    k = round(n*rate)
    if family == 'random':
        mask[np.random.default_rng(seed).choice(n,k,replace=False)] = True
    elif family == 'middle':
        left = (n-k)//2
        mask[left:left+k] = True
    elif family == 'tail' and k:
        mask[-k:] = True
    elif family != 'clean':
        raise ValueError(family)
    assert int(mask.sum()) == (0 if family == 'clean' else k)
    return mask

def baselines(x: np.ndarray, h: int, period: int) -> np.ndarray:
    """Persistence, calendar-aligned last observed phase, phase median."""
    observed = np.flatnonzero(np.isfinite(x))
    if not len(observed):
        raise ValueError('No observed context')
    last = float(x[observed[-1]])
    result = np.full((h,3),last,dtype=np.float32)
    for t in range(h):
        phase = (len(x)+t)%period
        v = x[np.arange(len(x))%period == phase]
        v = v[np.isfinite(v)]
        if len(v):
            result[t,1] = v[-1]
            result[t,2] = np.median(v)
    return result

def phase_fill(x: np.ndarray, period: int) -> np.ndarray:
    """Only observations already available at the forecast origin are used."""
    z = x.copy()
    default = np.nanmedian(x)
    for p in range(period):
        indices = np.arange(p,len(x),period)
        v = x[indices]
        good = np.isfinite(v)
        fill = np.median(v[good]) if good.any() else default
        z[indices[~good]] = fill
    assert np.isfinite(z).all()
    return z

def basic_features(x: np.ndarray, period: int) -> list[float]:
    good = np.isfinite(x)
    pos = np.flatnonzero(good)
    gaps = np.diff(np.r_[-1,pos,len(x)])-1
    vals = x[good].astype(float)
    sd = max(float(np.std(vals)),1e-8)
    paired = good[period:] & good[:-period]
    corr = 0.
    if paired.sum()>2:
        a,b = x[period:][paired],x[:-period][paired]
        if np.std(a)>1e-8 and np.std(b)>1e-8:
            corr = float(np.corrcoef(a,b)[0,1])
    first,last = np.array_split(x,2)
    trend = (np.nanmean(last)-np.nanmean(first))/sd if np.isfinite(first).any() and np.isfinite(last).any() else 0.
    recent = x[-period:]
    level = (np.nanmean(recent)-np.nanmean(x))/sd if np.isfinite(recent).any() else 0.
    return [float((~good).mean()),float((len(x)-1-pos[-1])/len(x)),
            float(gaps.max()/len(x)),float((~good[-24:]).mean()),
            float((~good[-72:]).mean()),sd/(abs(float(np.mean(vals)))+sd),
            corr,float(trend),float(level),sd]

def self_test() -> None:
    n,p,h = 336,24,24
    y = np.arange(n,dtype=np.float32)%p
    for family in ['random','middle','tail']:
        m=missing_mask(n,family,.25,17)
        assert m.sum()==84
        x=y.copy();x[m]=np.nan
        b=baselines(x,h,p)
        assert np.allclose(b[:,1:],(np.arange(n,n+h)%p)[:,None])
        assert np.isfinite(phase_fill(x,p)).all()
        assert np.isfinite(basic_features(x,p)).all()
    # Timestamp preservation: deleting NaNs would incorrectly rotate this phase.
    x=y.copy();x[-42:]=np.nan
    assert np.allclose(baselines(x,h,p)[:,1],np.arange(h)%p)
    # A forecast function cannot see or depend on future targets.
    a=np.r_[x,np.full(h,1.)]; b=np.r_[x,np.full(h,1e12)]
    assert np.array_equal(baselines(a[:n],h,p),baselines(b[:n],h,p))
    assert np.array_equal(missing_mask(n,'random',.25,1),missing_mask(n,'random',.25,1))
    assert not np.array_equal(missing_mask(n,'random',.25,1),missing_mask(n,'random',.25,2))
    print('SELF_TEST_PASS: exact mask counts, calendar alignment, causality, finite baselines, deterministic masks',flush=True)

def acquire(cfg: dict, out: Path) -> tuple[list[dict],list[dict]]:
    from huggingface_hub import hf_hub_download
    series, manifests = [],[]
    for d in cfg['datasets']:
        path=Path(hf_hub_download(cfg['dataset_repo'],d['path'],repo_type='dataset',revision=cfg['dataset_revision']))
        raw=pd.read_csv(path)
        original_rows=len(raw)
        duplicate_rows=int(raw.duplicated().sum())
        # Audit found one exactly duplicated weather record, not distinct readings.
        raw=raw.drop_duplicates().reset_index(drop=True)
        date_col=raw.columns[0]
        dates=pd.to_datetime(raw[date_col],dayfirst=('.' in str(raw[date_col].iloc[0])),format='mixed',errors='raise')
        if dates.duplicated().any() or not dates.is_monotonic_increasing:
            raise ValueError(f'{d["name"]}: timestamps not unique/increasing')
        frame=raw.drop(columns=date_col).apply(pd.to_numeric,errors='raise')
        frame.index=dates
        if d['name']=='weather':
            frame=frame.replace(-9999,np.nan)
        median_step=frame.index.to_series().diff().median()
        if median_step < pd.Timedelta(hours=1):
            frame=frame.resample('1h',label='right',closed='right').mean()
        elif median_step != pd.Timedelta(hours=1):
            raise ValueError(f'{d["name"]}: expected hourly/subhourly data, got {median_step}')
        expected=pd.date_range(frame.index[0],frame.index[-1],freq='1h')
        frame=frame.reindex(expected)
        n=len(frame); cutoff=int(.4*n)
        eligible=[]
        for col in frame:
            values=frame[col].to_numpy(dtype=np.float32)
            old=values[:cutoff]
            delta=np.abs(old[cfg['period']:]-old[:-cfg['period']])
            scale=float(np.nanmean(delta))
            if np.isfinite(old).mean()>=.95 and np.isfinite(scale) and scale>1e-8:
                eligible.append((col,values,scale))
        eligible.sort(key=lambda v:digest(f'{d["name"]}/{v[0]}/{cfg["seed"]}'.encode()))
        selected=eligible[:cfg['max_series']]
        if not selected:
            raise ValueError(f'No eligible series: {d["name"]}')
        rec={'dataset':d['name'],'domain':d['domain'],'path':d['path'],'sha256':digest(path.read_bytes()),
             'revision':cfg['dataset_revision'],'raw_rows':original_rows,'exact_duplicate_rows_removed':duplicate_rows,'hourly_rows':n,'columns_total':len(frame.columns),
             'columns_eligible':len(eligible),'selected_columns':[v[0] for v in selected],
             'start':str(frame.index[0]),'end':str(frame.index[-1]),'scale_prefix_end':str(frame.index[cutoff-1]),
             'source_step':str(median_step)}
        manifests.append(rec)
        for col,values,scale in selected:
            series.append({'dataset':d['name'],'domain':d['domain'],'series':str(col),'values':values,'scale':scale,
                           'dates':frame.index})
        print('DATA',json.dumps(rec),flush=True)
    (out/'data-manifest.json').write_text(json.dumps(manifests,indent=2))
    archive={}
    mapping=[]
    for i,item in enumerate(series):
        key=f's{i:03d}'
        archive[key]=item['values']
        archive[key+'_timestamps']=item['dates'].asi8
        mapping.append({k:item[k] for k in ['dataset','domain','series','scale']} | {'key':key})
    archive['mapping_json']=np.asarray(json.dumps(mapping))
    np.savez_compressed(out/'selected-series.npz',**archive)
    return series,manifests

def prepare(cfg: dict, series: list[dict], out: Path):
    L,H,P=cfg['context'],cfg['horizon'],cfg['period']
    conditions=[('clean',0.,0)]+[(f,r,s) for f in ['random','middle','tail'] for r in cfg['rates']
                                      for s in (cfg['mask_seeds'] if f=='random' else [0])]
    X,Y,B,F,M=[],[],[],[],[]
    RX,RY,RB,RM=[],[],[],[]
    exclusions=[]
    for item in series:
        values=item['values']; n=len(values)
        for split,left,right,count in [('dev',.50,.70,cfg['dev_origins']),('test',.80,1.,cfg['test_origins'])]:
            origins=np.linspace(int(left*n),int(right*n)-H,count,dtype=int)
            assert np.min(np.diff(origins))>=H
            for oi,origin in enumerate(origins):
                clean=values[origin-L:origin]; truth=values[origin:origin+H]
                if not (np.isfinite(clean).all() and np.isfinite(truth).all()):
                    exclusions.append({'dataset':item['dataset'],'series':item['series'],'origin':int(origin),'split':split,'reason':'original_missingness'})
                    continue
                for family,rate,mask_seed in conditions:
                    key=f'{item["dataset"]}/{item["series"]}/{origin}/{family}/{rate}/{mask_seed}'
                    mask=missing_mask(L,family,rate,stable_seed(key))
                    x=clean.copy();x[mask]=np.nan
                    owner=len(M)
                    X.append(x);Y.append(truth);B.append(baselines(x,H,P));F.append(basic_features(x,P))
                    M.append({'case_id':digest(key.encode())[:24],'dataset':item['dataset'],'domain':item['domain'],
                              'series':item['series'],'origin':int(origin),'origin_index':oi,'timestamp':str(item['dates'][origin]),
                              'split':split,'family':family,'rate':rate,'mask_seed':mask_seed,'scale':item['scale']})
                    if split=='test' and family=='tail':
                        gap=int(mask.sum()); anchor=origin-gap
                        for j in range(cfg['replay_windows']):
                            t=anchor-H*(j+1)
                            assert t+H<=anchor<=origin
                            historical=values[t-L:t].copy(); known=values[t:t+H].copy()
                            # All replay labels precede the outage and are observable.
                            if not (np.isfinite(historical).all() and np.isfinite(known).all()):
                                raise ValueError('Replay has original missingness; do not substitute hidden labels')
                            for kind in ['clean','matched']:
                                rx=historical.copy()
                                if kind=='matched':rx[mask]=np.nan
                                RX.append(rx);RY.append(known);RB.append(baselines(rx,H,P))
                                RM.append({'owner':owner,'kind':kind,'inner_origin':int(t),'label_end_exclusive':int(t+H),
                                           'outage_start':int(anchor),'replay_index':j})
    meta=pd.DataFrame(M);meta.to_csv(out/'cases.csv.gz',index=False)
    (out/'exclusions.json').write_text(json.dumps(exclusions,indent=2))
    assert meta.case_id.is_unique
    assert set(meta.domain)==set(d['domain'] for d in cfg['datasets'])
    print('CASES',len(meta),'REPLAYS',len(RM),'EXCLUSIONS',len(exclusions),flush=True)
    return (np.asarray(X),np.asarray(Y),np.asarray(B),np.asarray(F),meta,
            np.asarray(RX),np.asarray(RY),np.asarray(RB),pd.DataFrame(RM))

def quantiles_array(q) -> np.ndarray:
    import torch
    if isinstance(q,list):
        q=torch.cat([v if v.ndim==3 else v.unsqueeze(0) for v in q],dim=0)
    z=q.detach().float().cpu().numpy()
    if z.ndim!=3 or z.shape[-1]!=3:
        raise ValueError(f'Unexpected official quantile API shape: {z.shape}')
    if not np.isfinite(z).all():
        raise ValueError('Non-finite model output; do not silently drop cases')
    return z

def infer(pipe,X:np.ndarray,h:int,batch:int) -> np.ndarray:
    import torch
    chunks=[];start=time.perf_counter()
    for lo in range(0,len(X),batch):
        with torch.inference_mode():
            inputs=torch.from_numpy(X[lo:lo+batch])
            if type(pipe).__name__=='Chronos2Pipeline':
                inputs=inputs.unsqueeze(1)  # explicit independent univariate groups
            q,_=pipe.predict_quantiles(inputs,prediction_length=h,quantile_levels=[.1,.5,.9])
        chunks.append(quantiles_array(q))
        if lo%(batch*100)==0: print('INFERENCE',lo,'/',len(X),'seconds',round(time.perf_counter()-start,2),flush=True)
    return np.concatenate(chunks)

def analyse(cfg,meta,X,Y,B,F,Q,Qfill,RQ,RY,RB,RM,out):
    from sklearn.ensemble import HistGradientBoostingRegressor
    scale=meta.scale.to_numpy(); n=len(meta)
    point=Q[:,:,1]; repaired=Qfill[:,:,1]
    preds={'native':point,'phase_filled':repaired,'persistence':B[:,:,0],
           'seasonal_last':B[:,:,1],'seasonal_median':B[:,:,2],
           'equal_ensemble':.5*(point+B[:,:,2])}
    losses={k:np.mean(np.abs(v-Y),axis=1)/scale for k,v in preds.items()}
    table=meta.copy()
    for k,v in losses.items():table['mase_'+k]=v
    table['coverage80']=np.mean((Y>=Q[:,:,0])&(Y<=Q[:,:,2]),axis=1)
    table['width80_scaled']=np.mean(Q[:,:,2]-Q[:,:,0],axis=1)/scale
    table['quantile_crossing']=np.any(np.diff(Q,axis=2)<-1e-6,axis=(1,2))
    features=np.column_stack([F[:,:8],np.mean(Q[:,:,2]-Q[:,:,0],axis=1)/F[:,9],
                              np.mean(np.abs(point-B[:,:,2]),axis=1)/F[:,9],F[:,8]])
    assert np.isfinite(features).all()
    for k,col in enumerate(FEATURES):table['feature_'+col]=features[:,k]
    target=losses['native']-losses['seasonal_median']
    folds=[]
    for col in ['gate_rate','gate_uncertainty','gate_full','source_best_fixed']:
        table['mase_'+col]=np.nan
        table['choice_'+col]='unassigned'
    for domain in sorted(meta.domain.unique()):
        # No held-out domain labels, no source test labels, no tail outages or 50% masks.
        train=(meta.split.eq('dev')&meta.domain.ne(domain)&meta.family.ne('tail')&meta.rate.le(.25)).to_numpy()
        test=(meta.split.eq('test')&meta.domain.eq(domain)).to_numpy()
        assert not np.any(train&test)
        counts=meta.loc[train].groupby(['domain','family','rate']).case_id.transform('count').to_numpy()
        weights=1/counts;weights=weights/weights.mean()
        fold={'held_out_domain':domain,'train_cases':int(train.sum()),'test_cases':int(test.sum()),'train_families':sorted(meta.loc[train,'family'].unique().tolist())}
        for name,cols in [('gate_rate',[0]),('gate_uncertainty',[8]),('gate_full',list(range(len(FEATURES))))]:
            model=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=7,min_samples_leaf=40,
                        learning_rate=.05,l2_regularization=10,early_stopping=False,random_state=cfg['seed'])
            model.fit(features[train][:,cols],target[train],sample_weight=weights)
            choice=model.predict(features[test][:,cols])>0
            table.loc[test,'mase_'+name]=np.where(choice,losses['seasonal_median'][test],losses['native'][test])
            table.loc[test,'choice_'+name]=np.where(choice,'seasonal_median','native')
        best=min(losses,key=lambda name:np.average(losses[name][train],weights=weights))
        table.loc[test,'mase_source_best_fixed']=losses[best][test]
        table.loc[test,'choice_source_best_fixed']=best
        fold['source_best_fixed']=best;folds.append(fold)
    table['mase_oracle_pair']=np.minimum(losses['native'],losses['seasonal_median'])
    # Replay uses only historical labels before the currently observed tail outage.
    replay_mae=np.column_stack([np.abs(RQ[:,:,1]-RY).mean(axis=1),np.abs(RB-RY[:,:,None]).mean(axis=1)])
    rnames=['native','persistence','seasonal_last','seasonal_median']
    for k in rnames:RM['mae_'+k]=replay_mae[:,rnames.index(k)]
    for kind in ['clean','matched']:
        name='replay_'+kind
        table['mase_'+name]=losses['native']
        table['choice_'+name]='native'
        grouped=RM[RM.kind.eq(kind)].groupby('owner')[[f'mae_{k}' for k in rnames]].mean()
        for owner,row in grouped.iterrows():
            chosen=rnames[int(np.argmin(row.to_numpy()))]
            table.loc[owner,'mase_'+name]=losses[chosen][owner]
            table.loc[owner,'choice_'+name]=chosen
    table.to_csv(out/'scores.csv.gz',index=False);RM.to_csv(out/'replay-scores.csv.gz',index=False)
    (out/'selector-folds.json').write_text(json.dumps(folds,indent=2))
    cols=[c for c in table if c.startswith('mase_')]+['coverage80','width80_scaled','quantile_crossing']
    per=table[table.split.eq('test')].groupby(['dataset','domain','family','rate'])[cols].mean().reset_index()
    per.to_csv(out/'metrics.csv',index=False)
    # Aggregate conditions equally, series equally, datasets within domain equally.
    test=table[table.split.eq('test')]
    def macro(rows):
        a=rows.groupby(['domain','dataset','series','family','rate'])[cols].mean()
        a=a.groupby(['domain','dataset','family','rate']).mean().groupby(['domain','dataset']).mean().groupby('domain').mean().mean()
        return {k:float(v) for k,v in a.items()}
    summary={'scope':'E0 exploratory; not a confirmatory publication result','cases':n,'test_cases':len(test),
             'base_forecast_windows':int(len(test.groupby(['dataset','series','origin']))),
             'domains':sorted(meta.domain.unique().tolist()),'datasets':sorted(meta.dataset.unique().tolist()),
             'series':int(len(meta.groupby(['dataset','series']))),'all_test':macro(test),
             'tail_test':macro(test[test.family.eq('tail')]),'clean_test':macro(test[test.family.eq('clean')]),
             'seed':cfg['seed'],'no_test_domain_labels_in_gates':True,
             'replay_label_end_le_outage_start':bool((RM.label_end_exclusive<=RM.outage_start).all()),
             'bootstrap_status':'pending independent paired-block analysis','novelty_status':'not established',
             'publication_ready':False}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    print('SUMMARY',json.dumps(summary,indent=2),flush=True)
    return table,summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',required=False);parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args();self_test()
    if args.self_test:return
    cfg=json.loads((BASE/'protocol-E0.json').read_text());model_spec=cfg['models'][args.model]
    out=BASE/'evidence'/'E0'/args.model;out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    (out/'protocol-E0.json').write_text(json.dumps(cfg,indent=2))
    (out/'pip-freeze.txt').write_text(subprocess.check_output(['python','-m','pip','freeze'],text=True))
    series,manifests=acquire(cfg,out)
    X,Y,B,F,meta,RX,RY,RB,RM=prepare(cfg,series,out)
    import torch
    from chronos import BaseChronosPipeline
    torch.set_num_threads(4);torch.manual_seed(cfg['seed'])
    assert not torch.cuda.is_available(),'Protocol expects CPU only'
    t=time.perf_counter()
    pipe=BaseChronosPipeline.from_pretrained(model_spec['id'],revision=model_spec['revision'],device_map='cpu',torch_dtype=torch.float32)
    runtime={'model':model_spec,'class':type(pipe).__name__,'load_seconds':time.perf_counter()-t,
             'quantile_signature':str(inspect.signature(pipe.predict_quantiles)),
             'python':platform.python_version(),'torch':torch.__version__,'cpus':os.cpu_count(),'cuda':False,
             'commit':os.getenv('GITHUB_SHA'),'run_id':os.getenv('GITHUB_RUN_ID'),
             'code_sha256':digest(Path(__file__).read_bytes()),'protocol_sha256':digest((BASE/'protocol-E0.json').read_bytes())}
    (out/'runtime.json').write_text(json.dumps(runtime,indent=2))
    # Guard against accidental cross-series learning/leakage in a batched API.
    probe=np.stack([X[0],X[len(X)//2],X[-1]])
    qa=infer(pipe,probe,cfg['horizon'],3)[0]
    qb=infer(pipe,probe[:1],cfg['horizon'],1)[0]
    maxdiff=float(np.max(np.abs(qa-qb)));runtime['batch_invariance_maxdiff']=maxdiff
    assert np.allclose(qa,qb,rtol=2e-4,atol=2e-4),'Batch dependence: inspect model API before continuing'
    t=time.perf_counter();Q=infer(pipe,X,cfg['horizon'],cfg['batch_size']);runtime['native_seconds']=time.perf_counter()-t
    filled=np.stack([phase_fill(x,cfg['period']) for x in X])
    t=time.perf_counter();Qfill=infer(pipe,filled,cfg['horizon'],cfg['batch_size']);runtime['filled_seconds']=time.perf_counter()-t
    t=time.perf_counter();RQ=infer(pipe,RX,cfg['horizon'],cfg['batch_size']);runtime['replay_seconds']=time.perf_counter()-t
    np.savez_compressed(out/'predictions.npz',native=Q,phase_filled=Qfill,baseline=B,targets=Y,
                        mask_packed=np.packbits(~np.isfinite(X),axis=1),case_id=meta.case_id.to_numpy(dtype='U24'))
    np.savez_compressed(out/'replay-predictions.npz',native=RQ,baseline=RB,targets=RY)
    table,summary=analyse(cfg,meta,X,Y,B,F,Q,Qfill,RQ,RY,RB,RM,out)
    runtime['total_seconds']=time.perf_counter()-start
    runtime['forecast_calls_in_windows']=int(2*len(X)+len(RX)+4)
    (out/'runtime.json').write_text(json.dumps(runtime,indent=2))
    hashes={p.name:digest(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ['SHA256.json','run.log']}
    (out/'SHA256.json').write_text(json.dumps(hashes,indent=2))
    print('COMPLETED',json.dumps(runtime,indent=2),flush=True)

if __name__=='__main__':main()
