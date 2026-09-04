"""Complete G2 whitebox. Never call this final art.
All A-E geometry exists together. Building 32 x 13 m; rail-head z=.04,
platform/car floor z=1.15; 16 m original single carriage. Source fps=30.
"""
import bpy, bmesh, os, sys, math, random, json
from pathlib import Path
from contextlib import contextmanager
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import *

OUT=Path('workspaces/glasshouse-terminus/output/g2').resolve();OUT.mkdir(parents=True,exist_ok=True)
s=reset();world(s,(.62,.64,.67),.65)
mat={
 'structure':material('WB_structure',(.63,.64,.61),rough=.62),
 'secondary':material('WB_secondary',(.50,.53,.51),rough=.66),
 'glass':material('WB_glass',(.95,.98,.98),rough=.06,transmission=1),
 'stone':material('WB_stone',(.48,.49,.47),rough=.76),
 'cliff':material('WB_cliff',(.26,.29,.30),rough=.87),
 'train':material('WB_train_shell',(.71,.70,.65),rough=.48),
 'dark':material('WB_underframe',(.17,.20,.21),metal=.25,rough=.55),
 'interior':material('WB_interior',(.57,.55,.48),rough=.71),
 'plants':material('WB_plant_proxy',(.36,.43,.36),rough=.8),
 'proxy':material('QA_human_scale',(.51,.36,.23),rough=.65),
 'route':material('QA_walk_route',(.10,.30,.36),rough=.55),
 'light':material('WB_lamp',(.94,.91,.81),rough=.3,emission=2),
 'sea':material('WB_sea',(.14,.19,.22),metal=.18,rough=.33)
}
FLOOR=1.15;TRACK_Y=12.1;STOP=2.0;RAIL_C=.7515

@contextmanager
def component(name):
    before=set(bpy.data.objects)
    yield
    coll=bpy.data.collections.new(name);s.collection.children.link(coll)
    for ob in set(bpy.data.objects)-before:
        for c in list(ob.users_collection):c.objects.unlink(ob)
        coll.objects.link(ob);ob['component']=name


def thin_panel(name,verts,material_,thickness=.008):
    ob=mesh(name,verts,[tuple(range(len(verts)))],material_)
    m=ob.modifiers.new('Real surface thickness','SOLIDIFY');m.thickness=thickness
    return ob


def rail_pos(distance):
    if distance>=-24:return Vector((distance,TRACK_Y,0))
    a=(-24-distance)/50
    return Vector((-24-50*sin(a),TRACK_Y+50*(1-cos(a)),0))


def rail_tangent(distance):
    return (rail_pos(distance+.02)-rail_pos(distance-.02)).normalized()


def rail_offset(distance,offset,z):
    p=rail_pos(distance);t=rail_tangent(distance);n=Vector((-t.y,t.x,0))
    p+=n*offset;p.z=z;return tuple(p)

with component('E_cliff_foundation'):
    # A genuine closed rugged cliff, including unseen back and seabed intersection.
    rng=random.Random(23);n=40;verts=[]
    radial=[1+rng.uniform(-.06,.06) for _ in range(n)]
    for layer,(z,scale) in enumerate([(-23,1.06),(-16,1.09),(-7,1.00),(-.65,.94)]):
        for i in range(n):
            a=2*pi*i/n;r=radial[i]
            verts.append((-1+27*scale*r*cos(a),-2.5+21*scale*r*sin(a),z+(rng.uniform(-.65,.65) if layer<3 else 0)))
    faces=[]
    for j in range(3):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple(3*n+i for i in range(n))])
    mesh('Complete_cliff_mass',verts,faces,mat['cliff'])
    cube('Load_bearing_masonry_terrace',(0,3.4,-.35),(36,24,.65),mat['stone'],.15)
    cube('Hall_plinth',(0,0,.40),(32.6,13.6,1.12),mat['stone'],.06)
    cube('Hall_continuous_floor',(0,0,1.065),(32.3,13.25,.17),mat['stone'],.018)
    cube('Platform_continuous_slab',(0,8.575,.50),(34.4,4.15,1.30),mat['stone'],.015)
    cube('Platform_coping_edge',(0,10.57,1.13),(34.4,.16,.04),mat['structure'],.009)
    cube('Platform_drain_channel',(0,7.05,1.154),(33.8,.11,.018),mat['dark'])
    for x in range(-17,18,2):
        for y in [-8.8,15.0]:
            cylinder('Terrace_guard_post',(x,y,.0),(x,y,1.12),.043,mat['secondary'])
    for y in [-8.8,15.0]:
        for z in [.4,.72,1.10]:curve('Terrace_guard_rail',[(-17,y,z),(17,y,z)],.035,mat['secondary'])
    # Dry land-side entry stair reaches the hall, not an isolated floating room.
    for i in range(7):cube('Hall_entry_step',(16.4+i*.31,0,.08+i*.153),(.34,3.1,.16),mat['stone'],.008)
    cube('Ocean_extent',(0,0,-22.2),(1600,1600,.1),mat['sea'])

