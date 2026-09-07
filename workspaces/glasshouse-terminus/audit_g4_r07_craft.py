"""Read-only R07 craft audit. No Blender save, no render, no stage restart."""
import bpy,json,hashlib,os,re,math
from pathlib import Path
from mathutils import Vector
from collections import Counter
ROOT=Path('workspaces/glasshouse-terminus').resolve();OUT=ROOT/'output/g4-r07-craft-audit';OUT.mkdir(parents=True,exist_ok=True)
MASTER=ROOT/'output/g4-coast-r07/g4-full-scene-candidate.blend';EXPECTED='386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
def bounds(o):
 ps=[o.matrix_world@Vector(p) for p in o.bound_box]
 return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def props(x):
 r={}
 for p in x.bl_rna.properties:
  if p.identifier in ['rna_type'] or p.type in ['POINTER','COLLECTION']:continue
  try:
   v=getattr(x,p.identifier);r[p.identifier]=list(v) if p.is_array else v
  except Exception:pass
 return r
def mat(m):
 if not m or not m.use_nodes:return {'name':m.name if m else None}
 nodes=[]
 for n in m.node_tree.nodes:
  row={'name':n.name,'type':n.bl_idname,'inputs':{}}
  if n.type=='TEX_IMAGE':row['image']=n.image.name if n.image else None
  for p in ['operation','blend_type','attribute_name','uv_map','projection','noise_dimensions','wave_type','bands_direction']:
   if hasattr(n,p):row[p]=getattr(n,p)
  for i in n.inputs:
   if hasattr(i,'default_value'):
    v=i.default_value
    try:row['inputs'][i.name]={'value':list(v) if hasattr(v,'__len__') and not isinstance(v,str) else v,'linked':i.is_linked}
    except Exception:pass
  nodes.append(row)
 return {'name':m.name,'nodes':nodes,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in m.node_tree.links]}
selected=[];materials=set()
for o in sorted(s.objects,key=lambda o:o.name):
 name=o.name
 relevant=name.startswith(('Cab_complete_roof_loft','Train_roof','Car_roof','G4_car','Car_seat_','G4_bench_seat','Hall_plinth','Load_bearing_masonry_terrace','Coastal_cliff','Cliff_','Ocean_extent','Bridge_','Viaduct_','G4COAST_adapted_scanned'))
 if not relevant:continue
 row={'name':name,'type':o.type,'bounds':bounds(o),'matrix_world':[list(r) for r in o.matrix_world],'matrix_local':[list(r) for r in o.matrix_local],'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'modifiers':[props(m) for m in o.modifiers]}
 if o.type=='MESH':
  me=o.data;row.update(vertices=len(me.vertices),polygons=len(me.polygons),smooth_faces=sum(p.use_smooth for p in me.polygons),uv_layers=[u.name for u in me.uv_layers],materials=[m.name if m else None for m in me.materials],has_custom_normals=me.has_custom_normals)
  materials.update(m.name for m in me.materials if m)
  if name.startswith(('Cab_complete_roof_loft','Train_roof','Car_roof')) or name in ['Car_seat_cushion','Car_seat_back','G4_bench_seat_cushion','Hall_plinth']:
   if len(me.vertices)<10000:
    row['local_vertices']=[list(v.co) for v in me.vertices];row['faces']=[list(p.vertices) for p in me.polygons];row['face_normals']=[list(p.normal) for p in me.polygons]
  if name=='Ocean_extent':
   row['attributes']=[{'name':a.name,'domain':a.domain,'type':a.data_type} for a in me.attributes]
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();em.calc_loop_triangles()
   row['evaluated_counts']={'vertices':len(em.vertices),'triangles':len(em.loop_triangles)};ev.to_mesh_clear()
 selected.append(row)
# Actual repository source snippets around geometry definitions, not inferred paths.
snippets={}
for p in ROOT.glob('*.py'):
 if p.name==Path(__file__).name:continue
 lines=p.read_text().splitlines();hits=[]
 for i,line in enumerate(lines):
  if any(t in line for t in ["'Cab_complete_roof_loft'","'Car_seat_cushion'","'G4_bench_seat_cushion'","'Ocean_extent'","'Hall_plinth'"]):hits.append({'line':i+1,'text':'\n'.join(lines[max(0,i-5):min(len(lines),i+9)])})
 if hits:snippets[str(p.relative_to(ROOT))]=hits
report={'source_master_sha256':EXPECTED,'source_evidence_commit':'91b5bcc932c58e5a43b20061299bb6a6f606aaaa','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'blender':bpy.app.version_string,'revision':s.get('g4_revision'),'objects':selected,'materials':[mat(bpy.data.materials[n]) for n in sorted(materials)],'cameras':[{'name':o.name,'position':list(o.matrix_world.translation),'lens':o.data.lens,'matrix_world':[list(r) for r in o.matrix_world]} for o in s.objects if o.type=='CAMERA'],'source_snippets':snippets,'project_python_files':sorted(p.name for p in ROOT.glob('*.py')),'source_unchanged':sha(MASTER)==EXPECTED,'limits':['Geometric and node inventory only; no art acceptance.','Source polygons differ from evaluated geometry; modifiers recorded explicitly.'],'g4_stage_pass':False}
assert report['source_unchanged']
(OUT/'craft-audit.json').write_text(json.dumps(report,indent=2,default=str))
(OUT/'summary.json').write_text(json.dumps({k:report[k] for k in ['source_master_sha256','revision','objects','source_unchanged']},indent=2,default=str))
print('READ_ONLY_R07_CRAFT_AUDIT_COMPLETE',len(selected),flush=True)
