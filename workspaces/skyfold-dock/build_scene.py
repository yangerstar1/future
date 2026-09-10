"""Skyfold Dock R00: native editable geometry. Provisional, never auto-qualifies art.
Run with Blender 4.5.13: blender -b --factory-startup -t 4 --python-exit-code 1 -P this_file
Only bpy, mathutils and Python stdlib. Distances in metres, deterministic seed.
"""
import bpy, math, random, json, os, time, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
R=1600.0; WIDTH=3200.0; SEED=270910; random.seed(SEED)
OUT=Path(os.environ.get('SKYFOLD_OUT','output/r00')).resolve(); OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene; SC.unit_settings.system='METRIC'; SC.unit_settings.scale_length=1.0
COL={}
for name in ['01_RING_STRUCTURE','02_CITY_INSTANCES','03_DOCK','04_FREIGHTER','05_MAINTENANCE','06_TRANSPORT','07_LIGHTS','08_CAMERAS','09_PROTOTYPES']:
 c=bpy.data.collections.new(name);SC.collection.children.link(c);COL[name]=c
M=[]
def mat(name,color,metal=.0,rough=.5,emission=0,bump=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 if bump:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=7;tex.inputs['Detail'].default_value=2
  b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=bump
  m.node_tree.links.new(tex.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 M.append(m);return len(M)-1
PAINT=mat('Pearl ceramic-coated alloy',(.58,.63,.64),.42,.36)
DARK=mat('Structural graphite steel',(.055,.080,.105),.85,.30)
CONCRETE=mat('Pale structural composite',(.30,.35,.38),.05,.72)
ORANGE=mat('Oxide orange workzone coating',(.60,.16,.034),.25,.47)
GLASS=mat('Inset blue-black facade glazing',(.018,.053,.074),.58,.21)
SILVER=mat('Brushed bare metal',(.39,.47,.50),.92,.27)
DECK=mat('Foot-worn dark deck metal',(.09,.13,.145),.7,.56,bump=.006)
LIGHT=mat('Warm service luminaires',(.85,.49,.18),.05,.30,2.3)
RUBBER=mat('Wheel rubber',(.018,.023,.026),.0,.85)
CITY=mat('City pale panels',(.40,.46,.48),.32,.49)
GRAY=mat('Neutral inspection clay',(.50,.50,.50),.0,.68)

class Mesh:
 def __init__(self):self.v=[];self.f=[];self.mi=[]
 def poly(self,verts,faces,material):
  off=len(self.v);self.v.extend(verts);self.f.extend([tuple(off+i for i in f) for f in faces]);self.mi.extend([material]*len(faces))
 def box(self,p,s,m):
  x,y,z=p;a,b,c=[v/2 for v in s]
  v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
  self.poly(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
 def bevel_tower(self,p,w,d,h,b,m):
  x,y,z=p;w/=2;d/=2;b=min(b,w*.4,d*.4)
  xy=[(-w+b,-d),(w-b,-d),(w,-d+b),(w,d-b),(w-b,d),(-w+b,d),(-w,d-b),(-w,-d+b)]
  v=[(x+a,y+c,z+k) for k in [0,h] for a,c in xy]
  f=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
  self.poly(v,f,m)
 def object(self,name,col):
  me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(self.v,[],self.f);me.update()
  for ma in M:me.materials.append(ma)
  for p,k in zip(me.polygons,self.mi):p.material_index=k
  o=bpy.data.objects.new(name,me);COL[col].objects.link(o);return o
CACHE={}
def box(name,p,s,m,col,bevel=0):
 key=(tuple(round(x,5) for x in s),m,round(bevel,5))
 if key in CACHE:me=CACHE[key]
 else:
  g=Mesh();g.box((0,0,0),s,m);temp=g.object('_cache',col);me=temp.data
  if bevel:
   bpy.context.view_layer.objects.active=temp;temp.select_set(True);mod=temp.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=2
   bpy.ops.object.modifier_apply(modifier=mod.name);temp.select_set(False);me=temp.data
  bpy.data.objects.remove(temp,do_unlink=True);CACHE[key]=me
 o=bpy.data.objects.new(name,me);COL[col].objects.link(o);o.location=p;return o

def beam(name,a,b,width,depth,m,col):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),m,col);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def tube(name,points,radius,m,col):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=2;cu.use_fill_caps=True
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 cu.materials.append(M[m]);o=bpy.data.objects.new(name,cu);COL[col].objects.link(o);return o

def ring_strip(name,ra,rb,y0,y1,m,segments=768):
 g=Mesh()
 for i in range(segments):
  t=2*math.pi*i/segments;u=2*math.pi*(i+1)/segments
  def q(r,y,a):return(r*math.sin(a),y,R-r*math.cos(a))
  v=[q(ra,y0,t),q(ra,y0,u),q(ra,y1,u),q(ra,y1,t),q(rb,y0,t),q(rb,y0,u),q(rb,y1,u),q(rb,y1,t)]
  g.poly(v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)],m)
 return g.object(name,'01_RING_STRUCTURE')

