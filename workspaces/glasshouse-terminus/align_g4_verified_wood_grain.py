"""COAST-R05: measured wood-grain alignment on the integrated native coast.
Only three tabletop rims and seven sideboard members receive copied shaders and
an added UV layer. Old UVs, all source geometry and the coast/rain remain intact.
"""
import bpy, json, hashlib, os, sys, shutil, time
from pathlib import Path
from array import array
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import save, render
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r04';OUT=ROOT/'output/g4-coast-r05';OUT.mkdir(parents=True,exist_ok=True)
PARENT='51a3501edd81f879ba1b5c3e6dd6986e3306968d1319199a624f363667d65a9c'
REV='COAST-R05 verified horizontal veneer aligned to actual joinery and curved rims'
MODE=os.environ['G4_WOOD_MODE'];assert MODE in ['build','before','after']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
TABLES=['G3_walnut_cafe_top','G4_cafe_G3_walnut_cafe_top','G4_cafe_G3_walnut_cafe_top.001']
CABINET=['G3_sideboard_carcass','G3_cabinet_stile','G3_cabinet_stile.001','G3_cabinet_rail','G3_cabinet_rail.001','G3_cabinet_recessed_panel','G3_cabinet_recessed_panel.001']
TARGETS=TABLES+CABINET
EDGE='G4R03_G4_circumferential_edge_veneer';JOINERY='G4R03_G4_walnut_metre_UV';UVNAME='VerifiedWoodGrainMeters'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def protected(original_uvs):
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  h.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render,tuple(tuple(r) for r in o.matrix_world),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
   for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.material_index,p.use_smooth)).encode())
   for name in original_uvs[o.name]:
    layer=o.data.uv_layers[name];a=array('f',[0])*(len(o.data.loops)*2);layer.data.foreach_get('uv',a);h.update(repr((name,layer.active_render)).encode());h.update(a.tobytes())
   h.update(repr(o.data.uv_layers.active.name if o.data.uv_layers.active else None).encode())
  if hasattr(o.data,'materials') and o.name not in TARGETS:h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.render.motion_blur_shutter)).encode())
 return h.hexdigest()
