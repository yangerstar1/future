"""Read-only source probe, then isolated imported-asset/Ocean tests. No source save."""
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
report={'blender':bpy.app.version_string,'parent_sha256':EXPECTED,'source_objects':[],'api':{}}
for name in ['Complete_cliff_mass','Ocean_extent','Load_bearing_masonry_terrace','Cab_complete_roof_loft','Cab_complete_roof_loft.001','Car_complete_barrel_roof']:
 o=bpy.data.objects[name]
 report['source_objects'].append({'name':name,'bounds':bounds(o),'location':list(o.location),'matrix_world':[list(r) for r in o.matrix_world],
  'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'smooth_faces':sum(p.use_smooth for p in o.data.polygons),'normals':[list(p.normal) for p in list(o.data.polygons)[:50]],'materials':[m.name for m in o.data.materials]})
# The following tests occur in a new factory scene, never the user's source datablocks.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
manifest=json.loads((OUT/'STORM-ASSET-SOURCES.json').read_text());asset=manifest['assets'][0]
bpy.ops.import_scene.gltf(filepath=str(OUT/asset['entry']))
obs=[o for o in s.objects if o.type=='MESH'];assert obs
report['scan']={'entry':asset['entry'],'objects':[{'name':o.name,'bounds':bounds(o),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'uv':[l.name for l in o.data.uv_layers],'materials':[m.name for m in o.data.materials]} for o in obs]}
lo=Vector([min(bounds(o)[0][i] for o in obs) for i in range(3)]);hi=Vector([max(bounds(o)[1][i] for o in obs) for i in range(3)]);c=(hi+lo)*.5;span=max(hi-lo)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('probe_world')
d=bpy.data.cameras.new('ASSET_ONLY_NOT_PROJECT');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=span*1.3;d.clip_end=10000
for tag,dir in [('front',(0,-1,.35)),('reverse',(0,1,.35))]:
 cam.location=c+Vector(dir).normalized()*span*2;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('SCAN-ONLY-'+tag+'.png'));bpy.ops.render.render(write_still=True)
# Probe native modifier parameters on an isolated object, not source sea.
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
