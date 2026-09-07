"""G2 spatial/camera challenger from the verified complete master; NOT final art.
Only bridge supports and exterior framing are edited. Existing scene, materials,
walk route, train animation, observation cameras and helpers are reused.
"""
import bpy, bmesh, hashlib, json, math, os, sys
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene_common import cube, camera, render, save

BASE = Path('workspaces/glasshouse-terminus/output/g2').resolve()
OUT = Path('workspaces/glasshouse-terminus/output/g2-review').resolve()
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED = 'ef6fa3dd7e291564f2d1c158cb002f07dcf05c071c6f72e34e95c68ca2a22bf0'
master = BASE / 'g2-complete-whitebox.blend'
assert hashlib.sha256(master.read_bytes()).hexdigest() == EXPECTED, 'Parent bytes differ; do not adapt blindly'
s = bpy.context.scene
assert Path(bpy.data.filepath).resolve() == master
assert s.get('phase') == 'G2_WHITEBOX_NOT_FINAL_ART'
assert bpy.app.version[:2] == (4, 5)
s.frame_set(451)
coll = bpy.data.collections.get('E_curved_viaduct_and_track')
assert coll and bpy.data.collections.get('A_complete_glasshouse')
piers = [o for o in coll.objects if o.name.startswith('Viaduct_pier')]
feet = [o for o in coll.objects if o.name.startswith('Viaduct_bedrock_footing')]
assert len(piers) == len(feet) == 12, 'Expected old repeated span-end supports; inspect changed source'

def groups(objects):
    result = defaultdict(list)
    for ob in objects:
        assert ob.type == 'MESH' and ob.parent is None and ob.animation_data is None
        result[(round(ob.location.x, 5), round(ob.location.y, 5))].append(ob)
    assert len(result) == 7 and sorted(map(len, result.values())) == [1,1,2,2,2,2,2]
    return result

pg, fg = groups(piers), groups(feet)
assert set(pg) == set(fg)
protected_names = [o.name for o in s.objects if o not in piers + feet]

def protected_geometry():
    """Exact local mesh coordinates + evaluated transforms, excluding two lens edits."""
    h = hashlib.sha256()
    for name in sorted(protected_names):
        ob = bpy.data.objects[name]
        h.update(name.encode())
        h.update(repr(tuple(tuple(r) for r in ob.matrix_world)).encode())
        if ob.type == 'MESH':
            for v in ob.data.vertices: h.update(repr(tuple(v.co)).encode())
        if ob.type == 'CAMERA' and name not in ['C01_exterior_hero','FILM_01_HERO']:
            h.update(repr(ob.data.lens).encode())
    return h.hexdigest()

protected_before = protected_geometry()
report = {'stage':'G2', 'status':'CHALLENGER_NOT_ACCEPTED', 'parent_blend_sha256':EXPECTED,
          'issues':['G2-F01 exterior crop','G2-S01 duplicated/misaligned span-end supports'],
          'prior_supports':[], 'repaired_supports':[], 'framing':{},
          'unchanged':['A-D geometry','track centerline and rails','train/door/walk keyframes',
                       'all materials','all lights and exposure','C02-C09 cameras'],
          'independent_reviewer':False, 'g1_browser_status':'BLOCKED_UNCHANGED'}
for key, obs in sorted(pg.items()):
    report['prior_supports'].append({'xy':key,'objects':[{'name':o.name,'z':o.location.z,'height':o.dimensions.z,'yaw':o.rotation_euler.z} for o in obs]})
(OUT/'repair-progress.json').write_text(json.dumps(report, indent=2))

