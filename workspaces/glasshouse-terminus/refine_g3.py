"""G3-R02: targeted corrections to a saved candidate, never rebuild the world.
Issues come from actual R01 native overviews. The diagnostic is labelled separately;
the saved candidate keeps real glass responses and all six lights enabled.
"""
import bpy, hashlib, json, sys, shutil
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render, save
BASE=Path('workspaces/glasshouse-terminus/output/g3').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-r02').resolve()
PARENT=BASE/'g3-bay-candidate.blend'
EXPECTED='e95b37d7f2d8a28efc8bca32815b0624acae7a787e2c7bbe7565eb30e3588027'
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
assert Path(bpy.data.filepath).resolve()==PARENT
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE'
OUT.mkdir(parents=True,exist_ok=True)
s.frame_set(451);bpy.context.view_layer.update()
required=['G3_window_rim','G3_bay','Hall_continuous_floor','Platform_continuous_slab',
 'G3_walnut_cafe_top','G3_porcelain_saucer','G3_porcelain_cup','G3_coffee_meniscus','G3_cup_handle']
assert all(bpy.data.objects.get(n) for n in required)
rim=bpy.data.objects['G3_window_rim'];cam=bpy.data.objects['G3_bay']
assert (rim.location-Vector((-6,8,5))).length<.001
assert abs(rim.data.energy-300)<.01
hall=bpy.data.objects['Hall_continuous_floor'];platform=bpy.data.objects['Platform_continuous_slab']
assert hall.active_material.name=='G3_scoped_Hall_continuous_floor'
assert platform.active_material.name=='G3_scoped_Platform_continuous_slab'
contact_names=['G3_porcelain_saucer','G3_porcelain_cup','G3_coffee_meniscus','G3_cup_handle']
protected=[o.name for o in s.objects if o.name not in contact_names+['G3_window_rim']]

def signature():
    s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
    for name in sorted(protected):
        o=bpy.data.objects[name];h.update(name.encode());h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
    return h.hexdigest()

before_signature=signature()
report={'stage':'G3','status':'R02_CANDIDATE_NOT_ACCEPTED','parent_blend_sha256':EXPECTED,
 'parent_evidence_commit':'0dc1d2e9df7d044081a82756218250a4ddd6bfa2',
 'review':'G3-REVIEW-01.md','issues':['G3-L01','G3-M01','G3-M02'],
 'unchanged':['all cameras and lenses','exposure and color management','all train/door/walk keyframes',
 'building/track/vehicle geometry','glass reflection and transmission','all light ray visibility settings'],
 'independent_reviewer':False,'human_acceptance':False,'g4_allowed':False}
