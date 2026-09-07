"""G4 R01 full-scene art challenger from verified R07, with user stage-order exception.
Reuse the actual source and native helpers. No G2 rebuild, no automatic art PASS.
The original G3 gate stays historically unmet; carried craft work is addressed here.
"""
import bpy,os,sys,json,hashlib,math,time,shutil
from pathlib import Path
from array import array
from mathutils import Vector,Matrix
from math import sin,cos,pi
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,curve,lathe,mesh,area,save,render
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g3-r07-recovered';OUT=ROOT/'output/g4-r01';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e'
MODE=os.environ['G4_MODE'];assert MODE in ['build','overview','regression']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]
def center(o):
    a,b=bounds(o);return Vector([(a[i]+b[i])/2 for i in range(3)])
def collection(name):
    c=bpy.data.collections.new(name);s.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
    return c
def attach(o,parent):o.parent=parent;return o

def geometry_signature(names):
    h=hashlib.sha256()
    for n in sorted(names):
        o=bpy.data.objects[n];h.update(n.encode());h.update(o.type.encode())
        if o.type=='MESH':
            a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
        elif o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:h.update(repr(tuple(p.co)).encode())
    return h.hexdigest()
def motion_signature(names):
    h=hashlib.sha256()
    for f in [1,91,211,301,330,348,451,541,660,840]:
        s.frame_set(f);bpy.context.view_layer.update()
        for n in sorted(names):
            o=bpy.data.objects[n];h.update(repr((n,tuple(tuple(r) for r in o.matrix_world))).encode())
            if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end)).encode())
    s.frame_set(451);bpy.context.view_layer.update();return h.hexdigest()

def uv_material(src,name):
    m=src.copy();m.name=name;n=m.node_tree.nodes;l=m.node_tree.links
    uv=n.new('ShaderNodeTexCoord');uv.name='G4_explicit_surface_UV'
    for t in n:
        if t.type=='TEX_IMAGE':l.new(uv.outputs['UV'],t.inputs['Vector'])
    return m

def uv_faces(o,scale=.8,long_axis=None,train_space=False):
    """Face-oriented metre-scale UVs avoid planar projection collapse on side faces."""
    assert o.type=='MESH';o.data=o.data.copy()
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
    dims=list(o.dimensions)
    if long_axis is None:long_axis=max(range(3),key=lambda i:dims[i])
    for p in o.data.polygons:
        normal_axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=normal_axis]
        grain=long_axis if long_axis in axes else axes[1];across=next(i for i in axes if i!=grain)
        for li in p.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(float(v[across])*scale,float(v[grain])*scale)
    return o

