"""G4 R02 targeted response to actually reviewed R01 C01/C03.
Reuse R02 dry-stone mapping already proven in refine_g3.py; no new asset download.
Replace finite sky-light cards with a continuous native World shader, not ray hiding.
All architectural geometry, fixtures, animation and original cameras remain intact.
"""
import bpy,json,os,sys,time,hashlib,shutil
from pathlib import Path
from array import array
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import save,render
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-r01';OUT=ROOT/'output/g4-r02';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='2a7197af8f42ae6a543d1b028b4617a4784ec4fb262874e3b46f945216955819'
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
MODE=os.environ['G4_FINISH_MODE'];assert MODE in ['build','render']
ENV=['G3_night_sky','G3_window_rim','G4_overcast_environment']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def protected_signature():
    h=hashlib.sha256()
    for o in sorted(s.objects,key=lambda o:o.name):
        h.update(repr((o.name,o.type,o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),o.hide_render,
          getattr(o,'visible_camera',None),getattr(o,'visible_glossy',None),getattr(o,'visible_shadow',None),getattr(o,'visible_transmission',None))).encode())
        if o.type=='MESH':
            a=array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.type,o.data.clip_start,o.data.clip_end,o.data.shift_x,o.data.shift_y)).encode())
        if o.type=='LIGHT':h.update(repr((o.data.type,tuple(o.data.color),'ENVIRONMENT_REPLACED' if o.name in ENV else o.data.energy)).encode())
    h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode());return h.hexdigest()
