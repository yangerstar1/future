"""R03: lower only the camera-side working pier; preserve ship/city/cameras/light.
Run after loading the immutable R02 scene. Native helpers are reused by verified AST.
This is a G2 visibility/connection repair, never an automatic art qualification.
"""
import ast, hashlib, json, math, os
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ['SKYFOLD_OUT']).resolve()
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'output/r02/skyfold-r02.blend'
PARENT = 'dd44440aaf67972cf95cd9fd2623c5e434e4aad5dc1c93bcdafe2b7164dcb18b'
assert bpy.app.version[:3] == (4, 5, 13), bpy.app.version_string
assert Path(bpy.data.filepath).resolve() == BASE.resolve()
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == PARENT
source = (ROOT / 'build_scene_r01.py').read_bytes()
assert hashlib.sha256(source).hexdigest() == '1bb627df3637886da7e2d89107d6230e1caec87a50501c1d2e0eeb1a2b11249b'
SC = bpy.context.scene
COL = {c.name: c for c in bpy.data.collections}
M = [bpy.data.materials[n] for n in ['Pearl ceramic-coated alloy', 'Structural graphite steel', 'Pale structural composite', 'Oxide orange workzone coating', 'Inset blue-black facade glazing', 'Brushed bare metal', 'Foot-worn dark deck metal', 'Warm service luminaires', 'Wheel rubber', 'City pale panels', 'Neutral inspection clay']]
PAINT, DARK, CONCRETE, ORANGE, GLASS, SILVER, DECK, LIGHT, RUBBER, CITY, GRAY = range(11)
D, T = '03_DOCK', '06_TRANSPORT'
CACHE = {}
wanted = {'Mesh', 'box', 'beam', 'tube', 'rail_pair'}
defs = [n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in wanted]
assert {n.name for n in defs} == wanted
exec(compile(ast.Module(body=defs, type_ignores=[]), 'VERIFIED_R01_HELPERS', 'exec'), globals())

# Capture protected geometry, transforms and node values, not just object counts.
def signature(collection):
    rows = []
    for o in sorted(COL[collection].objects, key=lambda q: q.name):
        r = {'name': o.name, 'type': o.type, 'matrix': [list(v) for v in o.matrix_world], 'hidden': [o.hide_render, o.hide_viewport]}
        if o.type == 'MESH':
            r['vertices'] = [list(v.co) for v in o.data.vertices]
            r['faces'] = [(list(p.vertices), p.material_index) for p in o.data.polygons]
        if o.type == 'CAMERA':
            r['camera'] = [o.data.lens, o.data.sensor_width, o.data.shift_x, o.data.shift_y, o.data.clip_start, o.data.clip_end]
        if o.type == 'LIGHT':
            r['light'] = [o.data.type, o.data.energy, list(o.data.color)]
        rows.append(r)
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()

def node_signature():
    rows = []
    for owner in list(bpy.data.materials) + list(bpy.data.worlds):
        if not owner.use_nodes:
            continue
        for node in owner.node_tree.nodes:
            values = []
            for socket in node.inputs:
                if hasattr(socket, 'default_value'):
                    val = socket.default_value
                    try:
                        val = list(val)
                    except TypeError:
                        pass
                    values.append((socket.name, val))
            rows.append((owner.name, node.name, node.bl_idname, values))
    return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()

protected = ['01_RING_STRUCTURE', '02_CITY_INSTANCES', '04_FREIGHTER', '05_MAINTENANCE', '07_LIGHTS', '08_CAMERAS', '09_PROTOTYPES']
bpy.context.view_layer.update()
before = {c: signature(c) for c in protected}
materials_before = node_signature()
changes = []

def select(prefix, x_limit=None):
    return [o for o in SC.objects if o.name.startswith(prefix) and (x_limit is None or abs(o.location.x) < x_limit)]

def move_down(o, dz):
    changes.append({'object': o.name, 'operation': 'translate_z', 'delta': -dz})
    o.location.z -= dz

def lower_top(o, dz):
    # Change a vertical member's top, preserving its grounded lower endpoint.
    h = o.dimensions.z
    assert h > dz + 1, (o.name, h, dz)
    o.scale.z *= (h-dz)/h
    o.location.z -= dz/2
    changes.append({'object': o.name, 'operation': 'shorten_top', 'delta': -dz})

def lower_bottom(o, dz):
    h = o.dimensions.z
    o.scale.z *= (h+dz)/h
    o.location.z -= dz/2
    changes.append({'object': o.name, 'operation': 'extend_bottom', 'delta': -dz})

