"""Bounded R01 -> R02 spatial revision. Execute in Blender after loading frozen R01.
Uses the verified R01 native mesh/instance helpers, not a second scene engine.
R02 is a structural candidate; no automatic visual PASS.
"""
import bpy, ast, hashlib, json, os, math, random, time
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ['SKYFOLD_OUT']).resolve();OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'output/r01/skyfold-r01.blend'
assert bpy.app.version[:3]==(4,5,13),bpy.app.version_string
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='84f4e77811724dc632de8abd3885b0a87783ccc937b45f2f82473a544e3fb42a'
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
source=(ROOT/'build_scene_r01.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
SC=bpy.context.scene;R=1600.;WIDTH=1800.;SEED=270910;random.seed(SEED)
COL={c.name:c for c in bpy.data.collections};CACHE={}
M=[bpy.data.materials[n] for n in ['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay']]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY=range(11)
D='03_DOCK';S='04_FREIGHTER';N='05_MAINTENANCE';T='06_TRANSPORT'
# Reuse precisely the inspected pure definitions; do not execute the R01 scene reset/build.
wanted={'mat','Mesh','box','beam','tube','ring_strip','frame','rail_pair'}
tree=ast.parse(source);defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted]
assert {n.name for n in defs}==wanted
exec(compile(ast.Module(body=defs,type_ignores=[]),'VERIFIED_R01_HELPERS','exec'),globals())
PARK=mat('Recessed planted courtyards',(.10,.16,.125),.0,.93)
ROAD=mat('City basalt roadbed',(.075,.09,.10),.05,.8)
# Keep all original cameras for same-matrix regression. They are never silently replaced.
original_cameras={o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens} for o in COL['08_CAMERAS'].objects}
for o in list(COL['08_CAMERAS'].objects):
 o.name='R01_'+o.name;o.data=o.data.copy()
