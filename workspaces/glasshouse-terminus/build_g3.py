"""G3-R01: finish the existing hall/platform bay; keep the complete G2 world.
Requires the exact reviewed master. Reuses native helpers and selected CC0 models.
This is a candidate, NOT full-scene final art and NOT a final acceptance script.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,pbr,cube,cylinder,curve,lathe,mesh,camera,area,save

ROOT=Path('workspaces/glasshouse-terminus/output/g3').resolve()
ROOT.mkdir(parents=True,exist_ok=True)
PARENT=Path('workspaces/glasshouse-terminus/output/g2-review/g2-complete-whitebox.blend').resolve()
EXPECTED='0468b615b2d6ebeab7d641ad70c97a3efd62c7f31d1009fbc245c3c9b0f5c8be'
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
assert Path(bpy.data.filepath).resolve()==PARENT
assert bpy.app.version[:2]==(4,5),bpy.app.version_string
s=bpy.context.scene
assert s.get('phase')=='G2_WHITEBOX_NOT_FINAL_ART'
for name in ['A_complete_glasshouse','B_cafe_and_waiting_proxies','A_botanical_volume_proxies','D_complete_enterable_train','C_platform_canopy']:
    assert bpy.data.collections.get(name),name
for name in ['Train_motion_root','Train_door_left','Train_door_right','FILM_04_CONTINUOUS_WALK','C03_hall_to_platform','Hall_continuous_floor','Platform_continuous_slab']:
    assert bpy.data.objects.get(name),name
s.frame_set(451);bpy.context.view_layer.update()
FLOOR=1.15

def bounds(ob):
    pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]
def center(ob):
    a,b=bounds(ob);return [(x+y)/2 for x,y in zip(a,b)]
def new_collection(name):
    c=bpy.data.collections.new(name);s.collection.children.link(c);return c
C=new_collection('G3_finished_hall_platform_bay')
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]

# Read actual geometry/animation BEFORE editing. Stop on unexpected master layout.
recon={'blender':bpy.app.version_string,'parent_sha256':EXPECTED,'stage':'G3_CANDIDATE',
       'bounds':{},'replacements':[],'materials_reused':'G1 processed Poly Haven walnut/slate maps',
       'scope':'One existing x=-4..0 bay, selected cafe set, plant and door interface. Remaining world stays whitebox.',
       'browser':'BLOCKED_UNCHANGED','human_acceptance':False}
for name in ['Hall_continuous_floor','Platform_continuous_slab','Car_door_threshold','Train_door_left','Train_door_right']:
    o=bpy.data.objects[name];recon['bounds'][name]={'location':list(o.location),'world':list(o.matrix_world.translation),'bounds':bounds(o) if o.type=='MESH' else None}
assert abs(bounds(bpy.data.objects['Hall_continuous_floor'])[1][2]-FLOOR)<.001
assert (bpy.data.objects['Train_motion_root'].location-Vector((2,12.1,0))).length<.001
(ROOT/'preflight.json').write_text(json.dumps(recon,indent=2))

# Identify only the known proxy families by actual position, not generated suffixes.
replace=[]
for ob in list(bpy.data.collections['B_cafe_and_waiting_proxies'].objects):
    p=center(ob)
    if ob.name.startswith(('Cafe_table_','Cafe_chair_','Chair_leg_')) and abs(p[0]+3.15)<.35:replace.append(ob)
    if ob.name.startswith('Cafe_sideboard_proxy') and abs(p[0]+3.7)<.1:replace.append(ob)
assert len(replace)==16,[(o.name,center(o)) for o in replace]
plants=[(-14,-5.3),(-8,-5.3),(-2,-5.3),(4,-5.3),(10,-5.3),(14,-5.3),(-.53,5.2),(-7.2,5.15),(5,5.1),(13,5.1)]
plant_replace=[]
for ob in bpy.data.collections['A_botanical_volume_proxies'].objects:
    p=center(ob);nearest=min(plants,key=lambda xy:(xy[0]-p[0])**2+(xy[1]-p[1])**2)
    if nearest==(-.53,5.2):plant_replace.append(ob)
assert len(plant_replace)>=6
replace+=plant_replace
recon['replacements']=[o.name for o in replace]
protected=[o.name for o in s.objects if o not in replace]

def signature():
    h=hashlib.sha256()
    s.frame_set(451);bpy.context.view_layer.update()
    for n in sorted(protected):
        o=bpy.data.objects[n];h.update(n.encode());h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
    return h.hexdigest()
prior_signature=signature()
for ob in replace:bpy.data.objects.remove(ob,do_unlink=True)

# Physically distinct finishes; no glow/DOF/fog used to disguise interfaces.
metal=material('G3_bottle_green_enamel',(.023,.064,.052),metal=.42,rough=.27,coat=.28)
brass=material('G3_satin_aged_brass',(.36,.235,.102),metal=.82,rough=.29)
rubber=material('G3_EPDM_seal',(.018,.021,.019),rough=.72)
steel=material('G3_brushed_steel',(.31,.34,.35),metal=.86,rough=.31)
ceramic=material('G3_warm_porcelain',(.73,.70,.62),rough=.19,coat=.36)
coffee=material('G3_coffee',(.025,.012,.007),rough=.13)
felt=material('G3_dark_felt',(.035,.046,.039),rough=.87)
glass=material('G3_clear_6mm_glass',(.96,.985,.975),rough=.024,transmission=1)
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
wetglass=glass.copy();wetglass.name='G3_exterior_rivulet_glass'
n=wetglass.node_tree.nodes;l=wetglass.node_tree.links
geo=n.new('ShaderNodeNewGeometry');mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(45,45,.8)
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.001
l.new(geo.outputs['Position'],mul.inputs[0]);l.new(mul.outputs['Vector'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
ASSETS=Path('workspaces/glasshouse-terminus/output/g1/assets').resolve()
for file in ['manifest.json','FINISH-RECIPES.json','american_walnut_veneer_finished_diff_2k.jpg','slate_floor_finished_diff_2k.jpg']:
    assert (ASSETS/file).is_file(),file
for file in ['manifest.json','FINISH-RECIPES.json','DERIVATION.txt']:
    if (ASSETS/file).exists():(ROOT/('G1-'+file)).write_bytes((ASSETS/file).read_bytes())

def mapped_pbr(name,asset,axes,repeat=1,coat=0):
    m=pbr(name,asset,ASSETS,normal_strength=.20,coat=coat);nodes=m.node_tree.nodes;links=m.node_tree.links
    nodes['diff'].image=bpy.data.images.load(str(ASSETS/(asset+'_finished_diff_2k.jpg')),check_existing=True)
    g=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');comb=nodes.new('ShaderNodeCombineXYZ')
    links.new(g.outputs['Position'],sep.inputs[0])
    for dst,src in zip(['X','Y'],axes):links.new(sep.outputs[src],comb.inputs[dst])
    scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=repeat
    links.new(comb.outputs[0],scale.inputs[0])
    for role in ['diff','rough','nor_gl']:links.new(scale.outputs[0],nodes[role].inputs['Vector'])
    return m
wood=mapped_pbr('G3_walnut_top_grain_XY','american_walnut_veneer',['X','Y'],.75,.28)
woodfront=mapped_pbr('G3_walnut_cabinet_vertical_grain','american_walnut_veneer',['Y','Z'],.8,.23)
woodedge=mapped_pbr('G3_walnut_edge_grain','american_walnut_veneer',['X','Z'],1,.2)
stone=mapped_pbr('G3_slate_dry','slate_floor',['X','Y'],.5)
wetstone=stone.copy();wetstone.name='G3_slate_exposed_edge_wet'
p=wetstone.node_tree.nodes.get('Principled BSDF')
for lk in list(p.inputs['Roughness'].links):wetstone.node_tree.links.remove(lk)
p.inputs['Roughness'].default_value=.19;p.inputs['Coat Weight'].default_value=.28

def apply(ob,mat):
    assert ob.type in {'MESH','CURVE'}
    ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(mat);ob['g3_finish']=mat.name
# Finish only existing bay parts; geometry and locations are not changed.
for name in ['A_complete_glasshouse','C_platform_canopy','D_complete_enterable_train']:
    for ob in list(bpy.data.collections[name].objects):
        if ob.type not in {'MESH','CURVE'}:continue
        p=center(ob)
        is_door=ob.parent and ob.parent.name.startswith('Train_door_')
        if not is_door and not (-4.10<=p[0]<=.10):continue
        if name=='A_complete_glasshouse' and p[1]<0:continue
        old=ob.active_material.name if ob.active_material else ''
        if 'glass' in old.lower():chosen=wetglass if p[1]>=6.49 and not is_door else glass
        elif 'stone' in old.lower():chosen=stone
        elif 'interior' in old.lower():chosen=woodfront
        elif 'dark' in old.lower():chosen=rubber
        elif 'secondary' in old.lower():chosen=brass
        else:chosen=metal
        apply(ob,chosen)

# Scope the existing continuous floor's surface finish without moving its collider.
def finish_floor(ob,finished,ymin,ymax):
    m=finished.copy();m.name='G3_scoped_'+ob.name;n=m.node_tree.nodes;l=m.node_tree.links
    p=n.get('Principled BSDF');out=n.get('Material Output');old=ob.active_material.node_tree.nodes.get('Principled BSDF')
    base=n.new('ShaderNodeBsdfPrincipled')
    for key in ['Base Color','Metallic','Roughness']:base.inputs[key].default_value=old.inputs[key].default_value
    g=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(g.outputs['Position'],sep.inputs[0])
    masks=[]
    for axis,op,value in [('X','GREATER_THAN',-4.10),('X','LESS_THAN',.10),('Y','GREATER_THAN',ymin),('Y','LESS_THAN',ymax)]:
        q=n.new('ShaderNodeMath');q.operation=op;q.inputs[1].default_value=value;l.new(sep.outputs[axis],q.inputs[0]);masks.append(q.outputs[0])
    fac=masks[0]
    for b in masks[1:]:
        q=n.new('ShaderNodeMath');q.operation='MULTIPLY';l.new(fac,q.inputs[0]);l.new(b,q.inputs[1]);fac=q.outputs[0]
    mix=n.new('ShaderNodeMixShader');l.new(fac,mix.inputs[0]);l.new(base.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
    apply(ob,m)
finish_floor(bpy.data.objects['Hall_continuous_floor'],stone,.0,6.65)
finish_floor(bpy.data.objects['Platform_continuous_slab'],wetstone,9.85,10.70)

# Gaskets/pressure caps follow the ACTUAL glazing polygons, including curves.
for ob in list(bpy.data.collections['A_complete_glasshouse'].objects):
    if ob.type!='MESH' or not ob.name.startswith(('Curved_roof_glazing','Side_wall_glass')):continue
    p=center(ob)
    if not (-4.05<p[0]<.05 and p[1]>=0):continue
    counts={}
    for face in ob.data.polygons:
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1
    for (a,b),count in counts.items():
        if count!=1:continue
        pa=ob.matrix_world@ob.data.vertices[a].co;pb=ob.matrix_world@ob.data.vertices[b].co
        curve('G3_glazing_compression_gasket',[tuple(pa),tuple(pb)],.006,rubber)
    if ob.name.startswith('Side_wall_glass'):
        a,b=bounds(ob)
        for z in [a[2]+.13,b[2]-.13]:
            for x in [a[0]+.035,b[0]-.035]:
                cube('G3_glass_retaining_clip',(x,6.476,z),(.060,.028,.055),brass,.004)
                cylinder('G3_clip_slotted_fastener',(x,6.462,z),(x,6.451,z),.0085,steel,12)
for x in [-4,0]:
    for dx in [-.15,.15]:
        for dy in [-.15,.15]:
            cylinder('G3_column_anchor_bolt',(x+dx,6.5+dy,1.295),(x+dx,6.5+dy,1.332),.015,brass,6)
    cube('G3_column_cap_plate',(x,6.47,4.84),(.40,.045,.18),metal,.008)
    for dx in [-.14,.14]:cylinder('G3_cap_rivet',(x+dx,6.44,4.84),(x+dx,6.417,4.84),.013,brass,16)
for side in ['left','right']:
    root=bpy.data.objects['Hall_door_'+side];sgn=1 if side=='left' else -1
    for z in [.27,1.45,2.61]:
        ob=cylinder('G3_hall_hinge_barrel',(0,-.045,z-.055),(0,-.045,z+.055),.025,brass,24);ob.parent=root
    ob=curve('G3_hall_pull_handle',[(sgn*1.03,-.07,1.12),(sgn*1.03,-.13,1.12),(sgn*1.03,-.13,1.45),(sgn*1.03,-.07,1.45)],.013,brass);ob.parent=root
for i in range(21):cube('G3_drain_grate',(-4+i*.2,7.05,1.158),(.055,.105,.012),steel,.003)

# Original designed joinery from the existing lathe/curve helpers.
x,y=-3.15,3.3
profile=[(0,.734),(.49,.734),(.55,.739),(.58,.749),(.586,.761),(.586,.783),(.578,.794),(0,.794)]
lathe('G3_walnut_cafe_top',profile,(x,y,FLOOR),wood,128)
lathe('G3_table_edge_inlay',[(.581,.761),(.589,.761),(.589,.768),(.581,.768)],(x,y,FLOOR),brass,128)
lathe('G3_turned_pedestal',[(.16,.08),(.16,.12),(.115,.15),(.09,.24),(.07,.44),(.10,.59),(.135,.66),(.135,.729)],(x,y,FLOOR),woodedge,80)
for i in range(3):
    a=2*pi*i/3+.2
    pts=[(x+r*cos(a),y+r*sin(a),FLOOR+z) for r,z in [(.07,.25),(.17,.18),(.28,.07),(.41,.045)]]
    curve('G3_carved_pedestal_foot',pts,.032,woodedge)
    cylinder('G3_foot_felt_contact',(pts[-1][0],pts[-1][1],FLOOR+.003),(pts[-1][0],pts[-1][1],FLOOR+.02),.047,felt)
cx,cy=-3.70,4.65
cube('G3_sideboard_carcass',(cx,cy,FLOOR+.56),(.48,1.42,.99),woodfront,.012)
cube('G3_sideboard_top',(cx+.015,cy,FLOOR+1.079),(.53,1.48,.06),wood,.014)
for yy in [cy-.69,cy+.69]:cube('G3_cabinet_stile',(cx+.256,yy,FLOOR+.57),(.035,.046,.94),woodfront,.005)
for zz in [.11,1.025]:cube('G3_cabinet_rail',(cx+.257,cy,FLOOR+zz),(.035,1.39,.055),woodedge,.005)
for yy in [cy-.345,cy+.345]:
    cube('G3_cabinet_recessed_panel',(cx+.247,yy,FLOOR+.56),(.028,.60,.81),woodfront,.006)
    for z in [.22,.90]:cube('G3_panel_border',(cx+.268,yy,FLOOR+z),(.013,.55,.017),brass,.002)
    cylinder('G3_cabinet_pull_mount',(cx+.273,yy+.22,FLOOR+.67),(cx+.30,yy+.22,FLOOR+.67),.016,brass)
    cylinder('G3_cabinet_pull',(cx+.315,yy+.22,FLOOR+.60),(cx+.315,yy+.22,FLOOR+.74),.011,brass)
for yy in [cy-.54,cy+.54]:
    for xx in [cx-.17,cx+.17]:cylinder('G3_cabinet_foot',(xx,yy,FLOOR+.004),(xx,yy,FLOOR+.14),.035,woodedge,24)
ux,uy=x+.20,y-.12;z=FLOOR+.797
lathe('G3_porcelain_saucer',[(0,0),(.048,0),(.081,.004),(.086,.010),(.079,.015),(.046,.012),(0,.008)],(ux,uy,z),ceramic,96)
lathe('G3_porcelain_cup',[(0,.013),(.026,.013),(.036,.022),(.042,.075),(.042,.090),(.038,.092),(.035,.084),(.030,.026),(0,.023)],(ux,uy,z),ceramic,96)
cylinder('G3_coffee_meniscus',(ux,uy,z+.078),(ux,uy,z+.079),.035,coffee,96)
curve('G3_cup_handle',[(ux+.037+.027*sin(a),uy,z+.057+.025*cos(a)) for a in [pi*i/24 for i in range(25)]],.005,ceramic)
lx,ly,lz=cx,cy+.26,FLOOR+1.11
lathe('G3_lamp_base',[(0,0),(.105,0),(.115,.018),(.090,.04),(.025,.06)],(lx,ly,lz),brass)
cylinder('G3_lamp_stem',(lx,ly,lz+.04),(lx,ly,lz+.34),.015,brass)
shade=material('G3_ivory_lamp_shade',(.63,.59,.48),rough=.58)
shade.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.07
lathe('G3_lamp_shade',[(.18,.31),(.18,.318),(.105,.52),(.10,.52),(.175,.318)],(lx,ly,lz),shade,96)
emit=material('G3_warm_lamp_diffuser',(.95,.79,.56),rough=.5,emission=2.8)
cylinder('G3_lamp_diffuser',(lx,ly,lz+.325),(lx,ly,lz+.33),.161,emit,64)

# Mature assets: inspect actual imported geometry, normalize metres, preserve UVs.
models=json.loads((ROOT/'models/MODEL-SOURCES.json').read_text())
recon['imported_assets']=[]
def import_asset(asset_id,location,height,forward=None):
    rec=next(a for a in models['assets'] if a['asset_id']==asset_id)
    path=(ROOT/'models'/rec['entry']).resolve();assert path.is_file()
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    imported=list(set(bpy.data.objects)-before);meshes=[o for o in imported if o.type=='MESH'];assert meshes
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
    scale=height/(hi.z-lo.z);assert .2<hi.z-lo.z<3.0,(asset_id,list(lo),list(hi))
    mid=(lo+hi)/2;shift=Vector((-mid.x,-mid.y,-lo.z));yaw=0
    if forward is not None:
        upper=[p for p in pts if p.z>lo.z+(hi.z-lo.z)*.72]
        back=sum(upper,Vector())/len(upper)-mid;back.z=0
        assert back.length>.015,'Cannot infer chair facing; inspect upstream axes'
        want=-Vector((forward[0],forward[1],0));yaw=math.atan2(want.y,want.x)-math.atan2(back.y,back.x)
    transform=Matrix.Translation(Vector(location))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(shift)
    for o in imported:
        if o.parent not in imported:o.matrix_world=transform@o.matrix_world
        for c in list(o.users_collection):c.objects.unlink(o)
        C.objects.link(o);o['source_asset']=asset_id;o['source_license']='CC0-1.0'
    bpy.context.view_layer.update()
    recon['imported_assets'].append({'asset':asset_id,'source_dimensions':list(hi-lo),'scale':scale,'yaw':yaw,'placement':list(location),'mesh_names':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials if m})})
    return imported
import_asset('GreenChair_01',(-3.15,2.16,FLOOR),1.10,(0,1))
import_asset('GreenChair_01',(-3.15,4.40,FLOOR),1.10,(0,-1))
import_asset('potted_plant_01',(-.53,5.2,FLOOR),1.55)
bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[C.name]

# Sliding guides follow door X, while plug motion stays on the moving leaf.
train=bpy.data.objects['Train_motion_root']
for xx in [-4.70,-3.30]:
    ob=cube('G3_door_jamb_cover',(xx,-1.424,2.28),(.11,.105,2.29),metal,.014);ob.parent=train
    ob=curve('G3_door_jamb_gasket',[(xx,-1.483,1.19),(xx,-1.483,3.32)],.011,rubber);ob.parent=train
ob=cube('G3_door_track_housing',(-4,-1.43,3.40),(2.95,.17,.145),metal,.015);ob.parent=train
for zz in [3.36,3.435]:
    ob=curve('G3_slide_guide_rail',[(-5.39,-1.533,zz),(-2.61,-1.533,zz)],.012,steel);ob.parent=train
for side in ['left','right']:
    dr=bpy.data.objects['Train_door_'+side]
    carriage=bpy.data.objects.new('G3_guide_carriage_'+side,None);C.objects.link(carriage);carriage.parent=train
    carriage.location=(dr.location.x,-1.43,FLOOR)
    driver=carriage.driver_add('location',0).driver;var=driver.variables.new();var.name='door_x';var.type='SINGLE_PROP';var.targets[0].id=dr;var.targets[0].data_path='location[0]';driver.expression='door_x'
    for xx in [-.21,.21]:
        ob=cube('G3_door_roller_bracket',(xx,-.047,2.20),(.053,.160,.09),steel,.006);ob.parent=dr
        ob=cylinder('G3_door_carriage_roller',(xx,-.12,2.247),(xx,-.08,2.247),.031,rubber,32);ob.parent=carriage
    ob=cube('G3_door_lower_kickplate',(0,-.044,.20),(.51,.012,.24),steel,.006);ob.parent=dr
    for xx in [-.215,.215]:
        for zz in [.115,.285]:
            ob=cylinder('G3_kickplate_fastener',(xx,-.05,zz),(xx,-.054,zz),.006,brass,12);ob.parent=dr
for i in range(7):
    ob=cube('G3_threshold_traction_groove',(-4,-1.49+i*.036,1.151),(1.27,.005,.002),rubber,.0005);ob.parent=train

original_lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('QA_')]
recon['neutral_lights']={o.name:o.data.energy for o in original_lights}
night=[]
night.append(area('G3_night_sky',(-4,12,13),(-2,4,2),950,12,(.42,.53,.68)))
night.append(area('G3_interior_softbox',(-2,1.0,5.6),(-2.7,4.7,1.7),420,4.0,(1,.83,.63)))
night.append(area('G3_window_rim',(-6,8,5),(-3.3,4,2.1),300,3,(.60,.72,.90)))
night.append(area('G3_cafe_practical',(lx,ly,lz+.322),(lx,ly,FLOOR+1.05),9,.28,(1,.78,.51)))
night.append(area('G3_door_practical',(-2,11.9,3.66),(-2,9,1.5),65,1.0,(1,.85,.69)))
cylinder('G3_pendant_drop',(-3,3.25,5+5.1*math.sin(pi/3)),(-3,3.25,4.4),.012,brass)
lathe('G3_pendant_shade',[(.26,0),(.26,.025),(.13,.19),(.045,.23)],(-3,3.25,4.38),metal,96)
cylinder('G3_pendant_diffuser',(-3,3.25,4.388),(-3,3.25,4.398),.238,emit,64)
night.append(area('G3_pendant_light',(-3,3.25,4.37),(-3,3.25,1.15),130,.47,(1,.85,.65)))
camera('G3_bay',(.30,.25,2.70),(-2.28,5.6,2.40),42)
camera('G3_D01',(-1.9,4.50,3.10),(-3.86,6.48,3.50),60)
camera('G3_D02',(-1.60,1.85,2.65),(-3.13,3.35,1.97),60)
camera('G3_D03',(-1.65,.55,2.08),(-3.15,2.17,1.83),62)
camera('G3_D05',(-.8,8.50,2.50),(-2,10.72,2.25),43)
camera('G3_reverse',(-2.2,8.8,3.05),(-2.5,3.45,2.00),39)
camera('G3_D06',(.45,3.36,2.40),(-.53,5.2,2.00),62)
assert signature()==prior_signature,'Protected geometry, camera or frame-451 transforms changed'
recon['protected_geometry_signature_before']=prior_signature;recon['protected_geometry_signature_after']=signature()
recon['night_lights']=[o.name for o in night]
recon['g3_cameras']=[o.name for o in s.objects if o.type=='CAMERA' and o.name.startswith('G3_')]
recon['detail_geometry']='Reused common helpers for original joinery/hardware; imported selected CC0 chair and plant; no whole-scene substitution'
(ROOT/'build-report.json').write_text(json.dumps(recon,indent=2))
s['g3_neutral_lights']=json.dumps(recon['neutral_lights']);s['g3_night_lights']=json.dumps(recon['night_lights'])
s['g3_parent_sha256']=EXPECTED;s['phase']='G3_SAMPLE_NOT_FINAL_SCENE';s['g3_scope']='x=-4..0 hall/platform bay; all other areas retain G2 level'
for ob in bpy.data.collections['QA_scale_and_route'].objects:ob.hide_render=True;ob.hide_viewport=True
for ob in original_lights:ob.data.energy=0
bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.10,.145,.22,1);bg.inputs['Strength'].default_value=.18
s.camera=bpy.data.objects['G3_bay'];s.cycles.samples=64;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
s.cycles.transparent_max_bounces=12;s.cycles.use_denoising=True
s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100
s.view_settings.exposure=0;s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast';s.frame_set(451)
s.camera=bpy.data.objects['G3_bay']
save(s,ROOT/'g3-bay-candidate.blend')
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==EXPECTED
recon['candidate_sha256']=hashlib.sha256((ROOT/'g3-bay-candidate.blend').read_bytes()).hexdigest()
(ROOT/'build-report.json').write_text(json.dumps(recon,indent=2))
print('G3_BAY_CANDIDATE_SAVED_NOT_ACCEPTED',recon['candidate_sha256'])
