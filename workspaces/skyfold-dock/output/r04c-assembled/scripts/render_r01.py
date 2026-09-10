"""Render true fixed-camera structural observations; outputs never imply artistic PASS."""
import bpy,os,time,json,hashlib,base64,struct
from pathlib import Path
OUT=Path(os.environ['SKYFOLD_OUT']);S=bpy.context.scene
source=(OUT/'BUILD-MANIFEST.json');man=json.loads(source.read_text());records=[]
scene_hash=hashlib.sha256((OUT/'skyfold-r01.blend').read_bytes()).hexdigest()
assert scene_hash==man['scene_sha256']
views=[('O01_HERO',960,16,False),('O01_SECOND',640,12,False),('O01_R00_FIXED',640,12,False),('O01_HERO',960,16,True),('O03_REAR',640,12,False),('O04_CRAFT',800,24,False),('O04_INTERFACE',640,16,False),('O05_ROUTE',640,12,False)]+[('O06_%03d'%(i*25),576,10,False) for i in range(5)]
# Host-size review transport is only a derivative. Original PNG and scene remain intact.
def derivative(p):
 im=bpy.data.images.load(str(p),check_existing=False);w=320;h=round(w*im.size[1]/im.size[0]);im.scale(w,h)
 old=(S.view_settings.view_transform,S.view_settings.look,S.view_settings.exposure,S.render.image_settings.file_format,S.render.image_settings.quality)
 S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=0;S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=24
 jpg=p.with_suffix('.review.jpg');im.save_render(str(jpg),scene=S);bpy.data.images.remove(im)
 S.view_settings.view_transform=old[0];S.view_settings.look=old[1];S.view_settings.exposure=old[2];S.render.image_settings.file_format=old[3];S.render.image_settings.quality=old[4]
 enc=base64.b64encode(jpg.read_bytes()).decode();jpg.with_suffix('.b64').write_text('\n'.join(enc[i:i+1000] for i in range(0,len(enc),1000)))
 return {'path':jpg.name,'width':w,'height':h,'bytes':jpg.stat().st_size,'kind':'NON_GENERATIVE_DOWNSIZED_REVIEW_ONLY_NOT_DELIVERY_RENDER'}
for name,width,samples,clay in views:
 label='O02_NEUTRAL' if clay else name
 S.camera=bpy.data.objects[name];S.render.resolution_x=width;S.render.resolution_y=round(width*9/16);S.render.resolution_percentage=100;S.cycles.samples=samples
 S.render.image_settings.file_format='PNG';S.view_layers[0].material_override=bpy.data.materials['Neutral inspection clay'] if clay else None
 bg=S.world.node_tree.nodes.get('Background');oldbg=(tuple(bg.inputs[0].default_value),bg.inputs[1].default_value)
 if clay:bg.inputs[0].default_value=(.5,.5,.5,1);bg.inputs[1].default_value=.8
 p=OUT/(label+'.png');S.render.filepath=str(p);start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
 bg.inputs[0].default_value=oldbg[0];bg.inputs[1].default_value=oldbg[1];S.view_layers[0].material_override=None
 assert p.is_file() and p.stat().st_size>1000
 with p.open('rb') as f:header=f.read(24)
 assert header[:8]==b'\x89PNG\r\n\x1a\n';dims=struct.unpack('>II',header[16:24]);assert dims==(width,round(width*9/16))
 rec={'observation':label,'candidate':'R01_PROVISIONAL','source_sha':os.environ['GITHUB_SHA'],'scene_sha256':scene_hash,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':name,'camera_matrix':[list(row) for row in S.camera.matrix_world],'dimensions':dims,'samples':samples,'seconds':elapsed,'render_engine':'CYCLES_CPU','compositing':False,'visual_verdict':'NOT_OBSERVED','review_derivative':derivative(p)}
 records.append(rec);(OUT/'OBSERVATIONS.json').write_text(json.dumps(records,indent=2));print('OBSERVATION_SAVED',json.dumps(rec))
print('OBSERVATIONS_COMPLETE',len(records),'NO_ARTISTIC_GATE_AUTOMATICALLY_PASSED')
