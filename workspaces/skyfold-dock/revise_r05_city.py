"""R05: replace uniform six-lot neighbourhood repetition, without changing cameras,
ship, ring shell, dock, foreground, lights or animation. Native R01 assets reused.
This is a bounded city-hierarchy comparison, not a new theme or art PASS.
"""
import ast, bpy, hashlib, json, math, os, random, struct
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parent; OUT=Path(os.environ['SKYFOLD_OUT']); OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath); PARENT='831c51340a7c81012e517d4ea0ce0da4a6412a1d86940ad74c7a7f0b1f760261'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert bpy.app.version[:3]==(4,5,13)
SC=bpy.context.scene;SC.frame_set(1);bpy.context.view_layer.update()
COL={c.name:c for c in bpy.data.collections};R=1600.0
material_names=['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay','Recessed planted courtyards','City basalt roadbed']
M=[bpy.data.materials[n] for n in material_names]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY,PARK,ROAD=range(13)
source=(ROOT/'build_scene_r01.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
defs=[n for n in ast.parse(source).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Mesh','frame'}]
assert {n.name for n in defs}=={'Mesh','frame'}
exec(compile(ast.Module(body=defs,type_ignores=[]),'VERIFIED_R01_HELPERS','exec'),globals())
city=list(COL['02_CITY_INSTANCES'].objects);assert len(city)>100
protected=[o for o in SC.objects if o not in city]
def signatures(objects):
    result={}
    for o in objects:
        h=hashlib.sha256();h.update(o.name.encode());h.update(str(o.type).encode());h.update(str(o.parent.name if o.parent else None).encode())
        for row in o.matrix_world:
            h.update(struct.pack('<4f',*row))
        if o.type=='MESH':
            for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
            for p in o.data.polygons:h.update(struct.pack('<I',p.material_index))
            h.update(str([ma.name if ma else None for ma in o.data.materials]).encode())
        result[o.name]=h.hexdigest()
    return result
before=signatures(protected)
old=[bpy.data.objects['City archetype %02d'%k] for k in range(10)]
# Reuse actual building meshes. Uniform scales keep buildings rigid, never bend them.
def append_building(g,k,x,y,scale):
    p=old[k].data;off=len(g.v)
    g.v.extend((x+v.co.x*scale,y+v.co.y*scale,4+v.co.z*scale) for v in p.vertices)
    for f in p.polygons:g.f.append(tuple(off+i for i in f.vertices));g.mi.append(f.material_index)
plans={
 'PLAZA':[(7,-61,-48,.42),(0,65,53,.5)],
 'RESIDENTIAL':[(1,-52,-44,.9),(0,49,-42,1.05),(5,-50,43,.82),(9,51,43,.8)],
 'CIVIC':[(7,-38,4,1.05),(6,49,39,.84),(0,49,-49,.7)],
 'OFFICE':[(8,0,21,1.0),(6,-61,-49,.78),(2,57,-46,.85)],
 'MIXED_CORE':[(4,-44,22,1.12),(3,46,-24,1.05),(0,-49,-56,.61)],
 'LANDMARK':[(8,3,8,1.35),(6,-61,-53,.72),(1,62,55,.83)],
 'INDUSTRIAL':[(7,-50,-39,.93),(5,51,39,.94),(0,57,-49,.63)],
 'TERRACES':[(5,-51,36,.95),(7,35,-35,1.02),(0,63,51,.7)]}
prototypes={}
for family,plan in plans.items():
    for variant in range(3):
        g=Mesh();g.box((0,0,0),(190,180,8),ROAD if family in ['PLAZA','INDUSTRIAL'] else CONCRETE)
        g.box((0,-85,4.15),(178,6,.3),ROAD);g.box((88,0,4.15),(5,164,.3),ROAD)
        if family=='PLAZA':
            g.box((-18,28,4.3),(70,82,.6),PARK);g.box((49,-37,4.3),(42,66,.6),PARK)
            g.box((-6,-35,4.3),(106,7,.6),CONCRETE)
        else:
            g.box((-3,0,4.2),(15,158,.4),ROAD)
            g.box((0,74,4.2),(106,12,.4),PARK)
        for n,(k,x,y,scale) in enumerate(plan):
            scale*=.90+.08*variant
            append_building(g,k,x+(variant-1)*(3 if n%2 else -3),y,scale)
        proto=g.object(f'R05 {family} prototype {variant}','09_PROTOTYPES');proto.hide_render=True;proto.hide_viewport=True
        prototypes[family,variant]=proto
layout=[]
for o in city:
    world=o.matrix_world.copy();theta=math.atan2(world.translation.x,R-world.translation.z)%(2*math.pi);y=float(world.translation.y)
    i=int(theta/(2*math.pi)*46);j=round((y-170)/230);rng=random.Random(270910+i*1009+j*9176)
    # Broad district rhythm plus sparse tall clusters; not a colour-only randomizer.
    activity=math.sin(theta*2.6-.9)+.66*math.cos(j*.56+theta*.8)
    if (i//4+j//3)%9==0 or rng.random()<.13:family='PLAZA'
    elif activity>1.04:family=rng.choice(['OFFICE','MIXED_CORE','MIXED_CORE','LANDMARK'])
    elif activity<-.8:family=rng.choice(['INDUSTRIAL','INDUSTRIAL','TERRACES'])
    else:family=rng.choice(['RESIDENTIAL','RESIDENTIAL','CIVIC','TERRACES','OFFICE'])
    variant=(i+j*2)%3;proto=prototypes[family,variant];o.data=proto.data
    # Keep the exact site anchor, local orientation, parent and scene-level animation.
    # Remove the previous whole-neighbourhood height stretch in favour of rigid archetypes.
    scales=world.to_scale();rot=world.to_quaternion().to_matrix().to_4x4();rot.translation=world.translation;o.matrix_world=rot
    o['prototype']=proto.name;o['R05_land_use']=family;o['local_up']='INWARD_RADIAL'
    inward=Vector((-o.matrix_world.translation.x,0,R-o.matrix_world.translation.z)).normalized()
    assert o.matrix_world.to_3x3().col[2].normalized().dot(inward)>.999
    layout.append({'object':o.name,'site_theta':theta,'axial_y':y,'family':family,'prototype':proto.name})
bpy.context.view_layer.update();after=signatures(protected);assert before==after,'Protected non-city geometry or transforms changed'
meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
SC['candidate']='R05_CITY_HIERARCHY_STUDY';SC['source_sha']=os.environ['GITHUB_SHA'];SC['auto_qualified']=False
meta.update({'candidate':SC['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,
 'intervention':'Only city neighbourhood meshes and height scaling; existing building archetypes reused. Cameras, shell, dock, ship, gallery, lighting and motion unchanged.',
 'protected_non_city_objects':len(before),'protected_signatures_unchanged':True,'layout':layout,
 'city_quality':'REVIEW_REQUIRED_NOT_PROVEN_BY_COUNTS','gate':'NOT_AUTO_QUALIFIED'})
p=OUT/'skyfold-r05.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2))
(OUT/'PROTECTED-SIGNATURES.json').write_text(json.dumps(before,indent=2))
print('R05_CITY_HIERARCHY_SAVED',meta['scene_sha256'],'VISUAL_REVIEW_REQUIRED')
