"""R03 rain/material challenger on the verified R02 scene; no scene rebuild.
Native geometry, shaders and time-driven instances. Rain trajectories are clipped
against evaluated, render-visible R02 surfaces at parked frame451; not fluid sim.
"""
import bpy, json, math, os, sys, time, random, hashlib, shutil
from pathlib import Path
from array import array
from collections import Counter
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material, mesh, curve, camera, render, save
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-r02';OUT=ROOT/'output/g4-r03';OUT.mkdir(parents=True,exist_ok=True)
PARENT='173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc'
REV='R03 rain layers and close-range physical surface response'
MODE=os.environ['G4_RAIN_MODE'];assert MODE in ['build','hero','detail','motion']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]
def collection(name):
    c=bpy.data.collections.new(name);s.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
    return c

def protected(names):
    h=hashlib.sha256()
    for name in sorted(names):
        o=bpy.data.objects[name];h.update(repr((name,o.type,o.parent.name if o.parent else None,o.hide_render,
          getattr(o,'visible_camera',None),getattr(o,'visible_glossy',None),getattr(o,'visible_shadow',None),getattr(o,'visible_transmission',None))).encode())
        if o.type=='MESH':
            a=array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
            for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.use_smooth)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.type,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y)).encode())
        if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
    for frame in [1,301,348,451,510,660,840]:
        s.frame_set(frame);bpy.context.view_layer.update()
        for name in sorted(names):h.update(repr(tuple(tuple(r) for r in bpy.data.objects[name].matrix_world)).encode())
    s.frame_set(451);bpy.context.view_layer.update()
    h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode())
    return h.hexdigest()

def mathnode(n,l,op,a,b=None,name=None):
    q=n.new('ShaderNodeMath');q.operation=op
    if name:q.name=name
    for idx,value in enumerate([a,b]):
        if value is None:continue
        if isinstance(value,(int,float)):q.inputs[idx].default_value=value
        else:l.new(value,q.inputs[idx])
    return q.outputs[0]
def remap(n,l,source,lo,hi,name):
    q=n.new('ShaderNodeMapRange');q.name=name;q.clamp=True
    q.inputs['From Min'].default_value=0;q.inputs['From Max'].default_value=1
    q.inputs['To Min'].default_value=lo;q.inputs['To Max'].default_value=hi
    l.new(source,q.inputs['Value']);return q.outputs['Result']
def noise(n,l,vector,scale,detail=2,name='Finish microstructure'):
    q=n.new('ShaderNodeTexNoise');q.name=name;q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail
    l.new(vector,q.inputs['Vector']);return q.outputs['Fac']
def scaled(n,l,vector,factors):
    q=n.new('ShaderNodeVectorMath');q.operation='MULTIPLY';q.inputs[1].default_value=factors;l.new(vector,q.inputs[0]);return q.outputs[0]
def bump(n,l,height,normal,strength,distance,name):
    q=n.new('ShaderNodeBump');q.name=name;q.inputs['Strength'].default_value=strength;q.inputs['Distance'].default_value=distance
    l.new(height,q.inputs['Height'])
    if normal is not None:l.new(normal,q.inputs['Normal'])
    return q.outputs['Normal']

def replace_material(src,new):
    affected=[]
    for o in list(s.objects):
        if not hasattr(o.data,'materials'):continue
        if src not in list(o.data.materials):continue
        o.data=o.data.copy()
        for i,m in enumerate(o.data.materials):
            if m==src:o.data.materials[i]=new
        affected.append(o.name)
    return affected

