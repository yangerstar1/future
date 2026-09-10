"""R04B: keep the editable R04 assembly; correct failed framing and unsafe camera motion."""
import bpy, math, json, os, hashlib, ast
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath);PARENT='afbefcd1cd70aed98978930785f663ce4ae27561e1314195a507d81b51eee859'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rig=bpy.data.objects['R04_HABITAT_ROTATION'];C=bpy.data.collections['08_CAMERAS']
meta=json.loads((BASE.parent/'BUILD-MANIFEST.json').read_text())
# Keep R04 camera as a labelled failure control, never overwrite the old observations.
for o in list(C.objects):
 if o.name.startswith('R04_'):o.name=o.name.replace('R04_','R04_REJECTED_',1)
oldpos=Vector((-930,500,650));oldtarget=Vector((180,1150,900))
pos=Vector((-820,30,335));target=Vector((130,1180,1140));lens=14.0

def ground(x):return 1600-math.sqrt(1600**2-x*x)
def basis(p,t):
 f=Vector((t.x-p.x,t.y-p.y,0)).normalized();r=Vector((f.y,-f.x,0));z=p.z-1.7
 return Matrix(((r.x,f.x,0,p.x),(r.y,f.y,0,p.y),(0,0,1,z),(0,0,0,1)))
oldF=basis(oldpos,oldtarget);F=basis(pos,target);xform=F@oldF.inverted()
for o in list(bpy.data.collections['10_R04_GALLERY'].objects):
 if o.name.startswith(('R04 gallery access bridge','R04 gallery ring footing','R04 gallery rooted tower','R04 gallery support head','R04 gallery lift')):
  bpy.data.objects.remove(o,do_unlink=True)
 else:o.matrix_world=xform@o.matrix_world
# Reuse verified mesh helpers to root the relocated platform; other cargo routes unchanged.
raw=(ROOT/'build_scene_r01.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
COL={c.name:c for c in bpy.data.collections};CACHE={};SC=s;R=1600.;WIDTH=1800.
M=[bpy.data.materials[n] for n in ['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay']]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY=range(11)
wanted={'Mesh','box','beam','tube'};nodes=[n for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'R01_VERIFIED_HELPERS','exec'),globals())
N='10_R04_GALLERY';before=set(COL[N].objects)
for a in [-7,7]:
 for b in [-12,12]:
  p=F@Vector((a,b,-1.5));g=ground(p.x)
  box('R04B rooted gallery footing',(p.x,p.y,g+1.5),(8,8,3),CONCRETE,N,.12)
  box('R04B rooted gallery pylon',(p.x,p.y,(g+3+p.z)/2),(1.2,1.2,p.z-g-3),DARK,N,.04)
  beam('R04B gallery diagonal',(p.x-3,p.y,g+3),(p.x+3,p.y,p.z),.5,.5,SILVER,N)
start=F@Vector((0,-16,-.7));end=Vector((-750,90,332))
beam('R04B access bridge',start,end,6,1.2,DARK,N)
g=ground(end.x)
for dy in [-4,4]:box('R04B access lift guide',(end.x,end.y+dy,(g+332)/2),(1,1,332-g),SILVER,N,.06)
for z in [g+1,331.5]:box('R04B access lift landing',(end.x,end.y,z),(8,10,1),ORANGE,N,.10)
for o in set(COL[N].objects)-before:
 mw=o.matrix_world.copy();o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted();o.matrix_world=mw
# Avoid uniform copy-wall heights without bending the rigid building neighbourhoods.
for o in bpy.data.collections['02_CITY_INSTANCES'].objects:
 if o.type=='MESH' and 'ground_theta' in o:
  a=float(o['ground_theta']);factor=.82+.30*(.5+.5*math.sin(a*3+.8))+.11*math.sin(o.location.y*.006+a*2)
  o.scale.z*=factor
# Less flat opening fill. This is explicitly a new art-direction revision, not single-variable evidence.
bpy.data.objects['R04 warm axial opening'].data.energy=42000000
bpy.data.objects['R04 cool reflected city fill'].data.energy=3500000
bpy.data.objects['Broad solar key'].data.energy=2.8
bpy.data.objects['R04 gallery soft bounce'].location+=pos-oldpos
s.world.node_tree.nodes['Background'].inputs[1].default_value=.15
s.view_settings.exposure=.15

def cam(name,p,t,l,roll=0):
 d=bpy.data.cameras.new(name);d.lens=l;d.sensor_width=36;d.clip_start=.08;d.clip_end=20000;o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=p;o.rotation_mode='QUATERNION';o.rotation_quaternion=(Vector(t)-o.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),roll);return o
hero=cam('R04_HERO',pos,target,lens)
cam('R04_HERO_LEVEL',pos,target,lens)
cam('R04_SECOND',(-1850,-2500,1650),(150,1050,1580),34)
cam('R04_GALLERY_CRAFT',F@Vector((3.5,1,2.4)),F@Vector((-4.5,7,1.15)),44)
cam('R04_ROUTE_FULL',(-800,-600,1000),(10,1010,410),30)
cam('R04_RETURN_LIFT_FULL',(-340,1210,390),(-46,1608,390),28)
# Genuine movement: coherent ring rotation plus a camera physically moving out from the landing.
# Camera position follows the assembly's origin motion, avoiding the floor crossing it at frame ~5.
# Its local dolly rises and backs away, producing parallax rather than only turning a still image.
pivot=Vector((0,900,1600));rig.animation_data_clear();motion=[]
for f in range(1,193):
 t=(f-1)/191;angle=math.radians(6)*t;rot=Matrix.Rotation(angle,3,'Y')
 rig.rotation_euler=(0,angle,0);rig.keyframe_insert(data_path='rotation_euler',frame=f)
 localpos=pos+Vector((-75*t,-110*t,48*t));focus=pivot+rot@(target-pivot)
 hero.location=pivot+rot@(localpos-pivot);hero.rotation_quaternion=(focus-hero.location).to_track_quat('-Z','Y')
 hero.keyframe_insert(data_path='location',frame=f);hero.keyframe_insert(data_path='rotation_quaternion',frame=f)
 if f in [1,49,97,145,192]:motion.append({'frame':f,'degrees':6*t,'camera_position':list(hero.location),'focus':list(focus),'camera_local_offset':list(localpos-pos)})
for i in range(5):
 p=pos+F.to_3x3().col[0]*((i-2)*1.2);cam('R04_PARALLAX_%03d'%(25*i),p,p+(target-pos),lens)
s.frame_set(1);bpy.context.view_layer.update();s.camera=hero;s['candidate']='R04B_OVERHEAD_REVEAL';s['source_sha']=os.environ['GITHUB_SHA']
meta.update({'candidate':s['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'camera_motion':motion,'camera_reason':'R04 rejected: rolled wall, rail crossing ship; R04B lower-ring wide-angle framing and safe dolly','motion_reason':'camera follows rigid assembly translation and adds 141m local dolly; never a 2D pan','cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in C.objects},'geometry':{'objects':len(s.objects),'mesh_datablocks':len(bpy.data.meshes)},'render_status':'NOT_RENDERED','gate':'NOT_AUTO_QUALIFIED'})
path=OUT/'skyfold-r04b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);meta['scene_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R04B_BUILT',meta['scene_sha256'])
