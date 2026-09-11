"""R06: released freighter flies bow-first; the camera follows actual geometry.
Read-only input: verified R05B. Build/probe/render use separate Blender processes.
User amendment: a free-flight tracking shot replaces co-rotation, not the core scene.
No external assets, generated image repair, interpolated video or automatic art PASS.
"""
import bpy, os, math, json, hashlib, time, struct, resource
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
MODE=os.environ.get('R06_MODE','build');S=bpy.context.scene
assert bpy.app.version[:3]==(4,5,13),bpy.app.version_string
PARENT='890c7d7d166371fb59627d1ab43bacae36a031c81f3a3eebc5de418e7cb363f2'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(o):return [list(r) for r in o.matrix_world]
def bbox(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
def write(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def config(width,samples,blur=False):
 S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=samples
 S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.035;S.cycles.adaptive_min_samples=8
 S.cycles.use_denoising=True;S.cycles.denoiser='OPENIMAGEDENOISE';S.cycles.seed=270910;S.cycles.use_animated_seed=False
 S.cycles.max_bounces=4;S.cycles.diffuse_bounces=2;S.cycles.glossy_bounces=2;S.cycles.transmission_bounces=2;S.cycles.transparent_max_bounces=4
 S.render.use_persistent_data=True;S.render.use_compositing=False;S.render.use_sequencer=False
 S.render.resolution_x=width;S.render.resolution_y=width*9//16;S.render.resolution_percentage=100
 S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
 S.render.use_motion_blur=blur;S.render.motion_blur_shutter=.25
 S.render.threads_mode='FIXED';S.render.threads=4

if MODE=='build':
 BASE=Path(bpy.data.filepath);assert digest(BASE)==PARENT
 S.frame_set(1);bpy.context.view_layer.update();C={c.name:c for c in bpy.data.collections}
 required=['01_RING_STRUCTURE','02_CITY_INSTANCES','03_DOCK','04_FREIGHTER','07_LIGHTS','08_CAMERAS','09_PROTOTYPES']
 assert all(n in C for n in required)
 oldcams={o.name:{'matrix':matrix(o),'lens':o.data.lens} for o in C['08_CAMERAS'].objects}
 habitat=bpy.data.objects['R04_HABITAT_ROTATION'];habitat.animation_data_clear();habitat.rotation_euler=(0,0,0);bpy.context.view_layer.update()
 environment=[o for o in S.objects if o.type in {'MESH','CURVE','FONT'} and o.name not in C['04_FREIGHTER'].objects]
 before={o.name:matrix(o) for o in environment}
 ship=list(C['04_FREIGHTER'].objects);hull=bpy.data.objects['Freighter tapered pressure hull']
 hp=bbox(hull);center=Vector(tuple((min(p[i] for p in hp)+max(p[i] for p in hp))/2 for i in range(3)))
 assert 800<max(p.y for p in hp)-min(p.y for p in hp)<1000
 assert 1200<center.z<1400
 coll=bpy.data.collections.new('13_R06_FLIGHT');S.collection.children.link(coll)
 root=bpy.data.objects.new('R06_SHIP_FORWARD_FLIGHT',None);coll.objects.link(root);root.location=center
 target=bpy.data.objects.new('R06_TRACKING_TARGET',None);coll.objects.link(target);target.parent=root;target.location=(0,-30,35)
 bpy.context.view_layer.update()
 for o in ship:
  mw=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=mw
 # Start already clear of all piers; stow the old loading bridge components.
 stowed=[]
 for o in C['03_DOCK'].objects:
  if o.name.startswith(('Ship loader service bridge','Docking service gasket','Loader bridge support')):
   mw=o.matrix_world.copy();side=-1 if mw.translation.x<280 else 1
   mw.translation.x+=side*200;o.matrix_world=mw;o['R06_state']='STOWED_FOR_DEPARTURE';stowed.append(o.name)
 recipes={
 'Pearl ceramic-coated alloy':('R06 satin titanium enamel',(.49,.53,.50),.64,.30),
 'Structural graphite steel':('R06 graphite structure',(.025,.035,.048),.78,.30),
 'Oxide orange workzone coating':('R06 ochre cargo enamel',(.38,.095,.018),.35,.40),
 'Brushed bare metal':('R06 machined alloy',(.38,.45,.49),.90,.24),
 'Inset blue-black facade glazing':('R06 flight glass',(.012,.035,.043),.65,.14)}
 mats={}
 for old,(name,color,metal,rough) in recipes.items():
  m=bpy.data.materials[old].copy();m.name=name;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
  for socket in ['Base Color','Roughness','Normal']:
   for link in list(p.inputs[socket].links):nt.links.remove(link)
  p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
  n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=.13;n.inputs['Detail'].default_value=2
  ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=1;ramp.inputs['To Min'].default_value=rough*.86;ramp.inputs['To Max'].default_value=rough*1.14
  nt.links.new(n.outputs['Fac'],ramp.inputs['Value']);nt.links.new(ramp.outputs[0],p.inputs['Roughness']);mats[old]=m
 for o in ship:
  for slot in o.material_slots:
   if slot.material and slot.material.name in mats:
    m=mats[slot.material.name];slot.link='OBJECT';slot.material=m
 # Actual hull facets drive the formed plates; no unrelated replacement ship.
 platecount=0
 for f in list(hull.data.polygons)[2:26]:
  if len(f.vertices)!=4:continue
  pts=[hull.matrix_world@hull.data.vertices[i].co for i in f.vertices]
  mid=sum(pts,Vector())/4;normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
  if normal.dot(Vector((mid.x-center.x,0,mid.z-center.z)))<0:normal=-normal
  a=[mid+(p-mid)*.91+normal*1.1 for p in pts];vs=a+[v-normal*.8 for v in a]
  me=bpy.data.meshes.new('R06 formed bow plate');me.from_pydata(vs,[],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]);me.update();me.materials.append(mats['Pearl ceramic-coated alloy'])
  o=bpy.data.objects.new('R06 formed bow plate %02d'%platecount,me);C['04_FREIGHTER'].objects.link(o)
  be=o.modifiers.new('Plate edge radius','BEVEL');be.width=.35;be.segments=2
  o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();platecount+=1;ship.append(o)
 thrust=bpy.data.materials.new('R06 active ion core');thrust.use_nodes=True;p=thrust.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.12,.36,.56,1);p.inputs['Emission Color'].default_value=(.22,.6,1,1);p.inputs['Emission Strength'].default_value=5
 for o in ship:
  if o.name.startswith('Recessed inactive engine core'):
   for slot in o.material_slots:
    if slot.material and slot.material.name in ['Inset blue-black facade glazing','R06 flight glass']:slot.link='OBJECT';slot.material=thrust
  if o.name.startswith('Aft engine shroud') and o.type=='CURVE':o.data=o.data.copy();o.data.use_fill_caps=False
 oldlights=[]
 for o in list(S.objects):
  if o.type=='LIGHT':oldlights.append({'name':o.name,'energy':o.data.energy,'matrix':matrix(o)});o.hide_render=True
 def light(name,typ,pos,aim,energy,color,size):
  d=bpy.data.lights.new(name,typ);d.energy=energy;d.color=color
  if typ=='SUN':d.angle=size
  else:d.shape='DISK';d.size=size
  o=bpy.data.objects.new(name,d);coll.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();return o
 light('R06 directional warm sun','SUN',(-2300,-4200,4500),(0,1600,1300),4.0,(1,.88,.72),.04)
 light('R06 sky reflection','AREA',(-2000,-2200,2600),(280,0,1300),12500000,(.49,.68,1),1500)
 light('R06 edge reflection','AREA',(1300,-2000,2400),(280,0,1300),15000000,(.67,.79,1),1200)
 world=bpy.data.worlds.new('R06 deep-space studio sky');world.use_nodes=True;nt=world.node_tree;bg=nt.nodes.get('Background');bg.inputs[0].default_value=(.16,.23,.33,1);bg.inputs[1].default_value=.35
 cam_bg=nt.nodes.new('ShaderNodeBackground');cam_bg.inputs[0].default_value=(.004,.007,.013,1);cam_bg.inputs[1].default_value=.8
 lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(bg.outputs[0],mix.inputs[1]);nt.links.new(cam_bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('World Output').inputs['Surface']);S.world=world
 S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.2
 def follow(name,offset,lens):
  d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.2;d.clip_end=30000;d.dof.use_dof=False
  o=bpy.data.objects.new(name,d);C['08_CAMERAS'].objects.link(o);o.parent=root;o.location=offset
  con=o.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y';return o
 offsets={'R06_FRONT_QUARTER':(-1050,-1750,320),'R06_CROSS_RING':(-1280,-420,180),'R06_WIDE_CONTEXT':(-1400,-1250,450)}
 cams=[follow(n,offsets[n],lens) for n,lens in [('R06_FRONT_QUARTER',38),('R06_CROSS_RING',35),('R06_WIDE_CONTEXT',30)]]
 S.frame_start=1;S.frame_end=192;S.render.fps=24;S.render.fps_base=1
 for f in range(1,193):
  t=(f-1)/191;root.location=center+Vector((0,-1700-640*t,30*t));root.keyframe_insert(data_path='location',frame=f)
  for o in cams:o.location=Vector(offsets[o.name])+Vector((100*t,-100*t,35*t));o.keyframe_insert(data_path='location',frame=f)
 S.camera=cams[1];config(1280,32);checks=[];static0=None
 for f in [1,25,49,73,97,121,145,169,192]:
  S.frame_set(f);bpy.context.view_layer.update();pts=[p for o in ship if o.type=='MESH' for p in bbox(o)]
  stern=max(p.y for p in pts);assert stern<0,('Ship must start clear of dock and ring mouth',f,stern)
  ringmat=matrix(bpy.data.objects['Continuous inhabited ring shell']);static0=static0 or ringmat;assert ringmat==static0
  projected=[world_to_camera_view(S,S.camera,p) for p in bbox(hull)]
  box2=[min(p.x for p in projected),max(p.x for p in projected),min(p.y for p in projected),max(p.y for p in projected)]
  assert all(p.z>0 for p in projected) and -.03<box2[0]<box2[1]<1.03 and -.03<box2[2]<box2[3]<1.03,box2
  checks.append({'frame':f,'root':matrix(root),'camera':matrix(S.camera),'ship_bbox_uv':box2,'stern_y':stern,'ring':ringmat})
 S.frame_set(1);bpy.context.view_layer.update()
 changes=[o.name for o in environment if matrix(o)!=before[o.name]];assert set(changes)<=set(stowed),changes
 for n in oldcams:assert n in bpy.data.objects
 write('READONLY-INPUT-RECON.json',{'parent':str(BASE),'sha256':PARENT,'blender':bpy.app.version_string,'collections':{n:len(c.objects) for n,c in C.items()},'hull_world_bounds':[list(p) for p in hp],'ship_objects':len(ship),'old_lights':oldlights,'existing_camera_count':len(oldcams)})
 manifest={'candidate':'R06_FORWARD_FLIGHT_LIGHTING_STUDY','source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'blender':bpy.app.version_string,'user_amendment':'Released ship flies forward in world -Y; tracked by a moving camera. Habitat is stationary, not co-rotated. Starts after release; release sequence is not simulated.','original_ship_center':list(center),'motion':{'frames':192,'fps':24,'distance_m':math.sqrt(640**2+30**2),'environment_stationary':True,'preflight_checks':checks},'geometry_changes':{'formed_bow_plates':platecount,'stowed_loading_parts':stowed,'unchanged_other_environment_transforms':True,'city_geometry_changed':False},'materials':'ship-only enamel, graphite, alloy and glass; subtle roughness variation','cameras':{o.name:{'matrix':matrix(o),'lens':o.data.lens} for o in cams},'protected_parent_snapshot':PARENT,'legacy_cameras_retained':list(oldcams),'physics_validation':'KINEMATIC_AND_START_CLEARANCE_ONLY_NOT_FULL_DYNAMICS','external_assets':[],'auto_qualified':False}
 S['candidate']=manifest['candidate'];S['source_sha']=os.environ['GITHUB_SHA'];S['auto_qualified']=False
 p=OUT/'skyfold-r06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);manifest['scene_sha256']=digest(p);write('BUILD-MANIFEST.json',manifest);print('R06_SAVED',manifest['scene_sha256'],flush=True)
else:
 BASE=Path(bpy.data.filepath);meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
 rows=[];selected=os.environ.get('R06_CAMERA','R06_CROSS_RING')
 if MODE=='probe':views=[('R06_FRONT_QUARTER',1,1280,32,False),('R06_CROSS_RING',1,1280,32,False),('R06_WIDE_CONTEXT',1,1280,32,False),('R06_CROSS_RING',97,1280,32,False),('R06_CROSS_RING',192,1280,32,False),('R06_CROSS_RING',1,960,24,True)]
 elif MODE=='stills':views=[(selected,1,2560,128,False),(selected,97,1920,96,False),(selected,192,1920,96,False),(selected,1,1280,32,True)]
 elif MODE=='motion':
  a=int(os.environ['FRAME_START']);b=int(os.environ['FRAME_END']);assert 1<=a<=b<=192
  views=[(selected,f,int(os.environ.get('R06_WIDTH','1920')),int(os.environ.get('R06_SAMPLES','32')),False) for f in range(a,b+1)]
 else:raise ValueError(MODE)
 for camera,f,w,samples,neutral in views:
  S.frame_set(f);S.camera=bpy.data.objects[camera];bpy.context.view_layer.update();config(w,samples,MODE=='motion')
  layer=S.view_layers[0];layer.material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
  name=('frame_%04d'%f) if MODE=='motion' else '%s_f%03d%s'%(camera,f,'_NEUTRAL' if neutral else '')
  p=OUT/(name+'.png');S.render.filepath=str(p);start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
  dims=struct.unpack('>II',p.read_bytes()[16:24]);assert dims==(w,w*9//16)
  rows.append({'file':p.name,'frame':f,'camera':camera,'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell']),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'sha256':digest(p),'dimensions':dims,'samples':samples,'seconds':elapsed,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'motion_blur':MODE=='motion','neutral':neutral,'visual_verdict':'NOT_OBSERVED'})
  write('OBSERVATIONS.json',rows);print('R06_RENDERED',name,round(elapsed,2),flush=True)
 layer.material_override=None
 write('COMPLETE.json',{'mode':MODE,'frames':len(rows),'seconds':sum(r['seconds'] for r in rows),'run_id':os.environ['GITHUB_RUN_ID'],'scene_sha256':meta['scene_sha256'],'auto_qualified':False})