# Additional neutral close view, not a replacement for any failing original angle.
key = sorted(pg)[2]
p = pg[key][0].location.copy()
joint_cam = camera('QA_G2_bridge_joint', (p.x+6,p.y+11,-1.5), (p.x,p.y,-7.1), 48)
# Timeline camera markers would override explicit diagnostic cameras at frame_set.
markers = [(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers]
s.timeline_markers.clear()
metrics = [render(s,joint_cam,OUT/'bridge-joint-before.png',res=(960,600),samples=24,frame=451)]

# A support belongs to a shared span boundary once, with its local track tangent.
# A bearing cap covers the change in chord direction; no floating decoration.
stone = bpy.data.materials['WB_stone']
for i, key in enumerate(sorted(pg)):
    ob = sorted(pg[key], key=lambda o:o.name)[0]
    foot = sorted(fg[key], key=lambda o:o.name)[0]
    x,y = key
    yaw = -math.asin(max(-1,min(1,(-24-x)/50))) if x < -24 else 0.0
    for duplicate in pg[key]:
        if duplicate != ob: bpy.data.objects.remove(duplicate, do_unlink=True)
    for duplicate in fg[key]:
        if duplicate != foot: bpy.data.objects.remove(duplicate, do_unlink=True)
    # The existing footing top is -22.05. Keep a 5 cm overlap, stop below the cap.
    bottom, top = -22.10, -7.15
    ob.location.z = (bottom+top)/2
    ob.dimensions.z = top-bottom
    ob.rotation_euler.z = yaw
    foot.rotation_euler.z = yaw
    cap = cube(f'Viaduct_bearing_cap_G2R01_{i:02d}',(x,y,-7.15),(2.40,4.25,.60),stone,.035)
    cap.rotation_euler.z = yaw
    for c in list(cap.users_collection): c.objects.unlink(cap)
    coll.objects.link(cap); cap['component'] = coll.name
    report['repaired_supports'].append({'xy':key,'pier':ob.name,'footing':foot.name,'cap':cap.name,
          'yaw':yaw,'pier_bottom':bottom,'pier_top':top,'cap_z_range':[-7.45,-6.85],
          'arch_spring_z':-7.2,'footing_top':-22.05})
bpy.context.view_layer.update()
assert protected_geometry() == protected_before, 'Protected scene changed during support repair'
metrics.append(render(s,joint_cam,OUT/'bridge-joint-after.png',res=(960,600),samples=24,frame=451))
old_cam = bpy.data.objects['C01_exterior_hero']
metrics.append(render(s,old_cam,OUT/'C01-repaired-same-camera.png',res=(1280,800),samples=24,frame=451))

# Fit the whole hall envelope, without changing its shape, view angle or exposure.
hall = bpy.data.collections['A_complete_glasshouse']
pts = [o.matrix_world@Vector(v) for o in hall.objects if o.type in {'MESH','CURVE'} for v in o.bound_box]
lo = [min(p[i] for p in pts) for i in range(3)]
hi = [max(p[i] for p in pts) for i in range(3)]
corners = [Vector((x,y,z)) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]

def extents(cam, frame):
    s.frame_set(frame); bpy.context.view_layer.update()
    q = [world_to_camera_view(s,cam,p) for p in corners]
    return {'frame':frame,'x':[min(p.x for p in q),max(p.x for p in q)],
            'y':[min(p.y for p in q),max(p.y for p in q)],'min_depth':min(p.z for p in q)}

def fit(cam, frames, resolution):
    s.render.resolution_x,s.render.resolution_y = resolution
    old = cam.data.lens
    before = [extents(cam,f) for f in frames]
    for step in range(25):
        cam.data.lens = old - step*.5
        after = [extents(cam,f) for f in frames]
        if all(e['min_depth']>0 and .035<=e['x'][0] and e['x'][1]<=.965 and .035<=e['y'][0] and e['y'][1]<=.965 for e in after): break
    else: raise RuntimeError('Lens-only framing cannot fit conservatively; stop for composition review')
    report['framing'][cam.name] = {'old_lens':old,'new_lens':cam.data.lens,'before':before,'after':after,'resolution':resolution}

fit(old_cam,[451],(1280,800))
fit(bpy.data.objects['FILM_01_HERO'],[1,31,61,90],(1280,720))
s.frame_set(451); bpy.context.view_layer.update()
assert protected_geometry() == protected_before, 'Protected geometry/cameras changed'
report['protected_geometry_hash_before'] = protected_before
report['protected_geometry_hash_after'] = protected_geometry()
for name, frame, camname in markers:
    marker = s.timeline_markers.new(name,frame=frame)
    if camname: marker.camera = bpy.data.objects[camname]
for o in bpy.data.collections['QA_scale_and_route'].objects: o.hide_render = True
s.frame_set(1);s.camera=bpy.data.objects['FILM_01_HERO']
s['g2_challenger']='G2-R01 supports and framing';s['parent_blend_sha256']=EXPECTED
s.render.resolution_x,s.render.resolution_y=1280,720
save(s,OUT/'g2-complete-whitebox.blend')
report['candidate_blend_sha256'] = hashlib.sha256((OUT/'g2-complete-whitebox.blend').read_bytes()).hexdigest()
(OUT/'repair-report.json').write_text(json.dumps(report,indent=2))
for name in ['layout-and-route.json','motion-states.json']:
    (OUT/name).write_bytes((BASE/name).read_bytes())

# All required observations come from this candidate, not mixed old/new renders.
s.timeline_markers.clear();s.frame_set(451)
for o in bpy.data.collections['QA_scale_and_route'].objects: o.hide_render=False
for key in ['C01','C02','C03','C04','C05','C06','C07','C09']:
    cam = next(o for o in s.objects if o.type=='CAMERA' and o.name.startswith(key+'_'))
    metrics.append(render(s,cam,OUT/(key+'.png'),res=(1280,800),samples=24,frame=451))
# Same disposable true-section procedure as the existing build_g2.py.
for o in bpy.data.collections['QA_scale_and_route'].objects: o.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
for ob in list(s.objects):
    if ob.type=='CURVE': ob.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.convert(target='MESH')
for ob in list(s.objects):
    if ob.type!='MESH' or ob.name.startswith('Ocean'): continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    plane=ob.matrix_world.inverted()@Vector((-2,0,0))
    normal=(ob.matrix_world.to_3x3().transposed()@Vector((1,0,0))).normalized()
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=plane,plane_no=normal,clear_inner=True,dist=.0001)
    bm.to_mesh(ob.data);bm.free();ob.data.update()
metrics.append(render(s,bpy.data.objects['C08_true_section'],OUT/'C08.png',res=(1280,800),samples=24,frame=451))
(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
assert hashlib.sha256(master.read_bytes()).hexdigest()==EXPECTED, 'Original master changed'
print('G2_R01_FIXED_VIEWS_COMPLETE_REVIEW_PENDING', report['candidate_blend_sha256'])
