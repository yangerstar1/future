"""R04: user-directed cinematic camera, coherent habitat rotation and working-city detail.
Input is the immutable R03B scene. Original cameras and original snapshot survive.
The animation is an art-direction study, NOT a substitute for unfinished G1-G6 gates.
"""
import bpy, ast, json, hashlib, math, os, random
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'output/r03b/skyfold-r03b.blend'
PARENT='dca722c1cbfada7ce9a5a9b16926b136a29fd1ee256d5073c9b41852e5c64c68'
assert bpy.app.version[:3]==(4,5,13)
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
source=(ROOT/'build_scene_r01.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
SC=bpy.context.scene;COL={c.name:c for c in bpy.data.collections};CACHE={};R=1600.;WIDTH=1800.;SEED=270910
names=['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay','Recessed planted courtyards','City basalt roadbed']
M=[bpy.data.materials[n] for n in names]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY,PARK,ROAD=range(13)
wanted={'mat','Mesh','box','beam','tube','ring_strip','frame'}
defs=[n for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted]
assert {n.name for n in defs}==wanted
exec(compile(ast.Module(body=defs,type_ignores=[]),'VERIFIED_R01_HELPERS','exec'),globals())
for name in ['10_R04_GALLERY','11_R04_MOTION','12_R04_CITY_SERVICE']:
 c=bpy.data.collections.new(name);SC.collection.children.link(c);COL[name]=c
N='10_R04_GALLERY';S='04_FREIGHTER';D='03_DOCK'
# Material changes are declared, not a claimed single-variable camera comparison.
for idx,color,metal,rough in [(PAINT,(.66,.69,.65),.40,.30),(DARK,(.036,.052,.064),.72,.36),(CONCRETE,(.30,.36,.39),.06,.76),(CITY,(.44,.53,.57),.25,.43),(ORANGE,(.56,.15,.033),.33,.45),(GLASS,(.024,.078,.094),.65,.19),(SILVER,(.38,.48,.52),.91,.26)]:
 p=M[idx].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
BLUE=mat('R04 cyan municipal indicators',(.14,.47,.58),.1,.34,1.6)
STONE=mat('R04 warm mineral city infill',(.38,.36,.30),.08,.82)
DARKRED=mat('R04 ochre cargo registration',(.30,.055,.024),.28,.42)
# Metre-scale low buildings between towers make a city, rather than uniform tall shelves.
for k in range(12):
 proto=bpy.data.objects['R02 urban block prototype %02d'%k];old=proto.data;g=Mesh()
 g.v=[tuple(v.co) for v in old.vertices];g.f=[tuple(p.vertices) for p in old.polygons]
 g.mi=[M.index(old.materials[p.material_index]) for p in old.polygons]
 rng=random.Random(SEED+900+k)
 for y in [-76,76]:
  for x in [-72,-24,24,72]:
   h=rng.uniform(9,23);w=rng.uniform(18,29);d=17
   g.bevel_tower((x,y,3),w,d,h,1.1,STONE if (k+int(x))%3==0 else CITY)
   g.box((x,y,3+h+.55),(w+1,d+1,1.1),PAINT)
   for z in range(7,int(h)+1,5):g.box((x,y-8.6,z),(w-3,.28,1.25),GLASS)
   g.box((x+3,y,4+h),(5,6,1.3),DARK)
   for v in [-2,0,2]:g.box((x+3+v,y,4.85+h),(.6,5.5,.4),SILVER)
 for x in [-92,92]:
  g.box((x,0,3.15),(2.0,163,.3),ROAD)
  for y in [-58,0,58]:g.box((x,y,3.5),(.65,12,.18),LIGHT if k%3==0 else BLUE)
 new=g.object('_R04_city_prototype','09_PROTOTYPES');mesh=new.data
 for o in list(bpy.data.objects):
  if o.type=='MESH' and o.data==old:o.data=mesh
 bpy.data.objects.remove(new,do_unlink=True)
# Keep the closed main hull and matching loader interfaces. Add organized service bands.
profile=[(-.74,-1),(.74,-1),(1,-.68),(1,.68),(.74,1),(-.74,1),(-1,.68),(-1,-.68)]
for j,y in enumerate([790,888,986,1084,1182,1280,1360]):
 g=Mesh()
 for i,(a,b) in enumerate(profile):
  c,d=profile[(i+1)%8]
  p=[(280+a*81,yy,610+b*53) for yy in [y-2,y+2]]
  q=[(280+c*81,yy,610+d*53) for yy in [y-2,y+2]]
  g.poly([p[0],q[0],q[1],p[1]],[(0,1,2,3)],DARKRED if j in [0,5] else DARK)
 o=g.object('R04 structural cargo band %02d'%j,S);m=o.modifiers.new('Band physical gauge','SOLIDIFY');m.thickness=.8
for side in [-1,1]:
 x=280+side*88
 for j,y in enumerate(range(820,1321,100)):
  box('R04 service shoulder cover',(x,y,634),(3,66,12),DARK,S,.35)
  for yy in range(-27,28,9):box('R04 louver blade',(x+side*1.9,y+yy,634),(.7,2,8.5),SILVER,S,.14)
  box('R04 service threshold',(x,y,575),(3,76,4.2),SILVER,S,.4)
  for yy in [-31,31]:box('R04 recessed work beacon',(x+side*1.7,y+yy,642),(.6,3,1.4),LIGHT,S,.12)
for y in [620,650,682,710]:
 w=22+(y-585)/(745-585)*(76-22);h=18+(y-585)/(745-585)*(48-18)
 for side in [-1,1]:
  tube('R04 tapered bow service seam',[(280+side*w*.78,y,610+h+1),(280+side*w*.78,y+10,610+h+3)],.7,DARK,S)
def text(name,body,pos,size,col,material,orientation=None):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.018;cu.space_character=1.15;cu.materials.append(M[material]);o=bpy.data.objects.new(name,cu);COL[col].objects.link(o);o.location=pos
 if orientation is not None:o.rotation_euler=orientation.to_euler()
 return o
port_basis=Matrix(((0,0,-1),(-1,0,0),(0,1,0)))
text('R04 vessel registration','SFD / 07',(188.8,1118,615),12,S,PAINT,port_basis)
text('R04 freight operator','SKYFOLD  /  ORBITAL LOGISTICS',(188.7,1258,590),4.4,S,PAINT,port_basis)
# New gallery belongs to the same habitat. Existing maintenance/cargo chain is retained.
POS=Vector((-930,500,650));TARGET=Vector((180,1150,900));LENS=22.;ROLL=math.radians(-25)
fwd=Vector((TARGET.x-POS.x,TARGET.y-POS.y,0)).normalized();right=Vector((fwd.y,-fwd.x,0));UP=Vector((0,0,1));floor=POS-UP*1.7
F=Matrix(((right.x,fwd.x,0,floor.x),(right.y,fwd.y,0,floor.y),(0,0,1,floor.z),(0,0,0,1)))
def q(v):return F@Vector(v)
def local_box(name,p,size,material,bevel=0):
 o=box(name,(0,0,0),size,material,N,bevel);o.matrix_world=F@Matrix.Translation(p);return o
local_box('R04 observation landing',(0,0,-.7),(18,34,1.4),DARK,.06)
for x in [-8.5,8.5]:local_box('R04 underside box girder',(x,0,-2.0),(.8,36,2.2),SILVER,.06)
for y in range(-14,15,2):
 local_box('R04 walking deck panel',(0,y,.065),(17.6,1.95,.13),DECK,.025)
 for x in [-7.9,7.9]:local_box('R04 safety stripe',(x,y,.14),(.28,1.8,.025),ORANGE,.008)
segments=[((-8.6,-16),(-8.6,16)),((8.6,-16),(8.6,16)),((-8.6,16),(8.6,16))]
for a,b in segments:
 length=math.dist(a,b);count=math.ceil(length/2)
 for z,r in [(1.1,.045),(.59,.026)]:tube('R04 gallery handrail',[tuple(q((*a,z))),tuple(q((*b,z)))],r,ORANGE if z>1 else SILVER,N)
 for i in range(count+1):
  t=i/count;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
  local_box('R04 gallery upright',(x,y,.55),(.09,.09,1.1),SILVER,.013)
  local_box('R04 gallery footplate',(x,y,.08),(.30,.30,.16),SILVER,.018)
for p,size,ma in [((-4.5,7,.55),(2.3,3.7,.42),DARK),((-4.5,7,.90),(2.7,4.0,.22),ORANGE),((-4.5,7,1.55),(2.2,2.9,1.12),PAINT),((-4.5,5.4,1.19),(1.6,.7,.45),DARK)]:local_box('R04 mobile diagnostic trolley',p,size,ma,.065)
for x in [-5.30,-3.70]:
 for y in [5.9,8.1]:
  tube('R04 trolley tyre',[tuple(q((x-.15,y,.36))),tuple(q((x+.15,y,.36)))],.36,RUBBER,N)
  tube('R04 trolley hub',[tuple(q((x-.17,y,.36))),tuple(q((x+.17,y,.36)))],.17,SILVER,N)
for y in [5.7,6.3,6.9,7.5,8.1]:local_box('R04 trolley lid rib',(-4.5,y,2.14),(2.1,.06,.08),SILVER,.012)
for x in [-5.1,-3.9]:local_box('R04 trolley marker',(x,5,1),(.18,.05,.1),LIGHT,.015)
bridge_start=q((0,-16,-.6));anchor=Vector((-885,600,648.0))
beam('R04 gallery access bridge',bridge_start,anchor,8,1.2,DARK,N)
for y in [475,550,615]:
 x=-885;ground=R-math.sqrt(R*R-x*x)
 box('R04 gallery ring footing',(x,y,ground+3),(23,23,6),CONCRETE,N,.3)
 box('R04 gallery rooted tower',(x,y,(ground+6+646)/2),(5.2,5.2,646-ground-6),DARK,N,.1)
 beam('R04 gallery support head',(x,y,645),q((0,max(-12,min(12,y-540)),-2)),3.2,3.2,SILVER,N)
for y in [595,605]:
 ground=R-math.sqrt(R*R-885**2)
 box('R04 gallery lift guide',(-875,y,(ground+650)/2),(1,1,650-ground),SILVER,N,.05)
box('R04 gallery lift landing',(-880,600,647.5),(12,14,1),ORANGE,N,.1)
# Directional light enters the open cylinder; no volumetric effects hide geometry.
for o in COL['07_LIGHTS'].objects:
 if o.data.type=='AREA':o.data.energy*=.35
sun=bpy.data.objects['Broad solar key'];sun.data.energy=3.2;sun.data.angle=.035;sun.data.color=(1,.86,.67);sun.rotation_euler=Vector((.25,.68,-.69)).to_track_quat('-Z','Y').to_euler()
def area(name,pos,target,energy,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);COL['07_LIGHTS'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('R04 warm axial opening',(-1000,-1600,1900),(0,1050,1300),130000000,1700,(1,.81,.61))
area('R04 cool reflected city fill',(-1250,550,1550),(240,1050,640),7500000,950,(.37,.65,1))
area('R04 gallery soft bounce',tuple(POS+Vector((-14,-8,16))),tuple(POS),2200,18,(.70,.84,1))
w=SC.world;nodes=w.node_tree.nodes;links=w.node_tree.links;bg=nodes.get('Background');bg.inputs[0].default_value=(.19,.26,.35,1);bg.inputs[1].default_value=.28
lp=nodes.new('ShaderNodeLightPath');cam_bg=nodes.new('ShaderNodeBackground');cam_bg.name='R04 deep space visible background';cam_bg.inputs[0].default_value=(.012,.022,.037,1);cam_bg.inputs[1].default_value=.6
mix=nodes.new('ShaderNodeMixShader');links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);links.new(bg.outputs[0],mix.inputs[1]);links.new(cam_bg.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('World Output').inputs['Surface'])
def camera(name,pos,target,lens,roll=0):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.08;d.clip_end=20000;o=bpy.data.objects.new(name,d);COL['08_CAMERAS'].objects.link(o);o.location=pos;o.rotation_mode='QUATERNION';o.rotation_quaternion=(Vector(target)-o.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),roll);return o
hero=camera('R04_HERO',POS,TARGET,LENS,ROLL)
camera('R04_SECOND',(-1300,-1900,1500),(100,850,1450),31,math.radians(-9))
camera('R04_GALLERY_CRAFT',q((3.5,1,2.4)),q((-4.5,7,1.15)),44)
camera('R04_ROUTE_FULL',(-600,-450,1100),(30,1130,340),31)
camera('R04_RETURN_LIFT_FULL',(-265,1340,406),(-46,1608,390),26)
camera('R04_HERO_LEVEL',POS,TARGET,LENS,0)
# A coherent assembly, not a rotating city passing through fixed dock foundations.
rig=bpy.data.objects.new('R04_HABITAT_ROTATION',None);COL['11_R04_MOTION'].objects.link(rig);rig.location=(0,900,1600);bpy.context.view_layer.update()
joined=[]
for name in ['01_RING_STRUCTURE','02_CITY_INSTANCES','03_DOCK','04_FREIGHTER','05_MAINTENANCE','06_TRANSPORT',N,'12_R04_CITY_SERVICE']:
 for o in list(COL[name].objects):
  if o.parent:raise RuntimeError('Unexpected existing parent '+o.name)
  mw=o.matrix_world.copy();o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted();o.matrix_world=mw;joined.append(o.name)
