"""G1 technical risk bay. Not the G2 whole scene or G3 final-quality sample."""
import sys, os, math, random, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import *

out=Path('workspaces/glasshouse-terminus/output/g1').resolve();out.mkdir(parents=True,exist_ok=True)
assets=out/'assets'
s=reset();s.frame_end=48
m={
 'iron':material('Enamel_bottle_green',(.028,.072,.059),metal=.55,rough=.28,coat=.35),
 'brass':material('Satin_brass',(.38,.25,.105),metal=.82,rough=.29),
 'rubber':material('Black_glazing_gasket',(.012,.017,.016),rough=.73),
 'glass':material('Clear_8mm_glass',(.96,.988,.98),rough=.035,transmission=1),
 'water':material('Adhered_rain_water',(.99,.995,1),rough=.018,transmission=1),
 'ceramic':material('Muted_cream_ceramic',(.58,.55,.45),rough=.29,coat=.3),
 'soil':material('Plant_soil',(.045,.031,.023),rough=.94),
 'leaf':material('Strelitzia_leaf',(.055,.16,.074),rough=.4,coat=.28),
 'vein':material('Leaf_rib',(.12,.21,.07),rough=.53),
 'stone_edge':material('Honed_threshold',(.21,.24,.255),rough=.43),
 'cloth':material('Woven_moss_fabric',(.105,.15,.105),rough=.77),
 'light':material('Warm_opal',(.95,.85,.68),rough=.25,emission=2),
}
m['wood']=pbr('Walnut_veneer_finished','american_walnut_veneer',assets,coat=.33,normal_strength=.14)
m['dry']=pbr('Dry_slate','slate_floor',assets,normal_strength=.22)
m['wet']=pbr('Wet_slate','slate_floor',assets,roughness_path=assets/'slate_wet_rough_2k.jpg',normal_strength=.12,coat=.65)

# Genuine separate dry and wet regions with a flush threshold and drainage slot.
for label,y0,y1,mat in [('dry',-3.2,-.16,m['dry']),('wet',.16,3.6,m['wet'])]:
    mesh('Floor_'+label,[(-2.35,y0,0),(2.35,y0,0),(2.35,y1,0),(-2.35,y1,0)],[(0,1,2,3)],mat,
         [(-2.35/2.3,y0/2.3),(2.35/2.3,y0/2.3),(2.35/2.3,y1/2.3),(-2.35/2.3,y1/2.3)])
    cube('Floor_substrate_'+label,(0,(y0+y1)/2,-.12),(4.7,y1-y0,.23),m['stone_edge'],.015)
cube('Threshold',(0,0,.025),(4.7,.28,.05),m['stone_edge'],.008)
cube('Drain_recess',(0,.39,.009),(4.6,.12,.016),m['rubber'])
for i in range(77):cube('Drain_bridge',(i*.06-2.28,.39,.023),(.025,.14,.025),m['iron'],.003)

# Frame has a broad visible flange, narrow web, rear flange and glazing gasket.
for x in [-1.8,-.6,.6,1.8]:
    cube('Mullion_front_flange',(x,.057,1.84),(.12,.026,3.6),m['iron'],.003)
    cube('Mullion_web',(x,-.007,1.84),(.024,.11,3.6),m['iron'],.002)
    cube('Mullion_rear_flange',(x,-.067,1.84),(.10,.023,3.6),m['iron'],.003)
    for z in [.32,1.82,3.32]:
        for dx in [-.038,.038]:
            cylinder('Frame_fastener',(x+dx,.073,z),(x+dx,.084,z),.010,m['brass'],16)
for z in [.10,1.75,3.59]:
    cube('Transom_flange',(0,.052,z),(3.72,.038,.092),m['iron'],.004)
    cube('Transom_web',(0,-.008,z),(3.72,.10,.022),m['iron'],.002)