old_res=(s.render.resolution_x,s.render.resolution_y,s.cycles.samples)
markers=[(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers]
s.timeline_markers.clear()
# A diagnostic isolates a cause; it is NOT saved as the final lighting solution.
rim.data.energy=0
report['light_isolation_render']=render(s,cam,OUT/'QA-L01-without-rim.png',res=(720,450),samples=24,frame=451)
rim.data.energy=300
report['light_isolation_render']['scope']='R01 geometry/materials, only G3_window_rim disabled; diagnostic only, not candidate'
for name,frame,camera_name in markers:
    m=s.timeline_markers.new(name,frame=frame)
    if camera_name:m.camera=bpy.data.objects[camera_name]
s.frame_set(451);s.camera=cam
# Move the real soft fill above the sightline into an exterior overhead-sky role.
# Do not hide the lamp from glossy/transmission rays or alter the glass shader.
s.render.resolution_x,s.render.resolution_y=1440,900
projected_before=list(world_to_camera_view(s,cam,rim.location))
report['light_before']={'position':list(rim.location),'energy':rim.data.energy,'size':rim.data.size,
 'projected_center':projected_before}
rim.location=(-6,8,11)
rim.rotation_euler=(Vector((-3.3,4,2.1))-rim.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
report['light_after']={'position':list(rim.location),'energy':rim.data.energy,'size':rim.data.size,
 'projected_center':list(world_to_camera_view(s,cam,rim.location)),
 'method':'Physical relocation/re-aim; all ray visibility and light energy preserved'}

# Preserve the original surface variation; remap only dry roughness, not the image.
def dry_roughness(mat,p):
    n=mat.node_tree.nodes;l=mat.node_tree.links
    assert n.get('rough') and n['rough'].type=='TEX_IMAGE'
    for edge in list(p.inputs['Roughness'].links):l.remove(edge)
    remap=n.new('ShaderNodeMapRange');remap.name='G3R02_dry_roughness_range'
    remap.inputs['From Min'].default_value=0;remap.inputs['From Max'].default_value=1
    remap.inputs['To Min'].default_value=.52;remap.inputs['To Max'].default_value=.78
    remap.clamp=True
    l.new(n['rough'].outputs['Color'],remap.inputs['Value']);l.new(remap.outputs['Result'],p.inputs['Roughness'])
    p.inputs['Coat Weight'].default_value=0
    return {'range':[.52,.78],'original_map':n['rough'].image.name,'coat':0}

hallmat=hall.active_material
report['hall_dry']=dry_roughness(hallmat,hallmat.node_tree.nodes['Principled BSDF'])
# Finish only the already-designated bay across the platform, with a real dry/wet
# shading boundary at the exposed edge. The continuous collision mesh is untouched.
mat=platform.active_material;n=mat.node_tree.nodes;l=mat.node_tree.links
wet=n['Principled BSDF'];out=n.get('Material Output')
outer=out.inputs['Surface'].links[0].from_node
assert outer.type=='MIX_SHADER' and outer.inputs[2].links[0].from_node==wet
thresholds=[q for q in n if q.type=='MATH' and q.operation=='GREATER_THAN'
 and abs(q.inputs[1].default_value-9.85)<.01 and q.inputs[0].links
 and q.inputs[0].links[0].from_socket.name=='Y']
assert len(thresholds)==1,'Unexpected platform mask; stop rather than blanket-rematerialize'
y_socket=thresholds[0].inputs[0].links[0].from_socket
thresholds[0].inputs[1].default_value=6.5
wet.inputs['Roughness'].default_value=.19
assert not wet.inputs['Roughness'].is_linked

dry=n.new('ShaderNodeBsdfPrincipled');dry.name='G3R02_platform_under_canopy_dry'
for inp in wet.inputs:
    if inp.name in ['Roughness','Coat Weight']:continue
    dst=dry.inputs.get(inp.name)
    if dst is None:continue
    if hasattr(inp,'default_value'):
        try:dst.default_value=inp.default_value
        except (TypeError,ValueError):pass
    for edge in inp.links:l.new(edge.from_socket,dst)
report['platform_dry']=dry_roughness(mat,dry)
edge=n.new('ShaderNodeMath');edge.operation='GREATER_THAN';edge.name='G3R02_exposed_wet_edge'
edge.inputs[1].default_value=9.85;l.new(y_socket,edge.inputs[0])
wetmix=n.new('ShaderNodeMixShader');wetmix.name='G3R02_dry_to_wet_boundary'
l.new(edge.outputs[0],wetmix.inputs[0]);l.new(dry.outputs[0],wetmix.inputs[1]);l.new(wet.outputs[0],wetmix.inputs[2])
l.new(wetmix.outputs[0],outer.inputs[2])
report['platform_scope']={'x':[-4.10,.10],'y':[6.5,10.70],'wet_edge_starts_y':9.85,
 'wet_roughness':.19,'geometry_unchanged':True,'outside_bay_mask_preserved':True}

# The source arithmetic leaves a 3mm saucer gap. Verify the ACTUAL bounds before
# adjusting the complete cup assembly; do not guess a height from object names.
def zbounds(o):
    z=[(o.matrix_world@Vector(v)).z for v in o.bound_box];return min(z),max(z)
bpy.context.view_layer.update()
gap=zbounds(bpy.data.objects['G3_porcelain_saucer'])[0]-zbounds(bpy.data.objects['G3_walnut_cafe_top'])[1]
assert .002<gap<.004,('Unexpected cup contact',gap)
for name in contact_names:bpy.data.objects[name].location.z-=gap
bpy.context.view_layer.update()
report['saucer_contact']={'before_gap_metres':gap,'after_gap_metres':zbounds(bpy.data.objects['G3_porcelain_saucer'])[0]-zbounds(bpy.data.objects['G3_walnut_cafe_top'])[1],
 'moved_together':contact_names,'reason':'Verified support contact; no tabletop or camera movement'}
assert signature()==before_signature,'Unapproved geometry/transform/camera regression'
report['protected_geometry_signature_before']=before_signature
report['protected_geometry_signature_after']=signature()
assert abs(s.view_settings.exposure)<1e-8
report['exposure']=s.view_settings.exposure;report['view_transform']=s.view_settings.view_transform
for file in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt']:
    if (BASE/file).is_file():shutil.copy2(BASE/file,OUT/file)
(OUT/'models').mkdir(exist_ok=True)
shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
(OUT/'SOURCE-RECOVERY.json').write_text(json.dumps({'raw_model_sources_commit':report['parent_evidence_commit'],
 'raw_model_root':'workspaces/glasshouse-terminus/output/g3/models',
 'all_images_packed_in_candidate':True,'new_external_downloads':0,'parent_sha256':EXPECTED},indent=2))
s.render.resolution_x,s.render.resolution_y,s.cycles.samples=old_res
s.frame_set(451);s.camera=cam;s['g3_revision']='R02 actual-light-placement and dry/wet correction'
s['g3_r02_parent_sha256']=EXPECTED
save(s,OUT/'g3-bay-candidate.blend')
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
report['candidate_sha256']=hashlib.sha256((OUT/'g3-bay-candidate.blend').read_bytes()).hexdigest()
(OUT/'repair-report.json').write_text(json.dumps(report,indent=2))
parent_report=json.loads((BASE/'build-report.json').read_text())
parent_report['candidate_sha256']=report['candidate_sha256']
parent_report['revision']='R02';parent_report['revision_report']='repair-report.json'
parent_report['g3_parent_candidate_sha256']=EXPECTED
(OUT/'build-report.json').write_text(json.dumps(parent_report,indent=2))
print('G3_R02_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
