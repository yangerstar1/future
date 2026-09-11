"""R06B: repair observed R06 ship/arc composition. Native assets only.
Build from exact R06. Root motion is retained and translated farther from the berth.
Old probes and cameras remain. No core quality gate is automatically approved.
"""
import bpy, os, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath);PARENT='b45e19f934f60c0257bcf28256e470bb15fba23f66f425df9b3832b94290f5fd'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert bpy.app.version[:3]==(4,5,13)
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']
C=bpy.data.collections['04_FREIGHTER'];CAM=bpy.data.collections['08_CAMERAS'];meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
oldcenter=Vector(meta['original_ship_center']);new=[];hidden=[]
# Old coarse dorsal containers and their seams are preserved but not used in this revision.
for o in list(C.objects):
 if o.name.startswith(('R04C sealed dorsal cargo vault','R04C cargo vault edge frame','R04C vault transverse band','R04C vault inspection cap','R04C vault recessed roof strip')) or o.type=='FONT':
  o.hide_render=True;o['R06B_state']='SUPERSEDED_BY_CARGO_ASSEMBLY';hidden.append(o.name)
def mat(name,color,metal,rough,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
white=mat('R06B cargo ceramic',(.52,.57,.53),.28,.42)
dark=mat('R06B carbon machinery',(.023,.031,.039),.68,.37)
metal=mat('R06B titanium edge',(.27,.34,.38),.85,.27)
bronze=mat('R06B thermal bronze',(.28,.105,.028),.62,.38)
blue=mat('R06B engine plasma',(.13,.43,.72),.15,.30,6)
stripe=mat('R06B safety chalk',(.58,.55,.41),.10,.52)
# Rebalance the existing ship paint instead of applying noise to the whole scene.
for name,color,metallic,roughness in [('R06 satin titanium enamel',(.26,.34,.36),.35,.37),('R06 ochre cargo enamel',(.28,.085,.021),.3,.43)]:
 p=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
cache={}
def mesh(name,verts,faces,material,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(material)
 o=bpy.data.objects.new(name,me);C.objects.link(o);o.parent=root
 if bevel:
  b=o.modifiers.new('Manufactured edge','BEVEL');b.width=bevel;b.segments=2
 new.append(o);return o
def box(name,p,size,ma,bevel=.5):
 key=(tuple(size),ma.name,bevel)
 if key not in cache:
  a,b,c=[v/2 for v in size];v=[(-a,-b,-c),(a,-b,-c),(a,b,-c),(-a,b,-c),(-a,-b,c),(a,-b,c),(a,b,c),(-a,b,c)]
  o=mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,bevel);cache[key]=o
 else:
  proto=cache[key];o=proto.copy();o.data=proto.data;C.objects.link(o);o.name=name;o.parent=root;new.append(o)
 o.location=p;return o
def cylinder(name,p,r,length,ma,segments=32,axis='Y'):
 v=[]
 for y in [-length/2,length/2]:
  for j in range(segments):
   t=2*math.pi*j/segments;v.append((r*math.cos(t),y,r*math.sin(t)))
 faces=[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]+[(j,(j+1)%segments,(j+1)%segments+segments,j+segments) for j in range(segments)]
 o=mesh(name,v,faces,ma,.45);o.location=p
 if axis=='X':o.rotation_euler.z=math.pi/2
 return o
def nozzle(name,p,r):
 rings=[(-30,r*.72),(-16,r),(17,r),(32,r*1.18),(33,r*.93),(12,r*.70),(-10,r*.50)]
 n=40;v=[(rad*math.cos(2*math.pi*j/n),y,rad*math.sin(2*math.pi*j/n)) for y,rad in rings for j in range(n)]
 faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(rings)-1) for j in range(n)]
 o=mesh(name,v,faces,metal,.4);o.location=p
 cylinder(name+' recessed core',(p[0],p[1]-8,p[2]),r*.48,1.2,blue,40)
 # Compact rigid luminous plume: no smoke, billboard or generated effect.
 rings2=[(34,r*.47),(47,r*.34),(72,r*.13),(89,0.3)]
 vv=[(rad*math.cos(2*math.pi*j/24),y,rad*math.sin(2*math.pi*j/24)) for y,rad in rings2 for j in range(24)]
 ff=[(k*24+j,k*24+(j+1)%24,(k+1)*24+(j+1)%24,(k+1)*24+j) for k in range(3) for j in range(24)]
 o=mesh(name+' exhaust core',vv,ff,blue);o.location=p