SC.render.fps=24;SC.frame_start=1;SC.frame_end=192;rig.rotation_mode='XYZ';pivot=Vector((0,900,1600));motion=[]
for f in range(1,193):
 t=(f-1)/191;angle=math.radians(6)*t;rig.rotation_euler=(0,angle,0);rig.keyframe_insert(data_path='rotation_euler',frame=f)
 rot=Matrix.Rotation(angle,3,'Y');focus=pivot+rot@(TARGET-pivot)
 hero.location=POS+Vector((-18*t,15*t,5*t));hero.rotation_quaternion=(focus-hero.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),ROLL)
 hero.keyframe_insert(data_path='location',frame=f);hero.keyframe_insert(data_path='rotation_quaternion',frame=f)
 if f in [1,49,97,145,192]:motion.append({'frame':f,'rotation_degrees':6*t,'camera_position':list(hero.location),'focus':list(focus)})
SC.frame_set(1);bpy.context.view_layer.update();SC.camera=hero
SC.render.engine='CYCLES';SC.cycles.device='CPU';SC.cycles.samples=64;SC.cycles.use_denoising=True;SC.cycles.seed=SEED;SC.cycles.use_animated_seed=False;SC.cycles.use_adaptive_sampling=True;SC.cycles.adaptive_threshold=.035;SC.cycles.adaptive_min_samples=8
SC.cycles.max_bounces=5;SC.cycles.diffuse_bounces=2;SC.cycles.glossy_bounces=2;SC.render.use_persistent_data=True;SC.render.use_compositing=False;SC.render.use_motion_blur=False
SC.render.resolution_x=2560;SC.render.resolution_y=1440;SC.render.resolution_percentage=100;SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.render.image_settings.color_depth='8'
SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=.2
SC['candidate']='R04_CINEMATIC_MOTION_STUDY';SC['source_sha']=os.environ['GITHUB_SHA'];SC['auto_qualified']=False
for j in range(5):
 p=POS+right*(j-2)*1.2;camera('R04_PARALLAX_%03d'%(j*25),p,p+(TARGET-POS),LENS,ROLL)
bpy.context.view_layer.update()
manifest={'candidate':SC['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'blender':bpy.app.version_string,'scope':'user-authorized camera and movement revision; not a core gate pass','ring_motion':{'axis':'Y','pivot_m':list(pivot),'start_degrees':0,'end_degrees':6,'frames':192,'fps':24,'co_rotating_objects':len(joined),'coherent_dock_and_ship':True,'physics_validated':False},'camera_motion':motion,'cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in COL['08_CAMERAS'].objects},'original_cameras_preserved':True,'added_gallery':'metre-scale physical viewing landing with rooted supports and an access lift','external_files':[],'geometry':{'objects':len(SC.objects),'mesh_datablocks':len(bpy.data.meshes)},'render_status':'NOT_RENDERED','gate':'NOT_AUTO_QUALIFIED'}
path=OUT/'skyfold-r04.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);manifest['scene_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2));print('R04_BUILT',manifest['scene_sha256'],manifest['geometry'])
