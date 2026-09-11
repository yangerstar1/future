"""R08 local camera/flight staging correction, not a new scene generator.
Reuse the verified R07B geometry and finite R06 renderer. Earlier scene snapshots
remain controls. Flight is already released; this does not validate dock interfaces.
"""
import bpy, os, json, hashlib, ast, time, struct, resource
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;BASE=Path(bpy.data.filepath);MODE=os.environ.get('R08_MODE','build')
PARENT='e9ffbb9051f27fe6c19d6ff7069cd5f419b9517e3b4ee2b0d0f889845e8086c6'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(o):return [list(r) for r in o.matrix_world]
def bounds(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
assert bpy.app.version[:3]==(4,5,13),bpy.app.version_string
if MODE=='build':
 assert digest(BASE)==PARENT
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
 S.frame_set(1);bpy.context.view_layer.update()
 ship=bpy.data.collections['04_FREIGHTER'];root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']
 def geometry_signature():
  h=hashlib.sha256()
  for m in sorted(bpy.data.meshes,key=lambda x:x.name):
   h.update(m.name.encode());h.update(str((len(m.vertices),len(m.polygons))).encode())
   for v in m.vertices:h.update(struct.pack('<3f',*v.co))
  return h.hexdigest()
 signature=geometry_signature()
 stationary={o.name:matrix(o) for key in ['01_RING_STRUCTURE','02_CITY_INSTANCES','03_DOCK','06_TRANSPORT'] for o in bpy.data.collections[key].objects}
 root.animation_data_clear();root.rotation_euler=(0,0,0)
 cams=[]
 choices=[('R08_CITY_TRACK',(-1900,-100,-1500),(1000,0,1500),32),('R08_CITY_WIDE',(-2400,-100,-1300),(1400,0,1700),28)]
 for name,offset,aim,lens in choices:
  target=bpy.data.objects.new(name+'_TARGET',None);bpy.data.collections['08_CAMERAS'].objects.link(target);target.parent=root;target.location=aim
  data=bpy.data.cameras.new(name);data.lens=lens;data.sensor_width=36;data.clip_start=.2;data.clip_end=80000;data.dof.use_dof=False
  cam=bpy.data.objects.new(name,data);bpy.data.collections['08_CAMERAS'].objects.link(cam);cam.parent=root;cam.location=offset
  con=cam.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y';cams.append(cam)
 for frame in [1,192]:
  t=(frame-1)/191;root.location=(-3500,1600-640*t,4300+20*t);root.keyframe_insert(data_path='location',frame=frame)
 if root.animation_data and root.animation_data.action:
  action=root.animation_data.action
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for point in fc.keyframe_points:point.interpolation='LINEAR'
 # Retain the same manufactured materials and three existing light cards. Only
 # the already-existing analytic sky fill is made useful inside the habitat.
 previous_world=S.world.name;world=S.world.copy();world.name='R08 inhabited-ring fill';S.world=world
 bg=world.node_tree.nodes.get('Background');assert bg is not None;bg.inputs['Strength'].default_value=.32
 S.camera=cams[0];S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
 checks=[]
 for frame in [1,49,97,145,192]:
  S.frame_set(frame);bpy.context.view_layer.update()
  points=[p for o in ship.objects if o.type=='MESH' and not o.hide_render for p in bounds(o)]
  assert max((Vector((p.x,0,p.z-10000))).length for p in points)<8500
  assert min(p.z for p in points)>3800
  for cam in cams:
   uv=[world_to_camera_view(S,cam,p) for p in points]
   rect=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
   assert all(p.z>0 for p in uv) and min(rect)>.01 and max(rect)<.99,(frame,cam.name,rect)
   checks.append({'frame':frame,'camera':cam.name,'bounds_uv':rect,'camera_matrix':matrix(cam),'ship_matrix':matrix(root)})
 for name,expected in stationary.items():assert matrix(bpy.data.objects[name])==expected,name
 assert geometry_signature()==signature
 S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R08_INHABITED_TRACKING_PROBE';S['source_sha']=os.environ['GITHUB_SHA'];S['auto_qualified']=False
 meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'current_motion':{'frames':192,'fps':24,'start':[-3500,1600,4300],'end':[-3500,960,4320],'camera':cams[0].name,'heading':'WORLD_NEGATIVE_Y','already_released':True,'checks':checks},'R08_intervention':{'geometry_unchanged':True,'mesh_signature':signature,'stationary_environment_objects_checked':len(stationary),'city_geometry_changed':False,'camera_and_ship_staging_changed':True,'old_world':previous_world,'analytic_fill_strength':.32,'hypothesis':'Read city as nearby buildings and a rising urban surface, not a distant hoop texture','scope':'Local shot correction; no new theme, no claim of core G2/G6 pass'},'quality_status':'TRUE_PROBE_REQUIRED'})
 p=OUT/'skyfold-r08.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=digest(p);dump('BUILD-MANIFEST.json',meta);print('R08_SAVED',meta['scene_sha256'],flush=True)
else:
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
 defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='config'];assert len(defs)==1
 exec(compile(ast.Module(body=defs,type_ignores=[]),'R06_VERIFIED_RENDER_CONFIG','exec'),globals())
 if MODE=='probe':views=[('R08_CITY_TRACK',1,1280,32,False),('R08_CITY_WIDE',1,1280,32,False),('R08_CITY_TRACK',192,1280,32,False),('R08_CITY_TRACK',1,960,24,True)]
 elif MODE=='hero':views=[('R08_CITY_TRACK',1,2560,96,False),('R08_CITY_TRACK',97,1920,48,False),('R08_CITY_TRACK',1,1280,32,True)]
 elif MODE=='motion':
  a=int(os.environ['FRAME_START']);b=int(os.environ['FRAME_END']);assert 1<=a<=b<=192
  views=[('R08_CITY_TRACK',f,1920,24,False) for f in range(a,b+1)]
 else:raise ValueError(MODE)
 rows=[]
 for camera,frame,width,samples,neutral in views:
  S.frame_set(frame);S.camera=bpy.data.objects[camera];bpy.context.view_layer.update();config(width,samples,MODE=='motion')
  S.render.use_compositing=False;S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
  name=('frame_%04d'%frame) if MODE=='motion' else '%s_f%03d%s'%(camera,frame,'_NEUTRAL' if neutral else '')
  p=OUT/(name+'.png');S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-t
  assert struct.unpack('>II',p.read_bytes()[16:24])==(width,width*9//16)
  rows.append({'file':p.name,'frame':frame,'camera':camera,'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell']),'dimensions':[width,width*9//16],'samples':samples,'seconds':seconds,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sha256':digest(p),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'neutral':neutral,'compositing':False,'visual_verdict':'NOT_OBSERVED'})
  dump('OBSERVATIONS.json',rows);print('R08_FRAME',name,round(seconds,2),flush=True)
 S.view_layers[0].material_override=None;dump('COMPLETE.json',{'run_id':os.environ['GITHUB_RUN_ID'],'mode':MODE,'frames':len(rows),'seconds':sum(r['seconds'] for r in rows),'auto_qualified':False})
