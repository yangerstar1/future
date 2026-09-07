"""G3-R03 candidate, not G4: preserve the saved world and finish the sample's
visible vestibule. Original cameras stay unchanged; new views supplement them.
Only run against the exact R02 master after its image review.
"""
import bpy, hashlib, json, math, sys, shutil
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,curve,lathe,camera,area,save
BASE=Path('workspaces/glasshouse-terminus/output/g3-r02').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-r03').resolve()
PARENT=BASE/'g3-bay-candidate.blend'
EXPECTED='3162ba27fbeb3055c5fbe94a6fc2422cc9cca11f68dda381b06627ebcaf6d680'
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
assert Path(bpy.data.filepath).resolve()==PARENT and bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE' and s.get('g3_revision','').startswith('R02')
s.frame_set(451);bpy.context.view_layer.update();OUT.mkdir(parents=True,exist_ok=True)
train=bpy.data.objects['Train_motion_root'];floor=bpy.data.objects['Car_floor']
assert (train.location-Vector((2,12.1,0))).length<.001
assert bpy.data.collections.get('G3_finished_hall_platform_bay')
coll=bpy.data.collections.new('G3R03_vestibule_finish');s.collection.children.link(coll)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[coll.name]

def box(o):
    ps=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]

cabinet=[o for o in s.objects if o.name.startswith(('G3_sideboard_','G3_cabinet_','G3_panel_border','G3_lamp_'))]
assert len(cabinet)>10
practical=bpy.data.objects['G3_cafe_practical'];move_names={o.name for o in cabinet}|{practical.name}
protected=[o.name for o in s.objects if o.name not in move_names]

