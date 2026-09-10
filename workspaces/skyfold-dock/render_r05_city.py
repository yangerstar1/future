"""Same-camera R04C/R05 comparison and bounded structural regressions, no art auto-pass."""
import bpy, os, json, hashlib, time, struct
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);BASE=Path(bpy.data.filepath)
meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());h=hashlib.sha256(BASE.read_bytes()).hexdigest();assert h==meta['scene_sha256']
S=bpy.context.scene;phase=os.environ['R05_PHASE'];assert phase in ['control','candidate']
views=[('R04_HERO',1,1280,24,False)]
if phase=='candidate':
 views += [('R04_HERO',1,1280,24,True),('R04_SECOND',1,960,16,False),('R04_HERO',97,960,12,False),('R04_HERO',192,960,12,False),('O01_HERO',1,640,8,False)]
 views += [('R04_PARALLAX_%03d'%(i*25),1,640,8,False) for i in range(5)]
rows=[]
for name,frame,width,samples,neutral in views:
 S.frame_set(frame);S.camera=bpy.data.objects[name];bpy.context.view_layer.update()
 S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=samples;S.cycles.adaptive_threshold=.035;S.cycles.adaptive_min_samples=8
 S.render.resolution_x=width;S.render.resolution_y=width*9//16;S.render.resolution_percentage=100;S.render.use_compositing=False;S.render.use_motion_blur=False
 S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
 S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
 old_world=S.world;colors={o.name:tuple(o.data.color) for o in S.objects if o.type=='LIGHT'}
 if neutral:
  w=bpy.data.worlds.new('R05 neutral inspection');w.use_nodes=True;bg=w.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.5,.5,.5,1);bg.inputs[1].default_value=.8;S.world=w
  for n in colors:bpy.data.objects[n].data.color=(1,1,1)
 fn=f'{phase}_{name}_{frame:03d}'+('_NEUTRAL' if neutral else '')+'.png';p=OUT/fn;S.render.filepath=str(p)
 start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==(width,width*9//16)
 rows.append({'file':fn,'phase':phase,'candidate':meta['candidate'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'scene_sha256':h,'sha256':hashlib.sha256(b).hexdigest(),'camera':name,'frame':frame,'camera_matrix':[list(r) for r in S.camera.matrix_world],'lens':S.camera.data.lens,'samples':samples,'dimensions':[width,width*9//16],'seconds':elapsed,'neutral':neutral,'color_management':{'view':S.view_settings.view_transform,'look':S.view_settings.look,'exposure':S.view_settings.exposure},'art_status':'NOT_REVIEWED'})
 (OUT/f'{phase}-OBSERVATIONS.json').write_text(json.dumps(rows,indent=2))
 if neutral:
  S.world=old_world;bpy.data.worlds.remove(w)
  for n,c in colors.items():bpy.data.objects[n].data.color=c
 S.view_layers[0].material_override=None
 print('R05_OBSERVATION',fn,elapsed,flush=True)
