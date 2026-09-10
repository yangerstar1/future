"""G1 sequential-self-review calibration. SYNTHETIC cases are not production outputs.
Aliases are randomized at runtime; inspect BLIND-INPUT.json and images before the key.
This tests detection of task-specific false completion, not expert-aesthetic equivalence.
"""
import bpy,json,os,secrets,hashlib,shutil,math,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;BASE=ROOT/'output/r01';OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256((BASE/'skyfold-r01.blend').read_bytes()).hexdigest()=='84f4e77811724dc632de8abd3885b0a87783ccc937b45f2f82473a544e3fb42a'
blind=[];key={}
def record(alias,paths,truth):
 blind.append({'anonymous_candidate':alias,'images':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]});key[alias]=truth

def render(alias,suffix,camera,w=800):
 s=bpy.context.scene;s.camera=camera;s.render.resolution_x=w;s.render.resolution_y=round(w*9/16);s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.use_compositing=False
 p=OUT/(alias+'-'+suffix+'.png');s.render.filepath=str(p);bpy.ops.render.render(write_still=True);return p
# Boundary sample: real project near-zone proxy, no claim that its finish is professional.
a='sample-'+secrets.token_hex(3);p=OUT/(a+'-primary.png');shutil.copyfile(BASE/'O04_CRAFT.png',p)
record(a,[p],{'class':'BOUNDARY_REAL_PROJECT_SAMPLE','expected':'REVISE','critical_findings':['CU05: basic rounded-box cart/crate','CU05: material/craft insufficient for professional close-up'],'source':'R01/O04_CRAFT.png','synthetic':False})
# Explicit missing-city failure, using a real new Cycles render.
bpy.ops.wm.open_mainfile(filepath=str(BASE/'skyfold-r01.blend'))
bpy.data.collections['02_CITY_INSTANCES'].hide_render=True
a='sample-'+secrets.token_hex(3);p=render(a,'primary',bpy.data.objects['O01_HERO'])
record(a,[p],{'class':'SYNTHETIC_OBVIOUS_FAILURE','expected':'REVISE','critical_findings':['CU01/CU04: inhabited city missing; ordinary band is not city turning overhead'],'synthetic':True,'intervention':'Hide city collection only; primary geometry remains'})
# Single-view appearance is baked into a real plane. Side view must expose the false 3D claim.
bpy.ops.wm.open_mainfile(filepath=str(BASE/'skyfold-r01.blend'));s=bpy.context.scene;cam=bpy.data.objects['O01_HERO'];basis=cam.matrix_world.to_3x3();right=basis@Vector((1,0,0));up=basis@Vector((0,1,0));forward=basis@Vector((0,0,-1));origin=cam.location.copy();centre=origin+forward*900
for c in s.collection.children:
 if c.name!='08_CAMERAS':c.hide_render=True
co=[centre-right*900-up*506.25,centre+right*900-up*506.25,centre+right*900+up*506.25,centre-right*900+up*506.25]
me=bpy.data.meshes.new('SYNTHETIC single-view plane');me.from_pydata(co,[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
for loop,xy in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=xy
ob=bpy.data.objects.new('SYNTHETIC reference-plane failure',me);s.collection.objects.link(ob)
m=bpy.data.materials.new('SYNTHETIC baked image');m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(BASE/'O01_HERO.png'));m.node_tree.links.new(tex.outputs['Color'],e.inputs['Color']);m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);me.materials.append(m)
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
world=s.world.node_tree.nodes.get('Background');world.inputs[0].default_value=(.04,.055,.075,1);world.inputs[1].default_value=1
# Main resembles the original render. This alone cannot establish 3D completion.
a='sample-'+secrets.token_hex(3);p1=render(a,'primary',cam)
d=bpy.data.cameras.new('SYNTHETIC side inspection');d.lens=34;d.clip_end=20000;o=bpy.data.objects.new('SYNTHETIC side inspection',d);s.collection.objects.link(o);o.location=centre-forward*600+right*1450+up*330;o.rotation_euler=(centre-o.location).to_track_quat('-Z','Y').to_euler();p2=render(a,'side',o)
record(a,[p1,p2],{'class':'SYNTHETIC_SINGLE_VIEW_FALSE_COMPLETION','expected':'REVISE','critical_findings':['CU01/CU06: primary appearance is a flat image plane','CU07/O03: side view has no ring/city/dock volume'],'synthetic':True,'intervention':'Project an existing actual render on a single plane; supply independent side view','not_production_asset':True})
blind.sort(key=lambda x:x['anonymous_candidate'])
(OUT/'BLIND-INPUT.json').write_text(json.dumps({'mode':'ANONYMIZED_ORDER_SEQUENTIAL_SELF_REVIEW_NOT_INDEPENDENT_AGENT','instructions':'Describe what each image actually shows; judge CU01/CU05/CU06; identify location and evidence; do not open CALIBRATION-KEY.json before writing verdicts. All files are calibration-only, not production evidence.','candidates':blind},indent=2))
(OUT/'CALIBRATION-KEY.json').write_text(json.dumps({'mode':'SYNTHETIC_TEST_KEY_WITHHELD_UNTIL_REVIEW','source_sha':os.environ['GITHUB_SHA'],'answers':key},indent=2))
print('CALIBRATION_RENDERED',len(blind),'READ_BLIND_INPUT_FIRST; NO_CALIBRATION_RESULT_ASSIGNED')
