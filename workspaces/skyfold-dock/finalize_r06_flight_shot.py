"""R06C: bounded correction of R06B framing and manufactured surfaces.
The new departure shot is not a replacement for the protected docked-scene checks.
"""
import bpy,bmesh,ast,os,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(bpy.data.filepath);PARENT='f110f64d0efa4557e52eb6b94f86fc8144bfded897ba31021f70d67f63cf81b6'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update()
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parent;C=bpy.data.collections['04_FREIGHTER'];CAM=bpy.data.collections['08_CAMERAS'];root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];new=[];cache={}
meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
# Reuse the candidate's finite mesh helpers, not its build/reset side effects.
names={'mesh','box','cylinder','mat'};defs=[n for n in ast.parse((ROOT/'refine_r06_departure.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in defs}==names
exec(compile(ast.Module(body=defs,type_ignores=[]),'R06B_SHIP_HELPERS','exec'),globals())
white=bpy.data.materials['R06B cargo ceramic'];dark=bpy.data.materials['R06B carbon machinery'];metal=bpy.data.materials['R06B titanium edge'];bronze=bpy.data.materials['R06B thermal bronze']
glass=mat('R06C bridge polarized glass',(.012,.043,.063),.60,.13)
# The legacy windows were left behind when R02 lengthened the bow; replace their placement.
for o in C.objects:
 if o.name.startswith(('Command crown','Recessed bridge window')):o.hide_render=True
v=[(-40,-365,52),(40,-365,52),(46,-299,52),(-46,-299,52),(-32,-357,74),(32,-357,74),(34,-307,90),(-34,-307,90)]
mesh('R06C tapered flight bridge',v,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],dark,1.1)
mesh('R06C bridge forward glazing',[(-30,-359,70),(30,-359,70),(30,-349,78),(-30,-349,78)],[(0,1,2,3)],glass)
for side in [-1,1]:
 for j in range(4):
  y=-341+j*8;box('R06C bridge side glass',(side*(34+(y+349)*.08),y,77+(y+349)*.21),(1,6,8),glass,.2)
box('R06C bridge top visor',(0,-326,91),(79,50,3),metal,.8)
# Recessed caps/locking rings and local manifolds remove the raw cylinder end appearance.
for i in range(6):
 y=-205+i*96
 for side in [-1,1]:
  x=side*39
  cylinder('R06C recessed cargo cap',(x,y-39,74),18,2.2,dark,32)
  cylinder('R06C cargo cap crown',(x,y-40.5,74),14.2,2,white,32)
  cylinder('R06C cargo pressure valve',(x,y-42,74),4.2,4,bronze,24)
  for a in range(0,360,60):
   t=math.radians(a);cylinder('R06C flange fastener',(x+20*math.cos(t),y-40,74+20*math.sin(t)),1.05,2.0,metal,6)
  box('R06C cargo feeder conduit',(side*68,y,43),(4,85,5),bronze,.5)
# A pair of radiating trusses makes the rear silhouette distinct without growing a second asset.
for side in [-1,1]:
 verts=[(side*95,255,60),(side*190,275,103),(side*181,401,96),(side*99,414,61)]
 verts+= [(x,y,z-5) for x,y,z in verts]
 mesh('R06C canted heat radiator',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],dark,.8)
 for j in range(9):
  y=280+j*13;box('R06C thermal radiator ribs',(side*145,y,79),(79,1.5,3),metal,.25).rotation_euler.y=-side*.42
# Repair orientability on new manufactured mesh components; leave all parent meshes untouched.
seen=set();normal_repairs=[]
for o in C.objects:
 if o.type!='MESH' or not o.name.startswith(('R06B','R06C')) or o.data.as_pointer() in seen:continue
 seen.add(o.data.as_pointer());bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();normal_repairs.append(o.data.name)
# Tone the broad ring substrate separately from building facades, avoiding a uniformly white wall.
substrate=mat('R06C ring charcoal composite',(.13,.17,.18),.25,.63)
changed=[]
for o in bpy.data.collections['01_RING_STRUCTURE'].objects:
 for slot in o.material_slots:
  if slot.material and slot.material.name=='Pale structural composite':slot.link='OBJECT';slot.material=substrate;changed.append(o.name)
# Geometric frame design: both front and back ring rims and the complete freighter fit.
# Flight begins already released; moving it here is the explicitly declared shot staging.
root.animation_data_clear();target=bpy.data.objects['R06_TRACKING_TARGET'];target.location=(-150,150,300)
d=bpy.data.cameras.new('R06C_DEPARTURE_TRACK');d.lens=35;d.sensor_width=36;d.clip_start=.2;d.clip_end=30000
cam=bpy.data.objects.new('R06C_DEPARTURE_TRACK',d);CAM.objects.link(cam);cam.parent=root
con=cam.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
for f in range(1,193):
 t=(f-1)/191;root.location=(-2500,-4500-640*t,1300+30*t);root.keyframe_insert(data_path='location',frame=f)
 cam.location=(-1300+70*t,-1500-60*t,350+20*t);cam.keyframe_insert(data_path='location',frame=f)
S.camera=cam;S.render.resolution_x=1920;S.render.resolution_y=1080;S.render.resolution_percentage=100
checks=[]
for f in [1,49,97,145,192]:
 S.frame_set(f);bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(v) for o in C.objects if o.type=='MESH' and not o.hide_render for v in o.bound_box]
 uv=[world_to_camera_view(S,cam,p) for p in points];bounds=[min(v.x for v in uv),max(v.x for v in uv),min(v.y for v in uv),max(v.y for v in uv)]
 rim=[Vector((1650*math.cos(a*math.pi/90),y,1600+1650*math.sin(a*math.pi/90))) for y in [0,5000] for a in range(180)]
 ru=[world_to_camera_view(S,cam,p) for p in rim];rb=[min(v.x for v in ru),max(v.x for v in ru),min(v.y for v in ru),max(v.y for v in ru)]
 assert .015<min(bounds) and max(bounds)<.985,bounds
 assert .015<min(rb) and max(rb)<.985,rb
 assert max(v.y for v in points)<0
 checks.append({'frame':f,'ship_bounds_uv':bounds,'ring_bounds_uv':rb,'camera_matrix':[list(r) for r in cam.matrix_world],'ship_matrix':[list(r) for r in root.matrix_world],'stern_y':max(v.y for v in points)})
S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R06C_FORWARD_FLIGHT_TRACKED';S['source_sha']=os.environ['GITHUB_SHA']
meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'R06C_corrections':{'camera':cam.name,'whole_ring_and_ship_checks':checks,'new_ship_parts':len(new),'reoriented_meshes':normal_repairs,'ring_substrate_objects':changed,'city_geometry_changed':False},'current_motion':{'frames':192,'fps':24,'direction':'WORLD_NEGATIVE_Y','delta_m':[0,-640,30],'stationary_habitat':True,'start_after_release':True},'quality_status':'ACTUAL_RENDERS_REQUIRED_NO_AUTOMATIC_ART_PASS'})
p=OUT/'skyfold-r06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('R06C_SAVED',meta['scene_sha256'],flush=True)
