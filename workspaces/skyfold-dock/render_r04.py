"""Render R04 snapshots: pilot, presentation stills or a bounded true frame range."""
import bpy, os, json, hashlib, time, struct, resource
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath);meta=json.loads((BASE.parent/'BUILD-MANIFEST.json').read_text());scene_hash=hashlib.sha256(BASE.read_bytes()).hexdigest();assert scene_hash==meta['scene_sha256']
s=bpy.context.scene;mode=os.environ.get('R04_MODE','pilot');rows=[]
if mode=='pilot':
 views=[('R04_HERO',1,1920,24,False),('R04_HERO_LEVEL',1,960,16,False),('R04_SECOND',1,960,16,False),('R04_GALLERY_CRAFT',1,960,24,False),('R04_HERO',192,960,16,False),('O01_HERO',1,800,16,False),('R04_RETURN_LIFT_FULL',1,960,16,False),('R04_HERO',1,1280,20,True)]
elif mode=='stills':
 views=[('R04_HERO',1,2560,96,False),('R04_SECOND',1,1920,64,False),('R04_GALLERY_CRAFT',1,1920,64,False),('R04_HERO',1,1280,24,True),('R04_ROUTE_FULL',1,1280,24,False),('R04_RETURN_LIFT_FULL',1,1280,24,False)]+[('R04_PARALLAX_%03d'%(i*25),1,960,16,False) for i in range(5)]
elif mode=='motion':
 start=int(os.environ['FRAME_START']);end=int(os.environ['FRAME_END']);assert 1<=start<=end<=192
 views=[('R04_HERO',f,1920,12,False) for f in range(start,end+1)]
else:raise ValueError(mode)
for name,frame,width,samples,neutral in views:
 s.frame_set(frame);s.camera=bpy.data.objects[name];s.render.resolution_x=width;s.render.resolution_y=width*9//16;s.render.resolution_percentage=100;s.cycles.samples=samples
 s.cycles.adaptive_threshold=.10 if mode=='motion' else .035;s.cycles.adaptive_min_samples=4 if mode=='motion' else 8
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.use_compositing=False;s.render.use_motion_blur=False
 s.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
 name_out=('frame_%04d'%frame) if mode=='motion' else (name+('_NEUTRAL' if neutral else '')+('_f%03d'%frame))
 path=OUT/(name_out+'.png');s.render.filepath=str(path);bpy.context.view_layer.update();t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
 data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';dims=struct.unpack('>II',data[16:24]);assert dims==(width,width*9//16)
 rows.append({'file':path.name,'frame':frame,'camera':name,'camera_matrix':[list(r) for r in s.camera.matrix_world],'ring_matrix':[list(r) for r in bpy.data.objects['R04_HABITAT_ROTATION'].matrix_world],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'scene_sha256':scene_hash,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'dimensions':dims,'samples':samples,'seconds':elapsed,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'neutral':neutral,'engine':'CYCLES_CPU','generated_or_interpolated_frames':False})
 (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R04_FRAME_SAVED',path.name,round(elapsed,3),flush=True)
s.view_layers[0].material_override=None
(OUT/'COMPLETE.json').write_text(json.dumps({'mode':mode,'frames':len(rows),'scene_sha256':scene_hash,'render_source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'visual_verdict':'REVIEW_REQUIRED','total_render_seconds':sum(r['seconds'] for r in rows)},indent=2))
