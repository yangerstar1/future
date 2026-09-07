"""Targeted read-only R02 rain/material inventory. No master save or scene edits."""
import bpy,json,hashlib,os,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve()
MASTER=ROOT/'output/g4-r02/g4-full-scene-candidate.blend'
OUT=ROOT/'output/g4-rain-inventory';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
assert s.get('g4_revision')=='R02 dry hall and continuous night-sky environment'
s.frame_set(451);bpy.context.view_layer.update()
def val(v):
    if isinstance(v,(int,float,str,bool)):return v
    try:return list(v)
    except:return str(v)
def nodes(tree):
    return [{'name':n.name,'type':n.type,'operation':getattr(n,'operation',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,
      'inputs':{i.name:{'value':val(i.default_value) if hasattr(i,'default_value') else None,'links':[(x.from_node.name,x.from_socket.name) for x in i.links]} for i in n.inputs}} for n in tree.nodes]
objects=[]
for o in s.objects:
    ps=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type in ['MESH','CURVE'] else []
    row={'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'position':list(o.matrix_world.translation),
      'bounds':[[min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]] if ps else None,
      'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'hide_render':o.hide_render,
      'modifiers':[{'name':m.name,'type':m.type,'levels':getattr(m,'levels',None),'width':getattr(m,'width',None),'thickness':getattr(m,'thickness',None)} for m in o.modifiers]}
    if o.type=='MESH':
        row.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),smooth_faces=sum(p.use_smooth for p in o.data.polygons),uv_layers=[u.name for u in o.data.uv_layers])
        if ('glass' in o.name.lower() or o.name.startswith(('G3_walnut_cafe_top','G3_sideboard','Cab_complete_roof_loft','G4_car_seat','Car_seat','Platform_canopy'))) and len(o.data.vertices)<300:
            row['world_vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices]
    if o.type=='LIGHT':row['light']={'type':o.data.type,'power':o.data.energy,'color':list(o.data.color),'direction':list(o.matrix_world.to_3x3()@Vector((0,0,-1)))}
    if o.type=='CAMERA':row['camera']={'lens':o.data.lens,'matrix_world':[list(r) for r in o.matrix_world],'dof':o.data.dof.use_dof}
    objects.append(row)
report={'parent_master_sha256':EXPECTED,'blender':bpy.app.version_string,'run_id':os.environ['GITHUB_RUN_ID'],'source_sha':os.environ['GITHUB_SHA'],
  'scene_properties':{k:val(v) for k,v in s.items()},'objects':objects,
  'materials':{m.name:{'users':m.users,'nodes':nodes(m.node_tree) if m.use_nodes else []} for m in bpy.data.materials},
  'images':[{'name':i.name,'size':list(i.size),'filepath':i.filepath,'packed':bool(i.packed_file),'color_space':i.colorspace_settings.name} for i in bpy.data.images],
  'world_nodes':nodes(s.world.node_tree),'particle_system_objects':[o.name for o in s.objects if o.particle_systems],
  'rain_named_objects':[o.name for o in s.objects if any(k in o.name.lower() for k in ['rain','rivulet','drop','puddle','ripple'])],
  'render':{'engine':s.render.engine,'device':s.cycles.device,'exposure':s.view_settings.exposure,'view_transform':s.view_settings.view_transform,'samples':s.cycles.samples,'max_bounces':s.cycles.max_bounces,'transmission_bounces':s.cycles.transmission_bounces},
  'source_master_unchanged':sha(MASTER)==EXPECTED,'human_acceptance':False}
assert report['source_master_unchanged']
(OUT/'R02-rain-material-inventory.json').write_text(json.dumps(report,indent=2))
code=OUT/'production-source';code.mkdir(exist_ok=True)
for name in ['extend_g4_scene.py','refine_g4_environment.py','scene_common.py','build_g3.py','build_g1.py','refine_g3.py','provision.sh','publish_evidence.sh']:
    shutil.copy2(ROOT/name,code/name)
for name in ['SESSION-HANDOFF-LATEST.md','G4-EVIDENCE-INDEX.json']:
    shutil.copy2(ROOT/name,code/name)
print('R02_RAIN_MATERIAL_INVENTORY',json.dumps({'objects':len(objects),'materials':len(report['materials']),'rain_named_objects':report['rain_named_objects'],'source_master_unchanged':True}),flush=True)