def frame(theta,y,z=0):
 c,s=math.cos(theta),math.sin(theta)
 return Matrix(((c,0,-s,(R-z)*s),(0,1,0,y),(s,0,c,R-(R-z)*c),(0,0,0,1)))

# One thick cylindrical ring band, with shared front/back fascia and external load paths.
ring_strip('Continuous inhabited ring shell',R,R+64,0,WIDTH,CONCRETE)
for y in [-4,WIDTH-28]:ring_strip('Deep ring edge girder',R-8,R+102,y,y+32,DARK)
for y in [20,WIDTH-42]:ring_strip('Ceramic edge cap',R-11,R+2,y,y+18,PAINT)
for y in [480,1040,1600,2160,2720]:
 ring_strip('Circumferential transport avenue',R-2,R-.1,y-14,y+14,DARK)
 ring_strip('Avenue centre guide',R-2.25,R-2.0,y-.9,y+.9,ORANGE)
for i in range(48):
 t=i*2*math.pi/48;F=frame(t,0,-83)
 for y in [18,800,1600,2400,3182]:
  a=F@Vector((0,y,0));b=F@Vector((0,min(y+760,3200),0));beam('External axial backbone',a,b,20,28,DARK,'01_RING_STRUCTURE')
 # transverse sector seam is actual narrow raised geometry, not flat reference projection
 seam=box('Sector seam',(0,0,0),(3.0,WIDTH,1.0),SILVER,'01_RING_STRUCTURE');seam.matrix_world=frame(t,WIDTH/2,1)

# Finite, differentiated, editable skyline prototypes. Buildings remain rigid and point inward.
PROT=[]
for k in range(10):
 g=Mesh();h=[42,64,92,145,190,73,118,52,235,88][k];w=[36,43,31,38,34,62,46,70,29,48][k];d=[35,40,31,37,32,50,44,52,30,41][k]
 g.box((0,0,3),(w+10,d+10,6),CONCRETE)
 g.bevel_tower((0,0,6),w,d,h*.66,3,CITY)
 g.bevel_tower((0,0,6+h*.66),w*.76,d*.73,h*.25,2,PAINT)
 g.bevel_tower((0,0,6+h*.91),w*.53,d*.53,h*.09,1.5,DARK)
 for z in range(12,int(h*.66),7):
  g.box((0,-d/2-.12,z),(w-6,.35,1.5),GLASS);g.box((0,d/2+.12,z),(w-6,.35,1.5),GLASS)
  g.box((-w/2-.12,0,z),(.35,d-6,1.5),GLASS);g.box((w/2+.12,0,z),(.35,d-6,1.5),GLASS)
 for x in [-w*.25,w*.25]:g.box((x,0,8+h*.91),(3,d*.63,3),SILVER)
 if k in [3,4,8]:g.box((0,0,h+17),(2,2,28),SILVER)
 o=g.object('City archetype %02d'%k,'09_PROTOTYPES');o.hide_render=True;o.hide_viewport=True;PROT.append(o)
