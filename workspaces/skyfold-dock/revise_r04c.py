"""R04C spatial intervention: more axial city depth, elevated working berth, stable human foreground.
Same single ring and same ship. Old R03B/R04/R04B snapshots and cameras are retained.
This is an explicit unfrozen-G2 structural revision; previous transport observations must be re-tested.
"""
import bpy,math,json,os,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);BASE=Path(bpy.data.filepath)
parent='67a82412f11c2dc678c8f6ddc3caef1348422901cfbae0bdc0fde2180663482f';assert hashlib.sha256(BASE.read_bytes()).hexdigest()==parent;assert bpy.app.version[:3]==(4,5,13)
SC=bpy.context.scene;SC.frame_set(1);bpy.context.view_layer.update();meta=json.loads((BASE.parent/'BUILD-MANIFEST.json').read_text());rig=bpy.data.objects['R04_HABITAT_ROTATION'];COL={c.name:c for c in bpy.data.collections};CACHE={};R=1600.;WIDTH=5000.
M=[bpy.data.materials[n] for n in ['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay','Recessed planted courtyards','City basalt roadbed']]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY,PARK,ROAD=range(13)
raw=(ROOT/'build_scene_r01.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
wanted={'Mesh','box','beam','tube','ring_strip','frame'};defs=[n for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted];exec(compile(ast.Module(body=defs,type_ignores=[]),'VERIFIED_R01_HELPERS','exec'),globals())
def parent_keep(o):
 mw=o.matrix_world.copy();o.parent=rig;o.matrix_parent_inverse=rig.matrix_world.inverted();o.matrix_world=mw

def translate(o,dz):o.matrix_world=Matrix.Translation((0,0,dz))@o.matrix_world

def bboxz(o):
 z=[(o.matrix_world@Vector(v)).z for v in o.bound_box];return min(z),max(z)

def extend_top(o,dz):
 lo,hi=bboxz(o);assert hi-lo>1,o.name
 o.matrix_world=Matrix.Translation((0,0,lo))@Matrix.Diagonal((1,1,(hi-lo+dz)/(hi-lo),1))@Matrix.Translation((0,0,-lo))@o.matrix_world

before=set(SC.objects)
# Extend only the shell and external structural members along the ring axis.
# City buildings retain their rigid footprints: more instance rows, not stretched buildings.
for o in list(COL['01_RING_STRUCTURE'].objects):
 if o.name.startswith(('R02 city transport corridor','R02 city median')):bpy.data.objects.remove(o,do_unlink=True);continue
 o.matrix_world=Matrix.Diagonal((1,WIDTH/1800,1,1))@o.matrix_world
for j in range(22):
 y=55+j*230
 ring_strip('R04C city transit right of way',R-3,R-2,y-10,y+10,ROAD)
 ring_strip('R04C transit median',R-3.2,R-3,y-.8,y+.8,CONCRETE)
protos=[bpy.data.objects['R02 urban block prototype %02d'%k] for k in range(12)]
for i in range(46):
 theta=(i+.5)*2*math.pi/46
 if min(theta,2*math.pi-theta)<.60:continue
 for j in range(7,21):
  k=(i//4+j*3+i%3)%12;o=bpy.data.objects.new('R04C axial neighbourhood %02d-%02d'%(i,j),protos[k].data);COL['02_CITY_INSTANCES'].objects.link(o);o.matrix_world=frame(theta+(j%2)*.006,170+j*230,1.4);o.scale.z=.82+.30*(.5+.5*math.sin(theta*3+.8))+.11*math.sin(o.location.y*.006+theta*2);o['prototype']=protos[k].name;o['ground_theta']=theta;o['local_up']='INWARD_RADIAL'
# Axial city depth provides a genuinely visible distant overhead neighbourhood behind the ship.
# Raise the rigid berth. Rooted supports keep their lower end on the original ring.
RAISE=690.0
for o in list(COL['03_DOCK'].objects):
 n=o.name
 if n.startswith(('Pylon foundation','R03 rear rooted foundation')):continue
 if n.startswith(('Dock grounded pylon','R02 rooted pier diagonal','R03 rear rooted riser')):extend_top(o,RAISE)
 else:translate(o,RAISE)
for o in COL['04_FREIGHTER'].objects:translate(o,RAISE)
# Preserve the low incoming route and extend its elevator to the raised near berth.
for o in list(COL['06_TRANSPORT'].objects):
 if o.name.startswith('R02 lift guide tower'):extend_top(o,RAISE)
 elif o.name.startswith('R03 incoming lift side lattice'):bpy.data.objects.remove(o,do_unlink=True)
 else:
  lo,hi=bboxz(o)
  if lo>250:translate(o,RAISE)
for z in range(208,941,40):
 for x in [-92,-80]:beam('R04C incoming lift lattice',(x,614,z),(x,626,z+38),.65,.65,SILVER,'06_TRANSPORT')
# More substantial cargo vaults and clear hoist clearance; existing ship interfaces do not move relative to the hull.
for j in range(6):
 y=830+j*98
 box('R04C sealed dorsal cargo vault',(280,y,1384),(110,83,48),PAINT,'04_FREIGHTER',4)
 for x in [224,336]:box('R04C cargo vault edge frame',(x,y,1384),(4,89,55),DARK,'04_FREIGHTER',.6)
 for yy in [-43,43]:box('R04C vault transverse band',(280,y+yy,1384),(119,4,56),ORANGE if j in [0,5] else SILVER,'04_FREIGHTER',.6)
 box('R04C vault inspection cap',(280,y,1409),(22,29,2),DARK,'04_FREIGHTER',.7)
 for x in [249,311]:box('R04C vault recessed roof strip',(x,y,1408.2),(2,68,.4),DARK,'04_FREIGHTER',.1)
for o in COL['03_DOCK'].objects:
 if o.name.startswith('R02 far crane rooted tower'):extend_top(o,80)
 elif o.name.startswith(('R02 far crane boom','R02 far crane diagonal','R02 crane trolley','R02 inactive hoist cable')):translate(o,80)
# Retain the actual metre-scale viewing platform; only its elevation and rooted piers change.
for o in COL['10_R04_GALLERY'].objects:
 n=o.name;lo,hi=bboxz(o)
 if n.startswith('R04B rooted gallery footing'):continue
 if n.startswith(('R04B rooted gallery pylon','R04B gallery diagonal','R04B access lift guide')):extend_top(o,725)
 elif n.startswith('R04B access lift landing') and hi<250:continue
 else:translate(o,725)
bpy.data.objects['R04 gallery soft bounce'].location.z+=725
# Moderate block-to-block surface variation while retaining the same facade construction.
ma=bpy.data.materials['City pale panels'];nt=ma.node_tree;info=nt.nodes.new('ShaderNodeObjectInfo');ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.22,.29,.33,1);ramp.color_ramp.elements[1].color=(.48,.50,.45,1);nt.links.new(info.outputs['Random'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
for o in set(SC.objects)-before:
 if o.type in {'MESH','CURVE','FONT'}:parent_keep(o)
# New camera version is explicit. All previous failure cameras remain available for regression.
for o in list(COL['08_CAMERAS'].objects):
 if o.name.startswith('R04_') and not o.name.startswith('R04_REJECTED_'):o.name=o.name.replace('R04_','R04B_CONTROL_',1)
def camera(n,p,t,l):
 d=bpy.data.cameras.new(n);d.lens=l;d.sensor_width=36;d.clip_start=.08;d.clip_end=20000;o=bpy.data.objects.new(n,d);COL['08_CAMERAS'].objects.link(o);o.location=p;o.rotation_mode='QUATERNION';o.rotation_quaternion=(Vector(t)-o.location).to_track_quat('-Z','Y');return o
POS=Vector((-820,30,1060));TARGET=Vector((280,1450,1500));LENS=20.5
hero=camera('R04_HERO',POS,TARGET,LENS);camera('R04_HERO_LEVEL',POS,TARGET,LENS)
camera('R04_SECOND',(-2500,-3600,2350),(150,2350,1620),35)
old=bpy.data.objects['R04B_CONTROL_R04_GALLERY_CRAFT'] if bpy.data.objects.get('R04B_CONTROL_R04_GALLERY_CRAFT') else bpy.data.objects['R04B_CONTROL_GALLERY_CRAFT']
p=old.location+Vector((0,0,725));t=p+old.rotation_quaternion@Vector((0,0,-15));camera('R04_GALLERY_CRAFT',p,t,44)
camera('R04_ROUTE_FULL',(-1900,-1000,1600),(0,950,680),28)
camera('R04_RETURN_LIFT_FULL',(-340,1210,1080),(-46,1608,1080),28)
# City and dock co-rotate. Camera rides the gallery's base motion then dollies out and upward.
rig.animation_data_clear();pivot=Vector((0,900,1600));motion=[]
for f in range(1,193):
 t=(f-1)/191;angle=math.radians(6)*t;rot=Matrix.Rotation(angle,3,'Y');rig.rotation_euler=(0,angle,0);rig.keyframe_insert(data_path='rotation_euler',frame=f)
 local=POS+Vector((-60*t,-110*t,45*t));focus=pivot+rot@(TARGET-pivot);hero.location=pivot+rot@(local-pivot);hero.rotation_quaternion=(focus-hero.location).to_track_quat('-Z','Y');hero.keyframe_insert(data_path='location',frame=f);hero.keyframe_insert(data_path='rotation_quaternion',frame=f)
 if f in [1,49,97,145,192]:motion.append({'frame':f,'degrees':6*t,'camera_position':list(hero.location),'focus':list(focus)})
forward=Vector((TARGET.x-POS.x,TARGET.y-POS.y,0)).normalized();right=Vector((forward.y,-forward.x,0))
for i in range(5):
 p=POS+right*((i-2)*1.2);camera('R04_PARALLAX_%03d'%(i*25),p,p+(TARGET-POS),LENS)
SC.frame_set(1);bpy.context.view_layer.update();SC.camera=hero;SC['candidate']='R04C_DEEP_CITY_HIGH_BERTH';SC['source_sha']=os.environ['GITHUB_SHA']
meta.update({'candidate':SC['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'camera_motion':motion,'structural_intervention':{'single_ring_radius_m':1600,'axial_width_m':5000,'berth_elevation_delta_m':690,'ship_center_z_m':1300,'gallery_camera_z_m':1060,'buildings_axially_stretched':False,'old_transport_validation_invalidated':True,'new_transport_visual_validation':'REQUIRED'},'cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in COL['08_CAMERAS'].objects},'geometry':{'objects':len(SC.objects),'mesh_datablocks':len(bpy.data.meshes),'neighbourhoods':len(COL['02_CITY_INSTANCES'].objects)},'render_status':'NOT_RENDERED','gate':'NOT_AUTO_QUALIFIED'})
path=OUT/'skyfold-r04c.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);meta['scene_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R04C_BUILT',meta['scene_sha256'])