def camera(name,pos,target,lens):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.08;d.clip_end=20000
 o=bpy.data.objects.new(name,d);COL['08_CAMERAS'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def remove(o):bpy.data.objects.remove(o,do_unlink=True)
# Replace the uniform shelf distribution with finite rigid neighbourhood prototypes.
# Each neighbourhood has real footprint/podium and several building silhouettes.
for o in list(COL['02_CITY_INSTANCES'].objects):remove(o)
for o in list(COL['01_RING_STRUCTURE'].objects):
 if o.name.startswith(('Circumferential transport avenue','Avenue centre guide')):remove(o)
for y in [55,285,515,745,975,1205,1435,1665]:
 ring_strip('R02 city transport corridor',R-3,R-2,y-10,y+10,ROAD)
 ring_strip('R02 city median',R-3.2,R-3,y-.8,y+.8,CONCRETE)
old_prototypes=[bpy.data.objects['City archetype %02d'%i] for i in range(10)]
new_prototypes=[]
for k in range(12):
 rng=random.Random(SEED+100*k);g=Mesh();g.box((0,0,0),(190,180,6),CONCRETE)
 # Staggered six-lot urban blocks, with courtyards and varied tower frequency.
 for ix,x in enumerate([-64,0,64]):
  for iy,y in enumerate([-43,43]):
   if (k+ix+iy)%7==0:
    g.box((x,y,3.25),(49,61,.5),PARK);continue
   p=old_prototypes[rng.choice([[0,1,5,7],[1,2,3,6],[2,4,8,9]][k%3])].data
   xy=rng.uniform(.55,.76);height=rng.uniform(.50,.88)
   if ix==1 and k in [2,5,8,11]:height=1.28
   v=[(x+a.co.x*xy,y+a.co.y*xy,3+a.co.z*height) for a in p.vertices]
   offset=len(g.v);g.v.extend(v)
   for f in p.polygons:g.f.append(tuple(offset+i for i in f.vertices));g.mi.append(f.material_index)
  # local pedestrian streets, not random pipes on rooftops
  g.box((x,0,3.12),(51,7,.24),ROAD)
 o=g.object('R02 urban block prototype %02d'%k,'09_PROTOTYPES');o.hide_render=True;o.hide_viewport=True;new_prototypes.append(o)
blocks=0
for i in range(46):
 theta=(i+.5)*2*math.pi/46
 for j in range(7):
  if min(theta,2*math.pi-theta)<.60:continue # coherent industrial reserve
  k=(i//4+j*3+i%3)%12
  o=bpy.data.objects.new('R02 neighbourhood %03d'%blocks,new_prototypes[k].data);COL['02_CITY_INSTANCES'].objects.link(o)
  o.matrix_world=frame(theta+(j%2)*.006,170+j*230,1.4)
  o['prototype']=new_prototypes[k].name;o['ground_theta']=theta;o['local_up']='INWARD_RADIAL';blocks+=1
# Real external edge buttress details expose structural depth in side/back observations.
for i in range(32):
 F=frame(i*2*math.pi/32,0,-40)
 for y in [4,WIDTH-4]:
  g=Mesh();g.box((0,0,0),(18,38,106),DARK);g.box((0,0,55),(32,44,5),PAINT)
  o=g.object('R02 rim buttress','01_RING_STRUCTURE');o.matrix_world=F@Matrix.Translation((0,y,0))

# The berth is a high-level assembly dock; its actual foundations remain on the ring.
RAISE=350.
for o in list(COL[D].objects):
 if o.name.startswith(('Gantry','Travelling crane','Crane hoist','Cargo spreader','Dock diagonal brace')):
  remove(o);continue
 if o.name.startswith('Pylon foundation'):continue
 if o.name.startswith('Dock grounded pylon'):
  old_height=o.dimensions.z;o.scale.z*=(old_height+RAISE)/old_height;o.location.z+=RAISE/2
 else:o.location.z+=RAISE
for x in [0,560]:
 for y in [170,430,700,970,1230,1570]:
  ground=R-math.sqrt(R*R-x*x)
  beam('R02 rooted pier diagonal',(x-48,y-36,ground+5),(x+43,y+36,492),9,9,SILVER,D)
# One aft portal and two far-side cantilever cranes; the forward hull has no enclosing portal.
for x in [-45,605]:
 box('R02 aft gantry footing',(x,1410,514),(55,70,10),ORANGE,D,2)
 box('R02 aft gantry column',(x,1410,655),(22,24,274),PAINT,D,2)
box('R02 aft lifting beam',(280,1410,797),(680,34,26),DARK,D,2)
for x in range(-40,605,46):beam('R02 aft beam bracing',(x,1388,786),(x+40,1388,808),3,4,SILVER,D)
for y in [620,1010]:
 x=605
 box('R02 far crane rooted tower',(x,y,615),(23,27,210),PAINT,D,2)
 box('R02 far crane boom',(427,y,724),(378,25,21),DARK,D,2)
 beam('R02 far crane diagonal',(605,y,677),(260,y,718),5,6,SILVER,D)
 box('R02 crane trolley',(322,y,713),(40,42,24),ORANGE,D,2)
 tube('R02 inactive hoist cable',[(310,y,700),(310,y,668)],.45,DARK,D)
for o in COL[S].objects:o.location.z+=RAISE
hull=bpy.data.objects['Freighter tapered pressure hull']
# Extend only the bow taper, rather than scaling the whole ship or its loading interfaces.
for v in hull.data.vertices:
 if v.co.y<745:v.co.y-=.60*(745-v.co.y)
hull.data.update()
# A continuous silhouette-defining dorsal spine connects the cargo bays to the command crown.
box('R02 freighter dorsal spine',(280,1080,672),(23,580,16),DARK,S,2)
for y in [850,1046,1242]:
 box('R02 spine cross saddle',(280,y,669),(124,19,10),PAINT,S,2)

# Move the human-scale platform into the inhabited band, retaining its real metre-scale parts.
DELTA=Vector((384,543,27.25))
for o in list(COL[N].objects):
 if o.name.startswith(('Catwalk grounded support','Catwalk diagonal grounded support','Cantilever bottom chord')):remove(o)
 else:o.location+=DELTA
for y in range(190,605,69):
 x=-306;ground=R-math.sqrt(R*R-x*x)
 box('R02 catwalk ring foundation',(x,y,ground+2),(16,14,4),CONCRETE,N,.12)
 box('R02 catwalk supported pylon',(x,y,(ground+4+191)/2),(2.8,3.2,191-ground-4),DARK,N,.08)
 beam('R02 catwalk transverse brace',(x-7,y-5,ground+4),(x+7,y+5,191),1,1,SILVER,N)
# Preserve cargo on the raised dock. Rebuild only the old broken/same-level transport route.
for o in list(COL[T].objects):
 if o.name.startswith(('Cargo staging pallet','Dock cargo container','Container side stiffener')):o.location.z+=RAISE
 else:remove(o)
LOW=194.43;HIGH=512.065
# Rounded rail bend: 12m radius, horizontal approach then cargo elevator.
route=[(-304,167,LOW),(-304,608,LOW)]
for i in range(1,13):
 t=math.pi-(math.pi/2)*i/12;route.append((-292+12*math.cos(t),608+12*math.sin(t),LOW))
route.append((-86,620,LOW));rail_pair(route)
box('R02 lower turn landing',(-302,611,LOW-.565),(24,36,1),DECK,T,.08)
beam('R02 lower transfer bridge',(-292,620,LOW-.565),(-86,620,LOW-.565),8,1,DECK,T)
for x in [-276,-218,-160,-100]:
 ground=R-math.sqrt(R*R-x*x)
 box('R02 transfer foundation',(x,620,ground+2),(12,12,4),CONCRETE,T,.1)
 box('R02 transfer pylon',(x,620,(ground+4+192.7)/2),(2.6,3,192.7-ground-4),DARK,T,.08)
for y in [616.3,623.7]:
 tube('R02 transfer handrail',[(-292,y,LOW+1.04),(-86,y,LOW+1.04)],.045,ORANGE,T)
 for x in range(-290,-88,4):box('R02 transfer handrail post',(x,y,LOW+.5),(.075,.075,1.1),SILVER,T,.01)
# An explicit two-level freight lift; lower and upper tracks do not falsely claim continuity.
for x in [-92,-80]:
 for y in [614,626]:
  ground=R-math.sqrt(R*R-x*x)
  box('R02 lift ring footing',(x,y,ground+2),(8,8,4),CONCRETE,T,.2)
  box('R02 lift guide tower',(x,y,(ground+4+HIGH+10)/2),(1.5,1.5,HIGH+10-ground-4),DARK,T,.1)
for level in [LOW,HIGH]:
 for x in [-92,-80]:box('R02 lift landing edge',(x,620,level-.34),(2,14,.55),PAINT,T,.08)
 for y in [614,626]:box('R02 lift landing edge',(-86,y,level-.34),(10,2,.55),PAINT,T,.08)
box('R02 cargo elevator cabin',(-86,620,LOW-.215),(9.6,9.6,.3),ORANGE,T,.07)
for z in range(210,510,24):
 beam('R02 lift side lattice',(-92,614,z),(-92,626,z+22),.55,.55,SILVER,T)
 beam('R02 lift side lattice',(-80,626,z),(-80,614,z+22),.55,.55,SILVER,T)
upper=[(-79,620,HIGH),(-60,620,HIGH)]
for i in range(1,13):
 t=-math.pi/2+(math.pi/2)*i/12;upper.append((-60+14*math.cos(t),634+14*math.sin(t),HIGH))
upper.append((-46,1602,HIGH));rail_pair(upper)
box('R02 upper lift transfer',(-58.5,629,HIGH-.565),(41,30,1),DECK,T,.08)
# Upper track x=-46 avoids the actual loader tower bases and cargo piles.

# New G2 camera proposal, with frozen R01 observations retained alongside it.
HERO=Vector((-310,220,196));TARGET=Vector((200,1450,930))
camera('O01_HERO',HERO,TARGET,18)
camera('O01_CAMERA_B',HERO,(200,1450,820),17)
camera('O01_CAMERA_C',HERO,(400,1450,980),17)
# Preserve second/back conditions exactly; these are full-structure regression views.
for n in ['O01_SECOND','O03_REAR']:
 old=bpy.data.objects['R01_'+n];o=old.copy();o.data=old.data.copy();o.name=n;COL['08_CAMERAS'].objects.link(o)
camera('O04_CRAFT',(-311,241,196.6),(-304,257,195.75),41)
camera('O04_INTERFACE',(75,565,623),(204,804,600),43)
camera('O05_ROUTE',(-650,-50,740),(130,1040,360),30)
camera('O05_LIFT',(-188,484,375),(-66,620,360),38)
for i in range(5):
 pos=HERO+Vector(((i-2)*7.5,0,(i-2)*.12));camera('O06_%03d'%(i*25),pos,pos+(TARGET-HERO),18)
# Keep R01 lighting/materials for structural comparability. No fog or generative post-processing.
SC.camera=bpy.data.objects['O01_HERO'];SC.cycles.seed=SEED;SC.cycles.samples=24
SC['candidate']='R02_SPATIAL_STUDY';SC['source_sha']=os.environ['GITHUB_SHA'];SC['quality_status']='G2_REVIEW_REQUIRED'
SC.render.use_compositing=False
bpy.context.view_layer.update()
# Native validation: real geometry, inward normals, frozen old cameras, finite transforms.
for old,record in original_cameras.items():
 o=bpy.data.objects['R01_'+old]
 assert max(abs(o.matrix_world[r][c]-record['matrix'][r][c]) for r in range(4) for c in range(4))<1e-6
for o in COL['02_CITY_INSTANCES'].objects:
 inward=Vector((-o.location.x,0,R-o.location.z)).normalized()
 assert o.matrix_world.to_3x3().col[2].normalized().dot(inward)>.999
for o in SC.objects:assert all(math.isfinite(v) for row in o.matrix_world for v in row),o.name
manifest={'candidate':'R02_SPATIAL_STUDY','source_sha':os.environ['GITHUB_SHA'],'blender':bpy.app.version_string,'parent_scene_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'reused_helper_sha256':hashlib.sha256(source).hexdigest(),'seed':SEED,'geometry':{'ring_radius_m':R,'band_width_m':WIDTH,'neighbourhood_instances':blocks,'objects':len(SC.objects),'meshes':len(bpy.data.meshes)},'scales':{'guardrail_m':1.1,'rail_gauge_m':1.44,'ring_diameter_m':3200,'freighter_hull_length_m':875,'freighter_total_length_m':907,'berth_raise_m':RAISE},'functional_route':{'lower':route,'lift_lower':[-86,620,LOW],'lift_upper':[-86,620,HIGH],'upper':upper,'loader_centres':[[198,790,602],[362,790,602],[198,1200,602],[362,1200,602]]},'cameras':{},'external_files':[],'tests':{'old_camera_matrices_preserved':True,'inward_neighbourhood_frames':True,'finite_transforms':True},'quality_map':{'ring':'full original shell/backbone with edge buttresses','city':'shared rigid neighbourhood blocks; external-only architecture','dock':'raised structural berth, rooted columns, reworked crane hierarchy; requires intersection review','freighter':'R01 closed hull with extended bow and silhouette spine; material/near craft pending','near':'R01 metre-scale cart/railings moved inside actual ring; new grounded supports and explicit freight lift'},'visual_gate':'NOT_REVIEWED','review_mode':'SEQUENTIAL_SELF_REVIEW'}
for o in COL['08_CAMERAS'].objects:manifest['cameras'][o.name]={'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens}
path=OUT/'skyfold-r02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
manifest['scene_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('R02_SAVED',manifest['scene_sha256'],len(SC.objects),'VISUAL_REVIEW_REQUIRED')