def signature():
    s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
    for name in sorted(protected):
        o=bpy.data.objects[name];h.update(name.encode());h.update(repr(tuple(tuple(row) for row in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
    return h.hexdigest()
before=signature()
report={'stage':'G3','revision':'R03','status':'CANDIDATE_NOT_ACCEPTED','parent_sha256':EXPECTED,
 'parent_evidence_commit':'87d75e3b90d6b330fb378d1fc2200f5d1a52e418','g4_allowed':False,
 'scope':'Same structural bay and its visible entrance vestibule only. Other areas retain G2 quality.',
 'changes':[],'original_cameras_preserved':True,'browser':'BLOCKED_UNCHANGED','human_acceptance':False}
# Enforce a measured lateral gap; an AABB overlap is not called a proven mesh collision.
chairs=[o for o in s.objects if o.type=='MESH' and o.get('source_asset')=='GreenChair_01']
assert len(chairs)==2
rear=max(chairs,key=lambda o:sum(box(o)[j][1] for j in [0,1]))
chair_left=box(rear)[0][0]
front=max(box(o)[1][0] for o in cabinet if o.type=='MESH')
dx=min(0.0,chair_left-.075-front)
assert -.30<=dx<=0,('Unexpected cabinet clearance; inspect instead of forcing',dx)
for o in cabinet+[practical]:o.location.x+=dx
bpy.context.view_layer.update()
report['cabinet_clearance']={'prior_x_gap':chair_left-front,'translation_x':dx,
 'after_x_gap':chair_left-max(box(o)[1][0] for o in cabinet if o.type=='MESH'),
 'method':'Conservative disjoint X bounds; not a claim that all prior intersecting AABBs intersected as meshes.',
 'moved_objects':sorted(move_names)}

metal=bpy.data.materials['G3_bottle_green_enamel'];brass=bpy.data.materials['G3_satin_aged_brass']
steel=bpy.data.materials['G3_brushed_steel'];glass=bpy.data.materials['G3_clear_6mm_glass']
woodbase=bpy.data.materials['G3_walnut_cabinet_vertical_grain'];woodfloor=bpy.data.materials['G3_walnut_top_grain_XY']
cream=material('G3R03_ceiling_cream',(.47,.45,.39),rough=.61)
velvet=material('G3R03_luggage_bench_fabric',(.055,.088,.064),rough=.78)

# Object coordinates follow the train, so a moving car does not slide through world-space grain.
def anchored(src,label,axes=None,anchor=None):
    m=src.copy();m.name=label;n=m.node_tree.nodes;l=m.node_tree.links
    tex=n.new('ShaderNodeTexCoord');tex.name='G3R03_attached_coordinates';tex.object=anchor or train
    for g in [g for g in n if g.type=='NEW_GEOMETRY']:
        for edge in list(g.outputs['Position'].links):l.new(tex.outputs['Object'],edge.to_socket)
    if axes:
        sep=next((q for q in n if q.type=='SEPXYZ'),None);comb=next((q for q in n if q.type=='COMBXYZ'),None)
        assert sep and comb,'Expected saved mapped PBR graph'
        for dest,axis in zip(['X','Y'],axes):l.new(sep.outputs[axis],comb.inputs[dest])
    return m
wood=anchored(woodbase,'G3R03_train_walnut_XZ',['X','Z'])
wooddeck=anchored(woodfloor,'G3R03_train_floor_XY',['X','Y'])

# Scope finishes on long original WB surfaces; the outside shader remains the same constants.
cache={}
def scoped(src,finish):
    key=(src.name,finish.name)
    if key in cache:return cache[key]
    old=src.node_tree.nodes.get('Principled BSDF');assert old and src.name.startswith('WB_')
    assert not any(i.is_linked for i in old.inputs),'Unexpected textured WB material; stop'
    m=finish.copy();m.name='G3R03_scoped_'+src.name+'_'+finish.name
    n=m.node_tree.nodes;l=m.node_tree.links;out=n.get('Material Output');inside=out.inputs['Surface'].links[0].from_socket
    outside=n.new('ShaderNodeBsdfPrincipled')
    for inp in old.inputs:
        dst=outside.inputs.get(inp.name)
        if dst is not None and hasattr(inp,'default_value'):
            try:dst.default_value=inp.default_value
            except (TypeError,ValueError):pass
    tex=n.new('ShaderNodeTexCoord');tex.object=train;sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0])
    a=n.new('ShaderNodeMath');a.operation='GREATER_THAN';a.inputs[1].default_value=-6.1;l.new(sep.outputs['X'],a.inputs[0])
    b=n.new('ShaderNodeMath');b.operation='LESS_THAN';b.inputs[1].default_value=-1.9;l.new(sep.outputs['X'],b.inputs[0])
    both=n.new('ShaderNodeMath');both.operation='MULTIPLY';l.new(a.outputs[0],both.inputs[0]);l.new(b.outputs[0],both.inputs[1])
    mix=n.new('ShaderNodeMixShader');l.new(both.outputs[0],mix.inputs[0]);l.new(outside.outputs[0],mix.inputs[1]);l.new(inside,mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
    cache[key]=m;return m

def apply(o,m):
    o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)

changed=[]
for o in list(bpy.data.collections['D_complete_enterable_train'].objects):
    if o.type not in {'MESH','CURVE'} or not o.active_material:continue
    lo,hi=box(o)
    if hi[0]<-4.1 or lo[0]>.1:continue
    src=o.active_material
    if not src.name.startswith('WB_'):
        if any(g.type=='NEW_GEOMETRY' and g.outputs['Position'].is_linked for g in src.node_tree.nodes):
            anchor=o.parent if o.parent and o.parent.name.startswith('Train_door_') else train
            apply(o,anchored(src,'G3R03_attached_'+src.name,anchor=anchor));changed.append(o.name)
        continue
    name=o.name
    if name.startswith(('Car_floor','Car_inner_wainscot')):finish=wooddeck if name.startswith('Car_floor') else wood
    elif name.startswith('Rear_luggage_bench'):finish=velvet
    elif name.startswith(('Car_curved_lower_shell','Car_complete_barrel_roof','Car_window_pillar')):finish=metal
    elif name.startswith(('Car_side_window','Door_glazing')):finish=glass
    elif name.startswith(('Car_window_horizontal_frame','Car_waist_trim','Car_luggage_rail')):finish=brass
    else:continue
    apply(o,scoped(src,finish));changed.append(o.name)
report['material_changed_objects']=changed
report['attached_mapping']={'anchor':'Train_motion_root','local_sample_x':[-6.1,-1.9],
 'official_reference':'https://docs.blender.org/manual/en/4.5/render/shader_nodes/input/texture_coordinate.html'}

# Build real joinery just inside the opposite vestibule wall. No new partitions or route changes.
def on_train(o):o.parent=train;return o
for xx in [-5.65,-4.55,-3.45,-2.35]:
    on_train(cube('G3R03_wood_recess_panel',(xx,1.255,1.70),(1.025,.025,.72),wood,.012))
    for z in [1.305,2.035]:on_train(cube('G3R03_panel_horizontal_bead',(xx,1.236,z),(1.08,.026,.026),brass,.004))
for xx in [-6.18,-5.10,-4,-2.90,-1.82]:
    on_train(cube('G3R03_panel_vertical_stile',(xx,1.238,1.70),(.037,.040,.80),wood,.007))
on_train(cube('G3R03_vestibule_cream_ceiling',(-4,0,3.91),(4.12,2.40,.045),cream,.020))
for side in [-1,1]:on_train(cube('G3R03_ceiling_cornice',(-4,side*1.19,3.86),(4.12,.07,.09),wood,.012))
# Existing practical gets a visible diffuser housing in the same place and moves with the train.
light=bpy.data.objects['G3_door_practical'];worldmat=light.matrix_world.copy();light.parent=train;light.matrix_world=worldmat
on_train(cube('G3R03_door_light_rim',(-4,-.20,3.745),(.95,.34,.085),brass,.035))
diffuser=material('G3R03_opal_diffuser',(.72,.62,.47),rough=.52,emission=1.5)
on_train(cube('G3R03_door_light_diffuser',(-4,-.20,3.695),(.85,.27,.025),diffuser,.023))
# Threshold fasteners do not raise or replace the walking surface.
for xx in [-4.52,-3.48]:
    on_train(cylinder('G3R03_threshold_countersink',(xx,-1.43,1.147),(xx,-1.43,1.152),.008,brass,24))

# Larger observation, not a replacement for the cropped original.
full=camera('G3R03_complete_bay',(.8,-3.0,3.1),(-2.8,4.8,2.5),36)
chaircam=camera('G3R03_chair_front',(-1.45,3.65,2.35),(-3.15,2.16,1.84),48)
doorcam=camera('G3R03_full_door',(-.6,7.30,2.52),(-2,10.73,2.25),35)
camera('G3R03_roof_node',(-1,3.9,5.15),(-3.92,5.9,5.25),55)
bpy.context.view_layer.update()
s.render.resolution_x,s.render.resolution_y=1440,900
observed=chairs+[bpy.data.objects[n] for n in ['G3_walnut_cafe_top','G3_turned_pedestal','potted_plant_01_pot','potted_plant_01_leaves','Platform_portal_lintel']]
projected=[world_to_camera_view(s,full,o.matrix_world@Vector(p)) for o in observed for p in o.bound_box]
report['full_bay_framing']={'x':[min(p.x for p in projected),max(p.x for p in projected)],'y':[min(p.y for p in projected),max(p.y for p in projected)],'min_depth':min(p.z for p in projected),'lens':full.data.lens}
assert all(p.z>0 and .02<=p.x<=.98 and .02<=p.y<=.98 for p in projected),'Complete furniture framing differs; inspect before rendering'
assert signature()==before,'Protected geometry/original camera/frame-451 transform changed'
report['protected_signature_before']=before;report['protected_signature_after']=signature()
report['supplemental_cameras']=[full.name,chaircam.name,doorcam.name,'G3R03_roof_node']
# Keep practical movement explicit: scene frame 451 is unchanged, other frames must follow train.
report['new_moving_light']='G3_door_practical parented preserving its actual stopped-world transform'
for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
    if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
(OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
s['g3_revision']='R03 vestibule craft and supplemental complete observations';s['g3_r03_parent_sha256']=EXPECTED
s['g3_scope']='Same structural sample bay plus entrance vestibule; not full-scene final art'
s.frame_set(451);s.camera=full
save(s,OUT/'g3-bay-candidate.blend')
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
report['candidate_sha256']=hashlib.sha256((OUT/'g3-bay-candidate.blend').read_bytes()).hexdigest()
(OUT/'finish-report.json').write_text(json.dumps(report,indent=2))
build=json.loads((BASE/'build-report.json').read_text());build['candidate_sha256']=report['candidate_sha256'];build['revision']='R03';build['revision_report']='finish-report.json'
(OUT/'build-report.json').write_text(json.dumps(build,indent=2))
print('G3_R03_EDITABLE_CANDIDATE_SAVED',report['candidate_sha256'],flush=True)
