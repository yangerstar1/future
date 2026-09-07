"""R06: minimal physical node wash, after R05 first-hit diagnosis.
No source geometry/material/light/camera edits; two compact supported projectors.
Geometry checks are preconditions only, never automatic artistic acceptance.
"""
import bpy, json, hashlib, math, os, sys, shutil, time
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g3-r05';OUT=ROOT/'output/g3-r06';OUT.mkdir(parents=True,exist_ok=True)
DIAG=ROOT/'output/g3-r05-node-diagnosis/node-path-diagnosis.json'
EXPECTED='8ca4ca940a98e80d980fbd895f5ae7c27568b28ee361422bfe4ed267b7b8f02e'
REVISION='R06 physically supported purlin node wash after measured R05 occlusion'
s=bpy.context.scene
MODE=os.environ['G3_UPPER_MODE'];assert MODE in ['build','render']
assert bpy.app.version[:2]==(4,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def vec(v):return [float(c) for c in v]
def first_hit(at,p):
    delta=p-at;distance=delta.length
    h,pos,n,face,o,m=s.ray_cast(bpy.context.evaluated_depsgraph_get(),at,delta.normalized(),distance=distance+.004)
    return {'object':o.name,'position':vec(pos),'distance':(pos-at).length,'gap':distance-(pos-at).length,
      'hide_render':o.hide_render,'visible_shadow':o.visible_shadow} if h else None

def geometry_signature(names):
    h=hashlib.sha256()
    for name in sorted(names):
        o=bpy.data.objects[name];h.update(name.encode());h.update(o.type.encode())
        h.update(repr((o.hide_render,getattr(o,'visible_camera',None),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None),getattr(o,'visible_diffuse',None))).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
            for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.material_index,p.use_smooth)).encode())
        if o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:h.update(repr(tuple(p.co)).encode())
                for p in sp.bezier_points:h.update(repr((tuple(p.co),tuple(p.handle_left),tuple(p.handle_right))).encode())
        if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.type,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y,o.data.dof.use_dof,o.data.dof.aperture_fstop)).encode())
        if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color),getattr(o.data,'spot_size',None),getattr(o.data,'spot_blend',None),getattr(o.data,'shadow_soft_size',None))).encode())
    for frame in [1,301,330,348,451,660,840]:
        s.frame_set(frame);bpy.context.view_layer.update()
        for name in sorted(names):h.update(repr(tuple(tuple(r) for r in bpy.data.objects[name].matrix_world)).encode())
    s.frame_set(451);bpy.context.view_layer.update()
    h.update(repr((s.view_settings.exposure,s.view_settings.gamma,s.view_settings.look,s.view_settings.view_transform)).encode())
    return h.hexdigest()

