"""Small native Blender representative slice: capability evidence, NOT project artwork."""
import bpy, json, os, math, time, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(os.environ['SKYFOLD_OUT']); OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=12; scene.cycles.use_denoising=True
scene.render.resolution_x=480; scene.render.resolution_y=270; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.world=bpy.data.worlds.new('NeutralWorld'); scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.25,0.29,0.36,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.view_settings.view_transform='AgX'
def material(name,col,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
coat=material('Coated alloy',(.48,.54,.56),.4,.33);steel=material('Dark metal',(.045,.075,.10),.85,.24);mark=material('Workzone amber',(.65,.19,.035),.15,.42)
def box(name,p,s,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
box('SlicePlatform',(0,0,-.3),(30,24,.6),coat)
proto=box('CityPrototype',(0,0,-100),(1.6,1.3,3),coat);proto.hide_render=True
for i in range(160):
 a=i*.19;x=(i%20-10)*1.25;y=(i//20-4)*2.3;o=bpy.data.objects.new('CityInstance_%03d'%i,proto.data);scene.collection.objects.link(o);o.location=(x,y,1.5+(i%5)*.13);o.scale.z=1+(i%5)*.15
for x in [-10,0,10]:
 o=box('DockBeam',(x,0,7),(.7,18,.7),steel);be=o.modifiers.new('EdgeRadius','BEVEL');be.width=.09;be.segments=2
box('Cargo',(0,-9,2),(5,2,3),mark)
bpy.ops.object.light_add(type='AREA',location=(4,-6,20));bpy.context.object.data.energy=4200;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=12
bpy.ops.object.camera_add(location=(29,-35,24));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=42;scene.camera=cam
scene.render.filepath=str(OUT/'slice.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'preflight.blend'),compress=True)
t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
report={'kind':'G0_CAPABILITY_ONLY_NOT_G2_ARTWORK','blender':bpy.app.version_string,'python':__import__('sys').version,'device':scene.cycles.device,'samples':scene.cycles.samples,'denoising':scene.cycles.use_denoising,'objects':len(scene.objects),'mesh_datablocks':len(bpy.data.meshes),'render_seconds':elapsed,'scene_sha256':hashlib.sha256((OUT/'preflight.blend').read_bytes()).hexdigest(),'result':'RENDERED_REOPEN_PENDING','visual_gate':'NOT_REVIEWED'}
(OUT/'capability.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
