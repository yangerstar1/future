"""COAST-R07: one bounded airborne-density candidate after actual R06 originals.
Reuse existing roof-clipped trajectories, velocities, round drops and native shutter.
No larger fake droplets, emissive streaks, image overlays or changes to sea/materials.
"""
import bpy,os,sys,json,hashlib,shutil,time
from pathlib import Path
import numpy as np
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import save,render
BASE=ROOT/'output/g4-coast-r06-checked';OUT=ROOT/'output/g4-coast-r07';OUT.mkdir(parents=True,exist_ok=True)
PARENT='590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738'
OLD='COAST-R06 surface-bound weather on preserved sea geology scanned wool and aligned wood'
REV='COAST-R07 increased airborne density on verified water-contact coast'
MODE=os.environ['G4_AIR_MODE'];s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
TARGETS=['G4R03_roof_clipped_rain','G4COAST_R06_exterior_round_rain']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def protect():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  h.update(repr((o.name,o.type,o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),o.hide_render,getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.name in TARGETS:continue
  if o.type=='MESH':
   a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.dof.use_dof)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.energy,tuple(o.data.color),o.data.type)).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.look,s.render.use_motion_blur,s.render.motion_blur_shutter)).encode())
 return h.hexdigest()
if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT and s.get('g4_revision')==OLD
 s.frame_set(451);bpy.context.view_layer.update();before=protect();rng=np.random.default_rng(202609087)
 report={'stage':'G4','revision':'COAST-R07','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'parent_master_sha256':PARENT,'parent_source_evidence_commit':'8edab03563070bc62a1a768aaf1f6389d72a68f6','basis':'Actually opened original R06 C03/C01 from artifact10031880766. Surface rain is now visible on windows but airborne rain remains too weak. Change density only; the native R04 motion proof also showed very weak airborne visibility. This is one explicit optical-density trial, not a presumed art improvement.','edits':[],'g4_stage_pass':False,'human_acceptance':False}
 for name in TARGETS:
  o=bpy.data.objects[name];old=o.data;count=len(old.vertices);assert count==(28000 if name==TARGETS[0] else 7200)
  co=np.empty(count*3,dtype=np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,3)
  attrs={}
  for key in ['rain_travel','rain_phase','rain_speed','rain_size']:
   a=old.attributes[key];assert a.domain=='POINT' and a.data_type=='FLOAT';v=np.empty(count,dtype=np.float32);a.data.foreach_get('value',v);attrs[key]=v
  # The original close-to-wall volume already has higher spatial concentration.
  # Keep that volume moderate, densify broad exterior trajectories more strongly.
  repeat=np.where(co[:,2]>10,16,2) if name==TARGETS[0] else np.full(count,8)
  indices=np.repeat(np.arange(count),repeat);newco=co[indices];N=len(indices)
  newattrs={k:v[indices].copy() for k,v in attrs.items()}
  newattrs['rain_phase']=rng.random(N).astype(np.float32)*newattrs['rain_travel']
  first=np.r_[0,np.cumsum(repeat)[:-1]];newattrs['rain_phase'][first]=attrs['rain_phase']
  assert np.array_equal(newco[first],co)
  assert np.all(newattrs['rain_phase']>=0) and np.all(newattrs['rain_phase']<=newattrs['rain_travel'])
  me=bpy.data.meshes.new(name+'_R07_same_supported_trajectories');me.vertices.add(N);me.vertices.foreach_set('co',newco.ravel());me.update()
  for k,v in newattrs.items():me.attributes.new(k,'FLOAT','POINT').data.foreach_set('value',v)
  o.data=me;mod=next(m for m in o.modifiers if m.type=='NODES');g=mod.node_group.copy();g.name=name+'_R07_exact_integer_lifetime_ID';mod.node_group=g;n=g.nodes;l=g.links
  setid=next(q for q in n if q.bl_idname=='GeometryNodeSetID');index=next(q for q in n if q.bl_idname=='GeometryNodeInputIndex')
  floors=[q for q in n if q.bl_idname=='ShaderNodeMath' and q.operation=='FLOOR'];assert len(floors)==1
  sphere=next(q for q in n if q.bl_idname=='GeometryNodeMeshUVSphere');transform=next(q for q in n if q.bl_idname=='GeometryNodeTransform')
  assert np.allclose(transform.inputs['Scale'].default_value,(.0021,.0021,.0024))
  # Large counts require true integer IDs, not float multiply-add past 2^24.
  mul=n.new('FunctionNodeIntegerMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=N;l.new(floors[0].outputs[0],mul.inputs[0])
  add=n.new('FunctionNodeIntegerMath');add.operation='ADD';l.new(mul.outputs[0],add.inputs[0]);l.new(index.outputs['Index'],add.inputs[1]);l.new(add.outputs[0],setid.inputs['ID'])
  for frame in [1,451,457,840]:
   lifetime=np.floor((frame/30*newattrs['rain_speed'].astype(np.float64)+newattrs['rain_phase'])/newattrs['rain_travel']).astype(np.int64)
   ids=lifetime*N+np.arange(N,dtype=np.int64);assert ids.min()>=0 and ids.max()<2**31 and np.unique(ids).size==N
  report['edits'].append({'object':name,'old_paths':count,'new_instances':N,'trajectory_positions_unchanged':True,'all_original_trajectories_and_original_phase_replicas_retained':True,'velocities_sizes_materials_and_prototype_unchanged':True,'lifetime_ID':'Native Integer Math, no float precision collisions','close_volume_multiplier':2 if name==TARGETS[0] else None,'broad_volume_multiplier':16 if name==TARGETS[0] else 8})
 s.frame_set(451);bpy.context.view_layer.update();after=protect();assert before==after
 report['protected_before']=before;report['protected_after']=after
 report['limits']=['This changes visual particle concentration, not a calibrated rainfall-rate simulation.','Original parked-frame rain supports are reused without spatial jitter. Moving-train collision still unverified.','No change to environment, exposure, practical lamps, glass, water contact, ocean, cliff, wool or wood.','If originals still do not show sufficient rain, stop increasing density and investigate radiance/reconstruction instead of an unbounded particle escalation.']
 for p in BASE.iterdir():
  if p.is_dir() and p.name in ['assets','models']:shutil.copytree(p,OUT/p.name,dirs_exist_ok=True)
  elif p.is_file() and p.suffix in ['.json','.txt'] and p.name not in ['build-report.json','MASTER-PARTS.json','DELIVERY.json','MASTER-RESTORE.txt','FINITE-REQUEST.txt'] and not p.name.endswith(('-metrics.json','-reopen.json')):shutil.copy2(p,OUT/p.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R06-checked-build-report.json')
 s['g4_revision']=REV;s['g4_airborne_density_parent']=PARENT;save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size;(OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('R07_DENSITY_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 assert MODE in ['hall','macro','motion'];master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 jobs={'hall':[('C03_hall_to_platform','C03-airborne-rain.png',(1440,900),64,451)],'macro':[('G4R03_rain_glass_macro','M01-airborne-and-attached-rain.png',(1600,1000),80,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.065
  jobs=[('G4R03_rain_glass_macro',f'motion/{j:04d}.png',(640,400),24,f) for j,f in enumerate(range(451,481,3))]
 metrics=[]
 for cam,file,res,samples,f in jobs:
  assert time.time()<float(os.environ['G4_AIR_DEADLINE'])
  row=render(s,bpy.data.objects[cam],OUT/file,res=res,samples=samples,frame=f);row.update(master_sha256=expected,native_render=True,revision='COAST-R07',proof_only=MODE=='motion');metrics.append(row);(OUT/(MODE+'-metrics.json')).write_text(json.dumps(metrics,indent=2));print('R07_NATIVE_VIEW',file,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
