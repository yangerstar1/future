"""Narrow geometry preflight for R06 water caps; no other art variable changes.
Use a canonical, vertex-ID-anchored polygon fan for volume invariance. Blender's
loop triangulation may choose another diagonal when a nonplanar quad reverses;
that is not a change in its saved vertex positions or topology.
"""
import bpy,bmesh,json,os,hashlib,shutil,sys
from pathlib import Path
import numpy as np
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r06';OUT=ROOT/'output/g4-coast-r06-checked'
SOURCE='190e8156502991a17b9437c71923e04faa475eba2357db144f445435fbe58144'
MODE=os.environ.get('G4_CAP_MODE','build')
if MODE!='build':
 script=ROOT/'refine_g4_integrated_water_contact.py';code=script.read_text();old="OUT=ROOT/'output/g4-coast-r06'";assert code.count(old)==1
 code=code.replace(old,"OUT=ROOT/'output/g4-coast-r06-checked'")
 exec(compile(code,str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
else:
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 master=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==master and sha(master)==SOURCE
 assert bpy.app.version[:3]==(4,5,13)
 s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
 o=bpy.data.objects['G4COAST_R06_roof_and_leeward_water_caps'];me=o.data;assert len(me.vertices)%40==0
 OUT.mkdir(parents=True,exist_ok=True)
 def volumes():
  co=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
  result=np.zeros(len(co)//40,dtype=np.float64);topology=[]
  for face in me.polygons:
   ids=list(face.vertices);group=ids[0]//40;assert all(i//40==group for i in ids)
   topology.append(sorted(ids));start=ids.index(min(ids));ids=ids[start:]+ids[:start]
   for j in range(1,len(ids)-1):
    p=co[[ids[0],ids[j],ids[j+1]]]-co[group*40]
    result[group]+=np.dot(p[0],np.cross(p[1],p[2]))/6
  return result,hashlib.sha256(co.tobytes()).hexdigest(),hashlib.sha256(json.dumps(sorted(topology)).encode()).hexdigest()
 before,positions,topology=volumes();assert len(before)>1000
 counts={'positive':int((before>0).sum()),'negative':int((before<0).sum()),'zero':int((before==0).sum())}
 assert counts['zero']==0,'Degenerate water caps need topology diagnosis'
 inward=set(int(i) for i in np.flatnonzero(before<0))
 if inward:
  bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.verts.index_update()
  fs=[f for f in bm.faces if next(iter(f.verts)).index//40 in inward]
  bmesh.ops.reverse_faces(bm,faces=fs);bm.to_mesh(me);bm.free();me.update()
 after,positions_after,topology_after=volumes()
 diagnostics={'signed_volume_before':counts,'positive_after':int((after>0).sum()),'positions_equal':positions==positions_after,'unordered_topology_equal':topology==topology_after,'max_absolute_canonical_volume_difference':float(np.max(abs(abs(before)-after))),'volume_method':'Canonical polygon fan anchored at smallest saved vertex ID; double precision after local translation.'}
 (OUT/'volume-diagnostics.json').write_text(json.dumps(diagnostics,indent=2))
 assert positions==positions_after and topology==topology_after and np.all(after>0)
 assert np.allclose(abs(before),after,rtol=1e-7,atol=1e-16),'Canonical volume changed despite identical saved vertices'
 for p in BASE.iterdir():
  if p.name in ['g4-full-scene-candidate.blend','master-parts','MASTER-PARTS.json','MASTER-RESTORE.txt','restore_master.py','build.log','provision-source.log']:continue
  if p.is_dir():shutil.copytree(p,OUT/p.name,dirs_exist_ok=True)
  else:shutil.copy2(p,OUT/p.name)
 report=json.loads((OUT/'build-report.json').read_text());report['preflight_parent_sha256']=SOURCE;report['preflight_source_sha']=os.environ['GITHUB_SHA'];report['preflight_run_id']=os.environ['GITHUB_RUN_ID']
 report['normal_preflight']={'object':o.name,'cap_count':len(after),'signed_volume_before':counts,'reversed_caps':len(inward),'all_closed_cap_volumes_positive':True,'absolute_canonical_volumes_unchanged':True,'vertex_positions_sha256':positions,'unordered_topology_sha256':topology,'only_polygon_winding_changed':True,'reason':'The cap tangent/across frame was left-handed; corrected actual mesh normals, not ray flags or material visibility.','preflight_retry':'Previous run34157504720 stopped before save because automatic loop triangulation changed its polygon diagonals after reversal. This method compares the same canonical fan without relaxing the geometric invariants.'}
 sys.path.insert(0,str(ROOT));from scene_common import save
 save(s,OUT/'g4-full-scene-candidate.blend');assert sha(master)==SOURCE
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));(OUT/'normal-preflight.json').write_text(json.dumps(report['normal_preflight'],indent=2));print('R06_CAP_NORMALS_VERIFIED',report['candidate_sha256'],flush=True)
