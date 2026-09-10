"""Small actual composition/movement samples; EEVEE is tested, never presumed faster."""
import bpy,os,json,time,hashlib,resource
from pathlib import Path
out=Path(os.environ['SKYFOLD_OUT']);s=bpy.context.scene;meta=json.loads((Path(bpy.data.filepath).parent/'BUILD-MANIFEST.json').read_text());h=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();assert h==meta['scene_sha256'];rows=[]
mode=os.environ.get('PROBE_ENGINE','CYCLES');s.render.engine=mode;s.camera=bpy.data.objects['R04_HERO'];s.render.use_compositing=False;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
if mode=='CYCLES':views=[(1,1280,16),(97,960,12),(192,960,12),(5,640,8)]
else:
 props=[p.identifier for p in s.eevee.bl_rna.properties];(out/'EEVEE-RNA.json').write_text(json.dumps(props));s.eevee.taa_render_samples=16
 if hasattr(s.eevee,'use_raytracing'):s.eevee.use_raytracing=False
 views=[(1,1920,16),(97,1920,16)]
for f,w,n in views:
 s.frame_set(f);s.render.resolution_x=w;s.render.resolution_y=w*9//16
 if mode=='CYCLES':s.cycles.samples=n;s.cycles.adaptive_min_samples=4;s.cycles.adaptive_threshold=.07
 bpy.context.view_layer.update();p=out/('%s_f%03d.png'%(mode,f));s.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True)
 row={'engine':mode,'frame':f,'file':p.name,'dimensions':[w,w*9//16],'seconds':time.perf_counter()-t,'samples':n,'scene_sha256':h,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera_matrix':[list(r) for r in s.camera.matrix_world],'ring_matrix':[list(r) for r in bpy.data.objects['R04_HABITAT_ROTATION'].matrix_world],'source_sha':os.environ['GITHUB_SHA'],'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'visual_status':'NOT_OBSERVED'};rows.append(row);(out/(mode+'-PROBE.json')).write_text(json.dumps(rows,indent=2));print('PROBE_FRAME',row,flush=True)
