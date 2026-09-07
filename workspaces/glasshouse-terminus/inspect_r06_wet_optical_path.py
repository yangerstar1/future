"""Read-only optical diagnosis on the exact checked integrated R06.
No scene save, no light/visibility/material changes. Ray results are geometric,
not a complete Cycles light-transport or interpolated shader-normal solution.
"""
import bpy, json, hashlib, os, math
from pathlib import Path
from collections import Counter
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve()
MASTER=ROOT/'output/g4-coast-r06-checked/g4-full-scene-candidate.blend'
OUT=ROOT/'output/g4-r06-optical-audit';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def val(x):
 if isinstance(x,(str,float,int,bool)):return x
 try:return list(x)
 except:return str(x)
def nodes(tree):
 return [{'name':n.name,'type':n.bl_idname,'operation':getattr(n,'operation',None),'uv_map':getattr(n,'uv_map',None),'image':n.image.name if hasattr(n,'image') and n.image else None,
  'inputs':[{'name':i.name,'value':val(i.default_value) if hasattr(i,'default_value') else None,'from':[(a.from_node.name,a.from_socket.name) for a in i.links]} for i in n.inputs]} for n in tree.nodes]
def bounds(o):
 vs=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in vs) for i in range(3)],[max(p[i] for p in vs) for i in range(3)]]
def rawhit(origin,direction,length=200):
 h,p,n,fi,o,m=s.ray_cast(dg,origin,direction.normalized(),distance=length)
 return {'object':o.name,'point':list(p),'normal':list(n),'face':fi,'distance':float((p-origin).length),'hide_render':o.hide_render,'shadow':o.visible_shadow} if h else None
names=[o.name for o in s.objects if o.name in ['Load_bearing_masonry_terrace','Hall_continuous_floor','G4R03_convex_glass_water_beads','Ocean_extent'] or o.name.startswith(('G4R03_shallow_rain_puddle','G4R03_puddle_impact_wave','G4R03_adherent_rivulet','G4COAST_R06_exterior_round_rain'))]
objects=[];mats=set()
for name in names:
 o=bpy.data.objects[name];r={'name':name,'type':o.type,'matrix_world':[list(v) for v in o.matrix_world],'bounds':bounds(o),'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'modifiers':[]}
 mats.update(r['materials'])
 for mod in o.modifiers:
  r['modifiers'].append({'name':mod.name,'type':mod.type,'thickness':getattr(mod,'thickness',None),'offset':getattr(mod,'offset',None),'node_group':getattr(getattr(mod,'node_group',None),'name',None)})
 if o.type=='MESH':
  r['base_normal_counts']=dict(Counter(str(tuple(round(v,3) for v in f.normal)) for f in o.data.polygons))
  r['vertex_count']=len(o.data.vertices);r['uv']={u.name:{'active_render':u.active_render,'range':[[min(v.uv[i] for v in u.data),max(v.uv[i] for v in u.data)] for i in range(2)]} for u in o.data.uv_layers}
  r['face_material_counts']=dict(Counter(f.material_index for f in o.data.polygons))
  if name=='Load_bearing_masonry_terrace':r['faces']=[{'id':p.index,'normal':list(p.normal),'material_index':p.material_index,'center':list(o.matrix_world@p.center)} for p in o.data.polygons]
  if name.startswith('G4R03_shallow_rain_puddle'):
   ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();r['eval_normal_counts']=dict(Counter(str(tuple(round(v,2) for v in f.normal)) for f in me.polygons));ev.to_mesh_clear()
 objects.append(r)
cam=bpy.data.objects['G4R03_wet_stone_macro'];s.render.resolution_x=1440;s.render.resolution_y=900
f=cam.data.view_frame(scene=s);x0=min(v.x for v in f);x1=max(v.x for v in f);y0=min(v.y for v in f);y1=max(v.y for v in f);z=f[0].z;origin=cam.matrix_world.translation.copy();rays=[]
for y in range(6):
 for x in range(9):
  u=(x+.5)/9;v=(y+.5)/6;d=(cam.matrix_world.to_3x3()@Vector((x0+(x1-x0)*u,y0+(y1-y0)*v,z))).normalized();h=rawhit(origin,d)
  r={'pixel':[round(u*1440),round((1-v)*900)],'hit':h}
  if h:
   p=Vector(h['point']);n=Vector(h['normal']);refl=d-2*d.dot(n)*n
   r['camera_facing_ndot']=n.dot(-d);r['reflected_first_hit']=rawhit(p+refl*.0002,refl)
   r['straight_through_first_hit']=rawhit(p+d*.002,d)
  rays.append(r)
for name in ['G4R03_roof_clipped_rain','G4R03_eave_drips','G4COAST_R06_exterior_round_rain']:
 o=bpy.data.objects[name]
 objects.append({'name':name,'rain_nodes':nodes(next(m.node_group for m in o.modifiers if m.type=='NODES')),'cycles_motion_blur':o.cycles.use_motion_blur,'deform_motion':o.cycles.use_deform_motion,'motion_steps':o.cycles.motion_steps})
report={'master_sha256':EXPECTED,'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'blender':bpy.app.version_string,'source_unchanged':sha(MASTER)==EXPECTED,'objects':objects,'camera_rays':rays,
 'materials':{name:nodes(bpy.data.materials[name].node_tree) for name in sorted(mats) if name and bpy.data.materials[name].use_nodes},'world':nodes(s.world.node_tree),
 'lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'position':list(o.matrix_world.translation)} for o in s.objects if o.type=='LIGHT'],
 'glazing':[{'name':o.name,'bounds':bounds(o),'materials':[m.name for m in o.data.materials],'matrix_world':[list(v) for v in o.matrix_world]} for o in s.objects if o.type=='MESH' and o.name.startswith('Side_wall_glass')],
 'limits':'Geometric normals/first hits; diagnostic ray dimensions in memory only. No source save or artistic acceptance.'}
assert report['source_unchanged']
(OUT/'wet-optical-audit.json').write_text(json.dumps(report,indent=2))
summary={'master_sha256':EXPECTED,'source_unchanged':True,'camera_hit_counts':dict(Counter(r['hit']['object'] if r['hit'] else 'WORLD' for r in rays)),'camera_facing_counts':dict(Counter('front' if r.get('camera_facing_ndot',0)>0 else 'back' for r in rays)),'objects':[{k:v for k,v in r.items() if k not in ['rain_nodes']} for r in objects]}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print('R06_WET_OPTICAL_READ_ONLY_DONE',json.dumps(summary)[:4000],flush=True)
