"""E2: fixed selector-training ablations; reuses E0 predictions, never test labels for fitting."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
import sklearn

BASE=Path(__file__).resolve().parent
FEATURES=['missing_rate','age_fraction','max_gap_fraction','missing_recent24','missing_recent72','observed_cv','seasonal_correlation','trend','native_width','disagreement','recent_level_change']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--e0',type=Path,required=True)
    args=ap.parse_args();start=time.perf_counter()
    assert sklearn.__version__=='1.6.1','Reproduction requires the original sklearn version'
    spec=json.loads((BASE/'protocol-E2.json').read_text())
    source_runtime=json.loads((args.e0/'runtime.json').read_text())
    assert source_runtime['commit']==spec['source_code_commit']
    expected=json.loads((args.e0/'SHA256.json').read_text())
    for name in ['scores.csv.gz','replay-scores.csv.gz','runtime.json']:
        assert sha(args.e0/name)==expected[name],f'Input hash mismatch: {name}'
    f=pd.read_csv(args.e0/'scores.csv.gz');r=pd.read_csv(args.e0/'replay-scores.csv.gz')
    X=f[['feature_'+k for k in FEATURES]].to_numpy();test=f.split.eq('test').to_numpy()
    assert test.sum()==14592 and np.isfinite(X).all()
    target=(f.mase_native-f.mase_seasonal_median).to_numpy()
    table=f[test].copy();folds=[];refit_checks=[]
    configurations=[('original','full',list(range(11))),('original','rate',[0]),('original','uncertainty',[8]),
                    ('source_tail','full',list(range(11))),('source_tail','rate',[0]),('source_tail','uncertainty',[8]),
                    ('source_all','full',list(range(11))),('target_tail','full',list(range(11)))]
    for domain in sorted(f.domain.unique()):
        heldout=test&f.domain.eq(domain).to_numpy()
        for regime,features,cols in configurations:
            train=f.split.eq('dev').to_numpy()
            train &= (f.domain.eq(domain) if regime=='target_tail' else f.domain.ne(domain)).to_numpy()
            if regime!='source_all': train &= f.rate.le(.25).to_numpy()
            if regime=='original': train &= f.family.ne('tail').to_numpy()
            assert not (train&test).any() and not (train&heldout).any()
            counts=f[train].groupby(['domain','family','rate']).case_id.transform('count').to_numpy()
            weights=1/counts;weights/=weights.mean()
            model=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=7,min_samples_leaf=40,
                       learning_rate=.05,l2_regularization=10,early_stopping=False,random_state=20260908)
            model.fit(X[train][:,cols],target[train],sample_weight=weights)
            excess=model.predict(X[heldout][:,cols]);choice=excess>0
            name=regime+'_'+features
            table.loc[f.index[heldout],'mase_'+name]=np.where(choice,f.loc[heldout,'mase_seasonal_median'],f.loc[heldout,'mase_native'])
            table.loc[f.index[heldout],'choice_'+name]=np.where(choice,'seasonal_median','native')
            table.loc[f.index[heldout],'predicted_excess_'+name]=excess
            if regime=='original':
                original=f.loc[heldout,'choice_gate_'+features].to_numpy()
                mismatch=int(np.sum(original!=np.where(choice,'seasonal_median','native')))
                refit_checks.append({'domain':domain,'gate':features,'mismatches':mismatch,'cases':int(heldout.sum())})
                assert mismatch==0,'Original gate refit differs; inspect before drawing new conclusions'
            folds.append({'domain':domain,'regime':regime,'features':features,'training_cases':int(train.sum()),
                          'test_cases':int(heldout.sum()),'max_training_rate':float(f.loc[train,'rate'].max()),
                          'training_domains':sorted(f.loc[train,'domain'].unique().tolist()),
                          'training_families':sorted(f.loc[train,'family'].unique().tolist())})
    for name in ['replay_pair','replay_pair_one_se']:
        table['mase_'+name]=table.mase_native
        table['choice_'+name]='native'
    for owner,group in r[r.kind.eq('matched')].groupby('owner'):
        assert len(group)==3 and (group.label_end_exclusive<=group.outage_start).all()
        delta=(group.mae_native-group.mae_seasonal_median).to_numpy()
        mean=float(delta.mean());se=float(delta.std(ddof=1)/np.sqrt(len(delta)))
        for name,switch in [('replay_pair',mean>0),('replay_pair_one_se',mean>se)]:
            if switch:
                table.loc[owner,'mase_'+name]=f.loc[owner,'mase_seasonal_median']
                table.loc[owner,'choice_'+name]='seasonal_median'
    out=BASE/'evidence'/'E2'/args.model;out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/'scores.csv.gz',index=False)
    (out/'folds.json').write_text(json.dumps(folds,indent=2))
    (out/'refit-checks.json').write_text(json.dumps(refit_checks,indent=2))
    (out/'protocol-E2.json').write_text(json.dumps(spec,indent=2))
    (out/'pip-freeze.txt').write_text(subprocess.check_output(['python','-m','pip','freeze'],text=True))
    cols=[c for c in table if c.startswith('mase_')]
    def macro(rows):
        a=rows.groupby(['domain','dataset','series','family','rate'])[cols].mean()
        a=a.groupby(['domain','dataset','family','rate']).mean().groupby(['domain','dataset']).mean().groupby('domain').mean().mean()
        return {k:float(v) for k,v in a.items()}
    summary={'scope':'E2 exploratory, reused test origins, no method novelty claimed','test_cases':len(table),
             'original_gate_refits_exact':True,'original_refit_predictions_checked':sum(x['cases'] for x in refit_checks),
             'tail_test':macro(table[table.family.eq('tail')]),'all_test':macro(table)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    runtime={'model':args.model,'source_run':spec['source_run'],'run_id':os.getenv('GITHUB_RUN_ID'),
             'commit':os.getenv('GITHUB_SHA'),'python':platform.python_version(),'sklearn':sklearn.__version__,
             'new_checkpoint_inference':False,'total_seconds':time.perf_counter()-start,
             'source_scores_sha256':sha(args.e0/'scores.csv.gz'),'code_sha256':sha(__file__),
             'protocol_sha256':sha(BASE/'protocol-E2.json')}
    (out/'runtime.json').write_text(json.dumps(runtime,indent=2))
    (out/'SHA256.json').write_text(json.dumps({p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name not in ['SHA256.json','run.log']},indent=2))
    print('SUMMARY',json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
