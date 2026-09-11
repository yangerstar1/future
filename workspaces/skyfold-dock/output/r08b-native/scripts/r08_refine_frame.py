"""R08B narrows the same framing repair, after R08 rendered the city as a side strip.
Camera projection predicts a ground-to-overhead arc in the low axial view. Real
renders still decide acceptance. No new geometry, ring radius or city allocation.
"""
import bpy,os,math,json,hashlib,ast,time,struct,resource
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);BASE=Path(bpy.data.filepath);S=bpy.context.scene
MODE=os.environ.get('R08B_MODE','build')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(o):return [list(r) for r in o.matrix_world]
def corners(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
def write(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False))
if MODE=='build':
 parent='2636f1582b1bdbd0d60ab08428f29f8ccc85b27aa2c52086832876aa30eaa6e4';assert digest(BASE)==parent;assert bpy.app.version[:3]==(4,5,13)
 old=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());S.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];ship=bpy.data.collections['04_FREIGHTER']
 env=[o for o in S.objects if o.type in {'MESH','CURVE','FONT'} and o.name not in ship.objects];before={o.name:matrix(o) for o in env}
 root.animation_data_clear();root.rotation_euler=(0,0,0)
 cams=[]
 for name,offset,aim,lens in [('R08B_LOW_AXIS',(-500,-700,-60),(0,300,500),12),('R08B_LOWER_PITCH',(-550,-850,20),(0,200,300),14)]:
  target=bpy.data.objects.new(name+' target',None);bpy.data.collections['13_R06_FLIGHT'].objects.link(target);target.parent=root;target.location=aim
  d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.2;d.clip_end=60000;d.dof.use_dof=False
  cam=bpy.data.objects.new(name,d);bpy.data.collections['08_CAMERAS'].objects.link(cam);cam.parent=root;cam.location=offset
  c=cam.constraints.new('TRACK_TO');c.target=target;c.track_axis='TRACK_NEGATIVE_Z';c.up_axis='UP_Y';cams.append(cam)
 for f in range(1,193):
  t=(f-1)/191;root.location=(-2800,2000-640*t,1200+20*t);root.keyframe_insert(data_path='location',frame=f)
 S.frame_start=1;S.frame_end=192;S.render.fps=24;S.render.resolution_x=1280;S.render.resolution_y=720;S.camera=cams[0];checks=[]
 for f in [1,49,97,145,192]:
  S.frame_set(f);bpy.context.view_layer.update();pts=[p for o in ship.objects if o.type=='MESH' and not o.hide_render for p in corners(o)]
  assert max(p.x for p in pts)<-2000,'Keep the freighter away from the old dock x region'
  assert max(math.hypot(p.x,p.z-10000) for p in pts)<9750
  for cam in cams:
   uv=[world_to_camera_view(S,cam,p) for p in pts];b=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
   assert all(p.z>0 for p in uv) and min(b)>-.04 and max(b)<1.04,(cam.name,b)
   checks.append({'frame':f,'camera':cam.name,'ship_bbox_uv':b,'camera_matrix':matrix(cam),'ship_matrix':matrix(root)})
 S.frame_set(1);bpy.context.view_layer.update();assert all(matrix(o)==before[o.name] for o in env)
 S['candidate']='R08B_LOW_AXIAL_CITY_FLIGHT';S['source_sha']=os.environ['GITHUB_SHA'];S['auto_qualified']=False
 meta={'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'blender':bpy.app.version_string,'scope':'Second and last bounded framing correction this continuation; no macro-geometry redesign. Preserve R08 and R07B inputs as failed framing controls.','environment_transforms_preserved':True,'city_ship_geometry_materials_and_lighting_unchanged':True,'motion':{'start':[-2800,2000,1200],'end':[-2800,1360,1220],'frames':192,'fps':24,'direction':'WORLD_NEGATIVE_Y','tracking':'Actual target constraint, camera follows ship root','checks':checks},'collision_scope':'Conservative radial and dock-region separation; no claim of all-triangle collision simulation','artistic_status':'NOT_REVIEWED','auto_qualified':False}
 p=OUT/'skyfold-r08b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=digest(p);write('BUILD-MANIFEST.json',meta);print('R08B_SAVED',meta['scene_sha256'],flush=True)
else:
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
 defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='config'];assert len(defs)==1;exec(compile(ast.Module(body=defs,type_ignores=[]),'EXISTING_RENDER_CONFIGURATION','exec'),globals())
 selected=os.environ.get('R08B_CAMERA','R08B_LOW_AXIS')
 if MODE=='probe':views=[('R08B_LOW_AXIS',1,1280,32,False,True),('R08B_LOWER_PITCH',1,1280,32,False,True),('R08B_LOW_AXIS',192,1280,32,False,True),('R08B_LOW_AXIS',1,960,16,True,False)]
 elif MODE=='stills':views=[(selected,1,2560,96,False,True),(selected,97,1920,64,False,True),(selected,192,1920,64,False,True),(selected,1,1280,32,False,False)]
 else:raise ValueError(MODE)
 rows=[]
 for name,f,w,n,neutral,grade in views:
  S.frame_set(f);S.camera=bpy.data.objects[name];bpy.context.view_layer.update();config(w,n,False);S.render.use_compositing=grade;S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
  p=OUT/('%s_f%03d_%s.png'%(name,f,'NEUTRAL' if neutral else 'BEAUTY' if grade else 'RAW'));S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
  assert struct.unpack('>II',p.read_bytes()[16:24])==(w,w*9//16)
  rows.append({'file':p.name,'frame':f,'camera':name,'dimensions':[w,w*9//16],'samples':n,'seconds':elapsed,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'neutral':neutral,'compositing':grade,'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell']),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'sha256':digest(p),'artistic_status':'NOT_OBSERVED'})
  write('OBSERVATIONS.json',rows);print('R08B_RENDERED',p.name,elapsed,flush=True)
 S.view_layers[0].material_override=None;write('COMPLETE.json',{'mode':MODE,'frames':len(rows),'run_id':os.environ['GITHUB_RUN_ID'],'scene_sha256':meta['scene_sha256'],'auto_qualified':False})