with component('E_curved_viaduct_and_track'):
    # Stone arch bridge along the same centreline used by the train.
    for a in range(-70,-19,10):
        b=a+10;p=rail_pos(a);q=rail_pos(b);mid=(p+q)/2
        tangent=(q-p).normalized();normal=Vector((-tangent.y,tangent.x,0));span=(q-p).length
        profile=[(-span/2,-.31),(span/2,-.31)]
        for j in range(25):
            theta=j*pi/24;profile.append((span/2*cos(theta),-7.2+5.9*sin(theta)))
        verts=[]
        for off in [-1.85,1.85]:
            for x,z in profile:
                v=mid+tangent*x+normal*off;v.z=z;verts.append(tuple(v))
        k=len(profile);faces=[tuple(reversed(range(k))),tuple(range(k,2*k))]
        faces += [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
        mesh('Viaduct_arch_spandrel',verts,faces,mat['stone'])
        for at in [a,b]:
            pt=rail_pos(at);post=cube('Viaduct_pier',(pt.x,pt.y,-14.8),(1.55,4.0,17.0),mat['stone'],.06)
            post.rotation_euler.z=math.atan2(tangent.y,tangent.x)
            foot=cube('Viaduct_bedrock_footing',(pt.x,pt.y,-22.6),(2.9,5.2,1.1),mat['stone'],.08)
            foot.rotation_euler.z=post.rotation_euler.z
    path=[rail_offset(-72+i*.25,0,-.34) for i in range(361)]
    sweep('Continuous_bridge_trackbed',path,[(-1.8,-.19),(1.8,-.19),(1.8,.02),(-1.8,.02)],mat['stone'],frame='Z')
    rail_profile=[(-.074,-.12),(.074,-.12),(.074,-.099),(.009,-.099),(.009,-.001),(.034,-.001),(.034,.04),(-.034,.04),(-.034,-.001),(-.009,-.001),(-.009,-.099),(-.074,-.099)]
    for side in [-1,1]:
        path=[rail_offset(-72+i*.25,side*RAIL_C,0) for i in range(361)]
        sweep('Running_rail',path,rail_profile,mat['dark'],frame='Z')
    for i in range(151):
        d=-72+i*.6;p=rail_pos(d);t=rail_tangent(d)
        ob=cube('Track_sleeper',(p.x,p.y,-.22),(.22,2.35,.20),mat['interior'],.015)
        ob.rotation_euler.z=math.atan2(t.y,t.x)
        if d<-19 and i%3==0:
            for side in [-1,1]:
                p=Vector(rail_offset(d,side*1.65,-.31));cylinder('Bridge_guard_post',p,p+Vector((0,0,1.12)),.032,mat['secondary'])
    for side in [-1,1]:
        for z in [.20,.73]:curve('Bridge_continuous_guard',[rail_offset(-72+i*.5,side*1.65,z) for i in range(107)],.028,mat['secondary'])
    cube('Buffer_stop_crossbar',(17.4,TRACK_Y,.68),(.22,2.2,.20),mat['dark'],.05)
    for y in [TRACK_Y-.7,TRACK_Y+.7]:cylinder('Buffer_stop_brace',(17.2,y,.1),(17.4,y,.7),.10,mat['dark'])

with component('A_complete_glasshouse'):
    primary=ibeam_profile(.20,.32,.024,.016)
    secondary=[(-.043,-.033),(.043,-.033),(.043,-.019),(.007,-.019),(.007,.032),(-.007,.032),(-.007,-.019),(-.043,-.019)]
    for x in range(-16,17):
        is_primary=x%4==0
        path=[(x,6.5*cos(j*pi/72),5.0+5.10*sin(j*pi/72)) for j in range(73)]
        sweep('Primary_elliptical_arch' if is_primary else 'Secondary_glazing_rib',path,primary if is_primary else secondary,mat['structure'] if is_primary else mat['secondary'])
        for y in [-6.5,6.5]:
            if is_primary:
                sweep('Load_column',[(x,y,FLOOR),(x,y,5.0)],ibeam_profile(.24,.32,.025,.017),mat['structure'])
                cube('Column_base_plinth',(x,y,FLOOR+.07),(.48,.48,.14),mat['stone'],.035)
                cube('Column_capital',(x,y,4.92),(.42,.44,.18),mat['structure'],.012)
            else:cube('Wall_glazing_mullion',(x,y,3.05),(.061,.076,3.62),mat['secondary'],.003)
    for j in range(13):
        a=j*pi/12;y=6.5*cos(a);z=5.0+5.1*sin(a)
        cube('Longitudinal_roof_purlin',(0,y,z),(32.18,.075,.085),mat['secondary'],.005)
    for x in range(-16,16):
        for j in range(12):
            verts=[]
            for xx in [x+.045,x+.955]:
                for k in range(5):
                    a=(j+(k/4)*.95+.025)*pi/12
                    verts.append((xx,6.507*cos(a),5.0+5.107*sin(a)))
            ob=mesh('Curved_roof_glazing',verts,[(k,k+1,k+6,k+5) for k in range(4)],mat['glass'])
            sol=ob.modifiers.new('Glass thickness 6mm','SOLIDIFY');sol.thickness=.006
    # Complete long walls, with a genuine clear portal in the selected G3 bay.
    for side in [-1,1]:
        y=side*6.5
        for x in range(-16,16):
            portal=side==1 and -3.3<x+.5<-.7
            if not portal:
                cube('Wall_stone_sill',(x+.5,y,FLOOR+.18),(.99,.20,.36),mat['stone'],.009)
            for z,h in [(2.43,1.80),(4.15,1.38)]:
                if portal and z<3:continue
                thin_panel('Side_wall_glass',[(x+.04,y,z-h/2),(x+.96,y,z-h/2),(x+.96,y,z+h/2),(x+.04,y,z+h/2)],mat['glass'])
            for z in [FLOOR+.38,3.37,4.92]:
                if portal and z<3:continue
                cube('Wall_transom',(x+.5,y,z),(1.02,.08,.065),mat['secondary'],.003)
        cube('Continuous_eaves_gutter',(0,y,5.02),(32.55,.25,.18),mat['structure'],.018)
        for x in [-15.8,15.8]:
            curve('Downpipe',[(x,y,4.99),(x,y+side*.21,4.75),(x,y+side*.21,FLOOR+.1)],.055,mat['secondary'])
    # Both end elevations fit the same ellipse. Entry opening in the positive-X end.
    for x in [-16.03,16.03]:
        for j in range(10):
            y0=-6.5+j*1.3;y1=y0+1.3;yc=(y0+y1)/2
            top=5.0+5.1*math.sqrt(max(0,1-(max(abs(y0),abs(y1))/6.5)**2))
            lo=FLOOR+.38
            if x>0 and abs(yc)<1.31:lo=4.0
            thin_panel('End_wall_glazing',[(x,y0+.035,lo),(x,y1-.035,lo),(x,y1-.035,top-.035),(x,y0+.035,top-.035)],mat['glass'])
            cube('End_wall_mullion',(x,y0,(FLOOR+top)/2),(.09,.07,top-FLOOR),mat['secondary'],.003)
            if not(x>0 and abs(yc)<1.31):cube('End_wall_sill',(x,yc,FLOOR+.18),(.22,1.29,.36),mat['stone'],.008)
        for z in [3.96,5.0]:cube('End_elevation_crossbar',(x,0,z),(.12,13.0,.085),mat['structure'],.006)
    # Roof lantern establishes a readable crown, not an unrelated tower.
    for x in range(-12,13,2):
        for y in [-.65,.65]:cube('Ridge_vent_stanchion',(x,y,10.34),(.05,.05,.36),mat['secondary'])
    cube('Ridge_vent_cap',(0,0,10.56),(24.4,1.65,.12),mat['structure'],.035)
    # Platform portal: source frames and physically swung leafs leave the path clear.
    for x in [-3.28,-.72]:cube('Platform_portal_jamb',(x,6.47,2.70),(.15,.19,3.10),mat['structure'],.013)
    cube('Platform_portal_lintel',(-2,6.47,4.22),(2.71,.21,.15),mat['structure'],.015)
    for side,hinge in [('left',-3.2),('right',-.8)]:
        root=bpy.data.objects.new('Hall_door_'+side,None);bpy.context.collection.objects.link(root);root.location=(hinge,6.49,FLOOR)
        sign=1 if side=='left' else -1
        before=set(bpy.data.objects)
        for xx in [0,sign*1.2]:cube('Hall_door_stile',(xx,0,1.45),(.06,.064,2.90),mat['structure'],.005)
        for z in [.03,1.05,2.87]:cube('Hall_door_rail',(sign*.6,0,z),(1.23,.064,.075),mat['structure'],.005)
        thin_panel('Hall_door_glass',[(sign*.04,0,1.09),(sign*1.16,0,1.09),(sign*1.16,0,2.83),(sign*.04,0,2.83)],mat['glass'])
        cube('Hall_door_kickpanel',(sign*.6,0,.53),(1.12,.058,.96),mat['interior'],.008)
        for ob in set(bpy.data.objects)-before:ob.parent=root
        root.rotation_euler.z=sign*math.radians(83)

with component('C_platform_canopy'):
    # A covered dry route bridges the hall portal and train doors.
    for x in [-16,-12,-8,-4,0,4,8,12,16]:
        cube('Platform_canopy_beam',(x,8.64,4.65),(.09,4.45,.17),mat['structure'],.008)
        cylinder('Canopy_tension_brace',(x,6.55,5.18),(x,10.62,4.58),.024,mat['secondary'])
    for j in range(4):
        y0=6.6+j*1.03;y1=y0+1.00
        thin_panel('Platform_canopy_glass',[(-16,y0,4.73), (16,y0,4.73),(16,y1,4.70),(-16,y1,4.70)],mat['glass'])
    cube('Canopy_edge_fascia',(0,10.72,4.63),(32.4,.16,.22),mat['structure'],.01)

with component('B_cafe_and_waiting_proxies'):
    # Full-room placement before small prop detail. The selected final-quality bay is x in [-4,0].
    for x,y in [(-3.15,3.3),(-10.2,3.3),(7.4,3.2)]:
        cylinder('Cafe_table_top',(x,y,FLOOR+.73),(x,y,FLOOR+.79),.58,mat['interior'],48)
        cylinder('Cafe_table_pedestal',(x,y,FLOOR+.03),(x,y,FLOOR+.73),.075,mat['secondary'])
        cylinder('Cafe_table_foot',(x,y,FLOOR+.02),(x,y,FLOOR+.06),.30,mat['secondary'],32)
        for yy in [y-1.02,y+1.02]:
            cube('Cafe_chair_seat_proxy',(x,yy,FLOOR+.45),(.60,.60,.12),mat['interior'],.055)
            back=cube('Cafe_chair_back_proxy',(x,yy+(.27 if yy>y else -.27),FLOOR+.79),(.61,.12,.62),mat['interior'],.06)
            for dx in [-.23,.23]:
                for dy in [-.23,.23]:cylinder('Chair_leg_proxy',(x+dx,yy+dy,FLOOR),(x+dx,yy+dy,FLOOR+.40),.028,mat['secondary'])
    cube('Cafe_sideboard_proxy',(-3.7,4.55,FLOOR+.52),(.47,1.45,1.04),mat['interior'],.025)
    for x in [-11,-5,5,11]:
        y=-3.65
        cube('Waiting_bench_cushion_proxy',(x,y,FLOOR+.46),(2.4,.69,.17),mat['interior'],.065)
        cube('Waiting_bench_back_proxy',(x,y-.30,FLOOR+.85),(2.4,.16,.78),mat['interior'],.065)
        for dx in [-.86,.86]:cube('Waiting_bench_support',(x+dx,y,FLOOR+.20),(.09,.59,.4),mat['secondary'],.018)

with component('A_botanical_volume_proxies'):
    for idx,(x,y) in enumerate([(-14,-5.3),(-8,-5.3),(-2,-5.3),(4,-5.3),(10,-5.3),(14,-5.3),(-.53,5.2),(-7.2,5.15),(5,5.1),(13,5.1)]):
        cylinder('Plant_container_proxy',(x,y,FLOOR),(x,y,FLOOR+.62),.42,mat['stone'],24,radius2=.49)
        for j in range(5):
            a=j*2.399+idx;top=(x+.21*cos(a),y+.21*sin(a),FLOOR+1.5+.2*(j%3))
            cylinder('Plant_stem_proxy',(x,y,FLOOR+.58),top,.018,mat['plants'],10)
            leaf('Botanical_blade_proxy',top,(cos(a),sin(a),.37),1.15,.31,mat['plants'])

# Carriage geometry is authored in local coordinates, then all motion follows actual rail samples.
train_root=bpy.data.objects.new('Train_motion_root',None);s.collection.objects.link(train_root)
bogies=[];axles=[];doors=[]
with component('D_complete_enterable_train'):
    before_train=set(bpy.data.objects)
    cube('Car_underframe',(0,0,.87),(14.70,2.46,.30),mat['dark'],.055)
    cube('Car_floor',(0,0,1.10),(14.75,2.58,.10),mat['interior'],.01)
    edges=[-7.25,-5.45,-4.66,-3.34,-1.60,.15,1.90,3.65,5.40,7.25]
    for side in [-1,1]:
        for k in range(len(edges)-1):
            a,b=edges[k:k+2];is_door=side==-1 and abs(a+4.66)<.01
            if not is_door:
                verts=[]
                for xx in [a,b]:
                    for z,y in [(.98,1.22),(1.23,1.34),(1.82,1.40),(2.04,1.385)]:verts.append((xx,side*y,z))
                ob=mesh('Car_curved_lower_shell',verts,[(j,j+1,j+5,j+4) for j in range(3)],mat['train'])
                sol=ob.modifiers.new('Sheet thickness','SOLIDIFY');sol.thickness=.06
                thin_panel('Car_side_window',[(a+.07,side*1.381,2.10),(b-.07,side*1.381,2.10),(b-.07,side*1.35,3.30),(a+.07,side*1.35,3.30)],mat['glass'])
                for z in [2.065,3.34]:cube('Car_window_horizontal_frame',((a+b)/2,side*1.39,z),(b-a,.075,.07),mat['secondary'],.01)
            for xx in [a,b]:cube('Car_window_pillar',(xx,side*1.365,2.69),(.080,.095,1.36),mat['train'],.016)
        cube('Car_waist_trim',(0,side*1.40,2.02),(14.55,.039,.034),mat['secondary'],.009)
        # The near waist trim is split at the actual door; no invisible bar across the opening.
        if side==-1:
            bpy.data.objects.remove(bpy.context.object,do_unlink=True)
            for a,b in [(-7.25,-4.67),(-3.33,7.25)]:cube('Car_split_waist_trim',((a+b)/2,-1.40,2.02),(b-a,.039,.034),mat['secondary'],.009)
    verts=[]
    for x in [-7.25,7.25]:
        for j in range(49):
            a=-pi/2+j*pi/48;verts.append((x,1.39*sin(a),3.35+.72*cos(a)))
    roof=mesh('Car_complete_barrel_roof',verts,[(j,j+1,j+50,j+49) for j in range(48)],mat['train'])
    sol=roof.modifiers.new('Roof shell thickness','SOLIDIFY');sol.thickness=.065
    # Rounded end cabins, with true front and rear glass rather than capped empty boxes.
    for sign in [-1,1]:
        for side in [-1,1]:
            thin_panel('Cab_cheek',[(sign*7.25,side*1.39,1.08),(sign*8.0,side*1.10,1.12),(sign*8.0,side*1.10,2.06),(sign*7.25,side*1.385,2.06)],mat['train'],.06)
            thin_panel('Cab_side_glass',[(sign*7.30,side*1.375,2.13),(sign*7.92,side*1.115,2.13),(sign*7.90,side*1.10,3.18),(sign*7.30,side*1.345,3.28)],mat['glass'])
        points=[]
        for j in range(25):
            y=-1.10+2.2*j/24;x=sign*(8.07-.15*(y/1.1)**2);points.append((x,y))
        for z0,z1,role in [(1.10,2.10,'train'),(2.13,3.19,'glass'),(3.23,3.56,'train')]:
            vv=[(x,y,z) for z in [z0,z1] for x,y in points]
            ob=mesh('Cab_front_glass' if role=='glass' else 'Cab_front_fairing',vv,[(j,j+1,j+26,j+25) for j in range(24)],mat[role])
            sol=ob.modifiers.new('Cab skin thickness','SOLIDIFY');sol.thickness=.012 if role=='glass' else .07
        thin_panel('Cab_roof_closure',[(sign*7.25,-1.39,3.36),(sign*8.01,-1.10,3.56),(sign*8.01,1.10,3.56),(sign*7.25,1.39,3.36)],mat['train'],.07)
        for z in [2.09,3.23]:curve('Cab_windscreen_surround',[(x,y,z) for x,y in points],.035,mat['secondary'])
        cube('Cab_windscreen_mullion',(sign*8.08,0,2.66),(.05,.07,1.15),mat['secondary'],.014)
        cube('Cab_floor_extension',(sign*7.62,0,1.10),(.76,2.22,.10),mat['interior'],.02)
        cube('Cab_buffer_beam',(sign*7.9,0,.85),(.27,2.32,.22),mat['dark'],.06)
        for y in [-.71,.71]:
            cylinder('Train_headlamp_housing',(sign*8.02,y,1.62),(sign*8.17,y,1.62),.16,mat['secondary'],32)
            cylinder('Train_headlamp_lens',(sign*8.17,y,1.62),(sign*8.185,y,1.62),.135,mat['light'],32)
    # Interior stays present in every view, including the reverse end and cab.
    for x in [-1.90,.05,2.0,3.95,5.90]:
        for side in [-1,1]:
            cube('Car_seat_base',(x,side*.88,FLOOR+.24),(.76,.79,.40),mat['interior'],.04)
            cube('Car_seat_cushion',(x+.03,side*.88,FLOOR+.49),(.84,.82,.16),mat['interior'],.07)
            ob=cube('Car_seat_back',(x-.35,side*.88,FLOOR+.94),(.17,.82,.91),mat['interior'],.075);ob.rotation_euler.y=math.radians(-8)
            for y in [side*.48,side*1.28]:curve('Car_armrest',[(x-.28,y,FLOOR+.74),(x+.38,y,FLOOR+.74)],.027,mat['secondary'])
    for side in [-1,1]:
        cube('Car_inner_wainscot',(0,side*1.295,1.70),(14.20,.053,.97),mat['interior'],.015)
        if side==-1:
            bpy.data.objects.remove(bpy.context.object,do_unlink=True)
            for a,b in [(-7.1,-4.67),(-3.33,7.1)]:cube('Car_split_wainscot',((a+b)/2,-1.295,1.70),(b-a,.053,.97),mat['interior'],.015)
        curve('Car_luggage_rail',[(-6.8,side*1.08,3.23),(6.8,side*1.08,3.23)],.029,mat['secondary'])
    cube('Cab_control_console',(7.18,0,1.85),(.55,1.55,.56),mat['dark'],.08)
    cube('Cab_driver_seat',(6.65,0,1.72),(.55,.58,.17),mat['interior'],.08)
    cube('Rear_luggage_bench',(-6.65,.80,1.50),(1.25,.85,.7),mat['interior'],.05)
    for x in [-6,-2,2,6]:cube('Car_ceiling_light',(x,0,3.93),(.75,.28,.04),mat['light'],.04)
    # Sliding door leafs are independent, with thickness, window, frames, and a flush threshold.
    cube('Car_door_threshold',(-4,-1.37,FLOOR-.018),(1.33,.32,.036),mat['secondary'],.008)
    for side,xc in [('left',-4.31),('right',-3.69)]:
        root=bpy.data.objects.new('Train_door_'+side,None);bpy.context.collection.objects.link(root);root.location=(xc,-1.43,FLOOR)
        before=set(bpy.data.objects)
        cube('Door_lower_panel',(0,0,.45),(.59,.074,.90),mat['train'],.025)
        for xx in [-.275,.275]:cube('Door_vertical_frame',(xx,0,1.09),(.050,.083,2.18),mat['secondary'],.009)
        for z in [.95,2.15]:cube('Door_cross_frame',(0,0,z),(.56,.084,.064),mat['secondary'],.008)
        thin_panel('Door_glazing',[(-.247,0,.99),(.247,0,.99),(.247,0,2.11),(-.247,0,2.11)],mat['glass'])
        curve('Door_handle',[(0,-.065,.84),(0,-.065,1.15)],.015,mat['secondary'])
        for ob in set(bpy.data.objects)-before:ob.parent=root
        root.parent=train_root;doors.append((root,xc,-1 if side=='left' else 1))
    for local_x in [-5.0,5.0]:
        bogie=bpy.data.objects.new('Bogie_rear' if local_x<0 else 'Bogie_front',None);bpy.context.collection.objects.link(bogie);bogie.parent=train_root
        before=set(bpy.data.objects)
        cube('Bogie_cross_frame',(0,0,.72),(2.72,1.65,.23),mat['dark'],.045)
        for side in [-1,1]:
            cube('Bogie_side_frame',(0,side*.91,.61),(2.76,.18,.22),mat['dark'],.05)
            for x in [-.43,.43]:cylinder('Primary_suspension',(x,side*.87,.49),(x,side*.87,.85),.11,mat['secondary'],16)
        for ob in set(bpy.data.objects)-before:ob.parent=bogie
        for axle_x in [-.91,.91]:
            axle=bpy.data.objects.new('Rolling_wheelset',None);bpy.context.collection.objects.link(axle);axle.parent=bogie;axle.location=(axle_x,0,.42)
            before=set(bpy.data.objects)
            cylinder('Axle',(0,-.82,0),(0,.82,0),.065,mat['dark'],20)
            for side in [-1,1]:
                cylinder('Wheel_tread',(0,side*RAIL_C-.062,0),(0,side*RAIL_C+.062,0),.38,mat['dark'],40)
                y=side*(RAIL_C-.058)
                cylinder('Wheel_flange',(0,y-.012,0),(0,y+.012,0),.412,mat['secondary'],40)
                cylinder('Wheel_hub',(0,side*(RAIL_C+.07)-.021,0),(0,side*(RAIL_C+.07)+.021,0),.13,mat['secondary'],24)
            for ob in set(bpy.data.objects)-before:ob.parent=axle
            axles.append(axle)
        bogies.append((bogie,local_x))
    for ob in set(bpy.data.objects)-before_train:
        if ob.parent is None:ob.parent=train_root

# Exact source motion. Bogies sample the curve separately; body follows their chord.
motion=[]
for frame in range(1,841):
    t=(frame-1)/30;u=min(1,max(0,t/10));distance=STOP-48*(1-u)**2
    rear=rail_pos(distance-5);front=rail_pos(distance+5);mid=(rear+front)/2
    yaw=math.atan2((front-rear).y,(front-rear).x)
    train_root.location=mid;train_root.rotation_euler=(0,0,yaw)
    train_root.keyframe_insert('location',frame=frame);train_root.keyframe_insert('rotation_euler',frame=frame)
    c=cos(yaw);sn=sin(yaw)
    for bogie,offset in bogies:
        p=rail_pos(distance+offset)-mid;tg=rail_tangent(distance+offset)
        bogie.location=(c*p.x+sn*p.y,-sn*p.x+c*p.y,0)
        bogie.rotation_euler.z=math.atan2(tg.y,tg.x)-yaw
        bogie.keyframe_insert('location',frame=frame);bogie.keyframe_insert('rotation_euler',frame=frame)
    for axle in axles:
        axle.rotation_euler.y=-(distance+46)/.38;axle.keyframe_insert('rotation_euler',frame=frame)
    opening=min(1,max(0,(t-10.45)/1.1));opening=opening*opening*(3-2*opening)
    for door,xc,side in doors:
        door.location=(xc+side*.65*opening,-1.43-.095*opening,FLOOR)
        door.keyframe_insert('location',frame=frame)
    if frame in [1,91,211,301,315,348,391,541,661,840]:
        motion.append({'frame':frame,'seconds':t,'track_distance':distance,'body_location':list(mid),'body_yaw':yaw,'door_open_fraction':opening})
s.frame_set(451)

with component('QA_scale_and_route'):
    # 1.75 m scale mannequins; hidden for film preview, retained for diagnostics.
    for x,y in [(-1.1,3.0),(-2,8.55),(9.4,9.3)]:
        cylinder('Human_scale_leg',(x-.09,y,FLOOR),(x-.09,y,FLOOR+.78),.07,mat['proxy'],12)
        cylinder('Human_scale_leg',(x+.09,y,FLOOR),(x+.09,y,FLOOR+.78),.07,mat['proxy'],12)
        cube('Human_scale_torso',(x,y,FLOOR+1.12),(.38,.23,.64),mat['proxy'],.09)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.12,location=(x,y,FLOOR+1.63));bpy.context.object.name='Human_scale_head';bpy.context.object.data.materials.append(mat['proxy'])
    route=[(-2,1.1,FLOOR+.045),(-2,5.75,FLOOR+.045),(-2,8.6,FLOOR+.045),(-2,TRACK_Y,FLOOR+.045),(1.0,TRACK_Y,FLOOR+.045)]
    ob=curve('QA_continuous_passenger_route',route,.034,mat['route']);ob['diagnostic_only']=True

