"""Real departure keyframe/cost check; reuse verified R06 Cycles configuration."""
import bpy, os, ast, time, json, struct, hashlib, resource
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;ROOT=Path(__file__).resolve().parent
wanted={'config','matrix','digest'}
defs=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
assert {n.name for n in defs}==wanted
exec(compile(ast.Module(body=defs,type_ignores=[]),'R06_EXISTING_RENDER_HELPERS','exec'),globals())
BASE=Path(bpy.data.filepath);meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert digest(BASE)==meta['scene_sha256']
rows=[];camera=os.environ.get('R06_CHECK_CAMERA','R06B_DEPARTURE_TRACK');label=os.environ.get('R06_CHECK_LABEL','R06B')
for f,width,samples,neutral,blur in [(1,1280,32,False,False),(192,1280,32,False,False),(97,1920,24,False,True),(1,960,24,True,False)]:
 S.frame_set(f);S.camera=bpy.data.objects[camera];bpy.context.view_layer.update();config(width,samples,blur)
 S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if neutral else None
 p=OUT/('%s_f%03d%s.png'%(label,f,'_NEUTRAL' if neutral else ''));S.render.filepath=str(p)
 start=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-start
 assert struct.unpack('>II',p.read_bytes()[16:24])==(width,width*9//16)
 row={'file':p.name,'frame':f,'dimensions':[width,width*9//16],'samples':samples,'motion_blur':blur,'shutter':.25 if blur else 0,'seconds':seconds,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'camera':S.camera.name,'camera_matrix':matrix(S.camera),'ship_matrix':matrix(bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']),'ring_matrix':matrix(bpy.data.objects['Continuous inhabited ring shell']),'scene_sha256':meta['scene_sha256'],'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'sha256':digest(p),'neutral':neutral,'visual_verdict':'NOT_OBSERVED'}
 rows.append(row);(OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('DEPARTURE_FRAME_SAVED',p.name,seconds,flush=True)
S.view_layers[0].material_override=None
(OUT/'COMPLETE.json').write_text(json.dumps({'run_id':os.environ['GITHUB_RUN_ID'],'frames':len(rows),'scene_sha256':meta['scene_sha256'],'render_seconds':sum(r['seconds'] for r in rows),'auto_qualified':False},indent=2))
