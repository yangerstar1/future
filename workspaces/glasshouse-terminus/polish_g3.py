"""G3-R04: practical lighting and complete structural-bay finishes.
Verified R03 only. Protect source geometry, cameras, motion and glass response.
No generated imagery, ray-visibility tricks, exposure hiding or G4 expansion.
"""
import bpy, hashlib, json, sys, shutil
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,curve,camera,area,save
BASE=Path('workspaces/glasshouse-terminus/output/g3-r03').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-r04').resolve()
PARENT=BASE/'g3-bay-candidate.blend'
EXPECTED='cb1ae3c8ace74bcbeeaaf51684bf013cba5b7702803f432c91632e4395fadcfe'
assert Path(bpy.data.filepath).resolve()==PARENT
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('g3_revision')=='R03 vestibule craft and supplemental complete observations'
s.frame_set(451);bpy.context.view_layer.update();OUT.mkdir(parents=True,exist_ok=True)
hall=bpy.data.collections['A_complete_glasshouse'];canopy=bpy.data.collections['C_platform_canopy']
source_names=[o.name for o in s.objects if o.type in {'MESH','CURVE','CAMERA'}]
def signature():
    s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
    for name in sorted(source_names):
        o=bpy.data.objects[name];h.update(name.encode());h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
    return h.hexdigest()
def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
prior=signature()
report={'stage':'G3','revision':'R04','status':'CHALLENGER_NOT_ACCEPTED','parent_master_sha256':EXPECTED,
 'parent_evidence_commit':'22dceca579c272b51767c70c153c540f7defc547','light_diagnostic_artifact':10019119528,
 'light_diagnostic_zip_sha256':'e4d28113c0f9204326a2e14aeed927262b8c12bac8e07c61f2ac47b08282d88a',
 'scope':'Same x=-4..0 structural bay and doorway. No whole-scene expansion.',
 'materials':[],'lights':{},'human_acceptance':False,'g4_allowed':False,
 'protected':['original meshes and transforms','all original cameras','door/train/walk keyframes','glass IOR/transmission and ray visibility','exposure and color management']}
major=[o for o in hall.objects if o.name.startswith('Primary_elliptical_arch') and -4.15<=bounds(o)[0][0] and bounds(o)[1][0]<=.15]
minor=[o for o in hall.objects if o.name.startswith('Secondary_glazing_rib') and -4.15<=bounds(o)[0][0] and bounds(o)[1][0]<=.15]
assert len(major)==2 and len(minor)==3,'Unexpected structural bay; stop before edits'
report['actual_arches']={o.name:bounds(o) for o in major+minor}
(OUT/'preflight-r04.json').write_text(json.dumps(report,indent=2))
coll=bpy.data.collections.new('G3R04_lighting_and_splice_craft');s.collection.children.link(coll)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[coll.name]
metal=bpy.data.materials['G3_bottle_green_enamel'];brass=bpy.data.materials['G3_satin_aged_brass'];steel=bpy.data.materials['G3_brushed_steel']
secondary=material('G3R04_sage_green_secondary_enamel',(.072,.11,.092),metal=.20,rough=.34,coat=.20)
def apply(o,m):
    old=o.active_material.name if o.active_material else None
    o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
    report['materials'].append({'object':o.name,'old':old,'new':m.name,'bounds':bounds(o)})
# Full arches in this one bay; never infer coverage from a zero mesh origin.
for o in major:apply(o,metal)
for o in minor:apply(o,secondary)
for o in list(hall.objects)+list(canopy.objects):
    if o.type not in {'MESH','CURVE'}:continue
    lo,hi=bounds(o)
    if not(-4.25<=lo[0] and hi[0]<=.25):continue
    if o.name.startswith(('Load_column','Column_capital','Platform_canopy_beam')):apply(o,metal)
    elif o.name.startswith(('Wall_glazing_mullion','Portal_transom_mullion','Wall_transom')):apply(o,secondary)
