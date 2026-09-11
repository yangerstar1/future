"""One bounded R07B look correction on the inspected flight scene.
No geometry, camera, timing or subject path changes. Shader noise is physically
anchored to the ship root; the original scene and ungraded evidence are retained.
This is a cinematic light rig, not a claimed physically validated space environment.
"""
import bpy,os,json,hashlib,math,array
from pathlib import Path
from mathutils import Vector
BASE=Path(bpy.data.filepath);OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
PARENT='870c8f7706fbfc42666eb94301d9c8dced5487b2bfcf9e49100f2380a8349b6b'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert bpy.app.version[:3]==(4,5,13)
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update();meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
root=bpy.data.objects['R06_SHIP_FORWARD_FLIGHT']
def protected_geometry():
 h=hashlib.sha256()
 for o in sorted((o for o in S.objects if o.type in {'MESH','CURVE','FONT','CAMERA','EMPTY'}),key=lambda o:o.name):
  h.update(o.name.encode());h.update(str([list(r) for r in o.matrix_world]).encode())
  if o.type=='MESH':
   h.update(str((o.data.name,len(o.data.vertices),len(o.data.polygons))).encode())
 return h.hexdigest()
before=protected_geometry();motion=[]
for f in [1,49,97,145,192]:
 S.frame_set(f);bpy.context.view_layer.update();motion.append({'frame':f,'ship':[list(r) for r in root.matrix_world],'camera':[list(r) for r in bpy.data.objects['R07B_FLIGHT_TRACK'].matrix_world]})
S.frame_set(1);bpy.context.view_layer.update()
recipes={
 'R06 satin titanium enamel':((.32,.35,.34),.48,.34),
 'R06 ochre cargo enamel':((.24,.071,.019),.25,.43),
 'R06B cargo ceramic':((.40,.43,.39),.32,.39),
 'R06B carbon machinery':((.018,.025,.034),.75,.31),
 'R06B titanium edge':((.28,.34,.36),.92,.23),
 'R06B thermal bronze':((.24,.102,.03),.72,.31),
 'R06 graphite structure':((.023,.029,.036),.78,.32),
 'R06 machined alloy':((.34,.4,.44),.92,.22)}
used={}
for old,(color,metal,rough) in recipes.items():
 original=bpy.data.materials.get(old)
 if original is None:raise RuntimeError('Material from verified scene missing: '+old)
 m=original.copy();m.name='R07B Finish / '+old;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 for name in ['Base Color','Roughness','Normal']:
  for link in list(p.inputs[name].links):nt.links.remove(link)
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Coat Weight'].default_value=.12 if metal<.6 else .04;p.inputs['Coat Roughness'].default_value=.23
 tc=nt.nodes.new('ShaderNodeTexCoord');tc.object=root
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.065;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.6;nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
 tint=nt.nodes.new('ShaderNodeValToRGB');tint.color_ramp.elements[0].color=tuple(c*.86 for c in color)+(1,);tint.color_ramp.elements[1].color=tuple(c*1.06 for c in color)+(1,);nt.links.new(noise.outputs['Fac'],tint.inputs[0]);nt.links.new(tint.outputs[0],p.inputs['Base Color'])
 ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=rough*.85;ramp.inputs['To Max'].default_value=rough*1.15;nt.links.new(noise.outputs['Fac'],ramp.inputs['Value']);nt.links.new(ramp.outputs[0],p.inputs['Roughness'])
 # Microscopic coating relief: no random, metre-deep displacement on the silhouette.
 micro=nt.nodes.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=1.4;micro.inputs['Detail'].default_value=2;nt.links.new(tc.outputs['Object'],micro.inputs['Vector'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.02;nt.links.new(micro.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal']);used[old]=m
reassigned=[]
for o in bpy.data.collections['04_FREIGHTER'].objects:
 for slot in o.material_slots:
  if slot.material and slot.material.name in used:
   old=slot.material.name;slot.link='OBJECT';slot.material=used[old];reassigned.append({'object':o.name,'old':old,'new':slot.material.name})
assert reassigned
# The same analytic sky continues lighting/reflections, at a lower fill ratio.
world=S.world.copy();world.name='R07B Finish / controlled deep-space light';S.world=world;nt=world.node_tree;bg=nt.nodes.get('Background');bg.inputs['Strength'].default_value=.14
camera_bg=nt.nodes.new('ShaderNodeBackground');camera_bg.inputs['Color'].default_value=(.006,.013,.026,1);camera_bg.inputs['Strength'].default_value=1
path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(bg.outputs[0],mix.inputs[1]);nt.links.new(camera_bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes.get('World Output').inputs[0])
sun=bpy.data.objects['R07 soft directional daylight'];sun.data=sun.data.copy();sun.data.energy=3.4;sun.data.color=(1,.87,.69);sun.data.angle=.04
for name,offset,power,size,color in [
 ('R07 large reflected sky aperture',(-1600,-1200,2400),30000000,1400,(.78,.86,1)),
 ('R07 lower reflected city fill',(-1100,-900,-600),1800000,1600,(.43,.62,.88))]:
 o=bpy.data.objects[name];o.data=o.data.copy();o.location=offset;o.rotation_euler=(Vector((0,0,20))-Vector(offset)).to_track_quat('-Z','Y').to_euler();o.data.energy=power;o.data.size=size;o.data.color=color
# One broad specular edge card makes curved metal distinguishable from paint.
d=bpy.data.lights.new('R07B Finish / rear edge card','AREA');d.shape='DISK';d.size=1100;d.energy=35000000;d.color=(.52,.72,1)
o=bpy.data.objects.new(d.name,d);bpy.data.collections['15_R07_DAYLIGHT'].objects.link(o);o.parent=root;o.location=(1200,1000,1200);o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
# Remove excessive pale veil. Raw and neutral renders use the saved same geometry.
for n in S.node_tree.nodes:
 if n.bl_idname=='CompositorNodeMapRange':n.inputs['To Max'].default_value=.055
 if n.bl_idname=='CompositorNodeMixRGB':n.inputs[2].default_value=(.05,.09,.15,1)
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.12
bpy.context.view_layer.update();assert protected_geometry()==before,'Geometry, camera or object transforms unexpectedly changed'
for row in motion:
 S.frame_set(row['frame']);bpy.context.view_layer.update();assert row['ship']==[list(r) for r in root.matrix_world];assert row['camera']==[list(r) for r in bpy.data.objects['R07B_FLIGHT_TRACK'].matrix_world]
S.frame_set(1);bpy.context.view_layer.update();S['candidate']='R07B_FINISH_TRACKED_FLIGHT';S['source_sha']=os.environ['GITHUB_SHA'];S['auto_qualified']=False
meta.update({'candidate':S['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,'look_revision':{'geometry_camera_and_motion_preserved':True,'protected_geometry_sha256':before,'reassigned_material_slots':reassigned,'surface_detail':'Ship-root anchored subtle roughness and 0.02m coating bump, no displacement','light_rig':'Directional key, low fill and broad reflection cards','camera_background':'Non-generative constant deep navy','depth_grade_maximum':.055,'same_motion_key_samples':motion},'quality_status':'ACTUAL_RENDER_REVIEW_REQUIRED_NOT_CORE_CONTRACT_PASS'})
p=OUT/'skyfold-r07b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R07B_FINISH_SAVED',meta['scene_sha256'],flush=True)
