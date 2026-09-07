"""G4 R03 actual editable weather/environment work, never generated-image evidence.
Read and validate the exact R02 first. Reuse its scene, animation, assets and helpers.
Ocean is Blender's native Ocean modifier; rain is bounded deterministic GN motion,
not a claim of a general fluid simulation. All artistic acceptance remains pending.
"""
import bpy, math, json, hashlib, os, sys, random, time, shutil
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path('workspaces/glasshouse-terminus').resolve()
sys.path.insert(0,str(ROOT))
from scene_common import material,mesh,camera,render,save
BASE=ROOT/'output/g4-r02'
OUT=ROOT/'output/g4-r03-weather'
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='173da1291bff8a39da704539c737e21f9b2d739e3d32a106f629601bc2abefdc'
MASTER='g4-weather-scene-candidate.blend'
MODE=os.environ['G4_WEATHER_MODE']
assert MODE in ['build','overview','details','motion']
s=bpy.context.scene
assert bpy.app.version[:2]==(4,5),bpy.app.version_string

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def node(nt,typ,name):
    n=nt.nodes.new(typ);n.label=name;n.name=name;return n
def link(nt,a,b):nt.links.new(a,b)
def mathnode(nt,op,a=None,b=None,name=None):
    n=node(nt,'ShaderNodeMath',name or op);n.operation=op
    for socket,v in zip(n.inputs,[a,b]):
        if v is None:continue
        if isinstance(v,(float,int)):socket.default_value=v
        else:link(nt,v,socket)
    return n.outputs[0]
def ramp(nt,source,stops,name):
    n=node(nt,'ShaderNodeValToRGB',name);r=n.color_ramp
    r.elements.remove(r.elements[1])
    for i,(position,color) in enumerate(stops):
        e=r.elements[0] if i==0 else r.elements.new(position);e.position=position;e.color=color
    link(nt,source,n.inputs['Fac']);return n.outputs['Color']
def noise(nt,source,scale,detail=3,name='Surface texture'):
    n=node(nt,'ShaderNodeTexNoise',name);n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail
    n.inputs['Roughness'].default_value=.64;link(nt,source,n.inputs['Vector']);return n

def material_record(m):
    return {'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.use_nodes else []}
def principled(m):return next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
def protect(names):
    h=hashlib.sha256()
    for f in [1,301,330,348,451,660,840]:
        s.frame_set(f);bpy.context.view_layer.update()
        for name in sorted(names):
            o=bpy.data.objects[name]
            h.update(repr((f,name,tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
            if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y)).encode())
    s.frame_set(451);bpy.context.view_layer.update()
    h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode())
    return h.hexdigest()