for x in [-1.2,0,1.2]:
    for z,h in [(.94,1.52),(2.68,1.68)]:
        cube('EPDM_bedding',(x,-.001,z),(1.112,.015,h+.025),m['rubber'],.004)
        # Bedding is a rim, not an opaque panel. Replace the temporary centre by four seals.
        ob=bpy.context.object;bpy.data.objects.remove(ob,do_unlink=True)
        for dx in [-.553,.553]:cube('Glass_vertical_seal',(x+dx,-.002,z),(.018,.019,h+.02),m['rubber'],.003)
        for dz in [-h/2,h/2]:cube('Glass_horizontal_seal',(x,-.002,z+dz),(1.12,.019,.018),m['rubber'],.003)
        cube('Glazing_panel_8mm',(x,.004,z),(1.09,.008,h-.016),m['glass'],.0015)
# Head flashing, weather drip and dry-side structural member.
cube('Head_flashing',(0,-.03,3.66),(4.0,.38,.055),m['iron'],.008)
curve('Drip_edge',[(-2,.17,3.64),(2,.17,3.64)],.011,m['brass'])

# The wood coupon is intentionally simple geometry in this technical phase.
top=cube('Walnut_table_coupon',(-.65,-1.32,.88),(1.55,.78,.07),m['wood'],.025)
for poly in top.data.polygons:
    for li in poly.loop_indices:
        v=top.data.vertices[top.data.loops[li].vertex_index].co
        top.data.uv_layers.active.data[li].uv=(v.x+.8,v.y+.45) if abs(poly.normal.z)>.5 else (v.x+.8,v.z+.1)
for x in [-1.20,-.1]:
    for y in [-1.59,-1.05]:cylinder('Coupon_table_leg',(x,y,0),(x,y,.845),.036,m['iron'],24)
cube('Fabric_sample_pad',(-.7,-2.22,.51),(1.14,.58,.13),m['cloth'],.06)
cube('Seat_sample_base',(-.7,-2.22,.36),(1.20,.64,.15),m['wood'],.02)
for x in [-1.12,-.28]:
    for y in [-2.4,-2.05]:cylinder('Seat_test_leg',(x,y,0),(x,y,.31),.026,m['iron'])

# True ceramic rim and hollow cup used only to show contact/material contrast.
lathe('Saucer',[(0,.0),(.092,.0),(.12,.012),(.126,.020),(.123,.025),(.097,.018),(.052,.014),(0,.014)],(-.62,-1.27,.918),m['ceramic'])
lathe('Cup',[(.032,0),(.049,.008),(.059,.096),(.058,.105),(.053,.105),(.052,.096),(.043,.014),(.032,.01)],(-.62,-1.27,.939),m['ceramic'])
curve('Cup_handle',[(-.561,-1.27,.974),(-.519,-1.27,.969),(-.510,-1.27,1.003),(-.530,-1.27,1.023),(-.562,-1.27,1.022)],.007,m['ceramic'])
cylinder('Lamp_base',(-1.13,-1.4,.918),(-1.13,-1.4,.939),.09,m['brass'],48)
cylinder('Lamp_stem',(-1.13,-1.4,.939),(-1.13,-1.4,1.21),.012,m['brass'],24)
lathe('Lamp_shade',[(.125,0),(.145,.012),(.09,.22),(.087,.224),(.078,.214),(.134,.018)],(-1.13,-1.4,1.16),m['ceramic'])
lathe('Lamp_opal_bulb',[(0,0),(.04,.01),(.053,.045),(.04,.083),(0,.094)],(-1.13,-1.4,1.17),m['light'],32)

# Botanical laminae have actual curved surfaces, visible vein connections and soil contact.
lathe('Planter',[(.23,0),(.30,.03),(.34,.47),(.33,.51),(.30,.51),(.29,.47),(.23,.05)],(1.05,-.85,0),m['ceramic'])
cylinder('Soil',(1.05,-.85,.46),(1.05,-.85,.475),.29,m['soil'],48)
for i in range(8):
    a=i*2.399;z=.95+.15*(i%3);root=(1.05,-.85,.45)
    tip=(1.05+.19*cos(a),-.85+.19*sin(a),z)
    curve('Leaf_petiole',[root,((root[0]+tip[0])/2,(root[1]+tip[1])/2,z*.65),tip],.012,m['vein'])
    leaf('Leaf_blade',tip,(cos(a),sin(a),.5),.82+.07*(i%3),.21,m['leaf'],m['vein'])