# Lighting is neutral G2 diagnostic lighting, not a beauty claim.
area('QA_sky_key',(8,0,32),(0,0,0),22000,28,(1,1,1))
area('QA_front_fill',(10,28,18),(0,2,3),16000,24,(.89,.94,1))
area('QA_back_fill',(-20,-20,13),(0,0,3),13000,23,(1,.96,.89))
for x in [-10,0,10]:area('QA_interior_fill',(x,0,8),(x,0,1),950,5,(1,.97,.90))

cams={
 'C01':camera('C01_exterior_hero',(32,52,23),(-10,4,1.0),40),
 'C02':camera('C02_reverse_exterior',(-31,-38,20),(-2,0,2),43),
 'C03':camera('C03_hall_to_platform',(8,-4.5,3.0),(-2,6.5,2.7),35),
 'C04':camera('C04_platform_to_hall',(10,9.1,2.85),(-2,.5,3.8),32),
 'C05':camera('C05_along_platform',(-14,9.6,2.7),(5,11.35,2.55),43),
 'C06':camera('C06_car_to_hall',(-2,12.62,2.70),(-2,2.4,2.8),29),
 'C07':camera('C07_orthographic_plan',(-17,10,105),(-17,10,0),50,108),
 'C08':camera('C08_true_section',(-44,2.8,5.0),(-2,2.8,4.3),50,27),
 'C09':camera('C09_car_aisle_failure_check',(-3.0,TRACK_Y,2.7),(7.3,TRACK_Y,2.2),30)
}
# Five continuous source cameras; the walking shot does not cross walls or cut scenes.
film={
 'HERO':camera('FILM_01_HERO',(34,54,24),(-10,4,1),40),
 'DETAIL':camera('FILM_02_DETAIL',(-4.7,8.6,3.05),(-2.8,5.2,2.5),58),
 'ARRIVAL':camera('FILM_03_ARRIVAL',(-11,9.4,2.7),(-2,TRACK_Y,2.4),46),
 'WALK':camera('FILM_04_CONTINUOUS_WALK',(-2,1.1,2.76),(-2,8,2.73),36),
 'REVEAL':camera('FILM_05_REVEAL',(30,44,19),(-12,2,0),40)
}
walk_keys=[(13,(-2,1.1,2.76),(-2,8,2.73)),(15.5,(-2,5.55,2.76),(-2,11,2.75)),(18,(-2,10.92,2.76),(-2,13.0,2.75)),(19.3,(-2,12.1,2.76),(3.2,12.1,2.73)),(20.6,(-.2,12.1,2.76),(-2,9.0,2.9)),(22,(1.0,12.1,2.76),(-2,3.4,3.25))]

