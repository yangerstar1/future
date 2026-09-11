"""Read only the authorized repository's known flight jobs for budget accounting.
No secrets are logged, no billing guarantee is inferred, no jobs are dispatched.
This extends the existing RUN-LEDGER rather than inventing a second budget.
"""
import os,json,urllib.request,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['FLIGHT_COST_OUT']);OUT.mkdir(parents=True,exist_ok=True)
assert os.environ['GITHUB_REPOSITORY']=='yangerstar1/future'
TOKEN=os.environ['GH_TOKEN'];API='https://api.github.com/repos/yangerstar1/future'
previous=json.loads((ROOT/'RUN-LEDGER.json').read_text());rows=list(previous['runs'])
known=[34554600564,34554894554,34555726820,34556197487,34556576832,34557409694,34558225183,34559187757]
if os.environ.get('INCLUDE_CURRENT_RUN')=='1':known.append(int(os.environ['GITHUB_RUN_ID']))
existing={r.get('job_id') for r in rows};pending=[]
def get(path):
 req=urllib.request.Request(API+path,headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'skyfold-budget-audit'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def dt(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
for run in known:
 payload=get('/actions/runs/%d/jobs?per_page=100&filter=all'%run)
 assert payload['total_count']<=100,'Unexpected pagination; stop incomplete accounting'
 for j in payload['jobs']:
  if j['id'] in existing:continue
  if j['status']!='completed':pending.append({'run_id':run,'job_id':j['id'],'name':j['name'],'status':j['status'],'started_at':j['started_at']});continue
  seconds=(dt(j['completed_at'])-dt(j['started_at'])).total_seconds();assert seconds>=0
  rows.append({'run_id':run,'job_id':j['id'],'stage':j.get('workflow_name','')+' / '+j['name'],'source_sha':j['head_sha'],'started_at':j['started_at'],'completed_at':j['completed_at'],'seconds':seconds,'conclusion':j['conclusion'],'attempt':j.get('run_attempt',1)})
  existing.add(j['id'])
seconds=sum(r['seconds'] for r in rows)
sample=float(os.environ.get('FLIGHT_SAMPLE_SECONDS','0'));planned=192*sample*1.5+3600 if sample else 0
report={**previous,'runs':rows,'total_job_seconds':seconds,'runner_hours':seconds/3600,'remaining_ceiling_hours':48-seconds/3600,'job_count':len(rows),'run_count':len({r['run_id'] for r in rows}),'active_jobs_at_measurement':pending,'active_runs':sorted({r['run_id'] for r in pending}),'measured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planned_additional_seconds':planned,'planning_note':'1.5x the measured representative 1080p frame plus one hour for stills, tools, QA and retry. Not a statistical percentile or a core G4 quality pass.','paid_runners_or_model_APIs_started':False,'account_wide_storage_billing':'NOT_EXPOSED','measurement':'GitHub job timestamps, including failed jobs; not billing or chat wall-clock time'}
(OUT/'RUN-LEDGER.json').write_text(json.dumps(report,indent=2))
if sample:
 assert not pending,'Unexpected active older jobs: do not exceed two-job ceiling'
 assert seconds+planned<(48-9.6)*3600,'Insufficient budget after closing reserve'
print(json.dumps({k:report[k] for k in ['total_job_seconds','runner_hours','planned_additional_seconds','active_jobs_at_measurement']},indent=2))
