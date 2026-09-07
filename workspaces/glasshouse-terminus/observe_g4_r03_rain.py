"""Read-only native rain motion and exact-camera R02 baseline.
Never saves a source blend; preview is not the final film.
"""
import bpy,os,json,hashlib,sys,time
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path('workspaces/glasshouse-terminus').resolve()
SOURCE=ROOT/'output/g4-r03/g4-full-scene-candidate.blend'
PARENT=ROOT/'output/g4-r02/g4-full-scene-candidate.blend'
OUT=ROOT/'output/g4-r03-rain-proof';OUT.mkdir(parents=True,exist_ok=True)
SHA='dfd9a0e28967b8a474bc9688ce0b75d194dba20ce14aab5f18f1d11da7aa32b5'
OLD='173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==SOURCE and digest(SOURCE)==SHA and digest(PARENT)==OLD
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene;assert s.get('g4_revision')=='R03 rain layers and close-range physical surface response'
cam=bpy.data.objects['G4R03_rain_glass_macro'];matrix=cam.matrix_world.copy();lens=cam.data.lens
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()];assert not missing
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
s.cycles.max_bounces=10;s.cycles.transmission_bounces=8;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.065
(OUT/'frames').mkdir(exist_ok=True);metrics=[];frozen_camera=[list(v) for v in cam.matrix_world]
for j,f in enumerate(range(451,511,3)):
    assert time.time()<float(os.environ['G4_PROOF_DEADLINE']),'Finite proof time reached'
    row=render(s,cam,OUT/f'frames/{j:04d}.png',res=(640,400),samples=16,frame=f)
    assert [list(v) for v in cam.matrix_world]==frozen_camera
    row.update(source_master_sha256=SHA,native_render=True,source_frame_rate=30,output_frame_rate=10,proof_not_final_film=True)
    metrics.append(row);(OUT/'motion-metrics.json').write_text(json.dumps(metrics,indent=2));print('RAIN_PROOF_FRAME',j,f,flush=True)
assert digest(SOURCE)==SHA
bpy.ops.wm.open_mainfile(filepath=str(PARENT));s=bpy.context.scene
assert s.get('g4_revision')=='R02 dry hall and continuous night-sky environment'
d=bpy.data.cameras.new('R03_baseline_comparison_only');baseline=bpy.data.objects.new('R03_baseline_comparison_only',d);s.collection.objects.link(baseline)
baseline.matrix_world=matrix;d.lens=lens;d.dof.use_dof=False;d.clip_start=.06;d.clip_end=1000
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
s.cycles.max_bounces=10;s.cycles.transmission_bounces=8;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=24;s.cycles.adaptive_threshold=.025
assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
assert time.time()<float(os.environ['G4_PROOF_DEADLINE'])
row=render(s,baseline,OUT/'R02-same-camera-glass-baseline.png',res=(1600,1000),samples=96,frame=451)
row.update(source_master_sha256=OLD,native_render=True,supplemental_camera_memory_only=True,matched_R03_camera_matrix=frozen_camera)
(OUT/'baseline-metrics.json').write_text(json.dumps(row,indent=2))
assert digest(SOURCE)==SHA and digest(PARENT)==OLD
(OUT/'reopen-check.json').write_text(json.dumps({'fresh_process':True,'source_master_sha256':SHA,'source_master_unchanged':True,'baseline_master_sha256':OLD,'baseline_master_unchanged':True,'missing_external_images':missing,'motion_frame_count':20,'native_motion_resolution':[640,400],'output_fps':10,'seconds':2,'no_generated_frames':True,'camera_matrix':frozen_camera,'lens':lens,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'limits':'Two-second stationary-camera proof at parked train frames451-508, not the 4K final film or full train-weather interaction validation. Glass adhesion is static; falling rain and eave drops are native time-driven instances.','g4_stage_pass':False,'human_acceptance':False},indent=2))
