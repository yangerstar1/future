"""Read-only continuation from the integrated COAST-R05, never the old R02.
Record actual material/node/surface data before the next local weather intervention.
"""
import bpy, json, hashlib, os, sys, math
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-coast-r05';OUT=ROOT/'output/g4-wet-surface-audit';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='232a602326d2519d8f3bb5fe125a416c4d36149885173563df1297092e493445'
MASTER=BASE/'g4-full-scene-candidate.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
def val(v):
 try:return list(v) if hasattr(v,'__len__') and not isinstance(v,str) else v
 except:return str(v)
def graph(tree):
 if tree is None:return None
 rows=[]
 for n in tree.nodes:
  ins={}
  for i in n.inputs:
   if hasattr(i,'default_value'):
    v=val(i.default_value)
    if not isinstance(v,(str,float,int,bool,list,type(None))):v=str(v)
    ins[i.identifier]={'name':i.name,'value':v,'linked':i.is_linked}
  row={'name':n.name,'type':n.bl_idname,'inputs':ins}
  for k in ['operation','data_type','attribute_name','uv_map','vector_type','noise_dimensions']:
   if hasattr(n,k):row[k]=getattr(n,k)
  if hasattr(n,'image') and n.image:row['image']={'name':n.image.name,'size':list(n.image.size),'colorspace':n.image.colorspace_settings.name,'packed':bool(n.image.packed_file)}
  rows.append(row)
 return {'nodes':rows,'links':[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in tree.links]}
mode=os.environ.get('WET_AUDIT_MODE','audit')
if mode=='audit':
 objects=[];selected_materials=set();rain=[]
 for o in s.objects:
  if o.type not in ['MESH','CURVE','LIGHT','CAMERA']:continue
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  row={'name':o.name,'type':o.type,'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]], 'matrix_world':[list(r) for r in o.matrix_world], 'hide_render':o.hide_render,'parent':o.parent.name if o.parent else None}
  if hasattr(o.data,'materials'):row['materials']=[m.name if m else None for m in o.data.materials]
  if o.type=='MESH':
   row.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),uv_layers=[q.name for q in o.data.uv_layers],smooth_faces=sum(p.use_smooth for p in o.data.polygons))
   if o.name.startswith(('Curved_roof_glazing','Side_wall_glass','Canopy_glass','G4R03_roof_clipped_rain','G4R03_eave_drips')):
    selected_materials.update(row['materials']);row['modifiers']=[{'name':m.name,'type':m.type} for m in o.modifiers]
    if o.name.startswith(('Curved_roof_glazing','Side_wall_glass','Canopy_glass')) and len(o.data.vertices)<80:
     row['world_vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices];row['faces']=[list(p.vertices) for p in o.data.polygons]
   if o.name.startswith(('G4R03_roof_clipped_rain','G4R03_eave_drips')):
    row['attributes']=[{'name':a.name,'type':a.data_type,'domain':a.domain} for a in o.data.attributes]
    row['attribute_ranges']={a.name:[min(d.value for d in a.data),max(d.value for d in a.data)] for a in o.data.attributes if a.data_type=='FLOAT' and len(a.data)}
    row['motion_settings']={'use_motion_blur':o.cycles.use_motion_blur,'use_deform_motion':o.cycles.use_deform_motion,'motion_steps':o.cycles.motion_steps}
    row['graphs']=[graph(m.node_group) for m in o.modifiers if m.type=='NODES'];rain.append(row)
  if o.type=='LIGHT':row['light']={'energy':o.data.energy,'color':list(o.data.color),'type':o.data.type}
  if o.type=='CAMERA':row['camera']={'lens':o.data.lens,'clip_end':o.data.clip_end,'dof':o.data.dof.use_dof}
  objects.append(row)
 for name in ['Hall_continuous_floor','Platform_continuous_slab','Load_bearing_masonry_terrace','Ocean_extent']:
  selected_materials.update(m.name for m in bpy.data.objects[name].data.materials if m)
 report={'mode':'READ_ONLY_NO_SAVE','master_sha256':EXPECTED,'revision':s.get('g4_revision'),'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'objects':objects,'rain':rain,'materials':{m:graph(bpy.data.materials[m].node_tree) for m in selected_materials if m},'world':graph(s.world.node_tree),'render':{'engine':s.render.engine,'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'use_motion_blur':s.render.use_motion_blur,'motion_blur_shutter':s.render.motion_blur_shutter,'fps':s.render.fps,'max_bounces':s.cycles.max_bounces,'transmission_bounces':s.cycles.transmission_bounces},'source_unchanged':sha(MASTER)==EXPECTED,'g4_stage_pass':False}
 (OUT/'integrated-r05-wet-audit.json').write_text(json.dumps(report,indent=2))
 print('INTEGRATED_R05_READ_ONLY_AUDIT_SAVED',len(objects),flush=True)
else:
 assert mode=='baseline'
 sys.path.insert(0,str(ROOT));from scene_common import render
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
 s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=12;s.cycles.adaptive_threshold=.045;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 rows=[]
 for camera,file in [('C03_hall_to_platform','BASELINE-R05-hall.png'),('C01_exterior_hero','BASELINE-R05-coast.png')]:
  row=render(s,bpy.data.objects[camera],OUT/file,res=(1152,720),samples=40,frame=451);row.update(master_sha256=EXPECTED,native_render=True,diagnostic_resolution=True);rows.append(row);(OUT/'baseline-metrics.json').write_text(json.dumps(rows,indent=2))
 assert sha(MASTER)==EXPECTED
 (OUT/'baseline-reopen.json').write_text(json.dumps({'master_sha256':EXPECTED,'master_unchanged':True,'new_native_images':len(rows),'g4_stage_pass':False},indent=2))
