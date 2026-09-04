"""Technical diagnostic only. The factory cube is not a scene deliverable."""
import bpy, json, os, time
from pathlib import Path
out = Path(os.environ['GITHUB_WORKSPACE'])/'evidence'/'tool-probe'
out.mkdir(parents=True, exist_ok=True)
s = bpy.context.scene
assert bpy.app.version[:2] == (4,5), bpy.app.version_string
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=8
s.cycles.use_denoising=True
s.render.resolution_x=320;s.render.resolution_y=180;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=4
s.render.image_settings.file_format='PNG'
s.render.filepath=str(out/'diagnostic.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic.blend'))
t=time.monotonic();bpy.ops.render.render(write_still=True)
report={'blender':bpy.app.version_string,'python':__import__('sys').version,'engine':s.render.engine,'device':'CPU','probe_seconds':time.monotonic()-t,'samples':8,'resolution':[320,180],'build_hash':bpy.app.build_hash.decode(),'scene_saved':(out/'diagnostic.blend').is_file(),'original_png_bytes':(out/'diagnostic.png').stat().st_size,'visual_status':'FACTORY_SCENE_TECHNICAL_PROBE_NOT_ART'}
(out/'probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
