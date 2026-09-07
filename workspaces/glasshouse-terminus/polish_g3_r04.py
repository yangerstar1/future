"""G3 R04 art challenger: motivated lighting and one complete structural bay.
Exact R03 source required. Does not rebuild G2, expand G4 or grant acceptance.
"""
import bpy,json,hashlib,sys,math,shutil
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,sweep,camera,area,save
BASE=Path('workspaces/glasshouse-terminus/output/g3-r03').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-r04').resolve()
SOURCE=BASE/'g3-bay-candidate.blend'
EXPECTED='cb1ae3c8ace74bcbeeaaf51684bf013cba5b7702803f432c91632e4395fadcfe'
assert Path(bpy.data.filepath).resolve()==SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED and bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('g3_revision')=='R03 vestibule craft and supplemental complete observations'
s.frame_set(451);bpy.context.view_layer.update();OUT.mkdir(parents=True,exist_ok=True)
A=bpy.data.collections['A_complete_glasshouse'];old_objects=list(s.objects)
MARKERS=[(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers]
def box(ob):
    q=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    return [min(v[i] for v in q) for i in range(3)],[max(v[i] for v in q) for i in range(3)]
def signature():
    s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
    for ob in sorted(old_objects,key=lambda o:o.name):
        h.update(ob.name.encode());h.update(repr(tuple(tuple(r) for r in ob.matrix_world)).encode())
        if ob.type=='MESH':
            for v in ob.data.vertices:h.update(repr(tuple(v.co)).encode())
        if ob.type=='CAMERA':h.update(repr((ob.data.lens,ob.data.clip_start,ob.data.clip_end)).encode())
    return h.hexdigest()
protected=signature()
report={'stage':'G3','revision':'R04','status':'ART_CHALLENGER_NOT_ACCEPTED','source_master_sha256':EXPECTED,
 'source_evidence_commit':'22dceca579c272b51767c70c153c540f7defc547',
 'contract_sha256':'0101fa0f69edc3e261ead088c447818168c397e5ca8dbc26b0de341ad7f7c23f',
 'scope':'One existing x=-4..0 structural bay, including both sides of its vault; not full hall.',
 'diagnosis_run':34121257143,'diagnosis_zip_sha256':'e4d28113c0f9204326a2e14aeed927262b8c12bac8e07c61f2ac47b08282d88a',
 'source_arches':[],'material_edits':[],'light_edits':[],'g4_allowed':False,'human_acceptance':False,'browser_gate':'BLOCKED_UNCHANGED'}
arches=[];ribs=[]
for ob in A.objects:
    if ob.type!='MESH':continue
    lo,hi=box(ob);x=(lo[0]+hi[0])/2
    if -4.01<=x<=.01 and ob.name.startswith(('Primary_elliptical_arch','Secondary_glazing_rib')):
        report['source_arches'].append({'name':ob.name,'bounds':[lo,hi],'center_y':(lo[1]+hi[1])/2,'material':ob.active_material.name})
        assert lo[1]<-6.4 and hi[1]>6.4 and hi[2]>10,'Different arch layout; inspect first'
        (arches if ob.name.startswith('Primary') else ribs).append(ob)
assert len(arches)==2 and len(ribs)==3,report['source_arches']
(OUT/'art-preflight.json').write_text(json.dumps(report,indent=2))
C=bpy.data.collections.new('G3R04_arch_craft_and_luminaires');s.collection.children.link(C)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]
enamel=material('G3R04_satin_bottle_green',(.033,.070,.055),metal=.12,rough=.32,coat=.23)
bronze=material('G3R04_satin_bronze_fasteners',(.30,.215,.12),metal=.80,rough=.34)
seal=bpy.data.materials['G3_EPDM_seal'];glass=bpy.data.materials['G3_clear_6mm_glass'];wetglass=bpy.data.materials['G3_exterior_rivulet_glass']
stone=bpy.data.materials['G3_slate_dry'].copy();stone.name='G3R04_dry_slate_arch_plinth'
p=stone.node_tree.nodes.get('Principled BSDF')
for edge in list(p.inputs['Roughness'].links):stone.node_tree.links.remove(edge)
p.inputs['Roughness'].default_value=.65;p.inputs['Coat Weight'].default_value=0
# Use full X bounds with tolerance; record actual materials rather than guessing omissions.
def finish(ob,mat):
    old=ob.active_material;lo,hi=box(ob)
    if lo[0]>=-4.20 and hi[0]<=.20:new=mat
    else:
        new=old.copy();new.name='G3R04_zone_'+ob.name;n=new.node_tree.nodes;l=new.node_tree.links;output=n.get('Material Output')
        prior=output.inputs['Surface'].links[0].from_socket
        shader=n.new('ShaderNodeBsdfPrincipled');source=mat.node_tree.nodes.get('Principled BSDF')
        for inp in source.inputs:
            dst=shader.inputs.get(inp.name)
            if dst is not None and hasattr(inp,'default_value'):
                try:dst.default_value=inp.default_value
                except (TypeError,ValueError):pass
        g=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(g.outputs['Position'],sep.inputs[0])
        left=n.new('ShaderNodeMath');left.operation='GREATER_THAN';left.inputs[1].default_value=-4.11
        right=n.new('ShaderNodeMath');right.operation='LESS_THAN';right.inputs[1].default_value=.11
        l.new(sep.outputs['X'],left.inputs[0]);l.new(sep.outputs['X'],right.inputs[0])
        both=n.new('ShaderNodeMath');both.operation='MULTIPLY';l.new(left.outputs[0],both.inputs[0]);l.new(right.outputs[0],both.inputs[1])
        mix=n.new('ShaderNodeMixShader');l.new(both.outputs[0],mix.inputs[0]);l.new(prior,mix.inputs[1]);l.new(shader.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],output.inputs['Surface'])
    ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(new)
    report['material_edits'].append({'object':ob.name,'from':old.name,'to':new.name,'world_x_bounds':[lo[0],hi[0]]})