def mix(a,b,t):return tuple((1-t)*aa+t*bb for aa,bb in zip(a,b))
for frame in range(1,841):
    t=(frame-1)/30
    if t<3:
        cam=film['HERO'];f=t/3;pos=mix((34,54,24),(31,50,22.5),f);target=(-10,4,1)
    elif t<7:
        cam=film['DETAIL'];f=(t-3)/4;pos=mix((-4.7,8.6,3.05),(-4.35,8.4,2.98),f);target=(-2.8,5.2,2.5)
    elif t<13:
        cam=film['ARRIVAL'];f=(t-7)/6;pos=mix((-11,9.4,2.7),(-8.8,9.4,2.7),f);target=(-2,TRACK_Y,2.4)
    elif t<22:
        cam=film['WALK']
        for a,b in zip(walk_keys,walk_keys[1:]):
            if a[0]<=t<=b[0]:
                f=(t-a[0])/(b[0]-a[0]);pos=mix(a[1],b[1],f);target=mix(a[2],b[2],f);break
    else:
        cam=film['REVEAL'];f=(t-22)/6;pos=mix((30,44,19),(35,53,30),f);target=(-12,2,-.4)
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
for frame,key in [(1,'HERO'),(91,'DETAIL'),(211,'ARRIVAL'),(391,'WALK'),(661,'REVEAL')]:
    marker=s.timeline_markers.new('SHOT_'+key,frame=frame);marker.camera=film[key]
