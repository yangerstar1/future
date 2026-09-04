"""G1 challenger: reopen the actual previous artifact, preserve geometry/cameras/exposure.
The neutral source texture maps remain untouched. New color maps describe an
explicit finish adaptation; they are not generative edits to rendered evidence.
"""
import bpy, os, sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render, save, export_glb, manifest, world

out=Path('workspaces/glasshouse-terminus/output/g1').resolve()
s=bpy.context.scene
assert bpy.data.objects.get('G1_BEAUTY'), 'Expected actual G1 source camera'
assert bpy.data.materials.get('Strelitzia_leaf'), 'Expected saved botanical material'
for material_name,asset in [('Walnut_veneer_finished','american_walnut_veneer'),('Dry_slate','slate_floor'),('Wet_slate','slate_floor')]:
    m=bpy.data.materials[material_name]
    node=m.node_tree.nodes.get('diff')
    assert node and node.type=='TEX_IMAGE', material_name
    node.image=bpy.data.images.load(str(out/'assets'/(asset+'_finished_diff_2k.jpg')),check_existing=True)
    node.image.colorspace_settings.name='sRGB'
    m['finish_adaptation']='FINISH-RECIPES.json; original CC0 maps retained'
leaf=bpy.data.materials['Strelitzia_leaf'].node_tree.nodes.get('Principled BSDF')
leaf.inputs['Roughness'].default_value=.57
leaf.inputs['Coat Weight'].default_value=.045
leaf.inputs['Specular IOR Level'].default_value=.25
leaf.inputs['Base Color'].default_value=(.035,.115,.038,1)
bpy.data.materials['Strelitzia_leaf'].diffuse_color=(.035,.115,.038,1)
# Same geometry, lights, camera, focal lengths and exposure as first candidate.
records=[]
cams={name:bpy.data.objects[name] for name in ['G1_BEAUTY','G1_GLASS_NODE','G1_MATERIALS']}
records.append(render(s,cams['G1_BEAUTY'],out/'beauty.png',samples=40))
records.append(render(s,cams['G1_GLASS_NODE'],out/'glass-node.png',samples=48))
records.append(render(s,cams['G1_MATERIALS'],out/'materials.png',samples=48))
warm=bpy.data.objects['Interior_warm_softbox'];old=warm.data.color[:]
warm.data.color=(1,1,1);world(s,(.6,.6,.6),.45)
records.append(render(s,cams['G1_BEAUTY'],out/'neutral.png',samples=32))
warm.data.color=old;world(s,(.12,.16,.22),.5)
records.append(render(s,cams['G1_BEAUTY'],out/'moving-reflection.png',samples=40,frame=32))
s.camera=cams['G1_BEAUTY'];s.frame_set(1);s.cycles.samples=40
s['review_iteration']='G1_CHALLENGER_02_PALETTE_AND_OPTICS'
s['parent_evidence_run']='33927238957'
save(s,out/'g1-risk-study.blend')
seq=out/'reflection-frames';seq.mkdir(exist_ok=True)
for f in range(1,49,2):records.append(render(s,cams['G1_BEAUTY'],seq/f'{f:04d}.png',res=(640,400),samples=16,frame=f))
s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for ob in list(s.objects):
    if ob.type=='CURVE':ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
export_glb(out/'g1-risk-study.glb',animations=False)
(out/'render-metrics.json').write_text(json.dumps(records,indent=2))
manifest(out,{'phase':'G1','status':'CHALLENGER_REVIEW_REQUIRED','parent_evidence_run':'33927238957',
    'not_final_scene':True,'changes':['documented walnut finish','documented charcoal stone palette','leaf roughness and specular response'],
    'unchanged':['geometry','cameras','exposure','lamp energies','glass and metal nodes'],
    'browser_gate':'must capture actual exported pixels separately'})
