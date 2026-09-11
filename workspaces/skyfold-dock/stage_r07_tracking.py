"""R07B shot staging on the inspected R07, with no geometry replacement.
The protected interior study remains available. This exterior tracking shot starts
in free flight, shows a complete city ring behind the vessel, and is not an
undocking simulation or a replacement for docked-scene structural verification.
"""
import bpy,os,json,hashlib,time,struct,resource,ast,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);BASE=Path(bpy.data.filepath);S=bpy.context.scene
MODE=os.environ.get('R07B_MODE','build')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(o):return [list(r) for r in o.matrix_world]
def bb(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
if MODE=='build':
 parent='e633629812f6a51710d711415982f983a5dfff72bdf41f0b454ec3e527389b65';assert digest(BASE)==parent
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());S.frame_set(1);bpy.context.view_layer.update()
 root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];root.animation_data_clear();target=bpy.data.objects['R06_TRACKING_TARGET'];target.location=(-200,100,250)
 d=bpy.data.cameras.new('R07B_FLIGHT_TRACK');d.lens=35;d.sensor_width=36;d.clip_start=.2;d.clip_end=150000;d.dof.use_dof=False
 cam=bpy.data.objects.new('R07B_FLIGHT_TRACK',d);bpy.data.collections['08_CAMERAS'].objects.link(cam);cam.parent=root
 con=cam.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
 for f in range(1,193):
  t=(f-1)/191;root.location=(-20900,-40000-640*t,8100+20*t);root.keyframe_insert(data_path='location',frame=f)
  cam.location=(-1100+120*t,-1600-60*t,300+20*t);cam.keyframe_insert(data_path='location',frame=f)
 # Large reflected-light cards follow the craft so material evaluation remains
 # comparable to the R07 studio/daylight test at this different shot location.
 for name,offset,power in [('R07 large reflected sky aperture',(-1700,-1600,2200),20000000),('R07 lower reflected city fill',(-800,-800,-700),7000000)]:
  o=bpy.data.objects[name];o.parent=root;o.matrix_parent_inverse.identity();o.location=offset;o.rotation_euler=(Vector((0,0,20))-Vector(offset)).to_track_quat('-Z','Y').to_euler();o.data.energy=power
 # Keep distant city texture readable: depth grading does not grow into opaque fog.
 for n in S.node_tree.nodes:
  if n.bl_idname=='CompositorNodeMapRange':n.inputs['From Min'].default_value=3000;n.inputs['From Max'].default_value=90000;n.inputs['To Max'].default_value=.12
 S.camera=cam;S.render.resolution_x=1920;S.render.resolution_y=1080;S.render.resolution_percentage=100
 checks=[]
 for f in [1,49,97,145,192]:
  S.frame_set(f);bpy.context.view_layer.update();ps=[p for o in bpy.data.collections['04_FREIGHTER'].objects if o.type=='MESH' and not o.hide_render for p in bb(o)]
  uv=[world_to_camera_view(S,cam,p) for p in ps];bounds=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
  rim=[Vector((10650*math.sin(a*math.pi/90),y,10000-10650*math.cos(a*math.pi/90))) for a in range(180) for y in [0,5000]]
  rv=[world_to_camera_view(S,cam,p) for p in rim];rb=[min(p.x for p in rv),max(p.x for p in rv),min(p.y for p in rv),max(p.y for p in rv)]
  assert min(bounds)>.01 and max(bounds)<.99,bounds
  assert min(rb)>-.05 and max(rb)<1.06,rb
  assert max(p.y for p in ps)<-30000
  checks.append({'frame':f,'ship_bounds_uv':bounds,'ring_bounds_uv':rb,'ship_matrix':matrix(root),'camera_matrix':matrix(cam),'habitat_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell'])})
 S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R07B_TRACKED_FREE_FLIGHT';S['source_sha']=os.environ['GITHUB_SHA']
 meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'current_motion':{'frames':192,'fps':24,'start':[-20900,-40000,8100],'end':[-20900,-40640,8120],'camera':cam.name,'heading':'WORLD_NEGATIVE_Y','already_released':True,'geometry_changed_from_R07':False,'checks':checks},'quality_status':'TRACKING_SHOT_REVIEW_REQUIRED_NOT_CORE_QUALIFIED'})
 p=OUT/'skyfold-r07b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=digest(p);(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R07B_SAVED',meta['scene_sha256'],flush=True)
else:
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
 defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='config'];exec(compile(ast.Module(body=defs,type_ignores=[]),'R06_RENDER_CONFIG','exec'),globals())
 if MODE=='probe':views=[(1,1920,24,False,True),(192,1280,32,False,True),(1,1280,24,True,False)]
 elif MODE=='hero':views=[(1,2560,96,False,True),(1,1280,32,False,False)]
 elif MODE=='motion':
  a=int(os.environ['FRAME_START']);b=int(os.environ['FRAME_END']);assert 1<=a<=b<=192;views=[(f,1920,24,False,True) for f in range(a,b+1)]
 else:raise ValueError(MODE)
 rows=[]
 for f,w,samples,neutral,grade in views:
  S.frame_set(f);S.camera=bpy.data.objects['R07B_FLIGHT_TRACK'];bpy.context.view_layer.update();config(w,samples,not neutral);S.render.use_compositing=grade;S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
  name=('frame_%04d'%f) if MODE=='motion' else 'R07B_f%03d_%s'%(f,'NEUTRAL' if neutral else 'BEAUTY' if grade else 'RAW')
  p=OUT/(name+'.png');S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-t;assert struct.unpack('>II',p.read_bytes()[16:24])==(w,w*9//16)
  rows.append({'file':p.name,'frame':f,'camera':S.camera.name,'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell']),'dimensions':[w,w*9//16],'samples':samples,'seconds':seconds,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sha256':digest(p),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'motion_blur':not neutral,'compositing':grade,'neutral':neutral,'visual_verdict':'NOT_OBSERVED'})
  (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R07B_FRAME',name,seconds,flush=True)
 S.view_layers[0].material_override=None;(OUT/'COMPLETE.json').write_text(json.dumps({'mode':MODE,'frame_count':len(rows),'seconds':sum(r['seconds'] for r in rows),'scene_sha256':meta['scene_sha256'],'run_id':os.environ['GITHUB_RUN_ID'],'auto_qualified':False},indent=2))
