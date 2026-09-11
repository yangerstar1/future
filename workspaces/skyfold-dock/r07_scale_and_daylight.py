"""R07: one evidence-led scale correction after the small-ring camera studies failed.
Keep the 875m hull; enlarge the ring radius to 10km, rebuild only the curved urban
bases at that radius, preserve rigid buildings, and track a real airborne vessel.
Reference-grounded daylight and bounded depth grading are not geometry replacements.
"""
import bpy,ast,os,math,json,hashlib,random,time,struct,resource
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);S=bpy.context.scene;BASE=Path(bpy.data.filepath)
MODE=os.environ.get('R07_MODE','build')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matx(o):return [list(r) for r in o.matrix_world]
def bbox(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
if MODE=='build':
 parent='a11cb63ae232672ca92080250f10a6d5ad67c1b5d95e3e575763dfe4014b92dc';assert digest(BASE)==parent
 assert bpy.app.version[:3]==(4,5,13)
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());S.frame_set(1);bpy.context.view_layer.update()
 COL={c.name:c for c in bpy.data.collections};R=10000.;ANCHOR=1.4;CACHE={};footing_tests=[]
 materials=['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay','Recessed planted courtyards','City basalt roadbed']
 M=[bpy.data.materials[n] for n in materials];PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY,PARK,ROAD=range(13)
 raw=(ROOT/'build_scene_r01.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
 defs=[n for n in ast.parse(raw).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Mesh','box','frame','ring_strip'}];exec(compile(ast.Module(body=defs,type_ignores=[]),'VERIFIED_R01_GEOMETRY','exec'),globals())
 ground=(ROOT/'revise_r05b_city.py').read_bytes();assert hashlib.sha256(ground).hexdigest()=='29343bc95f19b21a7e3710b5797542109ab213efa4ca1eff58cb645d3c2d453b'
 defs=[n for n in ast.parse(ground).body if isinstance(n,ast.FunctionDef) and n.name in {'surface_z','patch','building'}];exec(compile(ast.Module(body=defs,type_ignores=[]),'R05B_GROUND_AT_NEW_RADIUS','exec'),globals())
 tree=ast.parse((ROOT/'revise_r05_city.py').read_text());plans=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='plans' for t in n.targets)))
 old=[bpy.data.objects['City archetype %02d'%k] for k in range(10)]
 # Structural radius changes; rigid city buildings and the ship are never stretched.
 old_radius=1600.;scale=R/old_radius;scaled=[];removed_roads=[]
 for o in list(COL['01_RING_STRUCTURE'].objects):
  if o.name.startswith(('R04C city transit','R04C transit median','R02 city transport','R02 city median')):
   removed_roads.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
  else:o.matrix_world=Matrix.Diagonal((scale,1,scale,1))@o.matrix_world;scaled.append(o.name)
 assert len(removed_roads)>30
 for j in range(21):
  y=55+j*230;ring_strip('R07 circumferential surface avenue',R-.12,R+.12,y-11,y+11,ROAD)
  ring_strip('R07 avenue median',R-.15,R-.11,y-.7,y+.7,CONCRETE)
 protos={}
 for family,plan in plans.items():
  for variant in range(3):
   g=Mesh();patch(g,(0,-85),(178,6),ROAD);patch(g,(92.5,0),(3,164),ROAD)
   if family=='PLZA':raise AssertionError('Unexpected land-use spelling')
   if family=='PLAZA':
    patch(g,(-18,28),(70,82),PARK,.35);patch(g,(49,-37),(42,66),PARK,.35);patch(g,(-6,-35),(106,7),CONCRETE)
   else:
    if family in {'RESIDENTIAL','MIXED_CORE','INDUSTRIAL'}:patch(g,(-3,0),(10,158),ROAD)
    patch(g,(0,78),(106,6),PARK,.35)
   for n,(k,x,y,sz) in enumerate(plan):building(g,k,x+(variant-1)*(3 if n%2 else -3),y,sz*(.90+.08*variant))
   o=g.object('R07 %s prototype %d'%(family,variant),'09_PROTOTYPES');o.hide_render=True;o.hide_viewport=True;protos[family,variant]=o
 old_city_count=len(COL['02_CITY_INSTANCES'].objects)
 for o in list(COL['02_CITY_INSTANCES'].objects):bpy.data.objects.remove(o,do_unlink=True)
 layout=[]
 for i in range(270):
  theta=(i+.5)*2*math.pi/270
  if min(theta,2*math.pi-theta)<.12:continue
  for j in range(21):
   rng=random.Random(270910+i*1009+j*9176);activity=math.sin(theta*2.6-.9)+.66*math.cos(j*.56+theta*.8)
   if (i//14+j//3)%9==0 or rng.random()<.1:family='PLAZA'
   elif activity>1.04:family=rng.choice(['OFFICE','MIXED_CORE','MIXED_CORE','LANDMARK'])
   elif activity<-.8:family=rng.choice(['INDUSTRIAL','INDUSTRIAL','TERRACES'])
   else:family=rng.choice(['RESIDENTIAL','RESIDENTIAL','CIVIC','TERRACES','OFFICE'])
   variant=(i+j*2)%3;p=protos[family,variant];o=bpy.data.objects.new('R07 urban site %03d-%02d'%(i,j),p.data);COL['02_CITY_INSTANCES'].objects.link(o);o.matrix_world=frame(theta+(j%2)*.002,150+j*230,ANCHOR);o['prototype']=p.name;o['ground_theta']=theta;o['local_up']='INWARD_RADIAL'
   layout.append({'name':o.name,'theta':theta,'y':150+j*230,'prototype':p.name})
 # Existing equipment stays metre-scale. Add only the missing foundation depth to the lower-curvature floor.
 extra=bpy.data.collections.new('14_R07_FOUNDATION_ADAPTERS');S.collection.children.link(extra);COL[extra.name]=extra;foundation_adapters=[]
 for c in [v for k,v in COL.items() if k.startswith(('03_','05_','06_','10_'))]:
  for o in list(c.objects):
   if o.type!='MESH' or not any(k in o.name.lower() for k in ['foundation','footing']):continue
   ps=bbox(o);x=sum(p.x for p in ps)/8;y=sum(p.y for p in ps)/8;bottom=min(p.z for p in ps)
   if abs(x)>=R or not 0<=y<=5000:continue
   ground=R-math.sqrt(R*R-x*x)
   if bottom>ground+.2:
    w=max(p.x for p in ps)-min(p.x for p in ps);d=max(p.y for p in ps)-min(p.y for p in ps)
    a=box('R07 foundation adapter for '+o.name,(x,y,(ground+bottom)/2),(w,d,bottom-ground+.4),CONCRETE,extra.name,.1);foundation_adapters.append({'object':a.name,'supports':o.name,'ground_z':ground,'old_bottom_z':bottom})
 # Same freighter, safely above the existing berth and inside the large inhabited ring.
 root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'];root.animation_data_clear();root.rotation_euler=(0,0,0)
 target=bpy.data.objects['R06_TRACKING_TARGET'];target.location=(0,0,120)
 cameras=[]
 for name,offset,lens in [('R07_GRAZING_TRACK',(-1050,-60,-850),26),('R07_WIDE_TRACK',(-1650,-180,-1350),24)]:
  d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.2;d.clip_end=50000
  o=bpy.data.objects.new(name,d);COL['08_CAMERAS'].objects.link(o);o.parent=root;o.location=offset
  q=o.constraints.new('TRACK_TO');q.target=target;q.track_axis='TRACK_NEGATIVE_Z';q.up_axis='UP_Y';cameras.append(o)
 for f in range(1,193):
  t=(f-1)/191;root.location=(280,3250-640*t,3000+20*t);root.keyframe_insert(data_path='location',frame=f)
  for cam,offset in zip(cameras,[(-1050,-60,-850),(-1650,-180,-1350)]):cam.location=Vector(offset)+Vector((-80*t,-80*t,40*t));cam.keyframe_insert(data_path='location',frame=f)
 # Atmosphere/lighting reuses Blender's analytic sky, without external texture or model services.
 for o in S.objects:
  if o.type=='LIGHT':o.hide_render=True
 lighting=bpy.data.collections.new('15_R07_DAYLIGHT');S.collection.children.link(lighting)
 def light(name,kind,p,aim,power,color,size):
  d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
  if kind=='SUN':d.angle=size
  else:d.shape='DISK';d.size=size
  o=bpy.data.objects.new(name,d);lighting.objects.link(o);o.location=p;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler();return o
 light('R07 soft directional daylight','SUN',(-4000,-8000,11000),(280,3250,3000),2.8,(1,.89,.75),.06)
 light('R07 large reflected sky aperture','AREA',(-1800,2200,5200),(280,2850,3000),25000000,(.63,.79,1),2400)
 light('R07 lower reflected city fill','AREA',(-950,2600,1300),(280,2850,3000),18000000,(.77,.85,1),1700)
 world=bpy.data.worlds.new('R07 inhabited-ring daylight');world.use_nodes=True;nt=world.node_tree;sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_disc=False;sky.sun_elevation=.60;sky.sun_rotation=math.radians(230);sky.air_density=1.;sky.dust_density=.3;sky.ozone_density=1.1
 bg=nt.nodes.get('Background');bg.inputs['Strength'].default_value=.45;nt.links.new(sky.outputs['Color'],bg.inputs['Color']);S.world=world
 S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=0
 # Bounded depth grade; raw uncomposited and neutral observations remain available.
 S.use_nodes=True;nt=S.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');S.view_layers[0].use_pass_z=True
 depth=nt.nodes.new('CompositorNodeMapRange');depth.inputs['From Min'].default_value=1800;depth.inputs['From Max'].default_value=24000;depth.inputs['To Min'].default_value=0;depth.inputs['To Max'].default_value=.18;depth.use_clamp=True
 nt.links.new(rl.outputs['Depth'],depth.inputs['Value']);mix=nt.nodes.new('CompositorNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.25,.38,.55,1);nt.links.new(depth.outputs[0],mix.inputs[0]);nt.links.new(rl.outputs['Image'],mix.inputs[1]);comp=nt.nodes.new('CompositorNodeComposite');nt.links.new(mix.outputs[0],comp.inputs[0])
 S.frame_set(1);bpy.context.view_layer.update();S.camera=cameras[0];S.render.resolution_x=1280;S.render.resolution_y=720
 checks=[]
 for f in [1,49,97,145,192]:
  S.frame_set(f);bpy.context.view_layer.update();ps=[v for o in COL['04_FREIGHTER'].objects if o.type=='MESH' and not o.hide_render for v in bbox(o)]
  assert min(p.y for p in ps)>2000 and max(math.hypot(p.x,p.z-R) for p in ps)<8500
  for cam in cameras:
   uv=[world_to_camera_view(S,cam,p) for p in ps];bounds=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)]
   assert min(bounds)>.01 and max(bounds)<.99,bounds
   checks.append({'frame':f,'camera':cam.name,'ship_bounds_uv':bounds,'camera_matrix':matx(cam),'ship_matrix':matx(root)})
 S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R07_SCALE_CORRECTED_DAYLIGHT_FLIGHT';S['source_sha']=os.environ['GITHUB_SHA']
 (OUT/'CITY-LAYOUT.json').write_text(json.dumps(layout,indent=2))
 meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':parent,'R07_scale_change':{'old_ring_diameter_m':3200,'new_ring_diameter_m':20000,'axial_width_m':5000,'ship_hull_length_m':875,'old_city_sites':old_city_count,'new_city_sites':len(layout),'rigid_buildings_scaled':False,'rebuilt_ground_prototypes':len(protos),'ground_checks':footing_tests,'foundation_adapters':foundation_adapters,'city_layout_sha256':digest(OUT/'CITY-LAYOUT.json')},'current_motion':{'frames':192,'fps':24,'start':[280,3250,3000],'end':[280,2610,3020],'camera':'R07_GRAZING_TRACK','world_direction':'NEGATIVE_Y','checks':checks,'docked_status':'ALREADY_RELEASED_NOT_A_SIMULATED_UNDOCKING'},'rendering':{'lighting':'Analytic Nishita daylight plus sun and large reflected-light sources','grading':'Blender depth-based mix up to 18 percent; raw and neutral must be retained','external_assets':[]},'regression_warning':'Scale intervention invalidates prior habitat/dock/transport visual acceptance. Preserve all prior scene snapshots and do not promote G2 automatically.','quality_status':'MAJOR_SCALE_HYPOTHESIS_REQUIRES_REAL_VISUAL_REVIEW'})
 p=OUT/'skyfold-r07.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=digest(p);(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R07_SAVED',meta['scene_sha256'],len(layout),flush=True)