def simple_texture(name,base,rough,scale=100,bump_distance=.001,sheen=0):
    m=material(name,base,rough=rough);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Sheen Weight'].default_value=sheen
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=bump_distance
    l.new(tc.outputs['Object'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    return m

if MODE=='build':
    parent=BASE/'g3-bay-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==EXPECTED
    assert s.get('g3_revision')=='R07 two existing purlin wash powers calibrated after native R06 review'
    assert (ROOT/'G4-AUTHORIZATION.md').is_file()
    inventory=json.loads((ROOT/'output/g4-inventory/R07-extension-inventory.json').read_text())
    assert inventory['source_master_sha256']==EXPECTED and inventory['source_master_unchanged']
    assert {o['name'] for o in inventory['objects']}=={o.name for o in s.objects},'Source inventory changed; stop rather than guess'
    s.frame_set(451);bpy.context.view_layer.update()
    train=bpy.data.objects['Train_motion_root'];assert (train.location-Vector((2,12.1,0))).length<.001
    assert abs(bounds(bpy.data.objects['Hall_continuous_floor'])[1][2]-1.15)<.001
    originals=list(s.objects);original_names=[o.name for o in originals]
    report={'stage':'G4','revision':'R01','status':'CHALLENGER_NOT_ART_PASS','user_stage_order_exception':'G4-AUTHORIZATION.md',
      'g3_historical_status':'PAUSED_UNMET_G3_CRAFT_REVIEW','parent_master_sha256':EXPECTED,
      'parent_evidence_commit':'192eba1352585df211f1aa2447a193eec949f6be','inventory_evidence_commit':'00390f1a761b1f263e136395444e8bf7c5b7e74a',
      'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'replacements':[],
      'material_assignments':[],'new_lights':[],'craft_corrections':[],'human_acceptance':False,'g4_stage_pass':False}
    # Replace only explicitly observed placeholders and the flat ceiling that crosses the barrel envelope.
    replace=[o for o in originals if o.name.startswith(('Cafe_table_','Cafe_chair_','Chair_leg_','Waiting_bench_cushion_proxy','Waiting_bench_back_proxy'))]
    plant_sites=[(-14,-5.3),(-8,-5.3),(-2,-5.3),(4,-5.3),(10,-5.3),(14,-5.3),(-7.2,5.15),(5,5.1),(13,5.1)]
    broad_sites={(-14,-5.3),(14,-5.3),(13,5.1)}
    botanical=list(bpy.data.collections['A_botanical_volume_proxies'].objects)
    def plant_site(o):
        p=center(o);return min(plant_sites,key=lambda q:(p.x-q[0])**2+(p.y-q[1])**2)
    for o in botanical:
        if o.name.startswith('Plant_container_proxy') or plant_site(o) not in broad_sites:replace.append(o)
    flat=[bpy.data.objects[n] for n in ['G3R03_vestibule_cream_ceiling','G3R03_ceiling_cornice','G3R03_ceiling_cornice.001']]
    replace+=flat;removed={o.name for o in replace}
    protected=[n for n in original_names if n not in removed]
    g_before=geometry_signature(protected);motion_before=motion_signature(protected)
    report['replacements']=sorted(removed)
    # Inventory confirms XY on the round edge and YZ on all cabinet faces collapse one UV dimension.
    woodtop=bpy.data.materials['G3_walnut_top_grain_XY'];woodfront=bpy.data.materials['G3_walnut_cabinet_vertical_grain']
    wooduv=uv_material(woodfront,'G4_walnut_metre_UV');edgeuv=uv_material(woodtop,'G4_circumferential_edge_veneer')
    top=bpy.data.objects['G3_walnut_cafe_top'];top.data=top.data.copy();top.data.materials.append(edgeuv)
    uv=top.data.uv_layers.active;assert uv
    for p in top.data.polygons:
        if abs(p.normal.z)>.65:continue
        p.material_index=len(top.data.materials)-1
        angles=[math.atan2(top.data.vertices[top.data.loops[i].vertex_index].co.y-3.3,top.data.vertices[top.data.loops[i].vertex_index].co.x+3.15) for i in p.loop_indices]
        if max(angles)-min(angles)>pi:angles=[a+2*pi if a<0 else a for a in angles]
        for li,a in zip(p.loop_indices,angles):
            v=top.data.vertices[top.data.loops[li].vertex_index].co
            uv.data[li].uv=((v.z-1.884)*.8,a*.586*.8)
    report['craft_corrections'].append({'object':top.name,'change':'Only bevel/rim faces use continuous circumferential veneer UV; original planar top shading retained. Geometry unchanged.'})
    for o in originals:
        if o.name.startswith(('G3_sideboard_carcass','G3_cabinet_stile','G3_cabinet_rail','G3_cabinet_recessed_panel')):
            axis=2 if not o.name.startswith('G3_cabinet_rail') else 1
            uv_faces(o,long_axis=axis);o.data.materials.clear();o.data.materials.append(wooduv)
            report['craft_corrections'].append({'object':o.name,'change':'Face-oriented UV, vertical grain on panels/stiles and along-member grain on rails; no single-axis side-face collapse.'})
    for o in replace:bpy.data.objects.remove(o,do_unlink=True)
    metal=bpy.data.materials['G3R05_satin_column_paint'];body=bpy.data.materials['G3_bottle_green_enamel']
    sage=bpy.data.materials['G3R04_sage_green_secondary_enamel'];brass=bpy.data.materials['G3_satin_aged_brass'];steel=bpy.data.materials['G3_brushed_steel']
    rubber=bpy.data.materials['G3_EPDM_seal'];clear=bpy.data.materials['G3_clear_6mm_glass'];wetglass=bpy.data.materials['G3_exterior_rivulet_glass'];slate=bpy.data.materials['G3_slate_dry']
    cream=bpy.data.materials['G3R03_ceiling_cream'];opal=bpy.data.materials['G3R04_opal_wall_lamp']
    fabric=simple_texture('G4_moss_woven_upholstery',(.095,.125,.095),.66,180,.0005,.22)
    seam=material('G4_muted_fabric_piping',(.13,.155,.115),rough=.74)
    castiron=simple_texture('G4_graphite_cast_iron',(.048,.055,.057),.49,38,.001)
    terracotta=simple_texture('G4_fired_clay',(.23,.115,.069),.67,70,.002)
    soil=simple_texture('G4_potting_soil',(.032,.024,.015),.92,80,.006)
    # Procedural masonry in metres; no external asset download and no brick image pasted on geometry.
    stone=material('G4_weathered_grey_masonry',(.25,.27,.265),rough=.77)
    n=stone.node_tree.nodes;l=stone.node_tree.links;p=n.get('Principled BSDF')
    tc=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(1,1,1.8)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.4;noise.inputs['Detail'].default_value=4
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.14,.16,.16,1);ramp.color_ramp.elements[1].color=(.34,.355,.335,1)
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.035
    l.new(tc.outputs['Object'],v.inputs[0]);l.new(v.outputs[0],noise.inputs[0]);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    def assign(o,m):
        if o.type not in ['MESH','CURVE']:return
        old=[q.name if q else None for q in o.data.materials]
        o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
        report['material_assignments'].append({'object':o.name,'old':old,'new':m.name})
    # Extend the two-level green structure across both elevations, end walls and roof.
    hall=bpy.data.collections['A_complete_glasshouse'];canopy=bpy.data.collections['C_platform_canopy']
    new_glass=[]
    for o in list(hall.objects)+list(canopy.objects):
        if o.type not in ['MESH','CURVE']:continue
        name=o.name;old=o.active_material.name if o.active_material else ''
        if 'glass' in name.lower() or name.startswith(('Curved_roof_glazing','End_wall_glazing')):
            if old=='WB_glass':assign(o,wetglass);new_glass.append(o)
        elif name.startswith(('Primary_elliptical_arch','Load_column','Column_capital','Continuous_eaves_gutter','Ridge_vent_cap','Platform_canopy_beam','Platform_portal','Canopy_edge_fascia','End_elevation_crossbar')):assign(o,metal)
        elif name.startswith(('Wall_stone_sill','End_wall_sill','Column_base_plinth')):assign(o,stone)
        elif old.startswith('WB_') or old.startswith('G3R04_scoped_purlin'):assign(o,sage)
    # Full floor uses the actual slate recipe instead of its former rectangular whitebox mask.
    assign(bpy.data.objects['Hall_continuous_floor'],slate)
    platform=slate.copy();platform.name='G4_platform_sheltered_and_exposed_slate';n=platform.node_tree.nodes;l=platform.node_tree.links;p=n.get('Principled BSDF')
    for link in list(p.inputs['Roughness'].links):l.remove(link)
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');step=n.new('ShaderNodeMath');step.operation='GREATER_THAN';step.inputs[1].default_value=9.85
    mix=n.new('ShaderNodeMapRange');mix.inputs['From Min'].default_value=0;mix.inputs['From Max'].default_value=1;mix.inputs['To Min'].default_value=.50;mix.inputs['To Max'].default_value=.24
    l.new(geo.outputs['Position'],sep.inputs[0]);l.new(sep.outputs['Y'],step.inputs[0]);l.new(step.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Roughness'])
    assign(bpy.data.objects['Platform_continuous_slab'],platform)
    for o in list(bpy.data.collections['E_cliff_foundation'].objects)+list(bpy.data.collections['E_curved_viaduct_and_track'].objects):
        if o.type not in ['MESH','CURVE']:continue
        if o.name.startswith(('Complete_cliff_mass','Ocean_extent','Hall_continuous_floor','Platform_continuous_slab')):continue
        old=o.active_material.name if o.active_material else ''
        if o.name.startswith(('Running_rail','Wheel_')):assign(o,steel)
        elif o.name.startswith('Track_sleeper'):uv_faces(o,long_axis=1);assign(o,wooduv)
        elif 'guard' in o.name.lower() or old=='WB_underframe':assign(o,castiron)
        elif old.startswith('WB_'):assign(o,stone)
    collection('G4R01_architecture_craft')
    # Batched boundary curves keep complete pane seals economical and editable.
    data=bpy.data.curves.new('G4_full_pane_perimeter_seals','CURVE');data.dimensions='3D';data.bevel_depth=.0045;data.bevel_resolution=1
    for o in new_glass:
        if not o.name.startswith(('Curved_roof_glazing','Side_wall_glass','End_wall_glazing')):continue
        edges={}
        for f in o.data.polygons:
            vs=list(f.vertices)
            for a,b in zip(vs,vs[1:]+vs[:1]):key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
        for (a,b),count in edges.items():
            if count!=1:continue
            sp=data.splines.new('POLY');sp.points.add(1)
            for point,vi in zip(sp.points,[a,b]):point.co=(*(o.matrix_world@o.data.vertices[vi].co),1)
    ob=bpy.data.objects.new('G4_full_pane_perimeter_seals',data);bpy.context.collection.objects.link(ob);data.materials.append(rubber)
    def duplicate(src,T,label,light_power=None):
        o=src.copy();o.name=label;o.parent=None;o.animation_data_clear();o.matrix_world=T@src.matrix_world
        if src.type=='LIGHT':
            o.data=src.data.copy()
            if light_power is not None:o.data.energy=light_power
            report['new_lights'].append(o.name)
        bpy.context.collection.objects.link(o);o['g4_reused_source']=src.name;return o
    # Reuse the demonstrated bolted joints at every existing structural bay endpoint.
    joint=[o for o in list(s.objects) if o.type in ['MESH','CURVE'] and o.name.startswith(('G3R04_eave_splice_plate','G3R04_splice_','G3_column_anchor_bolt','G3_column_cap_plate','G3_cap_rivet')) and abs(center(o).x+4)<.5]
    assert len(joint)>12
    sconces=[o for o in list(s.objects) if o.type in ['MESH','CURVE'] and o.name.startswith(('G3R04_sconce_','G3R04_opal_diffuser')) and abs(center(o).x+4)<.3]
    assert len(sconces)==7,(len(sconces),[o.name for o in sconces])
    for side in [1,-1]:
        for x in range(-16,17,4):
            if side==1 and x in [-4,0]:continue
            T=Matrix.Translation((x,side*6.5,0))@Matrix.Rotation(0 if side==1 else pi,4,'Z')@Matrix.Translation((4,-6.5,0))
            for o in joint:duplicate(o,T,'G4_joint_'+o.name)
            for o in sconces:duplicate(o,T,'G4_sconce_'+o.name)
            duplicate(bpy.data.objects['G3_interior_softbox'],T,'G4_column_sconce',28)
    # Inlaid coping strip and real grate bars, avoiding the existing sample grate group.
    ivory=material('G4_warm_limestone_edge',(.44,.43,.35),rough=.57)
    cube('G4_platform_edge_inlay',(0,10.30,1.1508),(34.2,.065,.0016),ivory,.001)
    for x in [(-16.7+i*.24) for i in range(140)]:
        if -4.15<x<.15:continue
        cube('G4_drain_grate_bar',(x,7.05,1.158),(.050,.105,.012),steel,.002)
    # Reuse complete furniture groups, not basic box proxies or a new furniture download.
    collection('G4R01_furniture_and_botanical')
    table_set=[o for o in list(s.objects) if o.name.startswith(('G3_walnut_cafe_top','G3_table_edge_inlay','G3_turned_pedestal','G3_carved_pedestal_foot','G3_foot_felt_contact','GreenChair_01'))]
    for x,y in [(-10.2,3.3),(7.4,3.2)]:
        T=Matrix.Translation((x+3.15,y-3.3,0))
        for o in table_set:duplicate(o,T,'G4_cafe_'+o.name)
    def rounded_loop(xlen,ylen,z,rad=.05):
        points=[]
        for cx,cy,start in [(xlen/2-rad,ylen/2-rad,0),(-xlen/2+rad,ylen/2-rad,90),(-xlen/2+rad,-ylen/2+rad,180),(xlen/2-rad,-ylen/2+rad,270)]:
            for i in range(7):
                a=math.radians(start+i*15);points.append((cx+rad*cos(a),cy+rad*sin(a),z))
        return points
    for x in [-11,-5,5,11]:
        y=-3.65
        frame=cube('G4_waiting_bench_wood_frame',(x,y,1.53),(2.40,.68,.105),wooduv,.018);uv_faces(frame,long_axis=0)
        for side in [-1,1]:
            bar=cube('G4_bench_back_upright',(x+side*1.12,y-.30,1.90),(.070,.095,.83),wooduv,.012);uv_faces(bar,long_axis=2)
            cylinder('G4_bench_arm_support',(x+side*1.14,y+.17,1.58),(x+side*1.14,y+.17,1.91),.018,brass,24)
            grip=cube('G4_bench_wood_arm',(x+side*1.14,y-.02,1.94),(.09,.60,.06),wooduv,.025);uv_faces(grip,long_axis=1)
        cap=cube('G4_bench_top_rail',(x,y-.30,2.30),(2.38,.105,.075),wooduv,.025);uv_faces(cap,long_axis=0)
        for xx in [-.78,0,.78]:
            cushion=cube('G4_bench_seat_cushion',(x+xx,y,1.655),(.73,.63,.15),fabric,.052)
            back=cube('G4_bench_back_cushion',(x+xx,y-.25,2.04),(.73,.13,.47),fabric,.043)
            curve('G4_bench_seat_piping',[(x+xx+a,y+b,1.704) for a,b,c in rounded_loop(.68,.58,0,.055)],.0032,seam,True)
    for o in s.objects:
        if o.name.startswith('Waiting_bench_support'):assign(o,castiron)
    plant_asset=[bpy.data.objects[n] for n in ['potted_plant_01_pot','potted_plant_01_leaves','potted_plant_01_pebbles','potted_plant_01_stem']]
    for i,(x,y) in enumerate(plant_sites):
        if (x,y) in broad_sites:
            lathe('G4_broadleaf_clay_planter',[(.32,0),(.36,.04),(.37,.10),(.44,.51),(.49,.55),(.49,.62),(.455,.64),(.445,.60),(.415,.54),(.35,.14)],(x,y,1.15),terracotta,64)
            cylinder('G4_planter_soil',(x,y,1.69),(x,y,1.71),.423,soil,48)
        else:
            scale=1.27+.10*(i%3)
            T=Matrix.Translation((x,y,1.15))@Matrix.Rotation(.55*i,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation((.53,-5.2,-1.15))
            for o in plant_asset:duplicate(o,T,'G4_botanical_'+o.name)
    leafmat=material('G4_broadleaf_lamina',(.055,.11,.043),rough=.46)
    n=leafmat.node_tree.nodes;l=leafmat.node_tree.links;tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5
    ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';test=n.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=.018
    color=n.new('ShaderNodeMixRGB');color.inputs[1].default_value=(.045,.10,.037,1);color.inputs[2].default_value=(.10,.145,.055,1)
    l.new(tc.outputs['UV'],sep.inputs[0]);l.new(sep.outputs['X'],sub.inputs[0]);l.new(sub.outputs[0],ab.inputs[0]);l.new(ab.outputs[0],test.inputs[0]);l.new(test.outputs[0],color.inputs[0]);l.new(color.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
    stemmat=material('G4_broadleaf_stem',(.074,.11,.045),rough=.62)
    for o in list(bpy.data.collections['A_botanical_volume_proxies'].objects):
        if o.name.startswith('Botanical_blade_proxy'):assign(o,leafmat);o['g4_role']='Existing curved lamina retained, finished in coherent botanical palette'
        elif o.name.startswith('Plant_stem_proxy'):assign(o,stemmat)
    # Physically suspended practical lights retain the finished sample's visual language.
    collection('G4R01_supported_practical_lights')
    pendants=[bpy.data.objects[n] for n in ['G3_pendant_drop','G3_pendant_shade','G3_pendant_diffuser','G3_pendant_light']]
    for side in [1,-1]:
        for x in [-13,-9,-5,-1,3,7,11,15]:
            if side==1 and abs(x+3)<=2:continue
            T=Matrix.Translation((x,side*3.25,0))@Matrix.Rotation(0 if side==1 else pi,4,'Z')@Matrix.Translation((3,-3.25,0))
            for o in pendants:duplicate(o,T,'G4_hall_'+o.name,220 if o.type=='LIGHT' else None)
    for x in range(-14,15,4):
        cube('G4_canopy_lamp_mount',(x,8.62,4.66),(.12,.12,.11),metal,.015)
        cube('G4_canopy_lamp_housing',(x,8.62,4.54),(.47,.24,.14),metal,.024)
        cube('G4_canopy_lamp_opal',(x,8.62,4.458),(.38,.16,.025),opal,.020)
        ob=area('G4_canopy_practical',(x,8.62,4.44),(x,8.62,1.15),48,.35,(1,.92,.79),size_y=.13);report['new_lights'].append(ob.name)
    # Whole train: original shell/doors/turning wheelsets and keyframes stay in place.
    collection('G4R01_train_finish')
    carwood=uv_material(woodtop,'G4_train_wood_UV');carwood.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.15
    roofpaint=material('G4_train_graphite_roof',(.055,.070,.072),metal=.30,rough=.38,coat=.12)
    for o in list(bpy.data.collections['D_complete_enterable_train'].objects):
        if o.type not in ['MESH','CURVE']:continue
        name=o.name;old=o.active_material.name if o.active_material else ''
        if name.startswith(('Car_seat_cushion','Car_seat_back','Cab_driver_seat','Rear_luggage_bench')):assign(o,fabric)
        elif name.startswith(('Car_floor','Cab_floor_extension','Car_inner_wainscot','Car_seat_base')):
            uv_faces(o,long_axis=0 if 'floor' in name.lower() else 2);assign(o,carwood)
        elif name.startswith(('Car_complete_barrel_roof','Cab_complete_roof_loft')):assign(o,roofpaint)
        elif 'glass' in name.lower() or name.startswith('Car_side_window'):assign(o,clear)
        elif name.startswith(('Wheel_tread','Wheel_flange','Wheel_hub','Axle')):assign(o,steel if 'tread' in name or 'flange' in name else castiron)
        elif name.startswith(('Car_underframe','Bogie_','Primary_suspension','Cab_buffer_beam','Cab_control_console')):assign(o,castiron)
        elif name.startswith(('Car_curved_lower_shell','Cab_cheek','Cab_upper_cheek','Cab_front_fairing','Car_window_pillar','Door_lower_panel')):assign(o,body)
        elif name.startswith(('Car_ceiling_light','Train_headlamp_lens')):assign(o,opal)
        elif old.startswith('WB_') or old.startswith('G3R03_scoped_'):assign(o,brass)
    # True curved interior ceiling, inside the measured barrel rather than a flat plate protruding outside.
    verts=[]
    for x in [-7.16,7.16]:
        for j in range(49):
            a=-pi/2+j*pi/48;verts.append((x,1.325*sin(a),3.30+.695*cos(a)))
    vault=mesh('G4_train_curved_inner_vault',verts,[(j,j+1,j+50,j+49) for j in range(48)],cream,smooth=True)
    vault.modifiers.new('Interior lining thickness','SOLIDIFY').thickness=.020;attach(vault,train)
    report['craft_corrections'].append({'replaced':[o['name'] for o in inventory['objects'] if o['name'] in {f.name for f in []}],
      'objects':['G3R03_vestibule_cream_ceiling','G3R03_ceiling_cornice','G3R03_ceiling_cornice.001'],
      'change':'Flat 2.4m-wide ceiling at3.91m exceeded the curved roof envelope at its sides. Replaced with full conforming inner vault; source exterior roof unchanged.'})
    for x in [-6,-2,2,6]:
        attach(cylinder('G4_car_lamp_stem',(x,0,3.946),(x,0,3.983),.019,brass,24),train)
        ob=attach(area('G4_car_ceiling_practical',(x,0,3.897),(x,0,1.3),52,.60,(1,.93,.81),size_y=.19),train);report['new_lights'].append(ob.name)
    for x in [-7.0,-5.4,-1.6,.15,1.9,3.65,5.4,7.0]:
        pts=[(x,1.31*sin(-pi/2+j*pi/40),3.29+.683*cos(-pi/2+j*pi/40)) for j in range(41)]
        attach(curve('G4_car_vault_rib',pts,.013,brass),train)
    # Window-aligned panel joinery on both sides, except the already finished vestibule panel group.
    for window in [o for o in s.objects if o.name.startswith('Car_side_window')]:
        pts=[train.matrix_world.inverted()@(window.matrix_world@Vector(v)) for v in window.bound_box]
        lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
        x=(lo[0]+hi[0])/2;side=1 if (lo[1]+hi[1])>0 else -1;w=hi[0]-lo[0]-.04
        if side==1 and -6.2<x<-1.8:continue
        panel=attach(cube('G4_car_recessed_walnut_panel',(x,side*1.255,1.70),(w,.028,.71),carwood,.014),train);uv_faces(panel,long_axis=2)
        for z in [1.329,2.071]:attach(cube('G4_car_panel_bead',(x,side*1.232,z),(w+.03,.019,.018),brass,.003),train)
        for xx in [x-w/2,x+w/2]:
            stile=attach(cube('G4_car_panel_stile',(xx,side*1.245,1.70),(.035,.030,.76),carwood,.007),train);uv_faces(stile,long_axis=2)
    # Upholstery piping and upper seat grab rails follow the actual seat transforms.
    for o in [v for v in s.objects if v.name.startswith('Car_seat_cushion')]:
        pts=[tuple(o.matrix_local@Vector(p)) for p in rounded_loop(.76,.74,.053,.045)]
        attach(curve('G4_car_seat_piping',pts,.0032,seam,True),train)
    for o in [v for v in s.objects if v.name.startswith('Car_seat_back')]:
        pts=[tuple(o.matrix_local@Vector((-.113,y,.35))) for y in [-.31,.31]]
        attach(curve('G4_seat_back_grab_rail',pts,.014,brass),train)
    # Spring windings, axle discs and original-root lights remain attached to the motion hierarchy.
    for o in [v for v in s.objects if v.name.startswith('Primary_suspension')]:
        pts=[tuple(o.matrix_local@Vector((.125*cos(2*pi*5*j/90),.125*sin(2*pi*5*j/90),-.16+.32*j/90))) for j in range(91)]
        attach(curve('G4_suspension_helix',pts,.014,steel),o.parent)
    for axle in [o for o in s.objects if o.name.startswith('Rolling_wheelset')]:
        for side in [-1,1]:attach(cylinder('G4_wheelset_brake_disc',(0,side*.52-.013,0),(0,side*.52+.013,0),.23,castiron,48),axle)
    for y in [-.71,.71]:
        d=bpy.data.lights.new('G4_train_headlight','SPOT');d.energy=150;d.color=(1,.94,.82);d.spot_size=math.radians(34);d.spot_blend=.55;d.shadow_soft_size=.045
        ob=bpy.data.objects.new('G4_train_headlight',d);bpy.context.collection.objects.link(ob);ob.location=(8.203,y,1.62)
        ob.rotation_euler=Vector((1,0,-.045)).to_track_quat('-Z','Y').to_euler();attach(ob,train);report['new_lights'].append(ob.name)
    # A few machined cab details, not random mechanical clutter.
    dial=material('G4_ivory_instrument_face',(.52,.54,.46),rough=.44)
    for y in [-.43,0,.43]:
        attach(cylinder('G4_cab_gauge_bezel',(6.884,y,1.97),(6.868,y,1.97),.093,brass,48),train)
        attach(cylinder('G4_cab_gauge_face',(6.865,y,1.97),(6.861,y,1.97),.078,dial,48),train)
        attach(curve('G4_cab_gauge_needle',[(6.856,y,1.97),(6.856,y-.045,2.005)],.003,castiron),train)
    # Coast/support material and controlled geometric relief, keeping the original terrace contact intact.
    collection('G4R01_coast_and_support')
    cliff=bpy.data.objects['Complete_cliff_mass'];rock=stone.copy();rock.name='G4_dark_coastal_rock'
    ramp=next(q for q in rock.node_tree.nodes if q.type=='VALTORGB');ramp.color_ramp.elements[0].color=(.055,.070,.074,1);ramp.color_ramp.elements[1].color=(.16,.19,.19,1)
    assign(cliff,rock);group=cliff.vertex_groups.new(name='G4_relief_below_foundation')
    for v in cliff.data.vertices:group.add([v.index],max(0,min(1,(-v.co.z-.8)/3)), 'REPLACE')
    sub=cliff.modifiers.new('G4 controlled cliff tessellation','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;sub.render_levels=2
    tex=bpy.data.textures.new('G4_rock_form_noise',type='CLOUDS');tex.noise_scale=1.5;tex.noise_depth=2
    dis=cliff.modifiers.new('G4 constrained rock relief','DISPLACE');dis.texture=tex;dis.strength=.65;dis.mid_level=.5;dis.vertex_group=group.name;dis.texture_coords='GLOBAL'
    ocean=material('G4_rainy_ocean',(.022,.046,.060),rough=.23)
    n=ocean.node_tree.nodes;l=ocean.node_tree.links;p=n.get('Principled BSDF');p.inputs['IOR'].default_value=1.333
    tc=n.new('ShaderNodeTexCoord');sc=n.new('ShaderNodeVectorMath');sc.operation='MULTIPLY';sc.inputs[1].default_value=(.15,.65,.12)
    no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=1;no.inputs['Detail'].default_value=3
    bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.38;bu.inputs['Distance'].default_value=.18
    l.new(tc.outputs['Object'],sc.inputs[0]);l.new(sc.outputs[0],no.inputs[0]);l.new(no.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs[0],p.inputs['Normal'])
    assign(bpy.data.objects['Ocean_extent'],ocean)
    # Soft cloud-sky environmental illumination is distinct from all supported interior fixtures.
    ob=area('G4_overcast_environment',(0,-12,38),(0,2,-1),6500,40,(.56,.68,.85));report['new_lights'].append(ob.name)
    ob['g4_role']='Environmental cloud-sky source for full exterior, not a hidden interior studio card'
    # Explicit physical masonry arch edging, derived from each actual saved intrados polygon.
    for arch in [o for o in s.objects if o.name.startswith('Viaduct_arch_spandrel')]:
        assert len(arch.data.vertices)==54
        for offset in [0,27]:
            pts=[arch.matrix_world@arch.data.vertices[i].co for i in range(offset+2,offset+27)]
            centerline=sum(pts,Vector())/len(pts)
            curve('G4_viaduct_arch_edge_course',[tuple(p) for p in pts],.105,stone)
        if not any(m.type=='BEVEL' for m in arch.modifiers):
            b=arch.modifiers.new('G4 stone arris radius','BEVEL');b.width=.027;b.segments=2
    bpy.context.view_layer.update()
    # Original topology coordinates and sampled transforms/camera lenses survive the expansion.
    report['protected_geometry_before']=g_before;report['protected_geometry_after']=geometry_signature(protected)
    report['protected_motion_before']=motion_before;report['protected_motion_after']=motion_signature(protected)
    assert report['protected_geometry_before']==report['protected_geometry_after'],'Unapproved source vertex-coordinate mutation'
    assert report['protected_motion_before']==report['protected_motion_after'],'Original spatial/animation/camera state changed'
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    report['remaining_original_WB_objects']=[o.name for o in s.objects if o.type in ['MESH','CURVE'] and not o.hide_render and any(m and m.name.startswith('WB_') for m in o.data.materials)]
    report['coverage_limits']=['First full-scene candidate; artwork requires actual native review.',
      'G3 retained craft concerns must be judged from new D02, not just UV code.',
      'Bridge V-shaped chord junction remains a dedicated final construction-review item; edge courses are not a claim it is repaired.',
      'Ocean uses native surface bump, not fluid simulation; final animated rain and 4K films are later stages.',
      'No new web runtime; administrator browser gate unchanged.']
    # Lamp list supports exact neutral/night comparison in later fresh processes.
    s['g4_night_lights']=json.dumps(json.loads(s['g3_night_lights'])+report['new_lights'])
    for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
    bg=s.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.10,.145,.22,1);bg.inputs['Strength'].default_value=.18
    s['phase']='G4_FULL_SCENE_CHALLENGER';s['g4_revision']='R01 verified-source extension';s['g4_user_stage_exception']=True
    s['g4_parent_sha256']=EXPECTED;s['g3_acceptance']='NOT_PASSED_USER_AUTHORIZED_CONTINUATION'
    s.frame_set(451);s.camera=bpy.data.objects['C01_exterior_hero']
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==EXPECTED
    report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
    report['original_geometry_objects_protected']=len(protected);report['source_master_unchanged']=True
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('G4_R01_SAVED_NOT_ART_PASS',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g4-full-scene-candidate.blend';build=json.loads((OUT/'build-report.json').read_text());expected=build['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')=='R01 verified-source extension'
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.045;s.cycles.adaptive_min_samples=16
    night=json.loads(s['g4_night_lights']);powers={n:bpy.data.objects[n].data.energy for n in night};neutral=json.loads(s['g3_neutral_lights']);bg=s.world.node_tree.nodes['Background']
    jobs=[('C01_exterior_hero','C01-full-night.png','night',48,(1440,900)),('C03_hall_to_platform','C03-hall-night.png','night',48,(1440,900))] if MODE=='overview' else [
      ('C09_car_aisle_failure_check','C09-car-aisle-night.png','night',48,(1280,800)),
      ('G3R03_complete_bay','G3-bay-context-night.png','night',64,(1440,900)),
      ('G3_D02','D02-woodwork-night.png','night',64,(1280,800)),
      ('C02_reverse_exterior','C02-reverse-night.png','night',48,(1280,800)),
      ('C05_along_platform','C05-platform-night.png','night',48,(1280,800)),
      ('C03_hall_to_platform','C03-hall-neutral.png','neutral',40,(1280,800)),
      ('G3R03_roof_node','D01-roof-node-regression.png','night',64,(1280,800))]
    metrics=[] if MODE=='overview' else json.loads((OUT/'render-metrics.json').read_text())
    for cam,name,lighting,samples,res in jobs:
        assert time.time()<float(os.environ['G4_DEADLINE']),'Bounded G4 production time reached'
        for n,p in neutral.items():bpy.data.objects[n].data.energy=p if lighting=='neutral' else 0
        for n,p in powers.items():bpy.data.objects[n].data.energy=p if lighting=='night' else 0
        bg.inputs['Color'].default_value=(.16,.19,.23,1) if lighting=='neutral' else (.10,.145,.22,1)
        bg.inputs['Strength'].default_value=.65 if lighting=='neutral' else .18
        assert s.view_settings.exposure==0
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451)
        row.update(lighting=lighting,native_render=True,master_sha256=expected,revision='G4_R01')
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('G4_NATIVE_VIEW_SAVED',name,flush=True)
    assert sha(master)==expected
    (OUT/('overview-reopen-check.json' if MODE=='overview' else 'reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
