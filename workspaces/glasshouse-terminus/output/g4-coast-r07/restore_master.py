"""Lossless transport for a native .blend exceeding the repository single-file cap.
No resampling, decimation, Blender save, data mutation or remote upload outside
this project's existing data-only evidence publisher. Artifact keeps full .blend.
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
NAME='g4-full-scene-candidate.blend';CHUNK=53000000

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def prepare(root):
 master=root/NAME;parts=[]
 with master.open('rb') as f:
  i=0
  while True:
   b=f.read(CHUNK)
   if not b:break
   parts.append({'file':f'master-parts/{NAME}.part-{i:03d}','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});i+=1
 meta={'master':NAME,'bytes':master.stat().st_size,'sha256':digest(master),'parts':parts,'transport':'Persistent Git evidence stores lossless parts. Downloaded Actions artifact contains the original complete .blend instead. Restore before validating the canonical DELIVERY manifest.','changes_to_model_bytes':False}
 (root/'MASTER-PARTS.json').write_text(json.dumps(meta,indent=2))
 source=Path(__file__).resolve();target=root/'restore_master.py'
 if source!=target.resolve():shutil.copy2(source,target)
 (root/'MASTER-RESTORE.txt').write_text('This is the actual full-detail Blender master, not an image or LOD substitute.\nActions ZIP: open g4-full-scene-candidate.blend directly.\nGit evidence archive: run python3 restore_master.py restore . in this output directory.\nThe script validates every part and the final SHA-256, without changing the model.\n')
 return meta

def restore(root):
 q=json.loads((root/'MASTER-PARTS.json').read_text());master=root/q['master'];assert master.parent==root and q['master']==NAME
 if master.exists():assert digest(master)==q['sha256'];return
 tmp=root/(NAME+'.restoring')
 assert not tmp.exists(),'Do not overwrite interrupted reconstruction without inspection'
 try:
  with tmp.open('wb') as f:
   for r in q['parts']:
    p=(root/r['file']).resolve();assert p.is_relative_to(root) and p.is_file()
    assert p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],r['file']
    with p.open('rb') as source:shutil.copyfileobj(source,f,1048576)
  assert tmp.stat().st_size==q['bytes'] and digest(tmp)==q['sha256']
  os.replace(tmp,master)
 except BaseException:
  tmp.unlink(missing_ok=True);raise

def publish(root,stage):
 q=prepare(root);base=Path.cwd().resolve();relative=root.relative_to(base);assert str(relative).startswith('workspaces/glasshouse-terminus/output/')
 master=root/NAME;folder=root/'master-parts';assert not folder.exists(),'Do not overwrite transport parts'
 stash=Path(os.environ['RUNNER_TEMP'])/(stage+'-'+os.environ['GITHUB_RUN_ID']+'-'+NAME);assert not stash.exists()
 os.replace(master,stash);folder.mkdir()
 try:
  with stash.open('rb') as f:
   for r in q['parts']:
    b=f.read(r['bytes']);assert hashlib.sha256(b).hexdigest()==r['sha256'];(root/r['file']).write_bytes(b)
  subprocess.run(['bash','workspaces/glasshouse-terminus/publish_evidence.sh',str(relative),stage],check=True)
 finally:
  os.replace(stash,master);shutil.rmtree(folder)
 assert digest(master)==q['sha256']

if __name__=='__main__':
 assert len(sys.argv)>=3
 mode=sys.argv[1];root=Path(sys.argv[2]).resolve();assert root.is_dir()
 if mode=='restore':restore(root)
 elif mode=='prepare':prepare(root)
 elif mode=='publish':assert len(sys.argv)==4;publish(root,sys.argv[3])
 else:raise ValueError('Expected restore, prepare, or publish')
