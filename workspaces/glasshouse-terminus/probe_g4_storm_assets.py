"""Read-only source/API/scan data inspection. No render calls and no master save.
Runs separately from the already-active R03 production renderer; never edits it.
"""
import bpy,json,os,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();OUT=ROOT/'output/g4-storm-assets';MASTER=ROOT/'output/g4-r02/g4-full-scene-candidate.blend'
EXPECTED='173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED and bpy.app.version[:2]==(4,5)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
report={'blender':bpy.app.version_string,'parent_sha256':EXPECTED,'source_objects':[],'api':{},'render_calls':0,'source_save_calls':0}
for name in ['Complete_cliff_mass','Ocean_extent','Load_bearing_masonry_terrace','Cab_complete_roof_loft','Cab_complete_roof_loft.001','Car_complete_barrel_roof']:
 o=bpy.data.objects[name]
 report['source_objects'].append({'name':name,'bounds':bounds(o),'location':list(o.location),'matrix_world':[list(r) for r in o.matrix_world],
  'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'smooth_faces':sum(p.use_smooth for p in o.data.polygons),'normals':[list(p.normal) for p in list(o.data.polygons)[:50]],'materials':[m.name for m in o.data.materials]})
# All new test geometry lives in a factory scene, not the source datablocks.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
manifest=json.loads((OUT/'STORM-ASSET-SOURCES.json').read_text());asset=manifest['assets'][0]
bpy.ops.import_scene.gltf(filepath=str(OUT/asset['entry']))
obs=[o for o in s.objects if o.type=='MESH'];assert obs
rows=[]
for o in obs:
 total=sum(p.area for p in o.data.polygons);normal=Vector((0,0,0));bins={k:0.0 for k in ['+X','-X','+Y','-Y','+Z','-Z']}
 for p in o.data.polygons:
  wn=(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized();normal+=wn*p.area
  axis=max(range(3),key=lambda i:abs(wn[i]));bins[('+' if wn[axis]>=0 else '-')+'XYZ'[axis]]+=p.area
 rows.append({'name':o.name,'bounds':bounds(o),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'uv':[u.name for u in o.data.uv_layers],
  'materials':[m.name for m in o.data.materials],'area_weighted_normal':list(normal/max(total,1e-8)),'face_area_direction_bins':bins})
report['scan']={'entry':asset['entry'],'objects':rows}
# Native modifier test without rendering.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
bpy.ops.mesh.primitive_plane_add();o=bpy.context.object;m=o.modifiers.new('Ocean API probe','OCEAN')
for p in m.bl_rna.properties:
 if p.identifier in ['resolution','viewport_resolution','spatial_size','size','repeat_x','repeat_y','wave_scale','choppiness','wind_velocity','smallest_wave','wave_scale_min','spectrum','use_foam','foam_layer_name','foam_coverage','wave_alignment','wave_direction','random_seed','time','geometry_mode','depth']:
  v=getattr(m,p.identifier);report['api'][p.identifier]={'type':p.type,'value':v,'enum':[e.identifier for e in p.enum_items] if p.type=='ENUM' else None}
m.resolution=12;m.viewport_resolution=12;m.spatial_size=100;m.wave_scale=1.8;m.choppiness=1.2;m.wind_velocity=18;m.use_foam=True;m.foam_layer_name='OceanFoam';m.foam_coverage=.15
m.spectrum='JONSWAP';m.wave_alignment=.4;m.wave_direction=math.radians(25)
report['ocean_tests']=[]
for t in [15.0,15.25]:
 m.time=t;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();zs=[v.co.z for v in me.vertices]
 report['ocean_tests'].append({'time':t,'vertices':len(me.vertices),'zmin':min(zs),'zmax':max(zs),'z_rms':(sum(z*z for z in zs)/len(zs))**.5,'attributes':[(a.name,a.data_type,a.domain) for a in me.attributes]});e.to_mesh_clear()
report['source_master_unchanged']=sha(MASTER)==EXPECTED;assert report['source_master_unchanged']
(OUT/'ASSET-AND-API-PROBE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
