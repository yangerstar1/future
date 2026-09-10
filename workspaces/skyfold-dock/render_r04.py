"""Render immutable R04-family snapshots; image dimensions are explicit, not artistic PASS."""
import bpy, os, json, hashlib, time, struct, resource
from pathlib import Path
from mathutils import Vector
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath);meta=json.loads((BASE.parent/'BUILD-MANIFEST.json').read_text());scene_hash=hashlib.sha256(BASE.read_bytes()).hexdigest();assert scene_hash==meta['scene_sha256']
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';mode=os.environ.get('R04_MODE','pilot');rows=[]
if mode=='pilot':
 views=[('R04_HERO',1,1920,24,False),('R04_HERO_LEVEL',1,960,16,False),('R04_SECOND',1,960,16,False),('R04_GALLERY_CRAFT',1,960,24,False),('R04_HERO',192,960,16,False),('O01_HERO',1,800,16,False),('R04_RETURN_LIFT_FULL',1,960,16,False),('R04_HERO',1,1280,20,True)]
elif mode=='stills':
 views=[('R04_HERO',1,2560,96,False),('R04_SECOND',1,1920,64,False),('R04_GALLERY_CRAFT',1,1920,64,False),('R04_HERO',1,1280,24,True),('R04_ROUTE_FULL',1,1280,24,False),('R04_RETURN_LIFT_FULL',1,1280,24,False)]+[('R04_PARALLAX_%03d'%(i*25),1,960,16,False) for i in range(5)]
elif mode=='motion':
 start=int(os.environ['FRAME_START']);end=int(os.environ['FRAME_END']);assert 1<=start<=end<=192
 width=int(os.environ.get('MOTION_WIDTH','1920'));samples=int(os.environ.get('MOTION_SAMPLES','12'));assert width in [1280,1920] and 8<=samples<=64
 views=[('R04_HERO',f,width,samples,False) for f in range(start,end+1)]
else:raise ValueError(mode)
rig=bpy.data.objects['R04_HABITAT_ROTATION'];gallery=bpy.data.collections['10_R04_GALLERY']
solid_names=('R04 observation landing','R04 walking deck panel','R04 mobile diagnostic trolley')
for name,frame,width,samples,neutral in views:
 s.frame_set(frame);s.camera=bpy.data.objects[name];s.render.resolution_x=width;s.render.resolution_y=width*9//16;s.render.resolution_percentage=100;s.cycles.samples=samples
 s.cycles.adaptive_threshold=.10 if mode=='motion' else .035;s.cycles.adaptive_min_samples=4 if mode=='motion' else 8
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.use_compositing=False;s.render.use_motion_blur=False
 s.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
 old_world=s.world;light_colors={o.name:tuple(o.data.color) for o in s.objects if o.type=='LIGHT'}
 if neutral:
  world=bpy.data.worlds.new('TEMP_NEUTRAL_LIGHT');world.use_nodes=True;bg=world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.5,.5,.5,1);bg.inputs[1].default_value=.8;s.world=world
  for n in light_colors:bpy.data.objects[n].data.color=(1,1,1)
 name_out=('frame_%04d'%frame) if mode=='motion' else (name+('_NEUTRAL' if neutral else '')+('_f%03d'%frame))
 path=OUT/(name_out+'.png');s.render.filepath=str(path);bpy.context.view_layer.update()
 # Limited exact oriented-box intrusion check, not a claim of complete path collision simulation.
 if name=='R04_HERO':
  for o in gallery.objects:
   if o.type!='MESH' or not o.name.startswith(solid_names):continue
   p=o.matrix_world.inverted()@s.camera.matrix_world.translation;lo=[min(v[i] for v in o.bound_box) for i in range(3)];hi=[max(v[i] for v in o.bound_box) for i in range(3)]
   assert not all(lo[i]+.01<p[i]<hi[i]-.01 for i in range(3)),('Camera inside gallery solid',frame,o.name)
 for o in bpy.data.collections['04_FREIGHTER'].objects:assert o.parent==rig and o.animation_data is None,('Independent docked-ship motion',o.name)
 t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
 if neutral:
  s.world=old_world
  for n,c in light_colors.items():bpy.data.objects[n].data.color=c
  bpy.data.worlds.remove(world)
 data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';dims=struct.unpack('>II',data[16:24]);assert dims==(width,width*9//16)
 rows.append({'file':path.name,'frame':frame,'camera':name,'camera_matrix':[list(r) for r in s.camera.matrix_world],'ring_matrix':[list(r) for r in rig.matrix_world],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'scene_sha256':scene_hash,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'dimensions':dims,'samples':samples,'seconds':elapsed,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'neutral':neutral,'neutral_lighting':neutral,'engine':'CYCLES_CPU','gallery_camera_intrusion_check':'limited deck/trolley OBB checked' if name=='R04_HERO' else 'not applicable','generated_or_interpolated_frames':False})
 (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R04_FRAME_SAVED',path.name,round(elapsed,3),flush=True)
s.view_layers[0].material_override=None
(OUT/'COMPLETE.json').write_text(json.dumps({'mode':mode,'frames':len(rows),'scene_sha256':scene_hash,'render_source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'visual_verdict':'REVIEW_REQUIRED','total_render_seconds':sum(r['seconds'] for r in rows),'motion_720_status':'PREVIEW_NOT_CONTRACT_P2_1080_PASS' if mode=='motion' and width==1280 else 'not applicable'},indent=2))