# Keep the old surface outside the bay on shared longitudinal members.
for o in list(hall.objects):
    if not o.name.startswith('Longitudinal_roof_purlin'):continue
    src=o.active_material;old=src.node_tree.nodes.get('Principled BSDF')
    assert old and not any(i.is_linked for i in old.inputs),'Unexpected shared material graph'
    m=secondary.copy();m.name='G3R04_scoped_purlin_'+o.name;n=m.node_tree.nodes;l=m.node_tree.links
    inside=n.get('Principled BSDF');outside=n.new('ShaderNodeBsdfPrincipled')
    for inp in old.inputs:
        dst=outside.inputs.get(inp.name)
        if dst is not None and hasattr(inp,'default_value'):
            try:dst.default_value=inp.default_value
            except (TypeError,ValueError):pass
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0])
    a=n.new('ShaderNodeMath');a.operation='GREATER_THAN';a.inputs[1].default_value=-4.15;l.new(sep.outputs['X'],a.inputs[0])
    b=n.new('ShaderNodeMath');b.operation='LESS_THAN';b.inputs[1].default_value=.15;l.new(sep.outputs['X'],b.inputs[0])
    both=n.new('ShaderNodeMath');both.operation='MULTIPLY';l.new(a.outputs[0],both.inputs[0]);l.new(b.outputs[0],both.inputs[1])
    mix=n.new('ShaderNodeMixShader');l.new(both.outputs[0],mix.inputs[0]);l.new(outside.outputs[0],mix.inputs[1]);l.new(inside.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
    apply(o,m)
# Small bolted splice covers on both sides of the existing eave joints.
for x in [-4,0]:
    for side in [-1,1]:
        xx=x+side*.115
        cube('G3R04_eave_splice_plate',(xx,6.50,4.995),(.018,.27,.50),metal,.007)
        for y in [6.42,6.58]:
            for z in [4.825,5.165]:
                cylinder('G3R04_splice_washer',(xx+side*.009,y,z),(xx+side*.014,y,z),.022,steel,32)
                cylinder('G3R04_splice_hexbolt',(xx+side*.014,y,z),(xx+side*.028,y,z),.014,brass,6)
# Replace the identified 4m card with physical wall lights; retain all ray visibility.
opal=material('G3R04_opal_wall_lamp',(.77,.69,.54),rough=.36,transmission=.10,emission=1.0)
night=json.loads(s['g3_night_lights'])
for x in [-4,0]:
    cube('G3R04_sconce_mount',(x,6.305,3.20),(.12,.10,.38),metal,.025)
    curve('G3R04_sconce_bracket',[(x,6.275,3.05),(x,6.13,3.05),(x,6.08,3.10)],.015,brass)
    cube('G3R04_opal_diffuser',(x,6.13,3.27),(.11,.085,.28),opal,.035)
    for z in [3.105,3.435]:cube('G3R04_sconce_cap',(x,6.13,z),(.16,.135,.045),metal,.014)
    for dx in [-.064,.064]:cylinder('G3R04_sconce_cage',(x+dx,6.075,3.12),(x+dx,6.075,3.42),.006,brass,16)
    if x==-4:
        ob=bpy.data.objects['G3_interior_softbox']
        report['lights'][ob.name]={'before_position':list(ob.location),'before_power':ob.data.energy,'before_size':ob.data.size}
        assert abs(ob.data.energy-420)<1e-4 and abs(ob.data.size-4)<1e-4
        ob.location=(x,6.065,3.27);ob.rotation_euler=(Vector((x,4.3,3.6))-ob.location).to_track_quat('-Z','Y').to_euler()
        ob.data.shape='RECTANGLE';ob.data.size=.085;ob.data.size_y=.24;ob.data.energy=35;ob.data.color=(1,.85,.65)
        ob['g3_role']='Former fill reused as real left wall sconce, no ray visibility suppression'
    else:
        ob=area('G3R04_right_wall_sconce',(x,6.065,3.27),(x,4.3,3.6),35,.085,(1,.85,.65),size_y=.24);night.append(ob.name)
    report['lights'].setdefault(ob.name,{})['after']={'position':list(ob.location),'power':ob.data.energy,'shape':ob.data.shape,'size':ob.data.size,'size_y':ob.data.size_y}
for name,power in [('G3_pendant_light',280),('G3_cafe_practical',12),('G3_door_practical',95)]:
    ob=bpy.data.objects[name];report['lights'][name]={'before_power':ob.data.energy,'after_power':power};ob.data.energy=power
s['g3_night_lights']=json.dumps(night)
# Centreline witness beyond the hall opening. Every original camera remains intact.
cam=camera('G3R04_door_unoccluded',(-2,7.40,2.46),(-2,10.72,2.32),28)
objects=[o for o in s.objects if o.type in {'MESH','CURVE'} and (o.name.startswith(('G3_door_track_housing','G3_door_jamb_cover','Car_door_threshold')) or (o.parent and o.parent.name in ['Train_door_left','Train_door_right']))]
assert len(objects)>20
s.render.resolution_x,s.render.resolution_y=1280,800
frames=[301,330,348];projections=[]
for lens in [28,27,26,25,24]:
    cam.data.lens=lens;projections=[]
    for frame in frames:
        s.frame_set(frame);bpy.context.view_layer.update()
        p=[world_to_camera_view(s,cam,o.matrix_world@Vector(v)) for o in objects for v in o.bound_box]
        projections.append({'frame':frame,'x':[min(v.x for v in p),max(v.x for v in p)],'y':[min(v.y for v in p),max(v.y for v in p)],'depth':min(v.z for v in p)})
    if all(p['depth']>0 and .025<=p['x'][0] and p['x'][1]<=.975 and .025<=p['y'][0] and p['y'][1]<=.975 for p in projections):break
else:raise RuntimeError('Full doorway does not fit; stop without moving the scene')
rays=[]
for frame in frames:
    s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
    for x,z in [(-2,1.16),(-2,3.40),(-2.69,2.3),(-1.31,2.3),(-2.96,3.40),(-1.04,3.40)]:
        target=Vector((x,10.60,z));delta=target-cam.location
        hit,at,normal,idx,ob,matrix=s.ray_cast(deps,cam.location,delta.normalized(),distance=delta.length+.12)
        name=ob.name if ob else None;rays.append({'frame':frame,'target':list(target),'first_object':name})
        assert not(name and name.startswith('Hall_door')),'Hall leaf still obstructs required witness'
report['door_observation']={'camera':cam.name,'position':list(cam.location),'lens':cam.data.lens,'framing':projections,'first_hits':rays,'pixels_still_require_review':True}
camera('G3R04_roller_detail',(-2.40,9.25,3.67),(-2.96,10.59,3.40),55)
camera('G3R04_threshold_detail',(-.9,8.75,2.20),(-2,10.73,1.19),50)
assert signature()==prior,'Original geometry/camera changed'
report['protected_signature_before']=prior;report['protected_signature_after']=signature()
for n in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
    if (BASE/n).exists():shutil.copy2(BASE/n,OUT/n)
(OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
s['g3_revision']='R04 physical sconces, structural-bay palette and unobstructed witnesses'
s.frame_set(451);s.camera=bpy.data.objects['G3R03_complete_bay']
s.render.use_border=False;s.render.use_crop_to_border=False
save(s,OUT/'g3-bay-candidate.blend')
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
report['candidate_sha256']=hashlib.sha256((OUT/'g3-bay-candidate.blend').read_bytes()).hexdigest()
(OUT/'polish-report.json').write_text(json.dumps(report,indent=2))
build=json.loads((BASE/'build-report.json').read_text());build.update(candidate_sha256=report['candidate_sha256'],revision='R04',revision_report='polish-report.json')
(OUT/'build-report.json').write_text(json.dumps(build,indent=2))
print('G3_R04_CANDIDATE_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
