"""Native-size observation of the inspected R08B, not a new design or art PASS."""
import bpy,os,json,hashlib,time,struct,resource,ast
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True);ROOT=Path(__file__).resolve().parent;BASE=Path(bpy.data.filepath);S=bpy.context.scene
expected='e714356e215b7e857adaf29c224cb8d9261ab094f74cfb5e11ada45e0e05d877'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==expected
meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text());assert meta['scene_sha256']==expected;assert bpy.app.version[:3]==(4,5,13)
definitions=[n for n in ast.parse((ROOT/'r06_flight.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='config'];assert len(definitions)==1
exec(compile(ast.Module(body=definitions,type_ignores=[]),'EXISTING_R06_RENDER_CONFIG','exec'),globals())
rows=[]
for w,n,grade,label in [(2560,64,True,'R08B_HERO_2560'),(1280,32,False,'R08B_RAW_1280')]:
 S.frame_set(1);S.camera=bpy.data.objects['R08B_LOW_AXIS'];bpy.context.view_layer.update();config(w,n,False);S.render.use_compositing=grade;S.view_layers[0].material_override=None
 p=OUT/(label+'.png');S.render.filepath=str(p);t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
 data=p.read_bytes();dims=struct.unpack('>II',data[16:24]);assert dims==(w,w*9//16)
 rows.append({'file':p.name,'frame':1,'camera':S.camera.name,'camera_matrix':[list(r) for r in S.camera.matrix_world],'ship_matrix':[list(r) for r in bpy.data.objects['R06_SHIP_FORWARD_FLIGHT'].matrix_world],'ring_matrix':[list(r) for r in bpy.data.objects['Continuous inhabited ring shell'].matrix_world],'scene_sha256':expected,'scene_source_sha':meta['source_sha'],'render_source_sha':os.environ['GITHUB_SHA'],'dimensions':dims,'samples':n,'compositing':grade,'seconds':elapsed,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sha256':hashlib.sha256(data).hexdigest(),'visual_verdict':'NOT_OBSERVED'})
 (OUT/'OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));print('R08B_NATIVE_RENDER',label,elapsed,flush=True)
(OUT/'COMPLETE.json').write_text(json.dumps({'count':len(rows),'run_id':os.environ['GITHUB_RUN_ID'],'render_source_sha':os.environ['GITHUB_SHA'],'scene_sha256':expected,'auto_qualified':False},indent=2))
