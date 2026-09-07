"""Read-only geometric/illumination audit after the actual R06 wet-stone image failed.
No rendering, no save, no material or lamp edits. Geometry first hits are not a
full transmission/BRDF solver; retain material and ray visibility for interpretation.
"""
import bpy,math,json,hashlib,os
from pathlib import Path
from collections import Counter
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r06-checked';OUT=ROOT/'output/g4-wet-stone-path-audit';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738'
master=BASE/'g4-full-scene-candidate.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==master and sha(master)==EXPECTED
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['G4R03_wet_stone_macro'];s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100

def hit(at,direction,distance=1000):
 h,p,n,face,o,m=s.ray_cast(dg,at,direction,distance=distance)
 if not h:return None
 return {'object':o.name,'point':list(p),'normal':list(n),'face':face,'distance':(p-at).length,'hide_render':o.hide_render,'visible_shadow':getattr(o,'visible_shadow',None),'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}

frame=cam.data.view_frame(scene=s);z=frame[0].z;lo=[min(v[i] for v in frame) for i in range(2)];hi=[max(v[i] for v in frame) for i in range(2)];origin=cam.matrix_world.translation.copy()
counts=Counter();samples=[]
for iy in range(5):
 for ix in range(7):
  u=(ix+.5)/7;v=(iy+.5)/5;local=Vector((lo[0]+(hi[0]-lo[0])*u,lo[1]+(hi[1]-lo[1])*v,z));direction=(cam.matrix_world.to_3x3()@local).normalized();q=hit(origin,direction)
  if not q:continue
  counts[q['object']]+=1;row={'pixel':[round(u*1440),round((1-v)*900)],'camera_first_hit':q,'below_surface':[]}
  at=Vector(q['point'])+direction*.000015
  for _ in range(3):
   q2=hit(at,direction,20)
   if not q2:break
   row['below_surface'].append(q2);at=Vector(q2['point'])+direction*.000015
   if q2['object']=='Load_bearing_masonry_terrace':break
  samples.append(row)

surface_probes=[]
for x,y in [(-5.3,-7.55),(-5.3,-7.0),(-4.2,-7.6),(-6.5,-7.8),(-11,-7.8)]:
 top=hit(Vector((x,y,1)),Vector((0,0,-1)),3);assert top
 p=Vector(top['point'])+Vector((0,0,.003));sky=Counter();sky_visible=0
 for i in range(128):
  r=math.sqrt((i+.5)/128);phi=i*math.pi*(3-math.sqrt(5));d=Vector((r*math.cos(phi),r*math.sin(phi),math.sqrt(1-r*r)))
  q=hit(p,d,50000)
  if q:sky[q['object']]+=1
  else:sky_visible+=1
 lamps=sorted([o for o in s.objects if o.type=='LIGHT' and o.data.energy>0],key=lambda o:(o.matrix_world.translation-p).length)[:12]
 direct=[]
 for o in lamps:
  delta=o.matrix_world.translation-p;distance=delta.length;d=delta.normalized();q=hit(p,d,max(.001,distance-.01));axis=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
  direct.append({'object':o.name,'type':o.data.type,'energy':o.data.energy,'position':list(o.matrix_world.translation),'distance':distance,'surface_geometric_ndotl':d.z,'emitter_axis_dot_to_surface':axis.dot(-d),'first_hit':q})
 surface_probes.append({'xy':[x,y],'top_hit':top,'probe_position':list(p),'hemisphere_rays':128,'geometric_open_sky_rays':sky_visible,'hemisphere_first_hits':dict(sky),'nearby_practical_lights':direct})

objects=[]
for name in ['Load_bearing_masonry_terrace','Hall_continuous_floor','G4R03_shallow_rain_puddle.001']:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();rows=[]
 for f in me.polygons:
  if len(rows)>=12:break
  if o.name.startswith('G4R03') or abs(f.normal.z)>.8:
   rows.append({'face':f.index,'normal':list(f.normal),'material_index':f.material_index,'material':me.materials[f.material_index].name if f.material_index<len(me.materials) else None})
 objects.append({'object':name,'faces':rows,'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]});ev.to_mesh_clear()
materials={}
for name in {m for q in samples for m in q['camera_first_hit']['materials']}|{'G4COAST_R06_rain_darkened_exterior_slate'}:
 m=bpy.data.materials.get(name)
 if not m or not m.use_nodes:continue
 rows=[]
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':
   rows.append({'node':n.name,'inputs':{k:{'value':list(n.inputs[k].default_value) if hasattr(n.inputs[k].default_value,'__len__') else n.inputs[k].default_value,'linked_from':[(l.from_node.name,l.from_socket.name) for l in n.inputs[k].links]} for k in ['Base Color','Metallic','Roughness','IOR','Transmission Weight','Normal','Coat Weight','Coat Roughness']}})
 materials[name]=rows
report={'mode':'READ_ONLY_NO_SAVE_NO_RENDER','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'master_sha256':EXPECTED,'camera':{'name':cam.name,'position':list(origin),'lens':cam.data.lens,'frame':451,'exposure':s.view_settings.exposure},'camera_first_hit_counts':dict(counts),'camera_samples':samples,'surface_probes':surface_probes,'evaluated_faces':objects,'materials':materials,'source_unchanged':sha(master)==EXPECTED,'limits':['Geometric first hits; glass or water can transmit light, so blocked ray count alone is not a photometric result.','Cosine-weighted128-ray sampling diagnoses potential structural sky occlusion, not full irradiance.','No scene state is saved; render dimensions and frame set in memory only.'],'g4_stage_pass':False}
assert report['source_unchanged']
(OUT/'wet-stone-light-paths.json').write_text(json.dumps(report,indent=2));print('WET_STONE_READ_ONLY_PATHS',dict(counts),flush=True)
