"""Observe the existing integrated COAST-R04, never generate or alter imagery.
One full-resolution water witness and two short native frame sequences. This is
motion evidence, not the contract's finished film. Never saves a Blender master.
"""
import bpy, hashlib, json, os, sys, time
from pathlib import Path
from array import array
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-coast-r04'
OUT=ROOT/'output/g4-coast-r04-motion-proof';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='51a3501edd81f879ba1b5c3e6dd6986e3306968d1319199a624f363667d65a9c'
REV='COAST-R04 scanned wool and overcast surface response on native sea geology rain'
MODE=os.environ['G4_COMBINED_PROOF_MODE'];assert MODE in ['water','motion']
s=bpy.context.scene

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

master=BASE/'g4-full-scene-candidate.blend'
assert Path(bpy.data.filepath).resolve()==master and digest(master)==EXPECTED
assert bpy.app.version[:3]==(4,5,13) and s.get('g4_revision')==REV
assert s.render.engine=='CYCLES' and s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
assert not missing,missing
required=['Ocean_extent','G4COAST_ocean_close','G4R03_rain_glass_macro']
assert all(name in bpy.data.objects for name in required)
assert any(m.type=='OCEAN' for m in bpy.data.objects['Ocean_extent'].modifiers)
assert s.world.name=='G4COAST_R04_adapted_overcast_sky'
assert bpy.data.materials.get('G4COAST_R04_scanned_moss_wool') is not None
source_checks={'master_sha256':EXPECTED,'master_bytes':master.stat().st_size,'source_evidence_commit':'def004d60bb37a58a043a3506fb2bbda5c3a0e5c',
 'blender':bpy.app.version_string,'fresh_process':True,'missing_external_images':missing,'world':s.world.name,
 'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'motion_blur_enabled':s.render.use_motion_blur,
 'shutter_frames':s.render.motion_blur_shutter,'source_fps':s.render.fps,'source_fps_base':s.render.fps_base,
 'no_scene_save':True,'no_lighting_material_geometry_camera_changes':True,'g4_stage_pass':False,'human_acceptance':False}
assert s.render.fps==30 and s.render.fps_base==1
(OUT/(MODE+'-source-check.json')).write_text(json.dumps(source_checks,indent=2))
# Render settings only; the actual source cameras, surface/lighting and time are retained.
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04
s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
jobs=[]
if MODE=='water':
 jobs=[('G4COAST_ocean_close','E02-integrated-water.png',(1440,900),64,451)]
else:
 s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.065
 # Ten actual source samples over one second at 10FPS; no synthetic interpolation.
 # Interleave to preserve evidence from both phenomena if the deadline is reached.
 for j,f in enumerate(range(451,481,3)):
  jobs.extend([('G4COAST_ocean_close',f'ocean/{j:04d}.png',(640,400),24,f),
               ('G4R03_rain_glass_macro',f'rain/{j:04d}.png',(640,400),24,f)])
metrics=[]
for cam,name,res,samples,frame in jobs:
 if time.time()>=float(os.environ['G4_COMBINED_PROOF_DEADLINE']):
  (OUT/(MODE+'-deadline.txt')).write_text('Finite deadline reached; keep actual saved frames, do not claim a complete clip.\n')
  break
 path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
 assert not path.exists(),'Never overwrite a completed observation'
 row=render(s,bpy.data.objects[cam],path,res=res,samples=samples,frame=frame)
 row.update(file=name,native_render=True,master_sha256=EXPECTED,proof_only=MODE=='motion',
  display_fps=10 if MODE=='motion' else None,source_fps=30,source_frame_step=3 if MODE=='motion' else None,
  shutter_frames=s.render.motion_blur_shutter,revision='COAST-R04_SAME_MASTER_OBSERVATION')
 metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2))
 print('COMBINED_NATIVE_OBSERVATION_SAVED',name,flush=True)
assert digest(master)==EXPECTED
source_checks.update(master_unchanged_after_render=True,completed=len(metrics)==len(jobs),actual_frames=len(metrics),requested_frames=len(jobs))
(OUT/(MODE+'-reopen-check.json')).write_text(json.dumps(source_checks,indent=2))
print('COAST_R04_SAME_MASTER_OBSERVATIONS_PRESERVED',MODE,len(metrics),flush=True)