else:
 meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
 defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='config'];exec(compile(ast.Module(body=defs,type_ignores=[]),'R06_RENDER_CONFIGURATION','exec'),globals())
 if MODE=='probe':views=[('R07_GRAZING_TRACK',1,1280,32,False,True),('R07_WIDE_TRACK',1,1280,32,False,True),('R07_GRAZING_TRACK',192,1280,32,False,True),('R07_GRAZING_TRACK',1,960,24,True,False),('R07_GRAZING_TRACK',1,1280,32,False,False)]
 elif MODE=='hero':views=[('R07_GRAZING_TRACK',1,2560,128,False,True),('R07_GRAZING_TRACK',1,2560,128,False,False)]
 elif MODE=='motion':
  a=int(os.environ['FRAME_START']);b=int(os.environ['FRAME_END']);assert 1<=a<=b<=192;views=[('R07_GRAZING_TRACK',f,int(os.environ.get('R07_WIDTH','1920')),int(os.environ.get('R07_SAMPLES','24')),False,True) for f in range(a,b+1)]
 else:raise ValueError(MODE)
 rows=[]
 for camera,f,w,samples,neutral,grade in views:
  S.frame_set(f);S.camera=bpy.data.objects[camera];bpy.context.view_layer.update();config(w,samples,MODE=='motion');S.render.use_compositing=grade;S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
  name=('frame_%04d'%f) if MODE=='motion' else '%s_f%03d_%s'%(camera,f,'NEUTRAL' if neutral else 'BEAUTY' if grade else 'RAW')
  p=OUT/(name+'.png');S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-t
  dims=struct.unpack('>II',p.read_bytes()[16:24]);assert dims==(w,w*9//16)
  rows.append({'file':p.name,'frame':f,'camera':camera,'camera_matrix':matx(S.camera),'ship_matrix':matx(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matx(bpy.data.objects['Continuous inhabited ring shell']),'dimensions':dims,'samples':samples,'seconds':seconds,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sha256':digest(p),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'compositing':grade,'neutral':neutral,'motion_blur':MODE=='motion','visual_verdict':'NOT_OBSERVED'})
  (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R07_RENDERED',name,seconds,flush=True)
 S.view_layers[0].material_override=None;(OUT/'COMPLETE.json').write_text(json.dumps({'mode':MODE,'frames':len(rows),'render_seconds':sum(r['seconds'] for r in rows),'scene_sha256':meta['scene_sha256'],'run_id':os.environ['GITHUB_RUN_ID'],'auto_qualified':False},indent=2))