# Six discrete freight cassettes, separated by circulation slots, capped and banded.
for i in range(6):
 y=-205+i*96
 for side in [-1,1]:
  x=side*39
  cylinder('R06B sealed dorsal freight capsule',(x,y,74),24,73,white)
  cylinder('R06B cargo end cap',(x,y-37.5,74),22,2.5,metal)
  cylinder('R06B cargo end cap',(x,y+37.5,74),22,2.5,metal)
  for yy in [y-26,y+26]:
   cylinder('R06B capsule retention band',(x,yy,74),25.1,4.5,bronze if i in [0,5] else dark)
   box('R06B freight saddle',(x,yy,51),(49,10,12),dark,.8)
  box('R06B cargo equipment cabinet',(side*74,y,68),(10,49,21),dark,.9)
  for yy in [-17,-8,1,10,19]:box('R06B cabinet louvers',(side*80,y+yy,68),(2,2.5,17),metal,.2)
 box('R06B dorsal cargo walkway',(0,y,72),(9,84,2),metal,.4)
 for yy in [-33,-20,-7,6,19,32]:box('R06B walkway grating',(0,y+yy,73.3),(8,.9,.5),dark,.1)
# Useful aft machinery creates a defined stern, instead of a capped tube silhouette.
for side in [-1,1]:
 for level in [-1,1]:
  x=side*113;z=level*31
  cylinder('R06B outrigger engine casing',(x,335,z),22,112,dark)
  cylinder('R06B thermal engine collar',(x,364,z),23.5,12,bronze)
  box('R06B engine attachment',(side*84,307,z),(56,56,15),metal,1.5)
  nozzle('R06B main thruster',(x,410,z),20)
 for j in range(12):
  y=266+j*12;box('R06B radiator plate',(side*116,y,92),(62,4,42),dark,.6)
 box('R06B radiator manifold',(side*100,337,72),(7,155,8),bronze,.7)
# Bridge, inspection recesses and a fore-keel tie the nose into the industrial hull.
box('R06B fore keel service fairing',(0,-331,-38),(52,128,15),metal,2)
for side in [-1,1]:
 for y in [-385,-350,-315]:
  box('R06B bow attitude jet housing',(side*(35+(y+385)*.20),y,-12),(7,16,15),dark,1.2)
  cylinder('R06B bow attitude jet throat',(side*(39+(y+385)*.20),y,-12),3.3,2,metal,20,'X')
 for i in range(6):
  y=-205+i*96
  box('R06B service mounting rail',(side*91,y,-31),(7,84,7),metal,.6)
  for yy in [-32,32]:box('R06B service locking shoe',(side*95,y+yy,-23),(6,11,16),bronze,.5)
# A single registration is attached to the real side surface (old duplicate labels hidden).
for side in [-1,1]:
 cu=bpy.data.curves.new('R06B vessel registration','FONT');cu.body='SKYFOLD  /  07';cu.size=7.2;cu.extrude=.05;cu.materials.append(stripe)
 o=bpy.data.objects.new('R06B vessel registration',cu);C.objects.link(o);o.parent=root;o.location=(side*96,75,9)
 basis=Matrix(((0,0,side),(side,0,0),(0,1,0)));o.rotation_euler=basis.to_euler();new.append(o)
# Real separation in depth: ring remains a giant backdrop, ship remains close to camera.
root.animation_data_clear();target=bpy.data.objects['R06_TRACKING_TARGET'];target.location=(0,-20,85)
camdata=bpy.data.cameras.new('R06B_DEPARTURE_TRACK');camdata.lens=42;camdata.sensor_width=36;camdata.clip_start=.2;camdata.clip_end=30000
cam=bpy.data.objects.new('R06B_DEPARTURE_TRACK',camdata);CAM.objects.link(cam);cam.parent=root
con=cam.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
for f in range(1,193):
 t=(f-1)/191;root.location=oldcenter+Vector((0,-3400-640*t,30*t));root.keyframe_insert(data_path='location',frame=f)
 cam.location=Vector((-1050,-1500,420))+Vector((120*t,-60*t,40*t));cam.keyframe_insert(data_path='location',frame=f)
S.camera=cam;S.frame_set(1);bpy.context.view_layer.update();checks=[]
for f in [1,49,97,145,192]:
 S.frame_set(f);bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in C.objects if not o.hide_render and o.type=='MESH' for v in o.bound_box]
 uv=[world_to_camera_view(S,cam,p) for p in pts];bounds=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
 assert 0<bounds[0]<bounds[1]<1 and 0<bounds[2]<bounds[3]<1,bounds
 assert max(p.y for p in pts)<0
 checks.append({'frame':f,'camera_matrix':[list(r) for r in cam.matrix_world],'ship_matrix':[list(r) for r in root.matrix_world],'whole_ship_bounds_uv':bounds,'stern_y':max(p.y for p in pts)})
S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R06B_REFINED_FORWARD_DEPARTURE';S['source_sha']=os.environ['GITHUB_SHA']
meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'R06B_changes':{'added_ship_components':len(new),'superseded_ship_parts':hidden,'ship_start_translation_y':-3400,'city_geometry_changed':False,'camera':'R06B_DEPARTURE_TRACK','checks':checks},'quality_status':'PROBE_REQUIRED_NO_PROMOTION'})
p=OUT/'skyfold-r06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('R06B_SAVED',meta['scene_sha256'],flush=True)
