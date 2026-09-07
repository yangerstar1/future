"""R05 targeted response to actual R04 D01 darkness; not G4 or acceptance.
Reuse the verified R04 master, native helpers and material family. Preserve source
geometry/cameras/animation, glass responses, ray visibility and exposure.
"""
import bpy,json,hashlib,math,os,sys,shutil,time
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,cube,cylinder,save,render
BASE=Path('workspaces/glasshouse-terminus/output/g3-r04').resolve()
OUT=Path('workspaces/glasshouse-terminus/output/g3-r05').resolve();OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='18348be4c401601706e10e4346a32bf5e0c406fec2448e1a53290f7840b8a854'
mode=os.environ['G3_NODE_MODE'];assert mode in ['build','render']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
if mode=='build':
    parent=BASE/'g3-bay-candidate.blend'
    assert Path(bpy.data.filepath).resolve()==parent and digest(parent)==EXPECTED
    assert s.get('g3_revision')=='R04 physical sconces, structural-bay palette and unobstructed witnesses'
    s.frame_set(451);bpy.context.view_layer.update()
    originals=[o.name for o in s.objects if o.type in ['MESH','CURVE','CAMERA']]
    def signature():
        s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
        for name in sorted(originals):
            o=bpy.data.objects[name];h.update(name.encode());h.update(repr(tuple(tuple(r) for r in o.matrix_world)).encode())
            if o.type=='MESH':
                for v in o.data.vertices:h.update(repr(tuple(v.co)).encode())
            if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end)).encode())
        return h.hexdigest()
    before=signature();report={'stage':'G3','revision':'R05','status':'CHALLENGER_NOT_ACCEPTED',
      'parent_sha256':EXPECTED,'parent_evidence_commit':'a2b7d9d3c90e928a00bca7898247d764c83afe8a',
      'reviewed_r04_core_artifact':10020833705,'reviewed_core_zip_sha256':'ac73bfb391ee46270e76f2a770bdea32450d1692801637747dbd8b4cd58ad623',
      'issue':'G3-D01-DARK: R04 fixes glare but obscures actual arch/splice craft',
      'material_edits':[],'uplights':[],'g4_allowed':False,'human_acceptance':False,
      'preserved':['source meshes and transforms','all source cameras','motion','glass reflection/transmission','light ray visibility','exposure0/AgX'],
      'scope':'Local arch and column paint plus two small supported uplight fixtures, no full-scene expansion.'}
    paint=bpy.data.materials['G3_bottle_green_enamel'].copy();paint.name='G3R05_satin_column_paint'
    p=paint.node_tree.nodes['Principled BSDF']
    assert abs(p.inputs['Metallic'].default_value-.42)<.001
    p.inputs['Base Color'].default_value=(.033,.070,.055,1)
    p.inputs['Metallic'].default_value=.12;p.inputs['Roughness'].default_value=.32;p.inputs['Coat Weight'].default_value=.23
    report['paint_recipe']={'reuse':'Satin-paint recipe already present in polish_g3_r04.py; applied here to the verified later source, not a claim that the failed alternative produced a model.','base_color':[.033,.070,.055],'metallic':.12,'roughness':.32,'coat':.23}
    families=('Primary_elliptical_arch','Load_column','Column_capital','G3R04_eave_splice_plate')
    for o in list(s.objects):
        if o.type!='MESH' or not o.name.startswith(families):continue
        lo,hi=bounds(o)
        if lo[0]<-4.25 or hi[0]>.25:continue
        assert o.active_material.name=='G3_bottle_green_enamel',(o.name,o.active_material.name)
        o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(paint)
        report['material_edits'].append(o.name)
    assert len([n for n in report['material_edits'] if n.startswith('Primary_')])==2
    c=bpy.data.collections.new('G3R05_arch_wash_luminaires');s.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
    steel=bpy.data.materials['G3_brushed_steel'];trim=bpy.data.materials['G3_satin_aged_brass']
    lens=material('G3R05_uplight_diffuser',(.73,.70,.61),rough=.18,emission=.4)
    lights=[];walk=bpy.data.objects['FILM_04_CONTINUOUS_WALK']
    for arch,offset in [(-4,.34),(0,-.34)]:
        x=arch+offset;at=Vector((x,6.00,1.36));target=Vector((arch+offset*.28,6.34,5.05));direction=(target-at).normalized()
        distances=[]
        for f in range(391,661):
            s.frame_set(f);v=walk.matrix_world.translation
            distances.append(math.hypot(v.x-x,v.y-at.y))
        assert min(distances)>.55,'New fixture would intrude on the preserved route'
        s.frame_set(451)
        foot=cube('G3R05_uplight_foot',(x,6.00,1.19),(.15,.17,.08),paint,.018)
        body=cylinder('G3R05_uplight_body',at-direction*.14,at,.069,paint,48)
        cylinder('G3R05_uplight_bezel',at,at+direction*.014,.073,trim,48)
        cylinder('G3R05_uplight_lens',at+direction*.014,at+direction*.017,.060,lens,48)
        bpy.context.view_layer.update()
        assert abs(bounds(foot)[0][2]-1.15)<.001 and bounds(body)[0][2]<bounds(foot)[1][2], 'Fixture support contact failed'
        d=bpy.data.lights.new('G3R05_arch_wash','SPOT');d.energy=220;d.color=(1,.91,.76)
        d.spot_size=math.radians(50);d.spot_blend=.70;d.shadow_soft_size=.035
        ob=bpy.data.objects.new('G3R05_arch_wash',d);c.objects.link(ob);ob.location=at+direction*.032
        ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();lights.append(ob.name)
        report['uplights'].append({'object':ob.name,'position':list(ob.location),'target':list(target),'energy':220,'spot_angle_degrees':50,'minimum_xy_walk_clearance':min(distances),'supported_fixture':True,'foot_bounds':bounds(foot),'body_bounds':bounds(body)})
    s['g3_night_lights']=json.dumps(json.loads(s['g3_night_lights'])+lights)
    assert signature()==before,'Protected source geometry/cameras changed'
    report['protected_before']=before;report['protected_after']=signature()
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    s['g3_revision']='R05 readable arch nodes using physical uplights and satin column paint'
    s.frame_set(451);s.camera=bpy.data.objects['G3R03_complete_bay'];assert s.view_settings.exposure==0
    save(s,OUT/'g3-bay-candidate.blend');assert digest(parent)==EXPECTED
    report['candidate_sha256']=digest(OUT/'g3-bay-candidate.blend')
    (OUT/'node-light-report.json').write_text(json.dumps(report,indent=2))
    build=json.loads((BASE/'build-report.json').read_text());build.update(candidate_sha256=report['candidate_sha256'],revision='R05',revision_report='node-light-report.json')
    (OUT/'build-report.json').write_text(json.dumps(build,indent=2))
    print('R05_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g3-bay-candidate.blend';assert Path(bpy.data.filepath).resolve()==master
    assert s.get('g3_revision')=='R05 readable arch nodes using physical uplights and satin column paint'
    expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert digest(master)==expected
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights']);power={n:bpy.data.objects[n].data.energy for n in night};bg=s.world.node_tree.nodes['Background']
    jobs=[('G3R03_roof_node','D01-roof-node.png','night',48,(1280,800)),
      ('G3R03_complete_bay','R05-complete-bay-night.png','night',64,(1440,900)),
      ('G3_D01','D01-glass-metal.png','night',64,(1280,800)),
      ('G3_bay','G3-bay-night.png','night',64,(1440,900)),
      ('G3R03_complete_bay','R05-complete-bay-neutral.png','neutral',48,(1440,900)),
      ('G3R04_door_unoccluded','D05-unoccluded-interface.png','night',48,(1280,800))]
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
    metrics=[]
    for cam,name,light,samples,res in jobs:
        assert time.time()<float(os.environ['G3_NODE_DEADLINE']),'Bounded production time reached'
        for n,p in neutral.items():bpy.data.objects[n].data.energy=p if light=='neutral' else 0
        for n,p in power.items():bpy.data.objects[n].data.energy=p if light=='night' else 0
        bg.inputs['Color'].default_value=(.16,.19,.23,1) if light=='neutral' else (.10,.145,.22,1)
        bg.inputs['Strength'].default_value=.65 if light=='neutral' else .18;assert s.view_settings.exposure==0
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451)
        row.update(lighting=light,native_render=True,source_master_sha256=expected,adaptive_threshold=.04)
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
        print('R05_VIEW_SAVED',name,flush=True)
    assert digest(master)==expected
    (OUT/'reopen-check.json').write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'images':len(metrics),'scope':'Six targeted real images; not whole-scene acceptance or a new film','human_acceptance':False},indent=2))
    print('R05_TARGETED_VIEWS_RENDERED_REVIEW_PENDING',flush=True)