if MODE=='build':
    master=BASE/'g3-bay-candidate.blend'
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==EXPECTED
    assert s.get('g3_revision')=='R05 readable arch nodes using physical uplights and satin column paint'
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
    diagnosis=json.loads(DIAG.read_text());assert diagnosis['source_master_sha256']==EXPECTED and diagnosis['source_master_unchanged']
    assert diagnosis['target_summary']['G3R04_eave_splice_plate.001']['lights']['G3R05_arch_wash']['centre_blockers']['Column_capital.007']==5
    originals=[o.name for o in s.objects];before=geometry_signature(originals)
    beam=bpy.data.objects['Longitudinal_roof_purlin.001'];lo,hi=bounds(beam)
    assert abs(lo[1]-6.2410178)<.001 and abs(lo[2]-6.2774773)<.001 and abs(hi[2]-6.3624773)<.001
    samples=[r for r in diagnosis['samples'] if r['surface']['object'] in ['Primary_elliptical_arch.003','G3R04_eave_splice_plate.001']]
    upper=[r for r in samples if r['surface']['position'][2]>5.02]
    assert len(upper)==25
    specifications=[]
    for x,target_x in [(-2.70,-3.965),(-1.30,-.035)]:
        pivot=Vector((x,5.95,6.20));target=Vector((target_x,6.40,5.45));axis=(target-pivot).normalized()
        emitter=pivot+axis*.071
        # Read-only mounting test from room side to the actual purlin face.
        probe=Vector((x,lo[1]-.09,(lo[2]+hi[2])/2));mount_hit=first_hit(probe,probe+Vector((0,.15,0)))
        assert mount_hit and mount_hit['object']==beam.name,('Mount differs from diagnosed geometry',mount_hit)
        specifications.append({'pivot':vec(pivot),'target':vec(target),'axis':vec(axis),'emitter':vec(emitter),
          'mount_contact':mount_hit,'energy':36,'spot_degrees':70,'spot_blend':.55,'radius':.028})
    def probe_samples(spec):
        at=Vector(spec['emitter']);axis=Vector(spec['axis']);rows=[]
        for r in upper:
            p=Vector(r['surface']['position']);n=Vector(r['surface']['normal']).normalized();direction=(p-at).normalized()
            hit=first_hit(at,p);angle=math.degrees(math.acos(max(-1,min(1,axis.dot(direction)))))
            ndotl=n.dot(-direction);clear=not hit or hit['gap']<.004
            rows.append({'sample_id':r['id'],'object':r['surface']['object'],'point':vec(p),'normal':vec(n),
              'normal_dot_to_light':ndotl,'angle_degrees':angle,'first_hit':hit,'clear':clear,
              'direct_possible':clear and ndotl>.03 and angle<35})
        return rows
    pre=probe_samples(specifications[0])
    report={'stage':'G3','revision':'R06','status':'BUILD_NOT_ART_PASS','parent_master_sha256':EXPECTED,
      'diagnosis_evidence_commit':'4cb68d0db15031059ea05054847ae75491569e64','diagnosis_report_sha256':sha(DIAG),
      'diagnosed_root':'Capital/column shadowing plus grazing incidence; upper-node points are inside the near floor spotlight cone.',
      'proposed_intervention':'Two compact projectors clamped to the existing eave-level roof purlin, aimed obliquely downward at the two bay nodes. Preserve both existing floor uplights and all source surfaces.',
      'mount_object':beam.name,'mount_bounds':[lo,hi],'specifications':specifications,'pre_fixture_paths':pre,
      'g4_allowed':False,'human_acceptance':False}
    (OUT/'upper-node-report.json').write_text(json.dumps(report,indent=2))
    assert sum(r['direct_possible'] for r in pre)>=21,('Proposed mount does not bypass measured blockage',sum(r['direct_possible'] for r in pre))
    c=bpy.data.collections.new('G3R06_purlin_node_luminaires');s.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
    paint=bpy.data.materials['G3R05_satin_column_paint'];steel=bpy.data.materials['G3_brushed_steel'];trim=bpy.data.materials['G3_satin_aged_brass']
    lens=material('G3R06_recessed_projector_optic',(.67,.69,.66),rough=.24,emission=.18)
    new_lights=[]
    for i,spec in enumerate(specifications):
        pivot=Vector(spec['pivot']);axis=Vector(spec['axis']);x=pivot.x;z=(lo[2]+hi[2])/2
        clamp=cube('G3R06_purlin_clamp',(x,lo[1]+.005,z),(.13,.026,.08),paint,.006)
        # Back of clamp overlaps purlin face by 18 mm; short real bracket joins body.
        assert bounds(clamp)[1][1]>lo[1] and bounds(clamp)[0][1]<lo[1]
        cylinder('G3R06_projector_stem',(x,lo[1]-.01,z),pivot,.014,paint,32)
        for dx in [-.038,.038]:cylinder('G3R06_clamp_fastener',(x+dx,lo[1]-.009,z),(x+dx,lo[1]-.019,z),.008,trim,12)
        cylinder('G3R06_projector_housing',pivot-axis*.07,pivot+axis*.05,.052,paint,48)
        cylinder('G3R06_projector_bezel',pivot+axis*.05,pivot+axis*.058,.055,trim,48)
        cylinder('G3R06_projector_optic',pivot+axis*.058,pivot+axis*.062,.044,lens,48)
        data=bpy.data.lights.new('G3R06_upper_node_wash','SPOT');data.energy=spec['energy'];data.color=(1,.95,.86)
        data.spot_size=math.radians(spec['spot_degrees']);data.spot_blend=spec['spot_blend'];data.shadow_soft_size=spec['radius']
        ob=bpy.data.objects.new('G3R06_upper_node_wash',data);c.objects.link(ob);ob.location=spec['emitter']
        ob.rotation_euler=axis.to_track_quat('-Z','Y').to_euler();new_lights.append(ob.name)
        spec['light_object']=ob.name;spec['clamp_object']=clamp.name;spec['clamp_bounds']=bounds(clamp)
    bpy.context.view_layer.update()
    post=probe_samples(specifications[0]);report['post_fixture_paths']=post
    assert sum(r['direct_possible'] for r in post)>=21,'Fixture self-shadow invalidates proposed intervention'
    report['post_fixture_direct_count']=sum(r['direct_possible'] for r in post);report['upper_sample_count']=len(upper)
    report['protected_before']=before;report['protected_after']=geometry_signature(originals)
    assert report['protected_before']==report['protected_after'],'Protected R05 geometry, motion, cameras, lights or ray visibility changed'
    s['g3_night_lights']=json.dumps(json.loads(s['g3_night_lights'])+new_lights)
    s['g3_revision']=REVISION;s['g3_r06_parent_sha256']=EXPECTED
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    s.frame_set(451);s.camera=bpy.data.objects['G3R03_complete_bay'];save(s,OUT/'g3-bay-candidate.blend')
    assert sha(master)==EXPECTED
    report['candidate_sha256']=sha(OUT/'g3-bay-candidate.blend');report['source_master_unchanged']=True
    report['source_materials_unchanged']=True;report['source_lights_unchanged']=True
    (OUT/'upper-node-report.json').write_text(json.dumps(report,indent=2))
    build=json.loads((BASE/'build-report.json').read_text());build.update(candidate_sha256=report['candidate_sha256'],revision='R06',revision_report='upper-node-report.json')
    (OUT/'build-report.json').write_text(json.dumps(build,indent=2))
    print('R06_SAVED_ART_REVIEW_PENDING',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g3-bay-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g3_revision')==REVISION
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights']);powers={n:bpy.data.objects[n].data.energy for n in night};bg=s.world.node_tree.nodes['Background']
    jobs=[('G3R03_roof_node','D01-roof-node.png','night',64,(1280,800)),
      ('G3R03_complete_bay','R06-complete-bay-night.png','night',64,(1440,900)),
      ('G3_D01','D01-glass-metal.png','night',64,(1280,800)),
      ('G3_bay','G3-bay-night.png','night',64,(1440,900)),
      ('G3R03_complete_bay','R06-complete-bay-neutral.png','neutral',48,(1440,900)),
      ('G3R04_door_unoccluded','D05-unoccluded-interface.png','night',48,(1280,800))]
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
    metrics=[]
    for cam,name,lighting,samples,res in jobs:
        assert time.time()<float(os.environ['G3_UPPER_DEADLINE']),'Bounded production time reached'
        for n,p in neutral.items():bpy.data.objects[n].data.energy=p if lighting=='neutral' else 0
        for n,p in powers.items():bpy.data.objects[n].data.energy=p if lighting=='night' else 0
        bg.inputs['Color'].default_value=(.16,.19,.23,1) if lighting=='neutral' else (.10,.145,.22,1)
        bg.inputs['Strength'].default_value=.65 if lighting=='neutral' else .18
        assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451)
        row.update(lighting=lighting,native_render=True,source_master_sha256=expected,adaptive_threshold=.04)
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('R06_VIEW_SAVED',name,flush=True)
    assert sha(master)==expected and sha(BASE/'g3-bay-candidate.blend')==EXPECTED
    (OUT/'reopen-check.json').write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'parent_master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_allowed':False,'human_acceptance':False},indent=2))
    print('R06_SIX_NATIVE_VIEWS_COMPLETE_REVIEW_PENDING',flush=True)