city_count=0
for i in range(144):
 t=(i+.5)*2*math.pi/144
 for j in range(27):
  y=80+j*116
  # Clear actual avenue corridors; docks occupy a broad, unbuilt ground-sector reserve.
  if min(abs(y-a) for a in [480,1040,1600,2160,2720])<51:continue
  wrap=min(t,2*math.pi-t)
  if wrap<.43 and y<1780:continue
  if ((i//9)+(j//4))%7==0 and j%3!=0:continue
  district=(i//12+j//5)%5
  allowed=[[0,1,5,7],[1,2,3,6],[0,2,4,8],[1,5,7,9],[0,1,2,9]][district]
  k=random.choice(allowed);o=bpy.data.objects.new('District_%d_Building_%04d'%(district,city_count),PROT[k].data);COL['02_CITY_INSTANCES'].objects.link(o)
  scale=random.uniform(.72,1.16);F=frame(t+random.uniform(-.007,.007),y+random.uniform(-15,15),2.5)
  o.matrix_world=F@Matrix.Diagonal((scale,scale,random.uniform(.75,1.12),1));o['prototype']=PROT[k].name;o['ground_theta']=t;city_count+=1

# Main two-finger industrial dock. Each pier and crane has an explicit load path to the ring.
D='03_DOCK';S='04_FREIGHTER';N='05_MAINTENANCE';T='06_TRANSPORT'
for x in [0,560]:
 box('Long docking pier',(x,870,153),(132,1530,18),CONCRETE,D,2)
 for edge in [-63,63]:box('Pier box girder',(x+edge,870,140),(9,1530,17),DARK,D)
 for y in [170,430,700,970,1230,1570]:
  ground=R-math.sqrt(R*R-x*x)
  box('Dock grounded pylon',(x,y,(ground+140)/2),(46,42,140-ground),DARK,D)
  box('Pylon foundation',(x,y,ground+2),(78,72,4),CONCRETE,D)
  beam('Dock diagonal brace',(x-48,y-36,ground+5),(x+43,y+36,142),9,9,SILVER,D)
box('Aft cross-dock circulation bridge',(280,1650,153),(690,110,18),CONCRETE,D,1.5)
for y in [790,1200]:
 for x in [0,560]:
  box('Loader tower base',(x,y,164),(62,54,8),ORANGE,D,1)
  box('Loader vertical lift',(x,y,212),(22,26,94),DARK,D,1)
  endpoint=198 if x==0 else 362
  box('Ship loader service bridge',((x+endpoint)/2,y,244),(abs(endpoint-x),20,8),PAINT,D,1)
  box('Docking service gasket',(endpoint,y,252),(14,24,28),DARK,D,1)
  beam('Loader bridge support',(x,y,168),(endpoint,y,239),7,7,SILVER,D)
for y in [540,1410]:
 for x in [-45,605]:
  box('Gantry rooted foot',(x,y,163),(55,70,10),ORANGE,D,2)
  box('Gantry column',(x,y,311),(22,24,288),PAINT,D,2)
  box('Gantry inset guide',(x-12,y,311),(2,13,262),DARK,D)
 box('Gantry top beam',(280,y,457),(680,34,30),DARK,D,2)
 for z in [446,468]:box('Gantry chord',(280,y-22,z),(680,9,8),PAINT,D)
 for x in range(-35,600,48):beam('Gantry web diagonal',(x,y-23,446),(x+40,y-23,468),3,4,SILVER,D)
 box('Travelling crane head',(320,y,430),(82,63,35),ORANGE,D,3)
 for x in [295,345]:tube('Crane hoist cable',[(x,y,413),(x,y,322)],.6,DARK,D)
 box('Cargo spreader',(320,y,320),(76,12,8),PAINT,D,1)

# Freighter: a bevelled, tapered main hull, articulated cargo sections, bow and aft engines.
CX=280;CY=1080;CZ=260
hull=Mesh();stations=[(-435,22,18),(-405,45,30),(-335,76,48),(-280,78,49),(280,78,49),(352,62,42),(380,57,40)]
xybase=[(-.74,-1),(.74,-1),(1,-.68),(1,.68),(.74,1),(-.74,1),(-1,.68),(-1,-.68)]
verts=[(CX+a*w,CY+y,CZ+b*h) for y,w,h in stations for a,b in xybase]
faces=[tuple(reversed(range(8))),tuple((len(stations)-1)*8+i for i in range(8))]
for k in range(len(stations)-1):
 for i in range(8):faces.append((k*8+i,k*8+(i+1)%8,(k+1)*8+(i+1)%8,(k+1)*8+i))
hull.poly(verts,[tuple(reversed(f)) for f in faces],PAINT);hull.object('Freighter tapered pressure hull',S)
box('Continuous cargo keel',(CX,CY+20,CZ-48),(92,680,13),DARK,S,3)
for j in range(6):
 y=CY-250+j*98
 for side in [-1,1]:
  x=CX+side*78
  box('Cargo section external plating',(x,y,CZ),(9,88,66),PAINT if j%3 else ORANGE,S,2)
  box('Section frame',(x+side*5,y+45,CZ),(5,6,78),DARK,S,1)
  box('Lower service raceway',(x+side*6,y,CZ-27),(4,84,5),SILVER,S)
  box('Cargo locking hardpoint',(x+side*8,y-27,CZ+19),(5,11,10),DARK,S,.7)
 box('Dorsal segmented shell',(CX,y,CZ+48),(111,88,8),PAINT,S,2)
 box('Dorsal machinery inset',(CX,y,CZ+54),(35,61,6),DARK,S,1)
# The two specific hatch positions align with docking service bridges at y790 and1200.
for y in [790,1200]:
 for side in [-1,1]:box('Matched port docking interface',(CX+side*77,y,CZ-8),(7,26,30),DARK,S,1)
box('Bow command island',(CX,CY-332,CZ+42),(86,97,20),DARK,S,5)
for x in [-27,0,27]:box('Recessed bridge window',(CX+x,CY-381,CZ+45),(22,2,8),GLASS,S,.5)
box('Command crown',(CX,CY-332,CZ+56),(94,99,5),PAINT,S,1)
for x in [-42,42]:
 box('Aft radiator bank',(CX+x,CY+292,CZ+62),(29,144,14),DARK,S,1)
 for y in range(100):
  if y%5==0:box('Radiator fin',(CX+x,CY+232+y,CZ+72),(26,1.4,12),SILVER,S)
for x in [-34,34]:
 for z in [-21,21]:
  tube('Aft engine shroud',[(CX+x,CY+368,CZ+z),(CX+x,CY+410,CZ+z)],15,DARK,S)
  tube('Aft nozzle lip',[(CX+x,CY+408,CZ+z),(CX+x,CY+412,CZ+z)],15.6,SILVER,S)
  tube('Recessed inactive engine core',[(CX+x,CY+411,CZ+z),(CX+x,CY+412,CZ+z)],10,GLASS,S)

# Near maintenance catwalk; metre-scale, with thick deck, posts, shoes, fasteners and a freight cart.
box('Inspection deck slab',(-170,-160,16.5),(16,440,1),DARK,N,.06)
for y in range(-375,60,5):
 box('Deck replaceable panels',(-170,y,17.06),(15,4.86,.12),DECK,N,.025)
 for x in [-177,-163]:box('Deck panel edge traction strip',(x,y,17.14),(.8,4.8,.05),ORANGE,N,.005)
for x in [-178,-162]:
 box('Catwalk underside longitudinal girder',(x,-160,14.4),(1.0,440,3.1),DARK,N,.05)
 for y in range(-376,61,4):
  box('Guardrail base shoe',(x,y,17.16),(.26,.28,.16),SILVER,N,.015)
  box('Guardrail upright',(x,y,17.68),(.075,.075,1.12),SILVER,N,.015)
  for dx in [-.075,.075]:
   for dy in [-.083,.083]:box('Base fixing bolt',(x+dx,y+dy,17.265),(.03,.03,.035),DARK,N,.002)
 for z,rad in [(18.27,.045),(17.75,.028)]:tube('Continuous guardrail',[(x,-378,z),(x,61,z)],rad,ORANGE if z>18 else SILVER,N)
 box('Cantilever bottom chord',(x,-160,-22),(2,440,2.2),DARK,N,.05)
 for y in range(-360,40,28):
  box('Catwalk grounded support',(x,y,-4),(1.1,1.3,38),DARK,N,.06)
  beam('Catwalk diagonal grounded support',(x,y-7,-22),(x,y+7,14),.5,.5,SILVER,N)
# Low service route connects into a lift; upper track continues along the left docking pier.
route=[(-168,-374,17.18),(-168,70,17.18),(0,205,17.18),(0,230,17.18)]
for dx in [-.72,.72]:
 tube('Low freight rail',[(x+dx,y,z) for x,y,z in route],.065,SILVER,T)
 tube('Upper freight rail',[(dx,230,162.3),(dx,1602,162.3)],.11,SILVER,T)
beam('Service transfer bridge deck',(-168,70,16.5),(0,205,16.5),7,.9,DECK,T)
for y in [190,244]:
 for x in [-9,9]:box('Cargo elevator mast',(x,y,89),(2,2,146),DARK,T,.12)
box('Cargo elevator lower carriage',(0,217,17.3),(17,53,.6),PAINT,T,.1)
box('Cargo elevator top service landing',(0,217,162.0),(17,53,.6),PAINT,T,.1)
# Stair tower as visible pedestrian connection; 20 flights with landings.
for k in range(20):
 z=17+k*7.2;y=150+(k%2)*18
 box('Stair tower landing',(-25,y,z),(8,6,.7),PAINT,T,.08)
 for j in range(24):
  yy=y+(1 if k%2==0 else -1)*j*.72
  box('Service stair tread',(-25,yy,z+j*.30),(5,.75,.14),DECK,T,.015)
for x in [-30,-20]:box('Stair tower support',(x,160,89),(1.2,1.2,148),DARK,T,.08)
# Hero cart occupies its own lower-track lane; wheel/rubber and panel construction are real geometry.
VX,VY,VZ=-168,-288,18.15
box('Freight cart chassis',(VX,VY,VZ),(2.6,4.3,.55),DARK,N,.09)
box('Freight cart load tray',(VX,VY,VZ+.38),(2.9,4.5,.24),ORANGE,N,.06)
box('Ribbed service crate',(VX,VY+.15,VZ+1.07),(2.35,3.2,1.25),PAINT,N,.08)
for xx in [-1.20,1.20]:
 for yy in [-1.40,1.40]:
  tube('Cart wheel rubber',[(VX+xx-.12,VY+yy,VZ-.34),(VX+xx+.12,VY+yy,VZ-.34)],.35,RUBBER,N)
  tube('Cart wheel hub',[(VX+xx-.135,VY+yy,VZ-.34),(VX+xx+.135,VY+yy,VZ-.34)],.15,SILVER,N)
for y in [-1.25,-.7,0,.7,1.25]:box('Crate external rib',(VX,VY+y,VZ+1.73),(2.3,.06,.10),SILVER,N,.012)
box('Cart battery pack',(VX,VY-1.7,VZ+.70),(1.9,.6,.6),DARK,N,.045)
for xx in [-.9,.9]:box('Cart amber marker',(VX+xx,VY-2.28,VZ+.4),(.18,.045,.1),LIGHT,N,.018)
tube('Cart front towing eye',[(VX-.2,VY-2.2,VZ-.04),(VX-.2,VY-2.6,VZ-.04),(VX+.2,VY-2.6,VZ-.04),(VX+.2,VY-2.2,VZ-.04)],.055,SILVER,N)
# Limited left-edge framing, not a billboard or a geometry-hiding facade.
box('Maintenance frame upright',(-181,-313,24),(1.8,2.2,15),PAINT,N,.15)
box('Maintenance overhead beam',(-173,-313,31),(17,2.5,1.6),DARK,N,.12)
for x in [-179,-173,-166]:box('Overhead work luminaire',(x,-313,30.05),(1.4,.8,.16),LIGHT,N,.045)
for x in [-176.8,-175.9]:tube('Protected service conduit',[(x,-374,16),(x,-315,16),(x,-315,29)],.08,SILVER,N)
# Mid-distance cargo, on the actual rail side, varying silhouette and rhythm.
for y in [380,420,460,960,1000,1340]:
 for x in [-24,24]:
  box('Cargo staging pallet',(x,y,164),(19,32,2),DARK,T,.25)
  box('Dock cargo container',(x,y,173),(17,28,16),ORANGE if y%3 else PAINT,T,.65)
  for yy in range(-12,13,4):box('Container side stiffener',(x-8.8,y+yy,173),(.5,.7,15),SILVER,T,.08)

# Sun and neutral skylight; no atmosphere, DoF, bloom, reference-plane projection or image assets.
SC.world=bpy.data.worlds.new('Spaceport diffuse blue skylight');SC.world.use_nodes=True
bg=SC.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.27,.36,.48,1);bg.inputs[1].default_value=.65
ld=bpy.data.lights.new('Broad solar key','SUN');ld.energy=2.8;ld.angle=.025;ld.color=(1.0,.89,.74)
lo=bpy.data.objects.new('Broad solar key',ld);COL['07_LIGHTS'].objects.link(lo);lo.rotation_euler=Vector((-.55,.43,-.72)).to_track_quat('-Z','Y').to_euler()
ld=bpy.data.lights.new('Hangar bounce approximation','AREA');ld.energy=850000;ld.shape='DISK';ld.size=350;ld.color=(.54,.70,1)
lo=bpy.data.objects.new('Hangar bounce approximation',ld);COL['07_LIGHTS'].objects.link(lo);lo.location=(-300,-80,260);lo.rotation_euler=(Vector((200,900,140))-lo.location).to_track_quat('-Z','Y').to_euler()
CAMERAS={}
def camera(name,pos,target,lens):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.08;d.clip_end=20000
 o=bpy.data.objects.new(name,d);COL['08_CAMERAS'].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();CAMERAS[name]=o;return o
hero_pos=Vector((-174,-323,18.75));hero_target=Vector((260,1960,995))
camera('O01_HERO',hero_pos,hero_target,18)
camera('O01_SECOND',(3650,-3750,2350),(0,1420,1510),36)
camera('O03_REAR',(-3900,5300,3300),(0,1460,1500),37)
camera('O04_CRAFT',(-179,-308,19.35),(-168,-286,18.5),41)
camera('O04_INTERFACE',(75,565,273),(204,804,250),43)
camera('O05_ROUTE',(-710,-650,730),(115,720,55),40)
for i in range(5):
 p=hero_pos+Vector(((i-2)*7.5,0,(i-2)*.12));camera('O06_%03d'%(i*25),p,p+(hero_target-hero_pos),18)
SC.camera=CAMERAS['O01_HERO'];SC.render.engine='CYCLES';SC.cycles.device='CPU';SC.cycles.samples=24;SC.cycles.use_denoising=True;SC.cycles.seed=SEED;SC.cycles.use_animated_seed=False
SC.cycles.max_bounces=5;SC.cycles.diffuse_bounces=2;SC.cycles.glossy_bounces=3;SC.cycles.transmission_bounces=2;SC.cycles.transparent_max_bounces=4
SC.render.resolution_x=2560;SC.render.resolution_y=1440;SC.render.resolution_percentage=100;SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.render.image_settings.color_depth='8'
SC.render.threads_mode='FIXED';SC.render.threads=4;SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=0
SC.render.film_transparent=False;SC.render.use_compositing=False;SC.camera.data.dof.use_dof=False
SC['task']='skyfold-dock-premium-environment';SC['candidate']='R00_PROVISIONAL';SC['quality_status']='G2_REVIEW_REQUIRED_NOT_QUALIFIED';SC['source_sha']=os.environ.get('GITHUB_SHA','local-uncommitted');SC['seed']=SEED
SC['contract_sha256']='b29cc86937c4667652de7a954871c940e31e1c6493c34575ab8f84db970f7ea7'
manifest={'candidate':'R00_PROVISIONAL','contract_version':'1.0.0','source_sha':SC['source_sha'],'blender':bpy.app.version_string,'seed':SEED,'geometry':{'ring_radius_m':R,'band_width_m':WIDTH,'shell_thickness_m':64,'city_instances':city_count,'objects':len(SC.objects),'mesh_datablocks':len(bpy.data.meshes)},'scales':{'rail_gauge_m':1.44,'guardrail_height_m':1.1,'cart_length_m':4.5,'freighter_length_m':815,'ring_diameter_m':3200},'functional_route':{'lower_rail':route,'lift_lower':[0,217,17.3],'lift_upper':[0,217,162.0],'upper_rail_end':[0,1602,162.3],'loader_interfaces':[[198,790,252],[362,790,252],[198,1200,252],[362,1200,252]]},'cameras':{},'external_files':[],'quality_map':{'ring':'complete macro shell and rear edge; not structurally engineered','city':'rigid shared-mesh modular exteriors; no interiors','dock':'full two-pier/crane/loader layout; intersections require visual audit','freighter':'full closed hull and independent parts; preliminary detailing','near_zone':'complete rail/deck/cart components; no human character'},'review':'SEQUENTIAL_SELF_REVIEW_PENDING','gate':'NO_AUTOMATIC_PASS'}
bpy.context.view_layer.update()
for name,c in CAMERAS.items():manifest['cameras'][name]={'matrix_world':[list(row) for row in c.matrix_world],'lens_mm':c.data.lens,'clip':[c.data.clip_start,c.data.clip_end]}
(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
bpy.data.texts.new('BUILD-MANIFEST.json').write(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'skyfold-r00.blend'),compress=True)
manifest['scene_sha256']=hashlib.sha256((OUT/'skyfold-r00.blend').read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('SKYFOLD_BUILD_COMPLETE',json.dumps({'objects':len(SC.objects),'city':city_count,'scene_sha256':manifest['scene_sha256'],'status':'REVIEW_REQUIRED'}))
