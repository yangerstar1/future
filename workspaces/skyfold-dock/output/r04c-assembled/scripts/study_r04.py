"""Three bounded camera alternatives; native R03B geometry is not rebuilt or deleted."""
import bpy, json, os, time, hashlib, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'output/r03b/skyfold-r03b.blend'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='dca722c1cbfada7ce9a5a9b16926b136a29fd1ee256d5073c9b41852e5c64c68'
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene
views=[('A_FRONTAL_ARC',(-900,-720,470),(140,1230,1300),20),('B_BROADSIDE_CITY',(-930,500,650),(320,1080,1250),16),('C_MONUMENTAL_GATE',(-1350,-950,640),(150,1000,1400),24)]
records=[]
for name,pos,target,lens in views:
 d=bpy.data.cameras.new('R04_'+name);d.lens=lens;d.sensor_width=36;d.clip_start=.1;d.clip_end=20000
 c=bpy.data.objects.new(d.name,d);bpy.data.collections['08_CAMERAS'].objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();s.camera=c;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.cycles.samples=16;s.render.use_compositing=False
 s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/(name+'.png'))
 t=time.perf_counter();bpy.ops.render.render(write_still=True)
 records.append({'camera':name,'pos':pos,'target':target,'lens':lens,'matrix':[list(r) for r in c.matrix_world],'seconds':time.perf_counter()-t,'sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()})
(OUT/'CAMERA-STUDY.json').write_text(json.dumps({'source_sha':os.environ['GITHUB_SHA'],'input_scene_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'views':records,'verdict':'NOT_YET_REVIEWED','geometry_changed':False,'lights_changed':False},indent=2))
rows=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','LIGHT','CAMERA'}:continue
 rows.append({'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],'location':list(o.location),'dimensions':list(o.dimensions),'bounds':[[float(v) for v in o.matrix_world@Vector(co)] for co in o.bound_box] if o.type=='MESH' else None})
(OUT/'INVENTORY.json').write_text(json.dumps(rows))
print('R04_CAMERA_STUDY_COMPLETE',records)