def signature_mesh(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(repr(tuple(p.vertices)).encode())
    return h.hexdigest()

def add_bump(m,p,height,distance,strength,name,normal_socket='Normal'):
    nt=m.node_tree;n=node(nt,'ShaderNodeBump',name);n.inputs['Distance'].default_value=distance;n.inputs['Strength'].default_value=strength
    link(nt,height,n.inputs['Height'])
    old=p.inputs[normal_socket]
    if old.is_linked:link(nt,old.links[0].from_socket,n.inputs['Normal'])
    link(nt,n.outputs['Normal'],old)

def copy_family(objects,transform):
    copies={};changes=[]
    for o in objects:
        if not o.data or not hasattr(o.data,'materials'):continue
        # Never mutate a mesh shared with an object outside this explicitly selected family.
        o.data=o.data.copy()
        for i,old in enumerate(list(o.data.materials)):
            if not old:continue
            if old.name not in copies:
                new=old.copy();new.name='G4R03_'+old.name
                transform(new);copies[old.name]=new
            o.data.materials[i]=copies[old.name];changes.append({'object':o.name,'before':old.name,'after':copies[old.name].name})
    return changes

if MODE=='build':
    parent=BASE/'g4-full-scene-candidate.blend'
    assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==EXPECTED
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    s.frame_set(451);bpy.context.view_layer.update()
    sea=bpy.data.objects.get('Ocean_extent');cliff=bpy.data.objects.get('Complete_cliff_mass');floor=bpy.data.objects.get('Hall_continuous_floor')
    assert sea and sea.type=='MESH' and cliff and cliff.type=='MESH' and floor and floor.type=='MESH'
    assert bpy.data.objects.get('Train_motion_root') and bpy.data.objects.get('C01_exterior_hero') and bpy.data.objects.get('C03_hall_to_platform')
    slo,shi=bounds(sea);clo,chi=bounds(cliff)
    assert -24<sea.location.z<-20 and chi[2]<1 and clo[2]<-20,(bounds(sea),bounds(cliff))
    assert shi[0]-slo[0]>1000 and shi[1]-slo[1]>1000,'Unexpected existing sea domain; inspect instead of force fitting'
    originals=[o.name for o in s.objects]
    protected=[n for n in originals if n!='Ocean_extent']
    before=protect(protected)
    protected_meshes={o.name:signature_mesh(o) for o in s.objects if o.type=='MESH' and o.name not in ['Ocean_extent','Complete_cliff_mass']}
    glass=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('Curved_roof_glazing','Side_wall_glass','End_wall_glazing','Hall_door_glass','Car_side_window','Cab_front_glass','Cab_side_glass','Door_glazing','G4_canopy_glass'))]
    assert len(glass)>100,'Source glazing family differs; stop'
    inventory={'source_master_sha256':EXPECTED,'blender':bpy.app.version_string,'sea':{'name':sea.name,'bounds':[slo,shi],'vertices':len(sea.data.vertices),'materials':[material_record(m) for m in sea.data.materials if m]},'cliff':{'name':cliff.name,'bounds':[clo,chi],'vertices':len(cliff.data.vertices),'materials':[material_record(m) for m in cliff.data.materials if m]},'floor':{'name':floor.name,'bounds':bounds(floor),'materials':[material_record(m) for m in floor.data.materials if m]},'glass_names':[o.name for o in glass],'cameras':[{'name':o.name,'position':list(o.matrix_world.translation),'lens':o.data.lens} for o in s.objects if o.type=='CAMERA'],'source_scene_properties':{str(k):str(v) for k,v in s.items()},'source_unchanged':sha(parent)==EXPECTED}
    (OUT/'READ-ONLY-SOURCE-INVENTORY.json').write_text(json.dumps(inventory,indent=2))
    report={'stage':'G4','revision':'R03_WEATHER','status':'CANDIDATE_NOT_ART_PASS','source_master_sha256':EXPECTED,'parent_evidence_commit':'12ae1030686d97823548b2967805d85853d12ab2','run_id':os.environ.get('GITHUB_RUN_ID'),'source_sha':os.environ.get('GITHUB_SHA'),'user_request':'Actual project rain, premium materials, realistic sea and mountain/cliff. Generated concept images excluded.','changes':{},'g3_historical_pass':False,'g4_stage_pass':False,'human_acceptance':False}
    col=bpy.data.collections.new('G4R03_weather_environment');s.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[col.name]

    # Native spectral ocean: saved modifier and time driver, not a flat textured cube.
    original_sea_z=float(sea.location.z)
    sea.data=bpy.data.meshes.new('G4R03_native_ocean_seed')
    sea.data.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[],[(0,1,2,3)]);sea.data.update()
    for mod in list(sea.modifiers):sea.modifiers.remove(mod)
    ocean=sea.modifiers.new('Native Ocean - editable wind swell and foam','OCEAN')
    settings={'geometry_mode':'GENERATE','resolution':7,'viewport_resolution':6,'spatial_size':220,'size':1.0,'repeat_x':4,'repeat_y':4,'wave_scale':1.15,'wave_scale_min':.035,'choppiness':1.1,'wind_velocity':17.0,'wave_alignment':.35,'wave_direction':.42,'depth':140.0,'random_seed':37,'use_foam':True,'foam_coverage':.22,'foam_layer':'OceanFoam','time':15.0333333}
    # Blender versions expose chop_amount, not choppiness; only use actual RNA properties.
    settings.pop('choppiness');settings['choppiness']=1.1 if hasattr(ocean,'choppiness') else None
    if settings['choppiness'] is None:settings.pop('choppiness');settings['chop_amount']=1.1
    for k,v in settings.items():
        if not hasattr(ocean,k):raise RuntimeError('Ocean API mismatch: '+k)
        setattr(ocean,k,v)
    driver=ocean.driver_add('time').driver;driver.type='SCRIPTED';driver.expression='frame / 30.0'
    water=material('G4R03_deep_cold_seawater',(.008,.025,.033),rough=.105,transmission=.82)
    p=principled(water);p.inputs['IOR'].default_value=1.333
    nt=water.node_tree;tc=node(nt,'ShaderNodeTexCoord','Metre-scale water coordinates')
    micro=noise(nt,tc.outputs['Object'],2.3,4,'Capillary and small wind waves')
    add_bump(water,p,micro.outputs['Fac'],.028,.32,'Small wave normals under actual geometry')
    attr=node(nt,'ShaderNodeAttribute','Native breaking-wave foam');attr.attribute_name='OceanFoam'
    foam=ramp(nt,attr.outputs['Fac'],[(.12,(0,0,0,1)),(.58,(1,1,1,1))],'Foam coverage from native ocean solver')
    fn=noise(nt,tc.outputs['Object'],6.5,2,'Foam perforation');fac=mathnode(nt,'MULTIPLY',foam,fn.outputs['Fac'])
    mix=node(nt,'ShaderNodeMixRGB','Whitecaps over deep water');mix.blend_type='MIX';mix.inputs[1].default_value=(.008,.025,.033,1);mix.inputs[2].default_value=(.68,.76,.76,1)
    link(nt,fac,mix.inputs[0]);link(nt,mix.outputs[0],p.inputs['Base Color'])
    rough=mathnode(nt,'ADD',.105,mathnode(nt,'MULTIPLY',fac,.55));link(nt,rough,p.inputs['Roughness'])
    trans=mathnode(nt,'MULTIPLY',mathnode(nt,'SUBTRACT',1,fac),.82);link(nt,trans,p.inputs['Transmission Weight'])
    sea.data.materials.append(water)
    bpy.context.view_layer.update();ev=sea.evaluated_get(bpy.context.evaluated_depsgraph_get());olo,ohi=bounds(ev)
    # Center the generated repeated domain on the site without assuming modifier repeat origin.
    sea.location.x+=-8-(olo[0]+ohi[0])/2;sea.location.y+=-(olo[1]+ohi[1])/2
    bpy.context.view_layer.update();olo,ohi=bounds(sea.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    assert ohi[0]-olo[0]>600 and ohi[1]-olo[1]>600
    # A contiguous distant annulus removes the old finite square ocean edge.
    cx=(olo[0]+ohi[0])/2;cy=(olo[1]+ohi[1])/2
    inner=[(olo[0],olo[1]),(ohi[0],olo[1]),(ohi[0],ohi[1]),(olo[0],ohi[1])]
    outer=[(cx-20000,cy-20000),(cx+20000,cy-20000),(cx+20000,cy+20000),(cx-20000,cy+20000)]
    verts=[(x,y,original_sea_z) for x,y in inner]+[(x,y,original_sea_z-31) for x,y in outer]
    horizon=mesh('G4R03_distant_continuous_sea',verts,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],water,smooth=True)
    bottom=material('G4R03_deep_water_absorbing_background',(.004,.012,.014),rough=1)
    mesh('G4R03_submerged_dark_bed',[(cx-21000,cy-21000,-38),(cx+21000,cy-21000,-38),(cx+21000,cy+21000,-38),(cx-21000,cy+21000,-38)],[(0,1,2,3)],bottom)
    report['changes']['ocean']={'native_modifier':settings,'time_driver':'frame/30','generated_bounds':[olo,ohi],'distant_annulus_metres':40000,'native_foam_attribute':'OceanFoam','limitation':'Wind-wave ocean, not an impact or full coastal fluid solver. Far annulus has shader micro-waves; actual geometric swell is in the native Ocean domain.'}

    # Geological replacement of only the crude cliff mesh; preserve its actual top ring.
    worldverts=[cliff.matrix_world@v.co for v in cliff.data.vertices]
    topz=max(v.z for v in worldverts);top=[v for v in worldverts if v.z>topz-.08]
    assert len(top)>=24,'Cliff cap topology differs; inspect instead of deforming an unknown mesh'
    center=Vector((sum(v.x for v in top)/len(top),sum(v.y for v in top)/len(top),topz))
    rings=sorted([(math.atan2(v.y-center.y,v.x-center.x)%(2*math.pi),v) for v in top],key=lambda q:q[0])
    def top_xy(a):
        for i,(a0,v0) in enumerate(rings):
            a1,v1=rings[(i+1)%len(rings)];aa=a
            if i==len(rings)-1:a1+=2*math.pi
            if aa<a0:aa+=2*math.pi
            if a0<=aa<=a1:
                return v0.lerp(v1,(aa-a0)/(a1-a0))
        raise RuntimeError('Cliff ring interpolation failed')
    nv=320;nz=96;vs=[];faces=[];inv=cliff.matrix_world.inverted()
    bottomz=min(v.z for v in worldverts)
    for iz in range(nz+1):
        t=iz/nz;z=bottomz+(topz-bottomz)*t
        lock=min(1,max(0,(topz-z)/2.2))
        for j in range(nv):
            a=2*math.pi*j/nv;cap=top_xy(a);rad=Vector((cap.x-center.x,cap.y-center.y,0));u=rad.normalized()
            n=noise_vector(Vector((math.cos(a)*3.2,math.sin(a)*3.2,z*.115)))
            fracture=(abs(math.sin(a*8.3+.4*math.sin(z*.21)))*2-1)
            bedding=.24*math.sin(z*3.8+a*.4)+.10*math.sin(z*11.0+a*.7)
            detail=.16*noise_vector(Vector((cap.x*.8,cap.y*.8,z*.8))).x
            offset=lock*(.65+1.25*n.x+.62*fracture+bedding+detail)
            pnt=Vector((cap.x,cap.y,z))+u*offset
            vs.append(tuple(inv@pnt))
    for iz in range(nz):
        for j in range(nv):
            a=iz*nv+j;b=iz*nv+(j+1)%nv;c=b+nv;d=a+nv
            faces.append((a,b,c,d))
    faces.append(tuple(reversed(range(nv))));faces.append(tuple(nz*nv+j for j in range(nv)))
    old_material=cliff.active_material
    data=bpy.data.meshes.new('G4R03_stratified_cliff_mesh');data.from_pydata(vs,[],faces);data.update();cliff.data=data
    for f in data.polygons:f.use_smooth=len(f.vertices)==4
    for mod in list(cliff.modifiers):cliff.modifiers.remove(mod)
    rock=old_material.copy() if old_material and old_material.use_nodes else material('G4R03_rock',(.12,.15,.16),rough=.65)
    rock.name='G4R03_stratified_wet_rock';rp=principled(rock)
    assert rp,'Current rock surface is not a compatible Principled material'
    nt=rock.node_tree;tc=node(nt,'ShaderNodeTexCoord','Rock coordinates in metres');tex=noise(nt,tc.outputs['Object'],.32,5,'Geological colour variation')
    color=ramp(nt,tex.outputs['Fac'],[(.2,(.055,.067,.071,1)),(.48,(.12,.135,.137,1)),(.76,(.24,.25,.235,1))],'Low saturation mineral bands')
    link(nt,color,rp.inputs['Base Color'])
    rough=ramp(nt,tex.outputs['Fac'],[(.2,(.25,.25,.25,1)),(.8,(.68,.68,.68,1))],'Wet recesses and rough mineral faces');link(nt,rough,rp.inputs['Roughness'])
    rp.inputs['Metallic'].default_value=0;rp.inputs['Coat Weight'].default_value=.17;rp.inputs['Coat Roughness'].default_value=.12
    grain=noise(nt,tc.outputs['Object'],11,4,'Rock grain and small erosion');add_bump(rock,rp,grain.outputs['Fac'],.019,.48,'Mineral grain normals')
    # Optional selected CC0 rock maps fetched by the workflow, never unlicensed images.
    assets=OUT/'assets/rock-sources.json'
    if assets.exists():
        source=json.loads(assets.read_text());maps=source.get('maps',{})
        for role,socket in [('diff','Base Color'),('rough','Roughness')]:
            if role in maps:
                texnode=node(nt,'ShaderNodeTexImage','CC0 rock '+role);image=bpy.data.images.load(str((OUT/'assets'/maps[role]['file']).resolve()),check_existing=True);texnode.image=image;texnode.projection='BOX';texnode.projection_blend=.22
                if role!='diff':image.colorspace_settings.name='Non-Color'
                vector=node(nt,'ShaderNodeVectorMath','Rock metre mapping '+role);vector.operation='SCALE';vector.inputs[3].default_value=.58;link(nt,tc.outputs['Object'],vector.inputs[0]);link(nt,vector.outputs[0],texnode.inputs['Vector'])
                if role=='diff':
                    mult=node(nt,'ShaderNodeMixRGB','Damp mineral albedo');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(.60,.65,.68,1);link(nt,texnode.outputs['Color'],mult.inputs[1]);link(nt,mult.outputs[0],rp.inputs[socket])
                else:link(nt,texnode.outputs['Color'],rp.inputs[socket])
        report['changes']['rock_asset']=source
    cliff.data.materials.append(rock)
    report['changes']['cliff']={'object':cliff.name,'old_vertices':len(worldverts),'new_vertices':len(vs),'preserved_top_z':topz,'top_ring_locked':True,'geometric_features':'Large buttresses, fracture modulation and stratified shelves; no displacement of foundation, rails or building.','roughness_not_a_substitute_for_geometry':True}

    # Preserve existing image textures and add controlled scale-specific material response.
    def wet_glass(m):
        p=principled(m)
        if not p:return
        nt=m.node_tree;tc=node(nt,'ShaderNodeTexCoord','Attached local surface water coordinates')
        scale=node(nt,'ShaderNodeVectorMath','Millimetre bead distribution');scale.operation='MULTIPLY';scale.inputs[1].default_value=(165,165,85);link(nt,tc.outputs['Object'],scale.inputs[0])
        vor=node(nt,'ShaderNodeTexVoronoi','Water beads');vor.distance='EUCLIDEAN';vor.feature='F1';vor.inputs['Scale'].default_value=1;link(nt,scale.outputs[0],vor.inputs['Vector'])
        beads=ramp(nt,vor.outputs['Distance'],[(.08,(1,1,1,1)),(.24,(0,0,0,1))],'Convex sparse bead profile')
        streak=node(nt,'ShaderNodeVectorMath','Gravity elongated film coordinates');streak.operation='MULTIPLY';streak.inputs[1].default_value=(30,30,.75);link(nt,tc.outputs['Object'],streak.inputs[0])
        trails=noise(nt,streak.outputs[0],1,3,'Thin rivulet irregularity')
        streaks=ramp(nt,trails.outputs['Fac'],[(.66,(0,0,0,1)),(.79,(.4,.4,.4,1))],'Sparse flowing film')
        height=mathnode(nt,'ADD',beads,streaks)
        add_bump(m,p,height,.00065,.58,'Attached water relief')
        p.inputs['Coat Weight'].default_value=.75;p.inputs['Coat Roughness'].default_value=.025
        if 'Coat IOR' in p.inputs:p.inputs['Coat IOR'].default_value=1.333
    report['changes']['glass']=copy_family(glass,wet_glass)
    # Exterior wet paving only: do not make the sheltered hall floor wet.
    paving=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('Platform_continuous_slab','Platform_coping_edge','Hall_entry_step','Continuous_bridge_trackbed','Load_bearing_masonry_terrace'))]
    def wet_paving(m):
        p=principled(m)
        if not p:return
        nt=m.node_tree;tc=node(nt,'ShaderNodeTexCoord','Exterior stone coordinates');n=noise(nt,tc.outputs['Object'],.72,3,'Localized water retention')
        wet=ramp(nt,n.outputs['Fac'],[(.32,(.13,.13,.13,1)),(.52,(.24,.24,.24,1)),(.74,(.63,.63,.63,1))],'Puddles separated from drained stone')
        link(nt,wet,p.inputs['Roughness']);p.inputs['Coat Weight'].default_value=.42;p.inputs['Coat Roughness'].default_value=.08
        grain=noise(nt,tc.outputs['Object'],95,2,'Fine exposed paving grain');add_bump(m,p,grain.outputs['Fac'],.00028,.32,'Wet stone microrelief')
    report['changes']['outdoor_paving']=copy_family(paving,wet_paving)
    enamel=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('Primary_elliptical_arch','Load_column','Column_capital','Secondary_glazing_rib','Wall_glazing_mullion','Car_curved_lower_shell','Cab_front_fairing'))]
    def refined_paint(m):
        p=principled(m)
        if not p:return
        nt=m.node_tree;tc=node(nt,'ShaderNodeTexCoord','Paint local coordinates');n=noise(nt,tc.outputs['Object'],240,2,'Subtle cured enamel orange peel')
        add_bump(m,p,n.outputs['Fac'],.000035,.2,'Microscopic enamel relief')
    report['changes']['enamel']=copy_family(enamel,refined_paint)
    # Dry cut stone joints and fine grain; retain the proven dry roughness network.
    floor.data=floor.data.copy();fm=floor.active_material.copy();fm.name='G4R03_dry_cut_stone_floor';floor.data.materials[0]=fm;fp=principled(fm);assert fp
    nt=fm.node_tree;tc=node(nt,'ShaderNodeTexCoord','Dry slab metre coordinates');sep=node(nt,'ShaderNodeSeparateXYZ','Slab axes');link(nt,tc.outputs['Object'],sep.inputs[0])
    xx=mathnode(nt,'DIVIDE',sep.outputs['X'],1.1);yy=mathnode(nt,'DIVIDE',sep.outputs['Y'],.55)
    stagger=mathnode(nt,'MULTIPLY',mathnode(nt,'MODULO',mathnode(nt,'FLOOR',yy),2),.5);xx=mathnode(nt,'ADD',xx,stagger)
    ux=mathnode(nt,'FRACT',xx);uy=mathnode(nt,'FRACT',yy)
    dx=mathnode(nt,'MULTIPLY',mathnode(nt,'MINIMUM',ux,mathnode(nt,'SUBTRACT',1,ux)),1.1)
    dy=mathnode(nt,'MULTIPLY',mathnode(nt,'MINIMUM',uy,mathnode(nt,'SUBTRACT',1,uy)),.55)
    edge=mathnode(nt,'MINIMUM',dx,dy);joints=mathnode(nt,'LESS_THAN',edge,.0018)
    add_bump(fm,fp,mathnode(nt,'SUBTRACT',1,joints),.00085,.6,'Fine recessed slab joints')
    ng=noise(nt,tc.outputs['Object'],150,2,'Dry stone grain');add_bump(fm,fp,ng.outputs['Fac'],.00018,.35,'Cut stone tactile finish')
    fp.inputs['Coat Weight'].default_value=0
    report['changes']['dry_floor']={'object':floor.name,'tile_metres':[1.1,.55],'joint_width_metres':.0036,'original_roughness_and_albedo_preserved':True,'coat':0}

    # Real geometry-node rain, driven by saved scene time and occluded by actual roofs.
    shelters=bpy.data.collections.new('G4R03_actual_rain_shelters');s.collection.children.link(shelters)
    shelter_prefix=('Curved_roof_glazing','Car_complete_barrel_roof','Cab_complete_roof_loft','Ridge_vent_cap','Hall_continuous_floor','Platform_continuous_slab','Continuous_bridge_trackbed','G4_canopy')
    shelter_names=[]
    for o in list(s.objects):
        if o.type=='MESH' and o.name.startswith(shelter_prefix):shelters.objects.link(o);shelter_names.append(o.name)
    assert len(shelter_names)>100
    rainmat=material('G4R03_physical_rain_water',(.88,.94,.98),rough=.055,transmission=1)
    principled(rainmat).inputs['IOR'].default_value=1.333
    rng=random.Random(913)
    points=[(rng.uniform(-82,35),rng.uniform(-35,80),rng.uniform(0,47)) for _ in range(22000)]
    points += [(rng.uniform(-20,20),rng.uniform(-10,19),rng.uniform(0,24)) for _ in range(14000)]
    rain=mesh('G4R03_outdoor_rain',points,[],None)
    tree=bpy.data.node_groups.new('G4R03_rain_time_and_real_shelter_occlusion','GeometryNodeTree')
    tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    inp=node(tree,'NodeGroupInput','Saved deterministic seed points');out=node(tree,'NodeGroupOutput','Actual rain instances')
    pos=node(tree,'GeometryNodeInputPosition','Seed phase coordinates');sep=node(tree,'ShaderNodeSeparateXYZ','Rain coordinates');link(tree,pos.outputs['Position'],sep.inputs[0])
    st=node(tree,'GeometryNodeInputSceneTime','Saved scene time');seconds=mathnode(tree,'SUBTRACT',st.outputs['Seconds'],451/30)
    phase=mathnode(tree,'ADD',sep.outputs['Z'],mathnode(tree,'MULTIPLY',seconds,9));phase=mathnode(tree,'ADD',phase,47000)
    fall=mathnode(tree,'MODULO',phase,47)
    z=mathnode(tree,'SUBTRACT',26,fall);x=mathnode(tree,'ADD',sep.outputs['X'],mathnode(tree,'MULTIPLY',fall,-.12));y=mathnode(tree,'ADD',sep.outputs['Y'],mathnode(tree,'MULTIPLY',fall,.045))
    combine=node(tree,'ShaderNodeCombineXYZ','Diagonal rain trajectory');link(tree,x,combine.inputs['X']);link(tree,y,combine.inputs['Y']);link(tree,z,combine.inputs['Z'])
    sp=node(tree,'GeometryNodeSetPosition','Animated world positions');link(tree,inp.outputs['Geometry'],sp.inputs['Geometry']);link(tree,combine.outputs[0],sp.inputs['Position'])
    topts=node(tree,'GeometryNodeMeshToPoints','Vertex rain particles');topts.mode='VERTICES';link(tree,sp.outputs['Geometry'],topts.inputs['Mesh'])
    ci=node(tree,'GeometryNodeCollectionInfo','Actual shelter geometry including moving train');ci.inputs['Collection'].default_value=shelters
    if 'Separate Children' in ci.inputs:ci.inputs['Separate Children'].default_value=False
    if 'Reset Children' in ci.inputs:ci.inputs['Reset Children'].default_value=False
    realize=node(tree,'GeometryNodeRealizeInstances','Real shelter surfaces');link(tree,ci.outputs['Instances'],realize.inputs['Geometry'])
    ray=node(tree,'GeometryNodeRaycast','Upward actual-roof occlusion');ray.data_type='FLOAT';link(tree,realize.outputs['Geometry'],ray.inputs['Target Geometry']);link(tree,combine.outputs[0],ray.inputs['Source Position']);ray.inputs['Ray Direction'].default_value=(0,0,1);ray.inputs['Ray Length'].default_value=100
    delete=node(tree,'GeometryNodeDeleteGeometry','No rain below solid shelter');delete.domain='POINT';link(tree,topts.outputs['Points'],delete.inputs['Geometry']);link(tree,ray.outputs['Is Hit'],delete.inputs['Selection'])
    sphere=node(tree,'GeometryNodeMeshIcoSphere','True water streak geometry');sphere.inputs['Radius'].default_value=.0018;sphere.inputs['Subdivisions'].default_value=1
    tr=node(tree,'GeometryNodeTransform','Exposure-integrated droplet shape');tr.inputs['Scale'].default_value=(1,1,45);tr.inputs['Rotation'].default_value=(.045,.12,0);link(tree,sphere.outputs['Mesh'],tr.inputs['Geometry'])
    sm=node(tree,'GeometryNodeSetMaterial','Water not emissive screen lines');sm.inputs['Material'].default_value=rainmat;link(tree,tr.outputs['Geometry'],sm.inputs['Geometry'])
    instances=node(tree,'GeometryNodeInstanceOnPoints','Native rain instances');link(tree,delete.outputs['Geometry'],instances.inputs['Points']);link(tree,sm.outputs['Geometry'],instances.inputs['Instance']);link(tree,instances.outputs['Instances'],out.inputs['Geometry'])
    mod=rain.modifiers.new('Deterministic falling rain with actual shelter masking','NODES');mod.node_group=tree
    report['changes']['rain']={'seed':913,'seed_points':len(points),'speed_metres_per_second':9,'height_metres':47,'representation':'Native instanced exposure-length water geometry; not a fluid solver or screen overlay.','shelter_method':'Upward Geometry Nodes raycast against actual saved roof/overhang/deck meshes, including parented train roof.','shelter_names':shelter_names,'indoor_floor_wet':False,'emission':0}

    # Supplementary close views do not replace or move any failed original camera.
    camera('G4R03_ocean_detail',(-27,40,-11),(-26,17,-22),48)
    camera('G4R03_cliff_detail',(29,38,-2),(13,14,-11),52)
    camera('G4R03_wet_glass_detail',(-1.6,4.85,3.55),(-2.2,6.49,3.25),65)
    assert protect(protected)==before,'Protected camera/motion/transform/ray settings changed'
    aftermesh={n:signature_mesh(bpy.data.objects[n]) for n in protected_meshes}
    assert aftermesh==protected_meshes,'Unexpected original geometry edits outside ocean/cliff'
    report['protected_before']=before;report['protected_after']=protect(protected)
    report['source_master_unchanged']=sha(parent)==EXPECTED
    report['native_original_camera_names']=[n for n in originals if bpy.data.objects[n].type=='CAMERA']
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    if (BASE/'models/MODEL-SOURCES.json').exists():
        (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    s['g4_revision']='R03 actual native rain/ocean/stratified cliff and material refinement'
    s['g4_weather_parent_sha256']=EXPECTED;s.frame_set(451);s.camera=bpy.data.objects['C01_exterior_hero']
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True
    save(s,OUT/MASTER);report['candidate_sha256']=sha(OUT/MASTER);report['master_bytes']=(OUT/MASTER).stat().st_size
    assert sha(parent)==EXPECTED
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2))
    print('R03_NATIVE_SCENE_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
else:
    master=OUT/MASTER;report=json.loads((OUT/'build-report.json').read_text());expected=report['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    for n in json.loads(s.get('g3_neutral_lights','{}')):
        if bpy.data.objects.get(n):bpy.data.objects[n].data.energy=0
    # Keep the saved continuous R02 night World. Do not substitute a different sky per camera.
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025;s.cycles.adaptive_min_samples=24
    metrics=json.loads((OUT/'render-metrics.json').read_text()) if (OUT/'render-metrics.json').exists() else []
    if MODE=='overview':jobs=[('C03_hall_to_platform','C03-rain-hall.png',(1600,1000),96,451),('C01_exterior_hero','C01-rain-ocean-cliff.png',(1600,1000),96,451)]
    elif MODE=='details':jobs=[('G4R03_ocean_detail','D-ocean-waves-foam.png',(1280,800),96,451),('G4R03_cliff_detail','D-cliff-geology.png',(1280,800),96,451),('G4R03_wet_glass_detail','D-wet-glass.png',(1280,800),128,451),('G3R03_roof_node','D01-roof-node-regression.png',(1280,800),96,451)]
    else:
        (OUT/'motion').mkdir(exist_ok=True);jobs=[('G4R03_ocean_detail','motion/frame-%03d.png'%i,(640,400),16,451+i*3) for i in range(16)]
        s.cycles.adaptive_threshold=.08;s.cycles.adaptive_min_samples=8
    for cam,name,res,samples,frame in jobs:
        assert time.time()<float(os.environ['G4_WEATHER_DEADLINE']),'Finite production deadline reached'
        assert bpy.data.objects.get(cam),cam
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame)
        row.update(native_render=True,source_master_sha256=expected,lighting='saved continuous R02 world plus unchanged real fixtures',motion_probe=MODE=='motion')
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('R03_NATIVE_VIEW_SAVED',name,flush=True)
    assert sha(master)==expected and sha(BASE/'g4-full-scene-candidate.blend')==EXPECTED
    (OUT/('reopen-'+MODE+'.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'mode':MODE,'new_views':len(jobs),'g4_stage_pass':False,'human_acceptance':False},indent=2))
