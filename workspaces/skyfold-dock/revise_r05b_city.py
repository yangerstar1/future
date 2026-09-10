"""R05B: remove identical raised superblock plates, keep the same rigid buildings.
Original ring shell remains continuous. Individual footings penetrate its surface;
roads/landscape patches follow the exact local ring curvature. City-only change.
"""
import ast, bpy, hashlib, json, math, os, struct
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parent; OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(bpy.data.filepath);PARENT='cf54a7be3f679643ff6abd54ca438389bdf4654c206b53bdebca9205d80249c1'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PARENT
assert bpy.app.version[:3]==(4,5,13)
SC=bpy.context.scene;SC.frame_set(1);bpy.context.view_layer.update();meta=json.loads(BASE.with_name('BUILD-MANIFEST.json').read_text())
COL={c.name:c for c in bpy.data.collections};R=1600.;ANCHOR=1.4
names=['Pearl ceramic-coated alloy','Structural graphite steel','Pale structural composite','Oxide orange workzone coating','Inset blue-black facade glazing','Brushed bare metal','Foot-worn dark deck metal','Warm service luminaires','Wheel rubber','City pale panels','Neutral inspection clay','Recessed planted courtyards','City basalt roadbed']
M=[bpy.data.materials[n] for n in names]
PAINT,DARK,CONCRETE,ORANGE,GLASS,SILVER,DECK,LIGHT,RUBBER,CITY,GRAY,PARK,ROAD=range(13)
raw=(ROOT/'build_scene_r01.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
mesh_def=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef) and n.name=='Mesh')
exec(compile(ast.Module(body=[mesh_def],type_ignores=[]),'VERIFIED_R01_MESH','exec'),globals())
proposal=(ROOT/'revise_r05_city.py').read_bytes();assert hashlib.sha256(proposal).hexdigest()=='ecc21a7cec4c4bfc403dec9f87d01ee36b7c9702d16be2948be47b824b86cae6'
ptree=ast.parse(proposal);plans=ast.literal_eval(next(n.value for n in ptree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='plans' for t in n.targets)))
sig_def=next(n for n in ptree.body if isinstance(n,ast.FunctionDef) and n.name=='signatures')
exec(compile(ast.Module(body=[sig_def],type_ignores=[]),'VERIFIED_R05_SIGNATURES','exec'),globals())
city=list(COL['02_CITY_INSTANCES'].objects);protected=[o for o in SC.objects if o not in city];before=signatures(protected)
old=[bpy.data.objects['City archetype %02d'%k] for k in range(10)]

def surface_z(x):
    assert abs(x)<R
    return R-ANCHOR-math.sqrt(R*R-x*x)

def patch(g,p,size,material,thickness=.24):
    """Closed, tessellated shallow pavement on the existing cylindrical ground."""
    x,y=p;w,d=size;segments=6
    for j in range(segments):
        xa=x-w/2+w*j/segments;xb=x-w/2+w*(j+1)/segments
        za=surface_z(xa)-.05;zb=surface_z(xb)-.05
        vs=[(xa,y-d/2,za),(xb,y-d/2,zb),(xb,y+d/2,zb),(xa,y+d/2,za),
            (xa,y-d/2,za+thickness),(xb,y-d/2,zb+thickness),(xb,y+d/2,zb+thickness),(xa,y+d/2,za+thickness)]
        g.poly(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

footing_tests=[]
def building(g,k,x,y,scale):
    p=old[k].data;offset=len(g.v)
    # First eight vertices are the original six-metre foundation box, verified
    # in the frozen R01 source. Lower only its bottom four corners to bedrock;
    # roof, window bands and all other building vertices remain exactly as R05.
    assert len(p.vertices)>8 and all(abs(p.vertices[i].co.z)<1e-6 for i in range(4))
    assert all(abs(p.vertices[i].co.z-6)<1e-6 for i in range(4,8))
    for i,v in enumerate(p.vertices):
        xx=x+v.co.x*scale;yy=y+v.co.y*scale;zz=-2.0 if i<4 else 4+v.co.z*scale
        if i<4:assert zz<surface_z(xx)
        g.v.append((xx,yy,zz))
    for f in p.polygons:g.f.append(tuple(offset+i for i in f.vertices));g.mi.append(f.material_index)
    xs=[x+p.vertices[i].co.x*scale for i in range(8)]
    assert 4+6*scale>max(surface_z(v) for v in xs)
    footing_tests.append({'archetype':k,'x':x,'scale':scale,'bottom_z':-2,'top_z':4+6*scale,'max_ground_z':max(surface_z(v) for v in xs)})

protos={}
for family,plan in plans.items():
    for variant in range(3):
        g=Mesh()
        # Existing circumferential arteries remain in 01_RING_STRUCTURE. Local
        # streets are flush curved surfaces instead of floating rectangle trays.
        patch(g,(0,-85),(178,6),ROAD);patch(g,(92.5,0),(3,164),ROAD)
        if family=='PLAZA':
            patch(g,(-18,28),(70,82),PARK,.35);patch(g,(49,-37),(42,66),PARK,.35)
            patch(g,(-6,-35),(106,7),CONCRETE)
        else:
            if family in {'RESIDENTIAL','MIXED_CORE','INDUSTRIAL'}:patch(g,(-3,0),(10,158),ROAD)
            patch(g,(0,78),(106,6),PARK,.35)
        for n,(k,x,y,scale) in enumerate(plan):
            building(g,k,x+(variant-1)*(3 if n%2 else -3),y,scale*(.90+.08*variant))
        o=g.object(f'R05B {family} prototype {variant}','09_PROTOTYPES');o.hide_render=True;o.hide_viewport=True;protos[family,variant]=o

layout={r['object']:r for r in meta['layout']};assert len(layout)==len(city)
positions={o.name:[list(r) for r in o.matrix_world] for o in city}
for o in city:
    row=layout[o.name];family=row['family'];variant=int(row['prototype'].rsplit(' ',1)[-1]);proto=protos[family,variant]
    o.data=proto.data;o['prototype']=proto.name;o['R05B_ground_contact']='Independent foundations and conforming roads'
    row['prototype']=proto.name
bpy.context.view_layer.update();after=signatures(protected);assert before==after
for o in city:assert max(abs(o.matrix_world[i][j]-positions[o.name][i][j]) for i in range(4) for j in range(4))<1e-6
SC['candidate']='R05B_INDEPENDENT_CITY_FOUNDATIONS';SC['source_sha']=os.environ['GITHUB_SHA'];SC['auto_qualified']=False
meta.update({'candidate':SC['candidate'],'source_sha':os.environ['GITHUB_SHA'],'parent_scene_sha256':PARENT,
 'intervention':'Remove uniform raised 190x180m superblock plates. Keep every building/site/height; use individual foundations and curved ground-attached pavement.',
 'protected_non_city_objects':len(protected),'protected_signatures_unchanged':True,
 'all_city_site_transforms_preserved':True,'footing_contact_checks':footing_tests,'layout':list(layout.values()),
 'gate':'NOT_AUTO_QUALIFIED','city_quality':'VISUAL_REVIEW_REQUIRED'})
p=OUT/'skyfold-r05b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2))
(OUT/'PROTECTED-SIGNATURES.json').write_text(json.dumps(before,indent=2));print('R05B_SAVED',meta['scene_sha256'],'VISUAL_REVIEW_REQUIRED')