families=('Primary_elliptical_arch','Secondary_glazing_rib','Load_column','Column_capital','Column_base_plinth','Wall_glazing_mullion','Portal_transom_mullion','Wall_transom','Wall_stone_sill','Longitudinal_roof_purlin','Continuous_eaves_gutter','Curved_roof_glazing','Side_wall_glass')
for ob in list(A.objects):
    if ob.type not in {'MESH','CURVE'} or not ob.name.startswith(families):continue
    lo,hi=box(ob);center=(lo[0]+hi[0])/2
    if hi[0]<-4.11 or lo[0]>.11:continue
    if hi[0]-lo[0]<4.2 and not -4.01<=center<=.01:continue
    if ob.name.startswith(('Curved_roof_glazing','Side_wall_glass')):mat=wetglass if ob.name.startswith('Side_wall_glass') else glass
    elif ob.name.startswith(('Column_base_plinth','Wall_stone_sill')):mat=stone
    else:mat=enamel
    finish(ob,mat)
# Pressure caps are actual extruded sections supported on continuous EPDM pads.
for ob in ribs:
    lo,hi=box(ob);x=(lo[0]+hi[0])/2;path=[];pads={-1:[],1:[]}
    for j in range(73):
        a=j*math.pi/72;n=Vector((0,math.cos(a)/6.5,math.sin(a)/5.1)).normalized()
        c=Vector((x,6.5*math.cos(a),5+5.1*math.sin(a)));path.append(tuple(c+n*.036))
        for side in [-1,1]:pads[side].append(tuple(c+Vector((side*.048,0,0))+n*.019))
    sweep('G3R04_glazing_pressure_cap',path,[(-.064,-.004),(.064,-.004),(.064,.008),(-.064,.008)],enamel)
    for pad in pads.values():sweep('G3R04_compression_gasket',pad,[(-.013,-.013),(.013,-.013),(.013,.013),(-.013,.013)],seal)
    for j in range(4,70,12):
        a=j*math.pi/72;n=Vector((0,math.cos(a)/6.5,math.sin(a)/5.1)).normalized();c=Vector((x,6.5*math.cos(a),5+5.1*math.sin(a)))
        cylinder('G3R04_pressure_cap_fixing',c+n*.044,c+n*.051,.008,bronze,12)
for ob in arches:
    lo,hi=box(ob);x=(lo[0]+hi[0])/2
    for side in [-1,1]:
        y=side*6.5;cube('G3R04_arch_splice_plate',(x+.108,y,5.065),(.016,.215,.42),enamel,.006)
        for yy in [y-.060,y+.060]:
            for z in [4.925,5.205]:
                cylinder('G3R04_splice_washer',(x+.118,yy,z),(x+.122,yy,z),.015,bronze,32)
                cylinder('G3R04_splice_hex_head',(x+.122,yy,z),(x+.130,yy,z),.010,bronze,6)
# Retire the unmotivated studio card after actual attribution, not by hiding rays.
for name,power in [('G3_interior_softbox',0),('G3_pendant_light',260),('G3_cafe_practical',14),('G3_door_practical',90)]:
    lamp=bpy.data.objects[name];report['light_edits'].append({'object':name,'before':lamp.data.energy,'after':power});lamp.data.energy=power
