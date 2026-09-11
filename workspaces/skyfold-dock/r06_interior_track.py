"""R06D: a bounded interior cross-ring flight comparison on the same native scene.
The previous exterior framing is preserved; no city, dock or hull replacement.
"""
import bpy,os,math,json,hashlib,ast,time,struct,resource
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);S=bpy.context.scene
BASE=Path(bpy.data.filepath);MODE=os.environ.get('R06D_MODE','build')
if MODE=='build':
 parent='11e379b64201eb4e308ab19ceb9324e5256e9bf1535297f75accd9c1ec563fad';assert hashlib.sha256(BASE.read_bytes()).hexdigest()==parent
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());S.frame_set(1);bpy.context.view_layer.update()
 root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];root.animation_data_clear();root.rotation_euler=(0,0,math.pi/2)
 target=bpy.data.objects['R06_TRACKING_TARGET'];target.location=(0,-20,65)
 # Same ship now flies across the empty ring centre, safely beyond the old berth's axial end.
 cams=[]
 for name,p,lens in [('R06D_INTERIOR_REAR',(-480,780,290),28),('R06D_INTERIOR_SIDE',(-900,450,260),34)]:
  d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.2;d.clip_end=20000
  o=bpy.data.objects.new(name,d);bpy.data.collections['08_CAMERAS'].objects.link(o);o.parent=root;o.location=p
  con=o.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y';cams.append(o)
 for f in range(1,193):
  t=(f-1)/191;root.location=(-330+640*t,2850,1510+20*t);root.keyframe_insert(data_path='location',frame=f)
 # Curved manufacture: smooth only cylinder walls, preserving planar end caps and boxes.
 smooth=[]
 for o in bpy.data.collections['04_FREIGHTER'].objects:
  if o.type=='MESH' and o.name.startswith(('R06B','R06C')) and any(t in o.name.lower() for t in ['capsule','cylinder','cap','collar','thruster','casing','throat','valve']):
   for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
   smooth.append(o.name)
 S.camera=cams[0];S.render.resolution_x=1280;S.render.resolution_y=720
 checks=[]
 for f in [1,49,97,145,192]:
  S.frame_set(f);bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in bpy.data.collections['04_FREIGHTER'].objects if o.type=='MESH' and not o.hide_render for v in o.bound_box]
  radial=max(math.hypot(p.x,p.z-1600) for p in pts);assert radial<1000,radial
  assert min(p.y for p in pts)>2500
  for cam in cams:
   uv=[world_to_camera_view(S,cam,p) for p in pts];bounds=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
   checks.append({'frame':f,'camera':cam.name,'bounds':bounds,'camera_matrix':[list(r) for r in cam.matrix_world],'ship_matrix':[list(r) for r in root.matrix_world],'ship_max_radius':radial,'ship_min_axial_y':min(p.y for p in pts)})
 S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R06D_INTERIOR_CROSS_RING_FLIGHT';S['source_sha']=os.environ['GITHUB_SHA']
 meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'R06D_changes':{'same_city_dock_geometry':True,'flight_direction':'WORLD_POSITIVE_X','frames':192,'fps':24,'start':[-330,2850,1510],'end':[310,2850,1530],'surface_smoothing':smooth,'checks':checks,'collision_scope':'Entire freighter bounding corners inside radius 1000m and axial y>2500m; not all-scene mesh intersection proof'},'quality_status':'CONTROLLED_SPATIAL_COMPARISON_NOT_ART_PASS'})
 p=OUT/'skyfold-r06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R06D_SAVED',meta['scene_sha256'],flush=True)
else:
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert hashlib.sha256(BASE.read_bytes()).hexdigest()==meta['scene_sha256']
 defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in {'config','matrix','digest'}];exec(compile(ast.Module(body=defs,type_ignores=[]),'R06_RENDER_HELPERS','exec'),globals())
 rows=[]
 for name,f,w,samples in [('R06D_INTERIOR_REAR',1,1280,32),('R06D_INTERIOR_SIDE',1,1280,32),('R06D_INTERIOR_REAR',192,1280,32)]:
  S.frame_set(f);S.camera=bpy.data.objects[name];bpy.context.view_layer.update();config(w,samples,False)
  p=OUT/('%s_f%03d.png'%(name,f));S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True)
  rows.append({'file':p.name,'frame':f,'camera':name,'dimensions':[w,w*9//16],'samples':samples,'seconds':time.perf_counter()-t,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sha256':digest(p),'scene_sha256':meta['scene_sha256'],'source_sha':os.environ['GITHUB_SHA'],'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'visual_verdict':'NOT_OBSERVED'})
  (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R06D_FRAME',p.name,rows[-1]['seconds'],flush=True)
 (OUT/'COMPLETE.json').write_text(json.dumps({'frames':len(rows),'auto_qualified':False,'run_id':os.environ['GITHUB_RUN_ID']},indent=2))