def replace_beam(o, a, b, width, depth):
    name = o.name
    bpy.data.objects.remove(o, do_unlink=True)
    beam(name, a, b, width, depth, SILVER, D)
    changes.append({'object': name, 'operation': 'replace_endpoints', 'a': a, 'b': b})

# Sparse ray checks are diagnostics, not an image score or a visual acceptance test.
def hull_visibility(camera_name):
    bpy.context.view_layer.update()
    camera = bpy.data.objects[camera_name]
    deps = bpy.context.evaluated_depsgraph_get()
    hull = bpy.data.objects['Freighter tapered pressure hull']
    ship_names = {o.name for o in COL['04_FREIGHTER'].objects}
    hits = []
    for poly in hull.data.polygons:
        target = hull.matrix_world @ poly.center
        uv = world_to_camera_view(SC, camera, target)
        if not (uv.z > 0 and 0 < uv.x < 1 and 0 < uv.y < 1):
            continue
        ray = target - camera.location
        hit, loc, normal, face, obj, matrix = SC.ray_cast(deps, camera.location, ray.normalized(), distance=ray.length+2)
        name = obj.name if hit else None
        hits.append({'polygon': poly.index, 'first_object': name, 'ship_first': name in ship_names})
    return {'camera': camera_name, 'in_frame_samples': len(hits), 'ship_first_samples': sum(h['ship_first'] for h in hits), 'samples': hits, 'limitation': 'sparse polygon-centre rays, not visible-area percentage or art qualification'}

visibility_before = hull_visibility('O01_HERO')
DROP = 240.0
LOW, HIGH, UPPER = 194.43, 272.065, 512.065
assert len(select('Long docking pier', 100)) == 1
assert len(select('Dock grounded pylon', 100)) == 6
for prefix in ['Long docking pier', 'Pier box girder', 'Loader tower base', 'R02 aft gantry footing']:
    for o in select(prefix, 100):
        move_down(o, DROP)
for o in select('Dock grounded pylon', 100):
    lower_top(o, DROP)
for prefix in ['Loader vertical lift', 'R02 aft gantry column']:
    for o in select(prefix, 100):
        lower_bottom(o, DROP)
for o in select('R02 rooted pier diagonal', 100):
    y = o.location.y
    replace_beam(o, (-48,y-36,5), (43,y+36,252), 9, 9)
for o in select('Loader bridge support', 150):
    y = o.location.y
    replace_beam(o, (0,y,278), (198,y,589), 7, 7)

# Cargo and incoming upper rail must move with their supporting working deck.
for prefix in ['Cargo staging pallet', 'Dock cargo container', 'Container side stiffener', 'R02 upper lift transfer']:
    for o in select(prefix):
        move_down(o, DROP)
upper_rail_count = 0
for o in select('Continuous service rail'):
    pts = [p for sp in o.data.splines for p in sp.points]
    if min(p.co.z for p in pts) > 500:
        o.data = o.data.copy()
        for sp in o.data.splines:
            for p in sp.points:
                p.co.z -= DROP
        upper_rail_count += 1
assert upper_rail_count == 2
for o in select('R02 lift landing edge'):
    if o.location.z > 500:
        move_down(o, DROP)
for o in select('R02 lift guide tower'):
    lower_top(o, DROP)
for o in select('R02 lift side lattice'):
    bpy.data.objects.remove(o, do_unlink=True)
for z in [210,234,258]:
    beam('R03 incoming lift side lattice', (-92,614,z), (-92,626,min(z+22,HIGH+8)), .55,.55,SILVER,T)
    beam('R03 incoming lift side lattice', (-80,626,z), (-80,614,min(z+22,HIGH+8)), .55,.55,SILVER,T)

# Preserve the high rear cross-dock and far pier; provide a real return lift instead
# of leaving a dangling bridge or disguising a vertical discontinuity as rail.
old = bpy.data.objects['Aft cross-dock circulation bridge']
assert abs(old.location.z - 503) < .01
bpy.data.objects.remove(old, do_unlink=True)
# Four solid slabs form the same bridge envelope, with a 14x14m lift aperture.
for x0,x1,y0,y1 in [(-65,-53,1595,1705),(-39,625,1595,1705),(-53,-39,1595,1601),(-53,-39,1615,1705)]:
    box('R03 rear bridge aperture slab', ((x0+x1)/2,(y0+y1)/2,503), (x1-x0,y1-y0,18), CONCRETE,D,.4)
