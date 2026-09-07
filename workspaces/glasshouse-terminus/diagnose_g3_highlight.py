"""Read-only R03 light attribution. Cropped native pixels are QA, never beauty.
Reuses the original camera/materials and common renderer. No master is saved.
"""
import bpy,json,hashlib,sys,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
BASE=Path('workspaces/glasshouse-terminus/output/g3-r03').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-light-check').resolve()
SOURCE=BASE/'g3-bay-candidate.blend'
EXPECTED='cb1ae3c8ace74bcbeeaaf51684bf013cba5b7702803f432c91632e4395fadcfe'
assert Path(bpy.data.filepath).resolve()==SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('g3_revision')=='R03 vestibule craft and supplemental complete observations'
cam=bpy.data.objects['G3R03_complete_bay']
assert abs(cam.data.lens-36)<1e-5
s.timeline_markers.clear();s.frame_set(451);s.camera=cam
s.render.resolution_x,s.render.resolution_y=1440,900
s.render.resolution_percentage=100
assert abs(s.view_settings.exposure)<1e-8
OUT.mkdir(parents=True,exist_ok=True)
large=['G3_night_sky','G3_interior_softbox','G3_window_rim']
night=json.loads(s['g3_night_lights'])
power={name:bpy.data.objects[name].data.energy for name in night}
assert all(power[name]>0 for name in large)
report={'stage':'G3','purpose':'Attribute remaining white transom patch in actual R03 native overview; not acceptance or a new art candidate',
 'source_master_sha256':EXPECTED,'source_evidence_commit':'22dceca579c272b51767c70c153c540f7defc547',
 'source_overview_artifact':10017903613,'source_overview_sha256':'49a427dfd2fb4f5ef3980e81a5a9583e9eba4c60cd69425e26cc9886ce1be08e',
 'camera':cam.name,'frame':451,'lights':{},'rays':[],'renders':[],
 'crop_normalized_bottom_left':[.56,.72,.90,1.0],
 'parent_frame_pixels':[1440,900],'scope':'Native Cycles border crop, no resized/render-painted evidence. Only lamp energy changes in memory for labelled diagnostic cases.',
 'geometry_edits':False,'material_edits':False,'human_acceptance':False,'g4_allowed':False}
for name in night:
 o=bpy.data.objects[name]
 report['lights'][name]={'energy':o.data.energy,'position':list(o.matrix_world.translation),'size':o.data.size if o.data.type=='AREA' else None,'projected_center':list(world_to_camera_view(s,cam,o.matrix_world.translation))}
# First surface along selected image rays: distinguishes glass/canopy/solid geometry.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
view=cam.data.view_frame(scene=s);lx=min(p.x for p in view);hx=max(p.x for p in view);ly=min(p.y for p in view);hy=max(p.y for p in view);z=view[0].z
for u in [.64,.72,.80]:
 for v in [.79,.88,.95]:
  direction=cam.matrix_world.to_3x3()@Vector((lx+(hx-lx)*u,ly+(hy-ly)*v,z))
  hit,at,normal,index,obj,matrix=s.ray_cast(deps,cam.matrix_world.translation,direction.normalized(),distance=100)
  report['rays'].append({'uv':[u,v],'hit':hit,'first_object':obj.name if obj else None,'point':list(at) if hit else None,'material':obj.active_material.name if obj and obj.active_material else None})
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.56;s.render.border_max_x=.90;s.render.border_min_y=.72;s.render.border_max_y=1.0
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
cases=[('L00-baseline.png',[]),('L01-no-sky-card.png',[large[0]]),('L02-no-interior-card.png',[large[1]]),('L03-no-rim-card.png',[large[2]]),('L04-practicals-only.png',large)]
try:
 for name,disabled in cases:
  for n,p in power.items():bpy.data.objects[n].data.energy=0 if n in disabled else p
  m=render(s,cam,OUT/name,res=(1440,900),samples=32,frame=451)
  m['diagnostic_disabled_lights']=disabled;m['cropped_native_pixels']=True
  report['renders'].append(m)
  (OUT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
finally:
 for n,p in power.items():bpy.data.objects[n].data.energy=p
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
report['source_master_unchanged']=True;report['status']='DIAGNOSTICS_RENDERED_REVIEW_PENDING'
(OUT/'light-diagnosis.json').write_text(json.dumps(report,indent=2))
print('R03_LIGHT_ATTRIBUTION_RENDERED',len(report['renders']),flush=True)
