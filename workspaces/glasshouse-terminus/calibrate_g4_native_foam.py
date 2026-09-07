"""One measured foam-range correction on the complete scanned-surface coast.
Actual read-only QA proved .0168..0222 foam values were suppressed by .12 threshold.
No geometry, lighting, rain, camera, material family or scope replacement.
"""
import bpy,json,os,sys,hashlib,shutil,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import save,render
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r04';OUT=ROOT/'output/g4-coast-r05';OUT.mkdir(parents=True,exist_ok=True)
PARENT='51a3501edd81f879ba1b5c3e6dd6986e3306968d1319199a624f363667d65a9c';REV='COAST-R05 measured native crest foam on scanned-surface coast'
MODE=os.environ['G4_FOAM_MODE'];assert MODE in ['build','context','closeups','motion']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
 assert s.get('g4_revision')=='COAST-R04 scanned wool and overcast surface response on native sea geology rain'
 s.frame_set(451);bpy.context.view_layer.update();sea=bpy.data.objects['Ocean_extent'];old=sea.active_material;assert old.name=='G4COAST_R03_dielectric_water_and_whitewater'
 n=old.node_tree.nodes;candidate=[q for q in n if q.type=='MAP_RANGE' and abs(q.inputs['From Min'].default_value-.12)<.00001 and abs(q.inputs['From Max'].default_value-.75)<.00001]
 assert len(candidate)==1,'Actual owned foam mapping differs; stop'
 samples=[]
 for frame in [451,460]:
  s.frame_set(frame);bpy.context.view_layer.update();ev=sea.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();a=me.attributes['OceanFoam'];assert a.domain=='CORNER' and a.data_type=='BYTE_COLOR'
  v=np.empty(len(a.data)*4,np.float32);a.data.foreach_get('color',v);v=v.reshape(-1,4)[:,:3].mean(1)
  assert .015<float(v.min())<float(v.max())<.025,'Measured source range differs'
  q=np.clip((v-.0196)/(.0222-.0196),0,1);q=q*q*(3-2*q)*.64
  samples.append({'frame':frame,'native_min':float(v.min()),'native_max':float(v.max()),'old_mask_nonzero_fraction':float((v>.12).mean()),'corrected_mask_mean':float(q.mean()),'corrected_mask_above_point1_fraction':float((q>.1).mean()),'not_physical_whitecap_coverage_measurement':True});ev.to_mesh_clear()
 assert all(r['old_mask_nonzero_fraction']==0 and 0<r['corrected_mask_mean']<.15 for r in samples)
 new=old.copy();new.name='G4COAST_R05_measured_crest_foam_water';node=new.node_tree.nodes[candidate[0].name]
 node.inputs['From Min'].default_value=.0196;node.inputs['From Max'].default_value=.0222;node.inputs['To Min'].default_value=0;node.inputs['To Max'].default_value=.64;node.interpolation_type='SMOOTHSTEP'
 sea.data.materials[0]=new
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in ['.json','.txt'] and p.name not in ['build-report.json','MASTER-PARTS.json','MASTER-RESTORE.txt','DELIVERY.json']:shutil.copy2(p,OUT/p.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R04-build-report.json');shutil.copytree(BASE/'models',OUT/'models',dirs_exist_ok=True)
 s.frame_set(451);s['g4_revision']=REV;s['g4_coast_r05_parent']=PARENT;s.camera=bpy.data.objects['C01_exterior_hero'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report={'stage':'G4','revision':'COAST-R05','parent_master_sha256':PARENT,'parent_evidence_commit':'def004d60bb37a58a043a3506fb2bbda5c3a0e5c','candidate_sha256':sha(OUT/'g4-full-scene-candidate.blend'),'master_bytes':(OUT/'g4-full-scene-candidate.blend').stat().st_size,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'only_edit':'One owned foam shader range .12...75 to measured .0196...0222 smoothstep, output0...64. No geometry, sky, lights, rain, textile, cameras or exposure modifications.','actual_qa_run_id':34154213591,'native_range_samples':samples,'reason':'Native foam existed as data but old mapping removed every crest. Actual scalar measurements, not object counts, exposed the mistake.','limits':['Live Ocean foam is a wave-crest field; it has no baked long-lived foam history and is not fluid collision simulation.','New threshold is an artistic calibrated map of existing native data, not measured physical storm whitecap coverage.','Other previous candidate defects and all fixed cameras remain; no automatic G4 PASS.'],'g4_stage_pass':False,'human_acceptance':False}
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('COAST_R05_MEASURED_FOAM_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 jobs={'context':[('C01_exterior_hero','C01-native-storm-coast.png',(1440,900),48,451),('G4COAST_ocean_close','E02-native-wave-foam.png',(1440,900),64,451),('G4COAST_rock_water_close','E01-native-coastal-rock.png',(1440,900),64,451)],'closeups':[('G4R03_textile_macro','M04-native-scanned-wool.png',(1440,900),64,451),('G4R03_rain_glass_macro','M01-native-rain-glass.png',(1600,1000),64,451),('C03_hall_to_platform','C03-native-rain-hall.png',(1440,900),64,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_threshold=.07;s.cycles.adaptive_min_samples=8
  jobs=[('G4COAST_ocean_close',f'motion/{i:04d}.png',(640,400),24,f) for i,f in enumerate(range(451,481,3))]
 rows=[]
 for camera,name,res,samples,frame in jobs:
  assert time.time()<float(os.environ['G4_FOAM_DEADLINE']),'Finite final-candidate observation deadline reached'
  row=render(s,bpy.data.objects[camera],OUT/name,res=res,samples=samples,frame=frame);row.update(native_render=True,master_sha256=expected,revision='COAST-R05',max_bounces=10,transmission_bounces=8);rows.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(rows,indent=2));print('COAST_R05_NATIVE_OBSERVATION',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(rows),'g4_stage_pass':False,'human_acceptance':False},indent=2))