s.camera=film['HERO'];s.frame_set(1)
s['task']='glasshouse-terminus-premium-scene';s['phase']='G2_WHITEBOX_NOT_FINAL_ART'
s['layout']={'hall_length':32.0,'hall_width':13.0,'rail_head_z':.04,'platform_z':FLOOR,'car_floor_z':FLOOR,'platform_edge_y':10.65,'train_near_side_y':TRACK_Y-1.4,'door_world_x':-2.0,'car_length':16.14,'walking_shot_seconds':[13,22]}
# Keep original full geometry and camera motion before any section or diagnostic operation.
for ob in bpy.data.collections['QA_scale_and_route'].objects:ob.hide_render=True
s.render.resolution_x=1280;s.render.resolution_y=720;s.cycles.samples=24
save(s,OUT/'g2-complete-whitebox.blend')
(OUT/'motion-states.json').write_text(json.dumps(motion,indent=2))
(OUT/'layout-and-route.json').write_text(json.dumps({'layout':dict(s['layout']),'walk_keys':walk_keys,'clearance_design_metres':{'platform_to_train':TRACK_Y-1.4-10.65,'train_door_clear_width':1.20,'station_portal_clear_width':2.40,'aisle_width':.64},'note':'Design parameters are not automatic visual acceptance. Check the actual C01-C09 frames and continuous walking shot.'},indent=2))

