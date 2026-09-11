"""R08B corrects the observed flat vertical city strip in R08.
Only camera/flight staging and the existing lower fill change. No new city engine,
new meshes or rescaled assets. Old output remains a rejected control.
"""
import bpy,os,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
S=bpy.context.scene;BASE=Path(bpy.data.filepath);OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
parent='a694ad8f00faceced0262b3d848fd2cccd3de6e1b1c63bdf91447c4d93cf6f08'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==parent
assert bpy.app.version[:3]==(4,5,13)
meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());S.frame_set(1);bpy.context.view_layer.update()
root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];root.animation_data_clear();root.rotation_euler=(0,0,0)
cam=bpy.data.objects['R08_CITY_TRACK'];cam.data=cam.data.copy();cam.data.lens=17.5;cam.location=(-500,-900,-1070)
target=bpy.data.objects['R08_CITY_TRACK_TARGET'];target.location=(1100,2600,3450)
for f in [1,192]:
 t=(f-1)/191;root.location=(-2300,200-640*t,1750+20*t);root.keyframe_insert(data_path='location',frame=f)
for layer in root.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for p in fc.keyframe_points:p.interpolation='LINEAR'
# Existing cinematic lower bounce is increased to expose, not hide, the underside.
fill=bpy.data.objects['R07 lower reflected city fill'];fill.data=fill.data.copy();fill.data.energy=9000000
S.camera=cam;S.render.resolution_x=1920;S.render.resolution_y=1080;S.render.resolution_percentage=100
checks=[]
for f in [1,49,97,145,192]:
 S.frame_set(f);bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(v) for o in bpy.data.collections['04_FREIGHTER'].objects if o.type=='MESH' and not o.hide_render for v in o.bound_box]
 uv=[world_to_camera_view(S,cam,p) for p in pts];rect=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
 assert all(p.z>0 for p in uv) and min(rect)>.01 and max(rect)<.99,(f,rect)
 assert min(p.z for p in pts)>1400
 checks.append({'frame':f,'ship_bounds_uv':rect,'camera_matrix':[list(r) for r in cam.matrix_world],'ship_matrix':[list(r) for r in root.matrix_world]})
S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R08B_LOW_OPENING_TRACKING';S['source_sha']=os.environ['GITHUB_SHA']
meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'current_motion':{'frames':192,'fps':24,'start':[-2300,200,1750],'end':[-2300,-440,1770],'camera':cam.name,'heading':'WORLD_NEGATIVE_Y','already_released':True,'checks':checks},'R08B_correction':{'observed_failure':'R08 sees the opposite curved surface as a nearly flat vertical strip','geometric_correction':'Low viewpoint near the open end, looking up through the ring; unchanged 20km habitat and rigid buildings','lens_mm':17.5,'geometry_changed':False,'lower_fill_power':9000000,'full_scene_collision_or_docking_validation':False,'old_R08_artifact_preserved':True},'quality_status':'ACTUAL_IMAGE_REVIEW_REQUIRED'})
p=OUT/'skyfold-r08b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('R08B_SAVED',meta['scene_sha256'],flush=True)