def add_surface_finish(srcname,kind,report):
    src=bpy.data.materials[srcname];m=src.copy();m.name='G4R03_'+srcname
    n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF'];tc=n.new('ShaderNodeTexCoord');tc.name='R03 metre-scale finish coordinates'
    vector=tc.outputs['Object'];oldnormal=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
    if kind=='paint':
        p.inputs['Metallic'].default_value=0;p.inputs['IOR'].default_value=1.48
        p.inputs['Coat Weight'].default_value=.20;p.inputs['Coat Roughness'].default_value=.24
        micro=noise(n,l,vector,1050,2,'Submillimetre paint orange peel')
        l.new(remap(n,l,noise(n,l,vector,42),.27,.36,'Paint gloss tolerance'),p.inputs['Roughness'])
        l.new(bump(n,l,micro,oldnormal,.18,.000085,'Paint 85 micron finish'),p.inputs['Normal'])
    elif kind in ['brass','steel']:
        p.inputs['Metallic'].default_value=1;p.inputs['Anisotropic'].default_value=.32 if kind=='brass' else .48
        v=scaled(n,l,vector,(260,260,3.5));micro=noise(n,l,v,1,2,'Directional machined grain')
        l.new(remap(n,l,micro,.24,.35 if kind=='brass' else .39,'Brushed reflection spread'),p.inputs['Roughness'])
        l.new(bump(n,l,micro,oldnormal,.18,.000035,'Fine brushed metal relief'),p.inputs['Normal'])
    elif kind=='wood':
        t=n.get('diff');vector=t.inputs['Vector'].links[0].from_socket if t and t.inputs['Vector'].is_linked else tc.outputs['UV']
        rough=n.get('rough')
        if rough:l.new(remap(n,l,rough.outputs['Color'],.30,.48,'Finished timber roughness'),p.inputs['Roughness'])
        p.inputs['Coat Weight'].default_value=.22;p.inputs['Coat Roughness'].default_value=.23
        fine=noise(n,l,scaled(n,l,vector,(450,28,1)),1,2,'Along-grain fine wood pores')
        l.new(bump(n,l,fine,oldnormal,.18,.00009,'Wood pores under the finish'),p.inputs['Normal'])
        l.new(bump(n,l,fine,None,.07,.000025,'Thin varnish microfinish'),p.inputs['Coat Normal'])
    elif kind=='cloth':
        p.inputs['Roughness'].default_value=.70;p.inputs['Sheen Weight'].default_value=.32;p.inputs['Sheen Roughness'].default_value=.48
        sep=n.new('ShaderNodeSeparateXYZ');l.new(vector,sep.inputs[0]);waves=[]
        for axis in ['X','Y','Z']:
            w=mathnode(n,l,'SINE',mathnode(n,l,'MULTIPLY',sep.outputs[axis],2*math.pi/.0012))
            waves.append(mathnode(n,l,'MULTIPLY_ADD',w,.5));waves[-1].node.inputs[2].default_value=.5
        pairs=[mathnode(n,l,'MULTIPLY',waves[1],waves[2]),mathnode(n,l,'MULTIPLY',waves[0],waves[2]),mathnode(n,l,'MULTIPLY',waves[0],waves[1])]
        geom=n.new('ShaderNodeNewGeometry');ns=n.new('ShaderNodeSeparateXYZ');l.new(geom.outputs['Normal'],ns.inputs[0])
        weighted=[mathnode(n,l,'MULTIPLY',pairs[i],mathnode(n,l,'ABSOLUTE',ns.outputs[i])) for i in range(3)]
        height=mathnode(n,l,'ADD',mathnode(n,l,'ADD',weighted[0],weighted[1]),weighted[2])
        l.new(bump(n,l,height,None,.28,.00018,'1.2mm warp and weft relief'),p.inputs['Normal'])
        l.new(remap(n,l,noise(n,l,vector,70),.61,.77,'Woven fibre roughness'),p.inputs['Roughness'])
    elif kind=='rubber':
        l.new(bump(n,l,noise(n,l,vector,850),oldnormal,.18,.00012,'Rubber micrograin'),p.inputs['Normal'])
    report['material_edits'].append({'source':srcname,'candidate':m.name,'kind':kind,'objects':replace_material(src,m)})
    return m

def first_visible_hit(origin,direction,maxdistance):
    dg=bpy.context.evaluated_depsgraph_get();at=origin.copy();walk=0
    for _ in range(24):
        h,p,n,fi,o,mat=s.ray_cast(dg,at,direction,distance=maxdistance-walk)
        if not h:return None
        dist=(p-origin).length
        if not o.hide_render and o.visible_camera and not o.name.startswith('G4R03_'):return {'name':o.name,'point':p,'normal':n,'distance':dist}
        at=p+direction*.003;walk=dist+.003
        if walk>=maxdistance:return None
    raise RuntimeError('Rain shelter ray exceeded hidden-object skip bound')

def attribute(me,name,values,vector=False):
    a=me.attributes.new(name,'FLOAT_VECTOR' if vector else 'FLOAT','POINT')
    a.data.foreach_set('vector' if vector else 'value',[c for v in values for c in v] if vector else values)

