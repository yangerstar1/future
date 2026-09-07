"""COAST-R02 integration, not a scene rebuild.
Adapt only the two inspected native rain groups using the already-read R04
optics correction. Preserve exact scanned geology, spectral ocean and finishes.
"""
import bpy,os,sys,json,hashlib,shutil,time
from pathlib import Path
from array import array
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r01';OUT=ROOT/'output/g4-coast-r02';OUT.mkdir(parents=True,exist_ok=True)
PARENT='1be3507f7c31ed2f8e5431aefaf787ff414a29fdce696b596a2baff68b0789c6'
REV='COAST-R02 native coast with integrated round-drop shutter correction'
MODE=os.environ['G4_COAST_INTEGRATION_MODE'];assert MODE in ['build','exterior','detail','motion']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signature():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  h.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(str(len(o.data.polygons)).encode())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.type,o.data.shift_x,o.data.shift_y)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.energy,tuple(o.data.color),o.data.type)).encode())
  h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
 ocean=bpy.data.objects['Ocean_extent'];om=next(m for m in ocean.modifiers if m.type=='OCEAN')
 h.update(repr(tuple((k,getattr(om,k)) for k in ['geometry_mode','resolution','spectrum','wind_velocity','wave_scale','choppiness','wave_direction','foam_coverage','foam_layer_name'])).encode())
 h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode())
 return h.hexdigest()
def mn(n,l,op,a,b=None):
 q=n.new('ShaderNodeMath');q.operation=op
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):q.inputs[i].default_value=v
  else:l.new(v,q.inputs[i])
 return q.outputs[0]

if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
 assert s.get('g4_revision')=='COAST-R01 native ocean and adapted licensed coast scan on rain master'
 s.frame_set(451);bpy.context.view_layer.update();before=signature();edits=[]
 for name in ['G4R03_roof_clipped_rain','G4R03_eave_drips']:
  o=bpy.data.objects[name];mod=next(m for m in o.modifiers if m.type=='NODES');old=mod.node_group;g=old.copy();g.name='G4COAST_R02_'+name+'_round_drop';mod.node_group=g;n=g.nodes;l=g.links
  tr=next(q for q in n if q.bl_idname=='GeometryNodeTransform');sphere=next(q for q in n if q.bl_idname=='GeometryNodeMeshUVSphere');sp=next(q for q in n if q.bl_idname=='GeometryNodeSetPosition');inst=next(q for q in n if q.bl_idname=='GeometryNodeInstanceOnPoints')
  assert all(abs(tr.inputs['Scale'].default_value[i]-[.0028,.0028,.075][i])<.00001 for i in range(3)),'Actual rain prototype differs: stop, no blind adaptation'
  assert len(o.data.vertices)>0
  tr.inputs['Scale'].default_value=(.0021,.0021,.0024);sphere.inputs['Segments'].default_value=24;sphere.inputs['Rings'].default_value=12
  smooth=n.new('GeometryNodeSetShadeSmooth');smooth.domain='FACE';smooth.inputs['Shade Smooth'].default_value=True;l.new(sphere.outputs['Mesh'],smooth.inputs['Geometry']);l.new(smooth.outputs['Geometry'],tr.inputs['Geometry'])
  attrs={q.inputs['Name'].default_value:q.outputs['Attribute'] for q in n if q.bl_idname=='GeometryNodeInputNamedAttribute'};tm=next(q for q in n if q.bl_idname=='GeometryNodeInputSceneTime')
  cycle=mn(n,l,'FLOOR',mn(n,l,'DIVIDE',mn(n,l,'ADD',mn(n,l,'MULTIPLY',tm.outputs['Seconds'],attrs['rain_speed']),attrs['rain_phase']),attrs['rain_travel']))
  idx=n.new('GeometryNodeInputIndex');ident=mn(n,l,'ADD',idx.outputs['Index'],mn(n,l,'MULTIPLY',cycle,len(o.data.vertices)));sid=n.new('GeometryNodeSetID');l.new(sp.outputs['Geometry'],sid.inputs['Geometry']);l.new(ident,sid.inputs['ID']);l.new(sid.outputs['Geometry'],inst.inputs['Points'])
  if hasattr(o.cycles,'use_motion_blur'):o.cycles.use_motion_blur=True
  if hasattr(o.cycles,'motion_steps'):o.cycles.motion_steps=2
  edits.append({'object':name,'old_group':old.name,'new_group':g.name,'prototype_scale':[.0021,.0021,.0024],'smooth_drop_surface':True,'lifetime_aware_ID':True,'paths_and_source_points_unchanged':True})
 s.render.use_motion_blur=True;s.render.motion_blur_shutter=.70
 if hasattr(s.cycles,'motion_blur_position'):s.cycles.motion_blur_position='CENTER'
 s.frame_set(451);bpy.context.view_layer.update();after=signature();assert before==after,'Coast, building, material bindings, cameras or lights changed'
 for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json','STORM-ASSET-SOURCES.json','ASSET-AND-API-PROBE.json','PARENT-R03-build-report.json']:
  if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
 (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json');shutil.copy2(BASE/'build-report.json',OUT/'COAST-R01-build-report.json')
 s['g4_revision']=REV;s['g4_coast_r02_parent_sha256']=PARENT;s.frame_set(451);s.camera=bpy.data.objects['C01_exterior_hero'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report={'stage':'G4','revision':'COAST-R02','parent_master_sha256':PARENT,'parent_evidence_commit':'84570c8224f709784b580a23d330b2a0f522fcf9','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'candidate_sha256':sha(OUT/'g4-full-scene-candidate.blend'),'master_bytes':(OUT/'g4-full-scene-candidate.blend').stat().st_size,'edits':edits,'protected_before':before,'protected_after':after,'shutter_fraction':.70,'shutter_seconds':.70/30,'reuse':'Inspected R04 correct_g4_rain_optics.py at e53df4ba7e86469c301fb40707015d3e90716803, adapted only after checking actual R03 prototype on the preserved coast source. Not a claim that separate R04 render already passed.','basis':'Actual R03 M01 original shows dark refractive rods; round drops plus native temporal integration replace static optical rods.','limitations':['Rain shelter still evaluated against parked-frame451 geometry, not dynamic collision for arriving train.','Attached glass water static. Ocean is native spectral water plus art-directed 3D proximity wash, not fluid coast-impact solver.','Coast R01 has not been visually accepted. This integrated native candidate still requires real-image review.'],'g4_stage_pass':False,'human_acceptance':False}
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('COAST_R02_NATIVE_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';report=json.loads((OUT/'build-report.json').read_text());expected=report['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX' and s.render.use_motion_blur
 jobs={'exterior':[('C01_exterior_hero','C01-coast-rain.png',(1440,900),48,451),('C02_reverse_exterior','C02-reverse-coast.png',(1280,800),40,451)],'detail':[('G4COAST_rock_water_close','E01-rock-and-water.png',(1440,900),64,451),('G4COAST_ocean_close','E02-wave-and-foam.png',(1440,900),64,451),('C03_hall_to_platform','C03-rain-hall-regression.png',(1440,900),64,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.08
  jobs=[('G4COAST_ocean_close',f'motion/{j:04d}.png',(640,400),16,f) for j,f in enumerate(range(451,481,3))]
 metrics=[]
 for cam,name,res,samples,frame in jobs:
  assert time.time()<float(os.environ['G4_COAST_INTEGRATION_DEADLINE']),'Finite request deadline reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame);row.update(master_sha256=expected,native_render=True,revision='COAST-R02',native_shutter=.70,proof_only=(MODE=='motion'));metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2));print('COAST_R02_NATIVE_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