if MODE=='build':
    parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==EXPECTED
    assert s.get('g4_revision')=='R01 verified-source extension'
    s.frame_set(451);bpy.context.view_layer.update();before=protected_signature()
    floor=bpy.data.objects['Hall_continuous_floor'];assert floor.active_material.name=='G3_slate_dry'
    source=floor.active_material;nodes=source.node_tree.nodes
    p=nodes['Principled BSDF'];assert p.inputs['Roughness'].is_linked and p.inputs['Roughness'].links[0].from_node.name=='rough'
    corrected=source.copy();corrected.name='G4R02_honed_dry_slate_existing_recipe'
    n=corrected.node_tree.nodes;l=corrected.node_tree.links;p=n['Principled BSDF']
    for link in list(p.inputs['Roughness'].links):l.remove(link)
    remap=n.new('ShaderNodeMapRange');remap.name='G3R02_dry_roughness_range_REUSED'
    remap.inputs['From Min'].default_value=0;remap.inputs['From Max'].default_value=1
    remap.inputs['To Min'].default_value=.52;remap.inputs['To Max'].default_value=.78;remap.clamp=True
    l.new(n['rough'].outputs['Color'],remap.inputs['Value']);l.new(remap.outputs['Result'],p.inputs['Roughness'])
    p.inputs['Coat Weight'].default_value=0
    floor.data=floor.data.copy();floor.data.materials.clear();floor.data.materials.append(corrected)
    environmental=[]
    for name in ENV:
        o=bpy.data.objects[name];assert o.type=='LIGHT' and o.data.type=='AREA'
        environmental.append({'object':name,'energy_before':o.data.energy,'energy_after':0,'replacement':'Shared continuous World illumination/reflection; original lamp remains as recoverable disabled source, all ray flags unchanged.'})
        o.data.energy=0
    oldworld=s.world;world=oldworld.copy();world.name='G4R02_clouded_night_environment';s.world=world
    n=world.node_tree.nodes;l=world.node_tree.links;bg=n['Background'];out=next(q for q in n if q.type=='OUTPUT_WORLD')
    assert len(out.inputs['Surface'].links)==1 and out.inputs['Surface'].links[0].from_node==bg
    coord=n.new('ShaderNodeTexCoord');coord.name='G4R02_world_direction'
    noise=n.new('ShaderNodeTexNoise');noise.name='G4R02_broad_cloud_variation';noise.inputs['Scale'].default_value=1.8;noise.inputs['Detail'].default_value=3.0;noise.inputs['Roughness'].default_value=.6
    ramp=n.new('ShaderNodeValToRGB');ramp.name='G4R02_low_saturation_blue_grey_sky'
    ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=(.055,.075,.105,1)
    ramp.color_ramp.elements[1].position=.80;ramp.color_ramp.elements[1].color=(.22,.27,.33,1)
    l.new(coord.outputs['Normal'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],bg.inputs['Color'])
    bg.inputs['Strength'].default_value=.75
    assert not any(q.type=='LIGHT_PATH' for q in n),'No per-ray cheating in environment'
    after=protected_signature();assert before==after,'Protected geometry, camera, practical lamp or ray state changed'
    s['g4_revision']='R02 dry hall and continuous night-sky environment'
    s['g4_r02_parent_sha256']=EXPECTED;s['g4_environment_card_replacements']=json.dumps(ENV)
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    report={'stage':'G4','revision':'R02','parent_master_sha256':EXPECTED,'parent_source_evidence_commit':'b5611004d3f224a2a41e2d589264ce6b3923f5ca',
      'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
      'basis':'Actually retrieved and opened R01 C01/C03 1440x900 originals from artifact10026285603. Hall floor over-reflects, cliff and bridge are underlit and roof shows finite sky cards.',
      'floor_root_verified':'R01 floor uses G3_slate_dry directly; original rough map linked without previously proven G3R02 remap. That transfer omitted the scoped R02 dry fix.',
      'floor_change':{'only_object':floor.name,'roughness_range':[.52,.78],'coat':0,'maps_and_UV_unchanged':True,'reused_source':'refine_g3.py dry_roughness'},
      'environmental_sources':environmental,
      'world_design':'Native broad low-contrast procedural blue-grey cloud environment, shared for illumination, camera and reflections. No area-light disc, no ray-conditioned shader, no fog or exposure change.',
      'protected_before':before,'protected_after':after,'g3_historical_pass':False,'g4_stage_pass':False,'human_acceptance':False,
      'limits':['This environmental art choice requires actual full-scene and sample regressions; not a predeclared visual success.',
                'Historical R01 views are not relabelled R02. No final animation or browser delivered.']}
    s.frame_set(451);s.camera=bpy.data.objects['C01_exterior_hero'];assert s.view_settings.exposure==0
    save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==EXPECTED
    report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
    report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend')
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('G4_R02_SAVED_NOT_ART_PASS',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g4-full-scene-candidate.blend';report=json.loads((OUT/'build-report.json').read_text());expected=report['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')=='R02 dry hall and continuous night-sky environment'
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    for name in json.loads(s['g3_neutral_lights']):bpy.data.objects[name].data.energy=0
    assert all(bpy.data.objects[name].data.energy==0 for name in ENV)
    assert s.world.node_tree.nodes['Background'].inputs['Color'].is_linked
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.045;s.cycles.adaptive_min_samples=16
    jobs=[('C01_exterior_hero','C01-full-night.png',(1440,900),48),
          ('C03_hall_to_platform','C03-hall-night.png',(1440,900),48),
          ('G3R03_complete_bay','G3-bay-context-night.png',(1440,900),64),
          ('G3R03_roof_node','D01-roof-node-regression.png',(1280,800),64),
          ('C09_car_aisle_failure_check','C09-car-aisle-night.png',(1280,800),48)]
    metrics=[]
    for cam,name,res,samples in jobs:
        assert time.time()<float(os.environ['G4_FINISH_DEADLINE']),'Finite R02 production deadline reached'
        assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451)
        row.update(lighting='night_continuous_world',native_render=True,master_sha256=expected,revision='G4_R02')
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('G4_R02_NATIVE_VIEW',name,flush=True)
    assert sha(master)==expected
    (OUT/'reopen-check.json').write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