def rain_instances(name,origins,travels,phases,speeds,scales,direction,water):
    ob=mesh(name,origins,[]);me=ob.data
    for label,values in [('travel',travels),('phase',phases),('speed',speeds),('size',scales)]:attribute(me,'rain_'+label,values)
    g=bpy.data.node_groups.new(name+'_native_time','GeometryNodeTree')
    g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n=g.nodes;l=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');tm=n.new('GeometryNodeInputSceneTime')
    attrs={}
    for label in ['travel','phase','speed','size']:
        q=n.new('GeometryNodeInputNamedAttribute');q.data_type='FLOAT';q.inputs['Name'].default_value='rain_'+label;attrs[label]=q.outputs['Attribute']
    t=mathnode(n,l,'MULTIPLY',tm.outputs['Seconds'],attrs['speed']);t=mathnode(n,l,'ADD',t,attrs['phase']);t=mathnode(n,l,'MODULO',t,attrs['travel'])
    vec=n.new('ShaderNodeVectorMath');vec.operation='SCALE';vec.inputs[0].default_value=direction;l.new(t,vec.inputs['Scale'])
    sp=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],sp.inputs['Geometry']);l.new(vec.outputs['Vector'],sp.inputs['Offset'])
    sphere=n.new('GeometryNodeMeshUVSphere');sphere.inputs['Segments'].default_value=8;sphere.inputs['Rings'].default_value=5;sphere.inputs['Radius'].default_value=1
    tr=n.new('GeometryNodeTransform');tr.inputs['Scale'].default_value=(.0028,.0028,.075)
    tr.inputs['Rotation'].default_value=Vector(direction).to_track_quat('Z','Y').to_euler();l.new(sphere.outputs['Mesh'],tr.inputs['Geometry'])
    sm=n.new('GeometryNodeSetMaterial');sm.inputs['Material'].default_value=water;l.new(tr.outputs['Geometry'],sm.inputs['Geometry'])
    inst=n.new('GeometryNodeInstanceOnPoints');l.new(sp.outputs['Geometry'],inst.inputs['Points']);l.new(sm.outputs['Geometry'],inst.inputs['Instance']);l.new(attrs['size'],inst.inputs['Scale']);l.new(inst.outputs['Instances'],out.inputs['Geometry'])
    mod=ob.modifiers.new('Native time and roof-clipped falling rain','NODES');mod.node_group=g
    return ob

