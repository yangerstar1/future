"""Bounded R03 light-source ablation and interface observations. No saved scene edits."""
import bpy,hashlib,json,sys,os,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import camera,render
ROOT=Path(os.environ['OBS_ROOT']).resolve();ROOT.mkdir(parents=True,exist_ok=True)
SOURCE=Path(os.environ['G3_OBS_SOURCE']).resolve()
EXPECTED='cb1ae3c8ace74bcbeeaaf51684bf013cba5b7702803f432c91632e4395fadcfe'
assert Path(bpy.data.filepath).resolve()==SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
s=bpy.context.scene;assert s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE'
assert s.get('g3_revision')=='R03 vestibule craft and supplemental complete observations'
s.frame_set(451);bpy.context.view_layer.update()
originals={o.name:(tuple(tuple(row) for row in o.matrix_world),o.data.lens) for o in s.objects if o.type=='CAMERA'}
objects=[o for o in s.objects if o.type in {'MESH','CURVE'}]
def geometry_signature():
    h=hashlib.sha256();s.frame_set(451);bpy.context.view_layer.update()
    for o in sorted(objects,key=lambda o:o.name):
        h.update(o.name.encode());h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
    return h.hexdigest()
before=geometry_signature();s.timeline_markers.clear()
night=json.loads(s['g3_night_lights']);power={n:bpy.data.objects[n].data.energy for n in night}
for n in ['G3_interior_softbox','G3_night_sky','G3_pendant_light','G3_cafe_practical','G3_door_practical']:assert n in power
report={'stage':'G3','type':'R03_LIGHT_DIAGNOSTIC_NOT_A_NEW_MASTER','master_sha256':EXPECTED,
 'parent_evidence_commit':'22dceca579c272b51767c70c153c540f7defc547','source_power':power,
 'original_geometry_signature':before,'views':[],'human_acceptance':False,'g4_allowed':False,
 'purpose':'Identify white reflected patch in actual R03 upper glass before making a further lighting change.',
 'limitation':'Low-resolution ablations diagnose cause; practical-only trial is not an accepted lighting solution.'}
(ROOT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
cam=bpy.data.objects['G3R03_complete_bay']
variants=[('L01-baseline',{}),('L02-no-interior-fill',{'G3_interior_softbox':0}),
 ('L03-no-sky-area',{'G3_night_sky':0}),
 ('L04-practical-trial',{'G3_interior_softbox':0,'G3_pendant_light':330,'G3_cafe_practical':14,'G3_door_practical':90})]
for name,changes in variants:
    if time.time()>float(os.environ['G3_OBSERVATION_DEADLINE']):raise TimeoutError('Save bounded partial diagnostic')
    for n,p in power.items():bpy.data.objects[n].data.energy=changes.get(n,p)
    m=render(s,cam,ROOT/(name+'.png'),res=(720,450),samples=24,frame=451)
    m['temporary_light_changes']=changes;report['views'].append(m)
    (ROOT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
for n,p in power.items():bpy.data.objects[n].data.energy=p
# Reuse the existing observe_g3.py witness positions on this exact later source.
neutral=json.loads(s['g3_neutral_lights']);bg=s.world.node_tree.nodes['Background']
for n,p in neutral.items():bpy.data.objects[n].data.energy=p
for n in night:bpy.data.objects[n].data.energy=0
bg.inputs['Color'].default_value=(.16,.19,.23,1);bg.inputs['Strength'].default_value=.65
rail=camera('QA_G3_R03_roller',(-2.40,9.25,3.67),(-2.96,10.59,3.40),55)
threshold=camera('QA_G3_R03_threshold',(-.9,8.75,2.20),(-2,10.73,1.19),50)
for c,n in [(rail,'W06-guide-roller.png'),(threshold,'W07-threshold.png')]:
    m=render(s,c,ROOT/n,res=(1000,625),samples=32,frame=348);m['lighting']='R03 legacy neutral'
    report['views'].append(m);(ROOT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
assert geometry_signature()==before
for name,(matrix,lens) in originals.items():
    ob=bpy.data.objects[name];assert tuple(tuple(r) for r in ob.matrix_world)==matrix and ob.data.lens==lens
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
report.update(status='DIAGNOSTICS_RENDERED_REVIEW_PENDING',master_bytes_unchanged=True,original_cameras_unchanged=True,geometry_signature_after=before)
(ROOT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
print('G3_LIGHT_DIAGNOSTICS_COMPLETE',len(report['views']),flush=True)
