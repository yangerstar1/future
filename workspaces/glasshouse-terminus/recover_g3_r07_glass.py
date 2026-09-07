"""Read-only image recovery, NOT a new art revision or power calibration.
Reopen verified R07, render only its missing fixed glass witness, preserve source.
"""
import bpy,os,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g3-r07';OUT=ROOT/'output/g3-r07-recovered'
EXPECTED='1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
master=OUT/'g3-bay-candidate.blend'
assert Path(bpy.data.filepath).resolve()==master and sha(master)==EXPECTED
assert sha(BASE/'g3-bay-candidate.blend')==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('g3_revision')=='R07 two existing purlin wash powers calibrated after native R06 review'
for name in ['G3R06_upper_node_wash','G3R06_upper_node_wash.001']:
    assert abs(bpy.data.objects[name].data.energy-144)<.001
originals=['D01-roof-node.png','R07-complete-bay-night.png','G3-bay-night.png']
for n in originals:assert sha(BASE/n)==sha(OUT/n)
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
assert not missing,missing
# Restore the exact original night-render configuration in memory only.
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
for n in json.loads(s['g3_neutral_lights']):bpy.data.objects[n].data.energy=0
bg=s.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.10,.145,.22,1);bg.inputs['Strength'].default_value=.18
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
metrics=json.loads((OUT/'render-metrics.json').read_text())
assert [r['file'] for r in metrics]==originals
assert not (OUT/'D01-glass-metal.png').exists(),'Do not overwrite an existing completed witness'
for r in metrics:r['origin_run_id']=34136755760;r['byte_reused_from_partial']=True
row=render(s,bpy.data.objects['G3_D01'],OUT/'D01-glass-metal.png',res=(1280,800),samples=64,frame=451)
row.update(lighting='night',native_render=True,source_master_sha256=EXPECTED,origin_run_id=int(os.environ['GITHUB_RUN_ID']),recovery_only=True)
metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
assert sha(master)==EXPECTED and sha(BASE/'g3-bay-candidate.blend')==EXPECTED
for n in originals:assert sha(BASE/n)==sha(OUT/n)
check={'fresh_process':True,'master_sha256':EXPECTED,'master_unchanged':True,'source_master_unchanged':True,
  'missing_external_images':missing,'native_images_total':4,'new_native_images_this_run':1,'byte_reused_image_count':3,
  'recovery_only':'Only D01-glass-metal rendered here; three already-complete R07 images and exact master copied byte-for-byte.',
  'source_partial_evidence_commit':'c68b1d2f746f8349b0ef1932076431f5c9fa12da','source_partial_run_id':34136755760,
  'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'g4_allowed':False,'human_acceptance':False}
(OUT/'reopen-check.json').write_text(json.dumps(check,indent=2))
(OUT/'recovery-report.json').write_text(json.dumps(check,indent=2))
print('R07_MISSING_GLASS_RECOVERED_NO_MASTER_SAVE',EXPECTED,flush=True)