opal=material('G3R04_opal_sconce',(.76,.70,.59),rough=.37,emission=2.0);new_lights=[]
for x in [-4,0]:
    cube('G3R04_sconce_backplate',(x,6.305,3.72),(.145,.030,.44),enamel,.018)
    cylinder('G3R04_sconce_mount',(x,6.288,3.72),(x,6.125,3.72),.022,bronze,24)
    cylinder('G3R04_sconce_opal',(x,6.12,3.54),(x,6.12,3.90),.046,opal,48)
    for z in [3.53,3.91]:cylinder('G3R04_sconce_endcap',(x,6.12,z-.018),(x,6.12,z+.018),.056,bronze,48)
    light=area('G3R04_sconce_light',(x,6.025,3.72),(-2,2.6,2.1),24,.28,(1,.84,.66));new_lights.append(light.name)
s['g3_night_lights']=json.dumps(json.loads(s['g3_night_lights'])+new_lights)
report['lighting_design']='Studio fill retired after isolated attribution. Existing real pendant/table/train fixtures strengthened; attached opal column sconces added. No light-path exclusions or exposure changes.'
# Evaluate the new camera transform before projecting bounds. The failed execution
# tested its stale identity matrix; this retry preserves the same requested view.
s.timeline_markers.clear();s.frame_set(451);bpy.context.view_layer.update()
door=camera('G3R04_unobstructed_interface',(-2,8.25,2.58),(-2,10.72,2.26),30)
report['new_camera_matrix_before_update']=[list(row) for row in door.matrix_world]
bpy.context.view_layer.update()
report['new_camera_matrix_after_update']=[list(row) for row in door.matrix_world]
threshold=bpy.data.objects['Car_door_threshold'];housing=bpy.data.objects['G3_door_track_housing']
lo1,hi1=box(threshold);lo2,hi2=box(housing);s.render.resolution_x=1280;s.render.resolution_y=800
pts=[o.matrix_world@Vector(v) for o in [threshold,housing] for v in o.bound_box]
report['interface_framing_trials']=[]
for lens in range(34,19,-1):
    door.data.lens=lens;q=[world_to_camera_view(s,door,p) for p in pts]
    report['interface_framing_trials'].append({'lens':lens,'x':[min(v.x for v in q),max(v.x for v in q)],'y':[min(v.y for v in q),max(v.y for v in q)],'depth':min(v.z for v in q)})
    (OUT/'art-progress.json').write_text(json.dumps(report,indent=2))
    if all(v.z>0 and .04<=v.x<=.96 and .04<=v.y<=.96 for v in q):break
else:raise RuntimeError('Evaluated interface frame does not fit; stop, never move source objects')
report['supplemental_interface']={'camera':door.name,'lens':door.data.lens,'position':list(door.location),'visibility':[]}
deps=bpy.context.evaluated_depsgraph_get()
for target,point in [('threshold',Vector(((lo1[0]+hi1[0])/2,lo1[1]+.04,hi1[2]))),('guide_housing',Vector(((lo2[0]+hi2[0])/2,lo2[1],(lo2[2]+hi2[2])/2)))]:
    d=point-door.location;hit,where,normal,index,obj,matrix=s.ray_cast(deps,door.location,d.normalized(),distance=d.length+.03)
    report['supplemental_interface']['visibility'].append({'target':target,'first_object':obj.name if obj else None,'point':list(where) if hit else None})
    assert hit and obj and not obj.name.startswith(('Hall_door','Platform_portal')),'Still occluded by hall; stop'
camera('G3R04_threshold_detail',(-1.7,9.1,2.12),(-2,10.69,1.18),48)
camera('G3R04_roller_detail',(-2.8,9.1,3.73),(-2.94,10.60,3.40),62)
assert signature()==protected,'Original geometry, transforms or cameras changed'
report['protected_geometry_before']=protected;report['protected_geometry_after']=signature()
for name,frame,camname in MARKERS:
    m=s.timeline_markers.new(name,frame=frame)
    if camname:m.camera=bpy.data.objects[camname]
report['restored_source_markers']=MARKERS
for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
    if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
(OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
s['g3_revision']='R04 motivated illumination and completed arch bay';s['g3_r04_parent_sha256']=EXPECTED
s.frame_set(451);s.camera=bpy.data.objects['G3R03_complete_bay'];s.view_settings.exposure=0
save(s,OUT/'g3-bay-candidate.blend')
report['candidate_sha256']=hashlib.sha256((OUT/'g3-bay-candidate.blend').read_bytes()).hexdigest()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
(OUT/'art-report.json').write_text(json.dumps(report,indent=2))
build=json.loads((BASE/'build-report.json').read_text());build.update(candidate_sha256=report['candidate_sha256'],revision='R04',revision_report='art-report.json')
(OUT/'build-report.json').write_text(json.dumps(build,indent=2))
print('R04_ART_CANDIDATE_SAVED_NOT_ACCEPTED',report['candidate_sha256'],flush=True)
