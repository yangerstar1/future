"""Read-only R08 observation recovery; neither parent nor candidate is saved.
The earlier additional cab camera was blocked by wet canopy, as its native PNG
actually shows. Keep it and add a ray-checked, below-canopy paired observation.
Existing original cloth/coast/carriage/ocean cameras stay exactly unchanged.
"""
import bpy,os,json,hashlib,sys,math,time
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import render,camera
OUT=ROOT/'output/g4-r08-observations';OUT.mkdir(parents=True,exist_ok=True)
R07=ROOT/'output/g4-coast-r07/g4-full-scene-candidate.blend'
R08=ROOT/'output/g4-coast-r08/g4-full-scene-candidate.blend'
SHA07='386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396'
SHA08='c96c202a13c5ecd342a7b614a77b1e24ec9889bdb79cc328a255607467d7e877'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
KEY=os.environ['G4_OBSERVATION_KEY']
JOBS={
 'after-cloth':('R08','G4R03_textile_macro','AFTER-upholstery.png',(1280,800),64),
 'before-cloth':('R07','G4R03_textile_macro','BEFORE-upholstery.png',(1280,800),64),
 'after-cab':('R08','QA_R08_cab_unoccluded','AFTER-cab-unoccluded.png',(1280,800),64),
 'before-cab':('R07','QA_R08_cab_unoccluded','BEFORE-cab-unoccluded.png',(1280,800),64),
 'after-sea':('R08','G4COAST_ocean_close','AFTER-wind-sea.png',(1280,800),48),
 'before-sea':('R07','G4COAST_ocean_close','BEFORE-wind-sea.png',(1280,800),48),
 'coast':('R08','C01_exterior_hero','C01-craft-coast.png',(1440,900),48),
 'carriage':('R08','C09_car_aisle_failure_check','C09-tailored-interior.png',(1280,800),48)}
assert KEY in JOBS
rev,camname,filename,res,samples=JOBS[KEY];master,expected=(R07,SHA07) if rev=='R07' else (R08,SHA08)
assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
report={'observation':KEY,'revision':rev,'master_sha256':expected,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'g4_stage_pass':False,'human_acceptance':False}
if 'cab' in KEY:
 assert camname not in bpy.data.objects
 cam=camera(camname,(12.55,9.60,4.43),(9.62,12.10,3.65),lens=48)
 dg=bpy.context.evaluated_depsgraph_get();o=bpy.data.objects['Cab_complete_roof_loft.001'];ev=o.evaluated_get(dg);me=ev.to_mesh()
 fs=[f for f in me.polygons if abs(f.normal.z)>.15];stride=max(1,len(fs)//32);rows=[]
 for f in fs[::stride]:
  pt=o.matrix_world@f.center;d=pt-cam.location;dist=d.length
  hit,p,n,fi,ob,mat=s.ray_cast(dg,cam.location,d.normalized(),distance=dist+.004)
  rows.append({'target':list(pt),'first_hit':ob.name if hit else None,'gap':dist-(p-cam.location).length if hit else None,'reaches_cab':bool(hit and ob.name==o.name and dist-(p-cam.location).length<.008)})
 ev.to_mesh_clear();report['cab_visibility']={'camera_position':list(cam.location),'target':[9.62,12.10,3.65],'lens':48,'paths':rows,'visible_surface_samples':sum(r['reaches_cab'] for r in rows),'reason':'Additional instrument below the actually observed canopy; does not move or hide any geometry or replace original C01/C09. Original blocked-camera PNG retained.'}
 (OUT/(KEY+'-visibility.json')).write_text(json.dumps(report,indent=2))
 assert report['cab_visibility']['visible_surface_samples']>=4,'Actual source differs: cab still blocked; stop instead of hiding canopy'
else:
 assert camname in bpy.data.objects
 cam=bpy.data.objects[camname]
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
assert not (OUT/filename).exists(),'Do not overwrite any completed observation'
row=render(s,cam,OUT/filename,res=res,samples=samples,frame=451)
row.update(native_render=True,master_sha256=expected,revision=rev,source_run=int(os.environ['GITHUB_RUN_ID']),motion_blur=s.render.use_motion_blur)
(OUT/(KEY+'-metrics.json')).write_text(json.dumps(row,indent=2))
assert sha(master)==expected
report.update(master_unchanged=True,fresh_process=True,missing_external_images=missing,file=filename,seconds=row['seconds'])
(OUT/(KEY+'-reopen.json')).write_text(json.dumps(report,indent=2));print('ACTUAL_CRAFT_OBSERVATION_SAVED',KEY,filename,flush=True)
