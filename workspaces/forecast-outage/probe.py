"""Read actual public manifests, installed APIs and CPU inference before experiments."""
import json, os, platform, subprocess, inspect, time
from pathlib import Path
import requests

out = Path('workspaces/forecast-outage/evidence/recon')
out.mkdir(parents=True, exist_ok=True)
report = {'platform': platform.platform(), 'python': platform.python_version(), 'cpus': os.cpu_count(), 'run_id': os.getenv('GITHUB_RUN_ID'), 'commit': os.getenv('GITHUB_SHA'), 'errors': []}
(out/'pip-freeze.txt').write_text(subprocess.check_output(['python','-m','pip','freeze'], text=True))

def get(url):
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    return r.json()

try:
    meta = get('https://huggingface.co/api/datasets/thuml/Time-Series-Library')
    report['dataset_repository'] = {'id': meta.get('id'), 'sha': meta.get('sha'), 'cardData': meta.get('cardData'), 'files': [x['rfilename'] for x in meta.get('siblings',[])]}
except Exception as e:
    report['errors'].append({'stage':'dataset_manifest','error':repr(e)})

try:
    import torch
    from chronos import BaseChronosPipeline
    torch.set_num_threads(4)
    report['torch'] = torch.__version__
    report['cuda'] = torch.cuda.is_available()
    report['models'] = []
    for model_id in ['amazon/chronos-bolt-tiny','autogluon/chronos-2-small','autogluon/chronos-2-synth']:
        try:
            meta = get('https://huggingface.co/api/models/'+model_id)
            rec = {'id':model_id,'sha':meta.get('sha'),'cardData':meta.get('cardData'),'files':[x['rfilename'] for x in meta.get('siblings',[])]}
            if model_id == 'amazon/chronos-bolt-tiny':
                t = time.perf_counter()
                pipe = BaseChronosPipeline.from_pretrained(model_id, revision=meta['sha'], device_map='cpu', torch_dtype=torch.float32)
                rec['load_seconds'] = time.perf_counter()-t
                rec['class'] = type(pipe).__name__
                rec['predict_signature'] = str(inspect.signature(pipe.predict))
                rec['quantiles_signature'] = str(inspect.signature(pipe.predict_quantiles))
                x = torch.sin(torch.arange(256).float()/24)[None,:].repeat(4,1)
                x[1,-32:] = float('nan')
                x[2,64:96] = float('nan')
                x[3,::8] = float('nan')
                t = time.perf_counter()
                q, mean = pipe.predict_quantiles(x, prediction_length=24, quantile_levels=[0.1,0.5,0.9])
                rec['inference_seconds'] = time.perf_counter()-t
                rec['quantile_shape'] = list(q.shape)
                rec['mean_shape'] = list(mean.shape)
                rec['finite'] = bool(torch.isfinite(q).all())
                (out/'installed-bolt-predict.txt').write_text(inspect.getsource(type(pipe).predict))
                del pipe
            report['models'].append(rec)
        except Exception as e:
            report['errors'].append({'stage':model_id,'error':repr(e)})
except Exception as e:
    report['errors'].append({'stage':'imports','error':repr(e)})
(out/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2), flush=True)
if report['errors']:
    raise SystemExit('Reconnaissance found errors; inspect report before proceeding.')
