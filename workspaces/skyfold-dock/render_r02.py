"""Real fixed observations of the immutable R02 scene; no quality auto-promotion."""
import bpy,os,json,time,hashlib,struct
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);SC=bpy.context.scene
man=json.loads((OUT/'BUILD-MANIFEST.json').read_text());digest=hashlib.sha256((OUT/'skyfold-r02.blend').read_bytes()).hexdigest()
assert man['scene_sha256']==digest
views=[('O01_HERO',1200,24,False),('O01_CAMERA_B',960,20,False),('O01_CAMERA_C',960,20,False),('O01_SECOND',960,20,False),('R01_O01_HERO',960,16,False),('O01_HERO',1200,24,True),('O03_REAR',960,20,False),('O04_CRAFT',1200,32,False),('O04_INTERFACE',960,24,False),('O05_ROUTE',1200,24,False),('O05_LIFT',960,20,False)]+[('O06_%03d'%(i*25),800,16,False) for i in range(5)]
records=[]
for name,w,samples,clay in views:
 label='O02_NEUTRAL' if clay else name
 SC.camera=bpy.data.objects[name];SC.render.resolution_x=w;SC.render.resolution_y=round(w*9/16);SC.render.resolution_percentage=100;SC.cycles.samples=samples
 SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if clay else None
 SC.render.use_compositing=False;SC.camera.data.dof.use_dof=False
 bg=SC.world.node_tree.nodes.get('Background');old=(tuple(bg.inputs[0].default_value),bg.inputs[1].default_value)
 if clay:bg.inputs[0].default_value=(.5,.5,.5,1);bg.inputs[1].default_value=.8
 path=OUT/(label+'.png');SC.render.filepath=str(path);t=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-t
 bg.inputs[0].default_value=old[0];bg.inputs[1].default_value=old[1];SC.view_layers[0].material_override=None
 header=path.read_bytes()[:24];assert header[:8]==b'\x89PNG\r\n\x1a\n';dimensions=struct.unpack('>II',header[16:24]);assert dimensions==(w,round(w*9/16))
 row={'observation':label,'candidate':'R02_SPATIAL_STUDY','source_sha':os.environ['GITHUB_SHA'],'scene_sha256':digest,'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':name,'matrix':[list(r) for r in SC.camera.matrix_world],'lens':SC.camera.data.lens,'dimensions':dimensions,'samples':samples,'seconds':elapsed,'engine':'CYCLES_CPU','compositing':False,'visual_verdict':'NOT_OBSERVED'}
 records.append(row);(OUT/'OBSERVATIONS.json').write_text(json.dumps(records,indent=2));print('OBSERVATION',json.dumps(row),flush=True)
print('R02_OBSERVATIONS_SAVED',len(records),'NOT_A_VISUAL_PASS')