# Physical exterior water droplets; no rain geometry is placed behind the dry-side glass.
rng=random.Random(71)
for i in range(70):
    x=rng.uniform(-1.73,1.73);z=rng.uniform(.18,3.52)
    if min(abs(x-c) for c in [-1.8,-.6,.6,1.8])<.065 or abs(z-1.75)<.06:continue
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(x,.012,z))
    ob=bpy.context.object;ob.name='Exterior_adhered_droplet';ob.scale=(.006+rng.random()*.011,.006,.012+rng.random()*.037);ob.data.materials.append(m['water'])
    for p in ob.data.polygons:p.use_smooth=True

# Moving reflection target: explicitly a risk-test proxy, not the train asset.
proxy=cube('MOVING_REFLECTION_TEST_PROXY',(-4.2,2.9,1.14),(1.6,.65,1.75),m['iron'],.15)
proxy['not_final_asset']=True
for f,x in [(1,-4.2),(24,-.4),(48,4.2)]:proxy.location.x=x;proxy.keyframe_insert('location',frame=f)
for fc in proxy.animation_data.action.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
head=cube('Proxy_light_strip',(0,-.332,.30),(1.05,.025,.12),m['light'],.04);head.parent=proxy
head.location=(0,-.332,.30)

warm=area('Interior_warm_softbox',(0,-2.3,4.2),(0,-.5,1),900,3.2,(1,.80,.60))
cool=area('Exterior_storm_softbox',(-3,3.7,5.6),(0,0,1.3),1600,4.0,(.62,.74,1))
area('Long_reflection_strip',(3.6,1.2,3.6),(0,0,2),360,1.2,(.87,.93,1),3.2)
cam=camera('G1_BEAUTY',(4.6,5.7,3.25),(0,-.66,1.63),52)
close=camera('G1_GLASS_NODE',(2.25,2.15,2.28),(.65,-.35,1.85),65)
inside=camera('G1_MATERIALS',(-2.45,-3.7,2.2),(-.05,-1.05,1.0),50)
records=[]
records.append(render(s,cam,out/'beauty.png',samples=40))
records.append(render(s,close,out/'glass-node.png',samples=48))
records.append(render(s,inside,out/'materials.png',samples=48))
# Fixed camera/exposure neutral diagnostic of the same geometry.
old=warm.data.color[:];warm.data.color=(1,1,1);world(s,(.6,.6,.6),.45)
records.append(render(s,cam,out/'neutral.png',samples=32))
warm.data.color=old;world(s,(.12,.16,.22),.5)
records.append(render(s,cam,out/'moving-reflection.png',samples=40,frame=32))
s.camera=cam;s.frame_set(1);s.cycles.samples=40
save(s,out/'g1-risk-study.blend')
# A small actual sequence measures time coherence; never call it the 28s film.
seq=out/'reflection-frames';seq.mkdir(exist_ok=True)
for f in range(1,49,2):records.append(render(s,cam,seq/f'{f:04d}.png',res=(640,400),samples=16,frame=f))
# Convert editable curves only in this export process; the saved source retains them.
s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for ob in list(s.objects):
    if ob.type=='CURVE':ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
export_glb(out/'g1-risk-study.glb',animations=False)
(out/'render-metrics.json').write_text(json.dumps(records,indent=2))
manifest(out,{'phase':'G1','status':'VISUAL_REVIEW_REQUIRED','not_final_scene':True,
    'scope':'wet glass, designed frame section, CC0 slate/walnut, physical botanical surfaces, moving reflection proxy',
    'references':'PRODUCTION-STATE.md','observations_pending':['glass transparency/reflection','material distinction','temporal stability','GLB browser adaptation']})