if MODE=='build':
    parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
    assert s.get('g4_revision')=='R02 dry hall and continuous night-sky environment'
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    inv=json.loads((ROOT/'output/g4-rain-inventory/R02-rain-material-inventory.json').read_text())
    assert inv['parent_master_sha256']==PARENT and inv['source_master_unchanged']
    original_names=[o.name for o in s.objects];assert set(original_names)=={o['name'] for o in inv['objects']}
    before=protected(original_names);rng=random.Random(73191)
    report={'stage':'G4','revision':'R03','status':'CHALLENGER_NOT_ART_PASS','parent_master_sha256':PARENT,
      'parent_evidence_commit':'12ae1030686d97823548b2967805d85853d12ab2','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
      'material_edits':[],'rain':{},'surface_water':{},'cameras':[],'g4_stage_pass':False,'human_acceptance':False,
      'scope':'Actual rain and material response, no layout rebuild or source-camera/exposure changes. Not a claim of top-tier or full project completion.'}
    direction=Vector((-.06,.12,-1)).normalized();origins=[];travels=[];phases=[];speeds=[];scales=[];hits=Counter()
    for i in range(28000):
        at=Vector((rng.uniform(-24,23),rng.uniform(-13,23),rng.uniform(14.5,19))) if i<18000 else Vector((rng.uniform(-16,16),rng.uniform(-9.4,-6.7),8.5))
        hit=first_visible_hit(at,direction,45)
        if not hit:continue
        dist=hit['distance']-.17
        if dist<.3:continue
        origins.append(list(at));travels.append(dist);phases.append(rng.uniform(0,dist));speeds.append(rng.uniform(6.5,10.5));scales.append(rng.uniform(.62,1.20));hits[hit['name']]+=1
    assert len(origins)>12000
    eave=bpy.data.objects['Continuous_eaves_gutter'];elo,ehi=bounds(eave)
    negative_gutters=[o for o in s.objects if o.name.startswith('Continuous_eaves_gutter') and bounds(o)[1][1]<0]
    assert len(negative_gutters)==1;elo,ehi=bounds(negative_gutters[0]);assert abs(elo[1]+6.625)<.03
    drips=[]
    for i in range(170):
        at=Vector((rng.uniform(-15.6,15.6),elo[1]-.018,elo[2]-.025));d=Vector((0,0,-1))
        hit=first_visible_hit(at,d,35)
        if hit and hit['distance']>.3:drips.append((list(at),hit['distance']-.14,rng.random(),rng.uniform(2.0,4.5)))
    report['rain']={'native_instances':len(origins),'trajectory_first_hits':dict(hits),'direction':list(direction),'shelter_reference_frame':451,
      'shelter_method':'Evaluated render-visible geometry first hits; water/glass are solid rain blockers. Source trails end 17cm before hit to avoid penetration.',
      'limits':'Native animated optical streak instances with analytic periodic motion, not fluid simulation. Collision paths frozen at parked frame451; moving train rain interaction still needs a dynamic collider before full film.',
      'emission':0,'eave_drip_paths':len(drips)}
    for name in ['G3R05_satin_column_paint','G3R04_sage_green_secondary_enamel','G3_bottle_green_enamel','G4_train_graphite_roof']:add_surface_finish(name,'paint',report)
    for name,kind in [('G3_brushed_steel','steel'),('G3_satin_aged_brass','brass'),('G3_EPDM_seal','rubber'),('G4_moss_woven_upholstery','cloth')]:add_surface_finish(name,kind,report)
    for name in ['G3_walnut_top_grain_XY','G3_walnut_edge_grain','G4_walnut_metre_UV','G4_circumferential_edge_veneer','G4_train_wood_UV']:add_surface_finish(name,'wood',report)
    src=bpy.data.objects['Hall_continuous_floor'].active_material;floor=src.copy();floor.name='G4R03_honed_slate_with_cut_joints';n=floor.node_tree.nodes;l=floor.node_tree.links;p=n['Principled BSDF']
    geo=n.new('ShaderNodeNewGeometry');brick=n.new('ShaderNodeTexBrick');brick.name='1.2m by 0.6m cut slate joints';brick.offset=.5
    brick.inputs['Scale'].default_value=1;brick.inputs['Mortar Size'].default_value=.0025;brick.inputs['Mortar Smooth'].default_value=.003
    brick.inputs['Brick Width'].default_value=1.2;brick.inputs['Row Height'].default_value=.6
    brick.inputs['Color1'].default_value=(.88,.89,.87,1);brick.inputs['Color2'].default_value=(1,1,1,1);brick.inputs['Mortar'].default_value=(.23,.24,.23,1)
    l.new(geo.outputs['Position'],brick.inputs['Vector']);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
    l.new(n['diff'].outputs['Color'],mul.inputs[1]);l.new(brick.outputs['Color'],mul.inputs[2]);l.new(mul.outputs[0],p.inputs['Base Color'])
    old=p.inputs['Normal'].links[0].from_socket;bn=bump(n,l,brick.outputs['Fac'],old,.34,.0025,'Recessed cut-stone mortar');bn.node.invert=True;l.new(bn,p.inputs['Normal'])
    report['material_edits'].append({'source':src.name,'candidate':floor.name,'kind':'dry_stone_metre_joints','objects':replace_material(src,floor)})
    water=material('G4R03_actual_water',(.985,.993,1),rough=.035,transmission=1);water.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.333
    collection('G4R03_actual_rainfall')
    rain=rain_instances('G4R03_roof_clipped_rain',origins,travels,phases,speeds,scales,list(direction),water)
    assert drips
    rain_instances('G4R03_eave_drips',[v[0] for v in drips],[v[1] for v in drips],[v[2]*v[1] for v in drips],[v[3] for v in drips],[.55]*len(drips),(0,0,-1),water)
    collection('G4R03_glass_attached_water');verts=[];faces=[];bead_count=0;rivulets=0;bead_support=[]
    def cap(x,y,z,r,elong):
        base=len(verts);seg=12;rings=6
        for j in range(rings):
            a=(j/(rings-1))*(math.pi/2-.018);rr=math.cos(a)
            for k in range(seg):
                t=2*math.pi*k/seg;verts.append((x+r*rr*math.cos(t),y-r*.68*math.sin(a),z+r*elong*rr*math.sin(t)))
        for j in range(rings-1):
            for k in range(seg):a=base+j*seg+k;b=base+j*seg+(k+1)%seg;faces.append((a,b,b+seg,a+seg))
        faces.append(tuple(base+k for k in reversed(range(seg))));faces.append(tuple(base+(rings-1)*seg+k for k in range(seg)))
    panels=[o for o in s.objects if o.name.startswith('Side_wall_glass') and bounds(o)[0][1]<-6.4]
    for o in panels:
        lo,hi=bounds(o);area=(hi[0]-lo[0])*(hi[2]-lo[2]);dense=lo[0]>=-6 and hi[0]<=-2 and hi[2]<3.4
        count=int(area*(170 if dense else 28));count=max(12,count)
        for k in range(count):
            radius=rng.uniform(.0015,.0065) if dense else rng.uniform(.0018,.0048)
            cap(rng.uniform(lo[0]+.016,hi[0]-.016),lo[1]-.0006,rng.uniform(lo[2]+.025,hi[2]-.025),radius,rng.uniform(1.0,2.1));bead_count+=1
        for k in range(3 if dense else 1):
            x=rng.uniform(lo[0]+.09,hi[0]-.09);z=rng.uniform(lo[2]+.4,hi[2]-.06);length=rng.uniform(.16,.42)
            pts=[(x+.006*math.sin(j*.58+k),lo[1]-.0019,z-length*j/16) for j in range(17)]
            curve('G4R03_adherent_rivulet',pts,rng.uniform(.00065,.00125),water);rivulets+=1
        bead_support.append({'object':o.name,'bounds':[lo,hi],'beads':count,'windward':True})
    beadob=mesh('G4R03_convex_glass_water_beads',verts,faces,water,smooth=True)
    report['surface_water']={'convex_beads':bead_count,'rivulets':rivulets,'support':bead_support,'glass_objects_unchanged':True,
      'method':'3D convex water caps and narrow attached rivulets, different IOR from the 8mm source glass. No screen overlay or generative image.'}
    collection('G4R03_exterior_puddles');puddle_report=[]
    wetstone=bpy.data.objects['Load_bearing_masonry_terrace'].active_material.copy();wetstone.name='G4R03_damp_terrace_stone';n=wetstone.node_tree.nodes;l=wetstone.node_tree.links;p=n['Principled BSDF']
    geo=n.new('ShaderNodeNewGeometry');field=noise(n,l,geo.outputs['Position'],.75,3,'Patchy rain wetting')
    l.new(remap(n,l,field,.27,.58,'Rain-wetted stone roughness'),p.inputs['Roughness']);p.inputs['Coat Weight'].default_value=.22;p.inputs['Coat Roughness'].default_value=.16
    terrace=bpy.data.objects['Load_bearing_masonry_terrace'];terrace.data=terrace.data.copy();terrace.data.materials.clear();terrace.data.materials.append(wetstone)
    for i,(x,y,rx,ry) in enumerate([(-11,-7.8,.72,.24),(-5.3,-7.55,.70,.33),(-2,-7.8,.86,.28),(4.8,-7.6,.62,.34),(10.3,-7.5,.55,.24)]):
        hit=first_visible_hit(Vector((x,y,1)),Vector((0,0,-1)),3)
        assert hit and hit['name']=='Load_bearing_masonry_terrace',(x,y,hit['name'] if hit else None)
        z=hit['point'].z+.0016;vv=[(x,y,z)]
        for k in range(96):
            a=2*math.pi*k/96;edge=1+.10*math.sin(5*a+i)+.04*math.sin(11*a+i*.8);vv.append((x+rx*edge*math.cos(a),y+ry*edge*math.sin(a),z))
        ob=mesh('G4R03_shallow_rain_puddle',vv,[(0,k+1,(k+1)%96+1) for k in range(96)],water)
        sol=ob.modifiers.new('Water film depth 0.8mm','SOLIDIFY');sol.thickness=.0008
        for k in range(3):
            cx=x+rng.uniform(-rx*.4,rx*.4);cy=y+rng.uniform(-ry*.35,ry*.35);rad=.05+k*.045
            ring=curve('G4R03_puddle_impact_wave',[(rad*math.cos(a*2*math.pi/64),rad*math.sin(a*2*math.pi/64),0) for a in range(64)],.0007,water,True);ring.location=(cx,cy,z+.001)
            phase=rng.random()
            for axis in [0,1]:
                fc=ring.driver_add('scale',axis);fc.driver.expression=f'0.15+1.15*((frame/30+{phase:.6f})%0.8)'
        puddle_report.append({'object':ob.name,'support_object':hit['name'],'point':list(hit['point']),'film_depth':.0008})
    report['puddles']=puddle_report
    collection('G4R03_material_observations')
    newcams=[('G4R03_rain_glass_macro',(-4.75,-8.30,2.72),(-4.52,-6.50,2.48),65),
      ('G4R03_wet_stone_macro',(-4.0,-8.48,.63),(-5.15,-7.53,-.02),55),
      ('G4R03_textile_macro',(-5.75,-2.88,2.17),(-5.64,-3.59,1.77),72),
      ('G4R03_rain_architecture',(21,-23,11),(-3,0,4.0),43)]
    for name,pos,target,lens in newcams:
        ob=camera(name,pos,target,lens);ob.data.dof.use_dof=False
        report['cameras'].append({'object':name,'position':pos,'target':target,'lens':lens,'supplemental_not_replacement':True})
    after=protected(original_names);assert before==after,'Protected original geometry, cameras, lamps or movement changed'
    report['protected_before']=before;report['protected_after']=after
    report['texture_reuse']='Original packed Poly Haven walnut/slate/chair/plant maps retained; no asset redownload or undisclosed generated textures.'
    report['remaining']='Cab geometry creases, coarse cliff/sea boundary and full moving-train weather/cold-start film remain unaccepted. Materials require actual closeup review, not node-count acceptance.'
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    s['g4_revision']=REV;s['g4_r03_parent_sha256']=PARENT;s['weather_scope']='Native geometric rain and static adhesion; parked-frame collider proof, not fluid sim or final film'
    for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
    s.frame_set(451);s.camera=bpy.data.objects['C03_hall_to_platform'];bpy.context.view_layer.update()
    positions={}
    for f in [451,457,451]:
        s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ps=[]
        for instance in dg.object_instances:
            if instance.is_instance and instance.parent and instance.parent.original.name==rain.name:
                ps.append(tuple(round(x,5) for x in instance.matrix_world.translation))
                if len(ps)>=8:break
        assert ps,'Native rain instances failed evaluation';positions.setdefault(str(f),ps)
        if f==451 and 'repeat' not in positions:positions['repeat']=ps
    assert positions['451']!=positions['457'] and ps==positions['451'];report['rain_time_probe']=positions
    s.frame_set(451);save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
    report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('G4_R03_SAVED_NOT_ACCEPTED',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g4-full-scene-candidate.blend';report=json.loads((OUT/'build-report.json').read_text());expected=report['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025;s.cycles.adaptive_min_samples=24
    s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
    jobs={
      'hero':[('G4R03_rain_glass_macro','M01-rain-glass.png',(1600,1000),96),('C03_hall_to_platform','C03-hall-rain.png',(1440,900),64)],
      'detail':[('G3_D02','M02-woodwork.png',(1600,1000),96),('G4R03_wet_stone_macro','M03-wet-stone.png',(1440,900),80),('G4R03_textile_macro','M04-woven-seat.png',(1440,900),80),('C01_exterior_hero','C01-rain-night.png',(1440,900),64),('G3R03_roof_node','D01-node-regression.png',(1280,800),64)],
      'motion':[]}[MODE]
    metrics=json.loads((OUT/'render-metrics.json').read_text()) if (OUT/'render-metrics.json').exists() else []
    for cam,name,res,samples in jobs:
        assert time.time()<float(os.environ['G4_RAIN_DEADLINE']),'Finite rain/material production bound reached'
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451)
        row.update(master_sha256=expected,native_render=True,revision='G4_R03',scope='Parked-frame weather/material observation')
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('G4_R03_NATIVE_VIEW',name,flush=True)
    if MODE=='motion':
        (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.07
        for j,f in enumerate(range(451,511,3)):
            assert time.time()<float(os.environ['G4_RAIN_DEADLINE'])
            row=render(s,bpy.data.objects['G4R03_rain_glass_macro'],OUT/f'motion/{j:04d}.png',res=(640,400),samples=16,frame=f)
            row.update(master_sha256=expected,native_render=True,proof_only=True)
            metrics.append(row);(OUT/'motion-metrics.json').write_text(json.dumps(metrics[-(j+1):],indent=2))
    assert sha(master)==expected
    (OUT/f'{MODE}-reopen-check.json').write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'mode':MODE,'new_still_images':len(jobs),'g4_stage_pass':False,'human_acceptance':False},indent=2))