for x in [-53,-39]:
    for y in [1601,1615]:
        box('R03 return lift base shoe', (x,y,273), (3,3,2), ORANGE,T,.12)
        box('R03 return lift guide', (x,y,394), (1.2,1.2,240), DARK,T,.08)
for z in range(280,495,24):
    beam('R03 return lift bracing', (-53,1601,z), (-53,1615,z+22), .45,.45,SILVER,T)
box('R03 return lift platform', (-46,1608,271.85), (10,10,.3), ORANGE,T,.06)
rail_pair([(-46,1602,HIGH),(-46,1608,HIGH)])
# Both rear landings are real; the lift is deliberately static, not a motion claim.
rail_pair([(-46,1608,UPPER),(-46,1655,UPPER),(-34,1667,UPPER),(548,1667,UPPER),(560,1655,UPPER),(560,1605,UPPER)])
ground = 1600-math.sqrt(1600**2-15**2)
box('R03 rear rooted foundation', (15,1640,ground+2), (24,24,4), CONCRETE,D,.3)
box('R03 rear rooted riser', (15,1640,(ground+4+494)/2), (8,10,494-ground-4), DARK,D,.2)
beam('R03 rear riser brace', (15,1640,450), (72,1640,494), 4,4,SILVER,D)

bpy.context.view_layer.update()
after = {c: signature(c) for c in protected}
assert before == after, 'Protected collection changed'
assert materials_before == node_signature(), 'Material/light environment changed'
visibility_after = hull_visibility('O01_HERO')
# Additional diagnostic only; every original R02 camera is still preserved.
cam = bpy.data.cameras.new('O05_LIFT_R03_DIAGNOSTIC')
cam.lens = 38; cam.clip_end = 20000
obj = bpy.data.objects.new(cam.name, cam);COL['08_CAMERAS'].objects.link(obj)
obj.location = (-188,484,276)
obj.rotation_euler = (Vector((-66,620,238))-obj.location).to_track_quat('-Z','Y').to_euler()
for o in SC.objects:
    assert all(math.isfinite(v) for row in o.matrix_world for v in row), o.name
SC.camera = bpy.data.objects['O01_HERO']
SC['candidate'] = 'R03_NEAR_PIER_REPAIR'
SC['source_sha'] = os.environ['GITHUB_SHA']
SC['quality_status'] = 'G2_REVIEW_REQUIRED_NOT_QUALIFIED'
manifest = json.loads((ROOT/'output/r02/BUILD-MANIFEST.json').read_text())
manifest.update(candidate=SC['candidate'],source_sha=SC['source_sha'],parent_scene_sha256=PARENT,near_pier_drop_m=DROP,protected_before=before,protected_after=after,materials_signature=materials_before,changes=changes,visibility_before=visibility_before,visibility_after=visibility_after,visual_gate='NOT_REVIEWED',auto_qualified=False)
manifest['functional_route']['lift_upper'] = [-86,620,HIGH]
manifest['functional_route']['upper'] = [[x,y,z-DROP] for x,y,z in manifest['functional_route']['upper']]
manifest['functional_route']['return_lift'] = {'lower':[-46,1608,HIGH],'upper':[-46,1608,UPPER]}
manifest['scales']['R02_berth_raise_m'] = manifest['scales'].pop('berth_raise_m')
manifest['scales']['near_pier_deck_top_m'] = 272.0
manifest['scales']['far_pier_deck_top_m'] = 512.0
manifest['cameras'][obj.name] = {'matrix':[list(row) for row in obj.matrix_world], 'lens':cam.lens, 'role':'ADDITIONAL_DIAGNOSTIC_NOT_A_REPLACEMENT'}
manifest['tests']['protected_collections_unchanged'] = True
manifest['tests']['material_world_nodes_unchanged'] = True
manifest['tests']['upper_rail_pair_relocated'] = upper_rail_count
manifest['geometry']['objects'] = len(SC.objects)
manifest['geometry']['meshes'] = len(bpy.data.meshes)
manifest['quality_map']['dock'] = 'Two-level dock; lower near pier; existing interface tops and far pier preserved; connection/visibility review required'
path = OUT/'skyfold-r03.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
manifest['scene_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('R03_SAVED',manifest['scene_sha256'], 'RAYS',visibility_before['ship_first_samples'],visibility_after['ship_first_samples'],'NOT_A_VISUAL_PASS')
