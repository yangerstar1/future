"""Read-only R05 geometric diagnosis. Never saves or changes the source master.
Native scene ray casts are geometry evidence, not a photometric/BRDF solver.
Camera sample points are on visible evaluated surfaces, not guessed centres.
"""
import bpy, json, math, hashlib, os
from pathlib import Path
from collections import Counter
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path('workspaces/glasshouse-terminus')
BASE=ROOT/'output/g3-r05'
OUT=ROOT/'output/g3-r05-node-diagnosis'
OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e'
MASTER=BASE/'g3-bay-candidate.blend'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER.resolve() and sha(MASTER)==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('g3_revision')=='R05 readable arch nodes using physical uplights and satin column paint'
s.frame_set(451);bpy.context.view_layer.update()
assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
cam=bpy.data.objects['G3R03_roof_node']
dg=bpy.context.evaluated_depsgraph_get()
FAMILIES=('Primary_elliptical_arch','Load_column','Column_capital','G3R04_eave_splice_plate')
def xyz(v): return [round(float(c),7) for c in v]
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def materials(o):
    result=[]
    for m in o.data.materials:
        if not m:continue
        row={'name':m.name}
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED':
                    row['principled']={}
                    for k in ['Base Color','Metallic','Roughness','Coat Weight','Coat Roughness','Transmission Weight','Normal']:
                        if k not in n.inputs:continue
                        v=n.inputs[k];d=v.default_value
                        row['principled'][k]={'value':list(d) if hasattr(d,'__len__') else float(d),'linked':v.is_linked}
        result.append(row)
    return result

def cast(origin,direction,distance):
    """Raw evaluated world-space first hit; retain hidden-render flags explicitly."""
    h,p,n,face,o,m=s.ray_cast(dg,origin,direction,distance=distance)
    if not h:return None
    return {'object':o.name,'position':xyz(p),'normal':xyz(n),'face':face,
      'distance':(p-origin).length,'hide_render':o.hide_render,
      'visible_shadow':getattr(o,'visible_shadow',None),'visible_camera':getattr(o,'visible_camera',None)}

def path(origin,point,normal,axis=None,half_angle=None):
    delta=point-origin;dist=delta.length;direction=delta.normalized()
    hit=cast(origin,direction,dist+.003)
    ndotl=normal.dot(-direction)
    angle=math.degrees(math.acos(max(-1,min(1,axis.dot(direction))))) if axis is not None else None
    return {'source':xyz(origin),'distance':dist,'normal_dot_to_light':ndotl,
      'angle_from_axis_degrees':angle,'inside_outer_cone':angle<=half_angle if angle is not None else None,
      'first_hit':hit,'unoccluded_to_sample':hit is None or hit['distance']>=dist-.003,
      'first_hit_gap_to_sample':dist-hit['distance'] if hit else None}

