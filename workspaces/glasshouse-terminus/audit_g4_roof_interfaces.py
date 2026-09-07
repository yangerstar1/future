"""Read-only main-roof/cab interface audit after actual R08 native comparison.
No save, no geometry edits. Source interfaces are not evaluated shell interfaces.
"""
import bpy,json,os,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();OUT=ROOT/'output/g4-r08-roof-interface-audit';OUT.mkdir(parents=True,exist_ok=True)
MASTER=ROOT/'output/g4-coast-r08/g4-full-scene-candidate.blend';SHA='c96c202a13c5ecd342a7b614a77b1e24ec9889bdb79cc328a255607467d7e877'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==SHA
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
report={'master_sha256':SHA,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'objects':[],'source_snippets':{},'g4_stage_pass':False}
for name in ['Car_complete_barrel_roof','Cab_complete_roof_loft','Cab_complete_roof_loft.001']:
 o=bpy.data.objects[name];me=o.data
 mods=[]
 for m in o.modifiers:
  r={'type':m.type,'name':m.name}
  for k in ['thickness','offset','use_even_offset','use_quality_normals','use_rim','show_render']:
   if hasattr(m,k):r[k]=getattr(m,k)
  mods.append(r)
 row={'name':name,'parent':o.parent.name if o.parent else None,'matrix_world':[list(r) for r in o.matrix_world],'modifiers':mods,'vertices':len(me.vertices),'faces':len(me.polygons),'smooth_faces':sum(p.use_smooth for p in me.polygons),'mean_normal_z':sum(p.normal.z for p in me.polygons)/len(me.polygons),'materials':[m.name for m in me.materials],'base_boundary':[],'evaluated_boundary':[]}
 if name=='Car_complete_barrel_roof':row['base_vertices']=[list(v.co) for v in me.vertices];row['base_faces']=[list(p.vertices) for p in me.polygons]
 for side in [-1,1]:
  x=side*7.25
  row['base_boundary'].append({'x':x,'points':[list(v.co) for v in me.vertices if abs(v.co.x-x)<.00001]})
 ev=o.evaluated_get(dg);em=ev.to_mesh()
 for side in [-1,1]:
  x=side*7.25;points=[list(v.co) for v in em.vertices if abs(v.co.x-x)<.001]
  row['evaluated_boundary'].append({'x':x,'points':points,'maximum_z':max((p[2] for p in points),default=None)})
 row['evaluated_bounds']=[[min(v.co[i] for v in em.vertices) for i in range(3)],[max(v.co[i] for v in em.vertices) for i in range(3)]]
 ev.to_mesh_clear();report['objects'].append(row)
for p in ROOT.glob('*.py'):
 if p.name==Path(__file__).name:continue
 lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if "'Car_complete_barrel_roof'" in line:report['source_snippets'].setdefault(p.name,[]).append({'line':i+1,'text':'\n'.join(lines[max(0,i-8):i+12])})
report['source_unchanged']=sha(MASTER)==SHA;assert report['source_unchanged']
(OUT/'roof-interface-audit.json').write_text(json.dumps(report,indent=2));print('ROOF_INTERFACE_READ_ONLY_COMPLETE',[(r['name'],r['mean_normal_z'],r['evaluated_bounds'][1][2]) for r in report['objects']],flush=True)