if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
 assert s.get('g4_revision')=='COAST-R04 scanned wool and overcast surface response on native sea geology rain'
 inspection=json.loads((ROOT/'output/g4-wood-axis-inspection/wood-axis-inspection.json').read_text())
 assert inspection['master_sha256']==PARENT and inspection['source_master_unchanged']
 assert [o['name'] for o in inspection['objects']]==TARGETS
 s.frame_set(451);bpy.context.view_layer.update()
 original_uvs={o.name:[uv.name for uv in o.data.uv_layers] for o in s.objects if o.type=='MESH'};before=protected(original_uvs)
 report={'stage':'G4','revision':'COAST-R05','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
  'parent_evidence_commit':'def004d60bb37a58a043a3506fb2bbda5c3a0e5c','parent_master_sha256':PARENT,
  'inspection_evidence_commit':'48f41c9f388ceeac396281ee682c9c5240e1348b','inspection_run_id':34155095899,
  'basis':'Actually opened and verified packed veneer JPG: grain is predominantly horizontal U. Read-only inspection confirmed member length and table circumference instead mapped to V. Correct those ten objects only, then render native paired before/after observations.',
  'source_scan_sha256':'c0ba49a1fbc7b6ef93dd87abd83eee21eab611a6b291a0bdc6e4cf67b468158f','changes':[],'g4_stage_pass':False,'human_acceptance':False}
 materials={}
 for srcname,newname in [(EDGE,'G4COAST_R05_circumferential_walnut'),(JOINERY,'G4COAST_R05_member_aligned_walnut')]:
  src=bpy.data.materials[srcname];m=src.copy();m.name=newname;n=m.node_tree.nodes;l=m.node_tree.links
  assert hashlib.sha256(bytes(n['diff'].image.packed_file.data)).hexdigest()==report['source_scan_sha256']
  old=n['G4_explicit_surface_UV'];assert old.type=='TEX_COORD'
  uv=n.new('ShaderNodeUVMap');uv.name='Measured U-direction grain follows member length';uv.uv_map=UVNAME
  outgoing=[q.to_socket for q in list(old.outputs['UV'].links)];assert len(outgoing)==4,(srcname,len(outgoing))
  for socket in outgoing:l.new(uv.outputs['UV'],socket)
  normals=[q for q in n if q.type=='NORMAL_MAP'];assert len(normals)==1 and normals[0].space=='TANGENT';normals[0].uv_map=UVNAME
  fine=n['Vector Math.001'];assert fine.type=='VECT_MATH' and fine.operation=='MULTIPLY' and tuple(fine.inputs[1].default_value)==(450.0,28.0,1.0)
  fine.inputs[1].default_value=(28,450,1)
  materials[srcname]=m
 for previous in inspection['objects']:
  o=bpy.data.objects[previous['name']];assert o.type=='MESH'
  assert len(o.data.vertices)==previous['vertices'] and len(o.data.polygons)==previous['polygons']
  assert [m.name if m else None for m in o.data.materials]==previous['materials']
  assert o.data.uv_layers.active.name==previous['active_uv'] and UVNAME not in o.data.uv_layers
  srcname=EDGE if o.name in TABLES else JOINERY
  for f in previous['faces']:
   face=o.data.polygons[f['polygon']];actual=np.asarray([o.data.uv_layers.active.data[li].uv[:] for li in face.loop_indices])
   assert np.max(np.abs(actual-np.asarray(f['uv_points'])))<1e-6
   if o.name in CABINET and 'member_length_mapped_predominantly_to' in f:assert f['member_length_mapped_predominantly_to']=='V'
  o.data=o.data.copy();old_name=o.data.uv_layers.active.name
  render_name=next((uv.name for uv in o.data.uv_layers if uv.active_render),None)
  coords=np.empty(len(o.data.loops)*2,dtype=np.float32);o.data.uv_layers[old_name].data.foreach_get('uv',coords);coords=coords.reshape(-1,2)
  affected=[]
  for face in o.data.polygons:
   if o.data.materials[face.material_index].name==srcname:affected.extend(face.loop_indices)
  assert affected
  # A proper quarter turn preserves tangent handedness rather than mirroring UV.
  rotated=coords[affected][:,[1,0]].copy();rotated[:,1]*=-1;coords[affected]=rotated
  new=o.data.uv_layers.new(name=UVNAME);new.data.foreach_set('uv',coords.reshape(-1))
  o.data.uv_layers.active_index=o.data.uv_layers.find(old_name)
  if render_name:o.data.uv_layers[render_name].active_render=True
  for i,m in enumerate(o.data.materials):
   if m.name==srcname:o.data.materials[i]=materials[srcname]
  for face in o.data.polygons:
   if o.name not in CABINET or o.data.materials[face.material_index]!=materials[srcname]:continue
   co=np.asarray([o.data.vertices[o.data.loops[li].vertex_index].co[:] for li in face.loop_indices]);uvdata=np.asarray([new.data[li].uv[:] for li in face.loop_indices])
   axes=[i for i in range(3) if i!=int(np.argmax(np.abs(np.asarray(face.normal))))];design_axis=1 if o.name.startswith('G3_cabinet_rail') else 2
   if design_axis not in axes:continue
   A=np.column_stack([co[:,axes],np.ones(len(co))]);direction=np.linalg.lstsq(A,uvdata,rcond=None)[0][axes.index(design_axis)]
   assert abs(direction[0])>100*max(abs(direction[1]),1e-9),'Member length remains cross-grain'
  report['changes'].append({'object':o.name,'new_uv':UVNAME,'old_uv_preserved':old_name,'changed_corner_count':len(affected),'old_material':srcname,'new_material':materials[srcname].name,'coordinate_edit':'Target-face Unew=Vold, Vnew=-Uold; unchanged scale. Rims map circumference to scan U; sideboard members map length to U. Original top-face shaders unchanged.'})
 after=protected(original_uvs);assert before==after,'Protected source geometry, old UVs, other materials or observation conditions changed'
 report.update(protected_before=before,protected_after=after,protected_scope='Source mesh positions/topology/material indices/smoothing, old UV buffers and active layers, transforms/parents/ray flags, other object materials, cameras/lamps/exposure/world identity/shutter. Not an exhaustive comparison of every Blender property.')
 for path in BASE.iterdir():
  if path.is_file() and path.suffix in ['.json','.txt'] and path.name not in ['build-report.json','MASTER-PARTS.json','DELIVERY.json','MASTER-RESTORE.txt','FINITE-REQUEST.txt']:shutil.copy2(path,OUT/path.name)
 (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json');shutil.copy2(BASE/'build-report.json',OUT/'COAST-R04-build-report.json')
 s['g4_revision']=REV;s['g4_verified_wood_parent']=PARENT;s.camera=bpy.data.objects['G3_D02'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('COAST_R05_LOCAL_GRAIN_CANDIDATE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=BASE/'g4-full-scene-candidate.blend' if MODE=='before' else OUT/'g4-full-scene-candidate.blend'
 expected=PARENT if MODE=='before' else json.loads((OUT/'build-report.json').read_text())['candidate_sha256']
 assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected
 assert s.get('g4_revision')==('COAST-R04 scanned wool and overcast surface response on native sea geology rain' if MODE=='before' else REV)
 missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
 s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 jobs=[('G3_D02','M02-before-native.png',(1600,1000),64)] if MODE=='before' else [('G3_D02','M02-aligned-wood-native.png',(1600,1000),64),('C01_exterior_hero','C01-integrated-coast-native.png',(1440,900),48)]
 metrics=[]
 for cam,name,res,samples in jobs:
  assert time.time()<float(os.environ['G4_WOOD_DEADLINE']),'Finite wood observation deadline reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451);row.update(native_render=True,master_sha256=expected,revision='COAST-R04_BASELINE' if MODE=='before' else 'COAST-R05',max_bounces=10,transmission_bounces=8)
  metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2));print('NATIVE_WOOD_ALIGNMENT_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