lights=sorted([o for o in s.objects if o.type=='LIGHT' and o.name.startswith('G3R05_arch_wash')],key=lambda o:o.name)
assert len(lights)==2
light_rows=[]
for o in lights:
    light_rows.append({'name':o.name,'type':o.data.type,'position':xyz(o.matrix_world.translation),
      'axis':xyz((o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()),
      'energy':o.data.energy,'color':list(o.data.color),'spot_size_degrees':math.degrees(o.data.spot_size),
      'spot_blend':o.data.spot_blend,'radius':o.data.shadow_soft_size})

# Frozen native camera footprint, with aspect taken from the saved R05 evidence.
s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100
frame=cam.data.view_frame(scene=s)
minx=min(v.x for v in frame);maxx=max(v.x for v in frame)
miny=min(v.y for v in frame);maxy=max(v.y for v in frame);z=frame[0].z
origin=cam.matrix_world.translation.copy()
samples=[];counts=Counter();seen=set()
for iy in range(40):
    for ix in range(64):
        u=(ix+.5)/64;v=(iy+.5)/40
        local=Vector((minx+(maxx-minx)*u,miny+(maxy-miny)*v,z))
        direction=(cam.matrix_world.to_3x3()@local).normalized()
        h=cast(origin,direction,100)
        if not h:continue
        counts[h['object']]+=1
        if not h['object'].startswith(FAMILIES):continue
        p=Vector(h['position']);n=Vector(h['normal']).normalized()
        # Spatial bins preserve face/height variation while bounding the report.
        key=(h['object'],tuple(round(float(c),1) for c in n),round(p.x*5),round(p.y*5),round(p.z*5))
        if key in seen:continue
        seen.add(key)
        projection=world_to_camera_view(s,cam,p)
        assert abs(projection.x-u)<.002 and abs(projection.y-v)<.002
        row={'id':len(samples),'pixel':[round(u*1280),round((1-v)*800)],'surface':h,
          'camera_facing_normal_dot':n.dot((origin-p).normalized()),'light_paths':{}}
        for o in lights:
            axis=(o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized()
            at=o.matrix_world.translation.copy();half=math.degrees(o.data.spot_size)/2
            q=path(at,p,n,axis,half)
            # Finite-radius cross samples: a centre ray alone cannot prove full blockage.
            right=o.matrix_world.to_3x3()@Vector((1,0,0));up=o.matrix_world.to_3x3()@Vector((0,1,0))
            q['radius_cross_paths']=[path(at+offset*o.data.shadow_soft_size,p,n,axis,half)
              for offset in [right,-right,up,-up]]
            row['light_paths'][o.name]=q
        samples.append(row)
assert samples,'No real target surfaces reached; do not infer root cause from empty data'

objects=[]
for o in s.objects:
    if o.type not in ['MESH','CURVE']:continue
    lo,hi=bounds(o)
    relevant=(o.name.startswith(FAMILIES) and lo[0]>=-4.3 and hi[0]<=.3) or (hi[0]>=-4.8 and lo[0]<=.8 and hi[1]>=5.2 and lo[1]<=7 and hi[2]>=3.5 and lo[2]<=6.4) or o.name.startswith('G3R05_uplight')
    if not relevant:continue
    row={'name':o.name,'type':o.type,'bounds':[lo,hi],'matrix_world':[list(r) for r in o.matrix_world],
      'hide_render':o.hide_render,'visible_shadow':getattr(o,'visible_shadow',None),'materials':materials(o),
      'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in o.modifiers]}
    if o.type=='MESH' and o.name.startswith(FAMILIES):
        row['raw_polygon_normal_counts']=dict(Counter(str(tuple(round(c,2) for c in f.normal)) for f in o.data.polygons))
        row['negative_transform_determinant']=o.matrix_world.to_3x3().determinant()<0
    objects.append(row)
summary={}
for name in sorted(set(r['surface']['object'] for r in samples)):
    subset=[r for r in samples if r['surface']['object']==name];entry={'samples':len(subset),'lights':{}}
    for o in lights:
        qs=[r['light_paths'][o.name] for r in subset]
        entry['lights'][o.name]={'centre_blockers':dict(Counter(q['first_hit']['object'] for q in qs if q['first_hit'] and not q['unoccluded_to_sample'])),
          'inside_cone':sum(q['inside_outer_cone'] for q in qs),'unoccluded_centre':sum(q['unoccluded_to_sample'] for q in qs),
          'front_facing_to_light':sum(q['normal_dot_to_light']>0 for q in qs),
          'direct_centre_possible':sum(q['inside_outer_cone'] and q['unoccluded_to_sample'] and q['normal_dot_to_light']>0 for q in qs),
          'angle_range':[min(q['angle_from_axis_degrees'] for q in qs),max(q['angle_from_axis_degrees'] for q in qs)],
          'ndotl_range':[min(q['normal_dot_to_light'] for q in qs),max(q['normal_dot_to_light'] for q in qs)]}
    summary[name]=entry
report={'stage':'G3','revision':'R05_DIAGNOSIS_ONLY','source_master_sha256':EXPECTED,
  'source_evidence_commit':'4436b5cb5f870e834ff65639d1a1fbd365b9d4e3','run_id':os.environ.get('GITHUB_RUN_ID'),
  'source_sha':os.environ.get('GITHUB_SHA'),'blender':bpy.app.version_string,
  'camera':{'name':cam.name,'position':xyz(origin),'matrix_world':[list(r) for r in cam.matrix_world],
    'lens':cam.data.lens,'frame':451,'native_resolution':[1280,800],'exposure':s.view_settings.exposure,
    'forward':xyz((cam.matrix_world.to_3x3()@Vector((0,0,-1))).normalized())},
  'lights':light_rows,'target_summary':summary,'camera_first_hit_counts':dict(counts),
  'samples':samples,'nearby_geometry':objects,
  'other_lights':[{'name':o.name,'type':o.data.type,'position':xyz(o.matrix_world.translation),'energy':o.data.energy,
    'axis':xyz((o.matrix_world.to_3x3()@Vector((0,0,-1))).normalized())} for o in s.objects if o.type=='LIGHT'],
  'limits':['World-space evaluated geometry first hits; not full Cycles transport or BRDF integration.',
    'Normals are geometric, not interpolated shader bump normals. Finite source tested at centre and four radius offsets, not exhaustively.',
    'Hidden-render/shadow flags retained. A flagged hit must be reviewed before calling it a physical occluder.',
    'No geometry, lighting, materials, ray flags, exposure or cameras are saved/edited; frame and probe render dimensions are memory only.'],
  'source_master_unchanged':sha(MASTER)==EXPECTED,'g4_allowed':False,'human_acceptance':False}
assert report['source_master_unchanged']
(OUT/'node-path-diagnosis.json').write_text(json.dumps(report,indent=2))
(OUT/'node-path-summary.json').write_text(json.dumps({k:report[k] for k in ['source_master_sha256','camera','lights','target_summary','source_master_unchanged','limits']},indent=2))
print('R05_READ_ONLY_PATH_DIAGNOSIS_COMPLETE',json.dumps(summary),flush=True)