# Fixed observation set, no camera substitutions to hide defects.
metrics=[]
s.timeline_markers.clear();s.frame_set(451)
for ob in bpy.data.collections['QA_scale_and_route'].objects:ob.hide_render=False
for key in ['C01','C02','C03','C04','C05','C06','C07','C09']:
    metrics.append(render(s,cams[key],OUT/(key+'.png'),res=(1280,800),samples=24,frame=451))
# Actual bisection in a disposable in-memory diagnostic; saved master remains complete.
for ob in bpy.data.collections['QA_scale_and_route'].objects:ob.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
for ob in list(s.objects):
    if ob.type=='CURVE':ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
for ob in list(s.objects):
    if ob.type!='MESH' or ob.name.startswith('Ocean'):continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    plane=ob.matrix_world.inverted()@Vector((-2,0,0))
    normal=(ob.matrix_world.to_3x3().transposed()@Vector((1,0,0))).normalized()
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=plane,plane_no=normal,clear_inner=True,dist=.0001)
    bm.to_mesh(ob.data);bm.free();ob.data.update()
metrics.append(render(s,cams['C08'],OUT/'C08.png',res=(1280,800),samples=24,frame=451))
(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
manifest(OUT,{'phase':'G2','status':'WHITEBOX_REVIEW_PENDING','not_final_art':True,'source_complete':'g2-complete-whitebox.blend','section_is_disposable_diagnostic':True,'views':['C01','C02','C03','C04','C05','C06','C07','C08','C09'],'animatic':'render_animatic.py must reopen master in a new process'})
