"""COAST-R09: measured main-roof shell orientation correction on saved R08.
Native A/B exposed a65mm step: barrel normals inward, cab normals outward.
Change only main barrel winding/shading; preserve coordinates, thickness and all
other art. No new materials, rain, lights, world, camera relocation or exposure.
"""
import bpy,bmesh,json,os,sys,hashlib,shutil,time
from pathlib import Path
from array import array
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import save,render,camera
BASE=ROOT/'output/g4-coast-r08';OUT=ROOT/'output/g4-coast-r09';OUT.mkdir(parents=True,exist_ok=True)
PARENT='c96c202a13c5ecd342a7b614a77b1e24ec9889bdb79cc328a255607467d7e877'
REV='COAST-R09 outward main barrel shell aligned to preserved R08 cab craft'
MODE=os.environ['G4_SHELL_MODE'];assert MODE in ['build','cab','coast','carriage']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest_data(me):
 a=array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a)
 return hashlib.sha256(a.tobytes()).hexdigest(),hashlib.sha256(json.dumps(sorted(sorted(p.vertices) for p in me.polygons)).encode()).hexdigest()
def protected():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.name=='Car_complete_barrel_roof':continue
  h.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_camera',None),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   h.update(repr(digest_data(o.data)).encode())
   for u in o.data.uv_layers:
    a=array('f',[0])*(len(u.data)*2);u.data.foreach_get('uv',a);h.update(a.tobytes())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y,o.data.dof.use_dof)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 for f in [1,301,451,466,660,840,451]:
  s.frame_set(f);bpy.context.view_layer.update()
  for o in sorted(s.objects,key=lambda x:x.name):h.update(repr((o.name,tuple(tuple(r) for r in o.matrix_world))).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.render.motion_blur_shutter)).encode());return h.hexdigest()
def evaluated_top(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();z=max(v.co.z for v in me.vertices);ev.to_mesh_clear();return z
if MODE=='build':
 master=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==master and sha(master)==PARENT
 assert s.get('g4_revision')=='COAST-R08 anchored cab shells sewn upholstery and layered native wind sea'
 audit=json.loads((ROOT/'output/g4-r08-roof-interface-audit/roof-interface-audit.json').read_text());assert audit['master_sha256']==PARENT and audit['source_unchanged']
 a=next(o for o in audit['objects'] if o['name']=='Car_complete_barrel_roof');assert a['mean_normal_z']<-.7 and a['vertices']==98 and a['faces']==48
 o=bpy.data.objects[a['name']];assert len(o.data.vertices)==98 and len(o.data.polygons)==48
 mod=o.modifiers[0];assert len(o.modifiers)==1 and mod.type=='SOLIDIFY' and abs(mod.thickness-.065)<1e-6 and mod.offset==-1
 assert sum(p.normal.z for p in o.data.polygons)/48<-.7 and not any(p.use_smooth for p in o.data.polygons)
 s.frame_set(451);bpy.context.view_layer.update();before=protected();old=o.data;old.use_fake_user=True;geometry_before=digest_data(old)
 top_before=evaluated_top(o);cab_top=evaluated_top(bpy.data.objects['Cab_complete_roof_loft.001']);assert .064<top_before-cab_top<.066
 o.data=old.copy();o.data.name='R09_outward_main_roof_same_coordinates';bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 for p in o.data.polygons:p.use_smooth=True
 mod.use_quality_normals=True;mod.use_even_offset=True
 assert digest_data(o.data)==geometry_before and min(p.normal.z for p in o.data.polygons)>0
 bpy.context.view_layer.update();top_after=evaluated_top(o);assert abs(top_after-cab_top)<1e-5
 after=protected();assert before==after,'Unexpected unrelated source edit'
 for p in BASE.iterdir():
  if p.name in ['g4-full-scene-candidate.blend','master-parts','MASTER-PARTS.json','MASTER-RESTORE.txt','restore_master.py','build-report.json','build.log','provision-source.log','FINITE-REQUEST.txt']:continue
  if p.is_dir():shutil.copytree(p,OUT/p.name,dirs_exist_ok=True)
  elif p.suffix in ['.json','.txt']:shutil.copy2(p,OUT/p.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R08-build-report.json')
 s['g4_revision']=REV;s['g4_roof_orientation_parent']=PARENT;s.frame_set(451);s.camera=bpy.data.objects['C01_exterior_hero']
 save(s,OUT/'g4-full-scene-candidate.blend');assert sha(master)==PARENT
 report={'stage':'G4','revision':'COAST-R09','parent_master_sha256':PARENT,'parent_evidence_commit':'caf093e65db1e364e2403e6a7807a3ef5da88b5b','audit_evidence_commit':'3171758a15f1aacba0c5fa14807f23bfba5b2637','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'candidate_sha256':sha(OUT/'g4-full-scene-candidate.blend'),'master_bytes':(OUT/'g4-full-scene-candidate.blend').stat().st_size,'edit_object':o.name,'actual_change':'Reverse48 inward main-roof faces and smooth the existing longitudinal roof. Preserve98 vertices,face connectivity,65mm shell,original offsets and material. Quality/even-thickness normals now operate inward rather than growing outside the envelope.','geometry_before_after_equal':True,'old_mesh_retained':old.name,'evaluated_main_top_before':top_before,'evaluated_main_top_after':top_after,'evaluated_cab_top_unchanged':cab_top,'protected_before':before,'protected_after':after,'default_opening_camera':'Original C01_exterior_hero; all diagnostic and failed-view cameras retained.','basis':'Actual R08 native before/after image removed cab faceting but exposed65mm raised rear band. Read-only source/evaluated audit confirmed main barrel still had inward normals and outward thickness. Source-vertex interface checks alone had missed evaluated-shell mismatch.','limitations':['Peak height match is not complete interface manufacture certification; actual same-camera native image still required.','Upholstery and wind sea inherited unchanged from R08, not separately fixed by this shell correction.','Rain distribution, dark walkway, coastal contact and complete event/4K/web gates remain open.'],'g4_stage_pass':False,'human_acceptance':False}
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('R09_MEASURED_SHELL_FIXED_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';report=json.loads((OUT/'build-report.json').read_text());expected=report['candidate_sha256']
 assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.frame_set(451);bpy.context.view_layer.update()
 if MODE=='cab':
  name='QA_R08_cab_unoccluded';assert name not in bpy.data.objects
  cam=camera(name,(12.55,9.60,4.43),(9.62,12.10,3.65),lens=48);filename='R09-cab-shell.png';res=(1280,800);samples=64
 else:
  name,filename,res,samples={'coast':('C01_exterior_hero','R09-complete-coast.png',(1440,900),48),'carriage':('C09_car_aisle_failure_check','R09-carriage-interior.png',(1280,800),48)}[MODE];cam=bpy.data.objects[name]
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 q=render(s,cam,OUT/filename,res=res,samples=samples,frame=451);q.update(master_sha256=expected,native_render=True,motion_blur=s.render.use_motion_blur,revision='COAST-R09')
 (OUT/(MODE+'-metrics.json')).write_text(json.dumps(q,indent=2));assert sha(master)==expected
 (OUT/(MODE+'-reopen.json')).write_text(json.dumps({'master_sha256':expected,'fresh_process':True,'master_unchanged':True,'missing_external_images':missing,'g4_stage_pass':False},indent=2));print('R09_NATIVE_IMAGE_COMPLETE',filename,flush=True)
