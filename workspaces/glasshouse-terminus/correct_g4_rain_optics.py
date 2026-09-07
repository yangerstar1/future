"""R04: replace refractive rain rods with smooth drops and native shutter integration.
Evidence: actual R03 M01 original shows long black glass spears. All source scene
geometry/materials/fixtures/cameras outside the two owned rain node groups stay.
"""
import bpy,os,json,hashlib,sys,time,shutil,math
from pathlib import Path
from array import array
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-r03';OUT=ROOT/'output/g4-r04';OUT.mkdir(parents=True,exist_ok=True)
PARENT='dfd9a0e28967b8a474bc9688ce0b75d194dba20ce14aab5f18f1d11da7aa32b5'
REV='R04 round rain drops with native shutter and cycle-aware instance IDs'
MODE=os.environ['G4_OPTICS_MODE'];assert MODE in ['build','hero','motion']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def invariant():
    h=hashlib.sha256()
    for o in sorted(s.objects,key=lambda o:o.name):
        h.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_camera',None),getattr(o,'visible_glossy',None),getattr(o,'visible_shadow',None),getattr(o,'visible_transmission',None))).encode())
        if o.type=='MESH':
            a=array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
            for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.use_smooth)).encode())
            for attr in o.data.attributes:
                if attr.name.startswith('rain_'):
                    a=array('f',[0])*len(attr.data);attr.data.foreach_get('value',a);h.update(a.tobytes())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.dof.use_dof)).encode())
        if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
        if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
    for frame in [451,457,508,451]:
        s.frame_set(frame);bpy.context.view_layer.update()
        for o in sorted(s.objects,key=lambda o:o.name):h.update(repr((o.name,tuple(tuple(r) for r in o.matrix_world))).encode())
    h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode())
    return h.hexdigest()
def node_math(n,l,op,a,b=None):
    q=n.new('ShaderNodeMath');q.operation=op
    for i,v in enumerate([a,b]):
        if v is None:continue
        if isinstance(v,(int,float)):q.inputs[i].default_value=v
        else:l.new(v,q.inputs[i])
    return q.outputs[0]
def set_motion():
    assert hasattr(s.render,'use_motion_blur') and hasattr(s.render,'motion_blur_shutter')
    s.render.use_motion_blur=True;s.render.motion_blur_shutter=.70
    if hasattr(s.cycles,'motion_blur_position'):s.cycles.motion_blur_position='CENTER'
    assert s.render.fps==30
if MODE=='build':
    parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
    assert s.get('g4_revision')=='R03 rain layers and close-range physical surface response'
    before=invariant();edits=[]
    for name in ['G4R03_roof_clipped_rain','G4R03_eave_drips']:
        ob=bpy.data.objects[name];mod=next(m for m in ob.modifiers if m.type=='NODES');g=mod.node_group.copy();g.name='G4R04_'+name+'_native_shutter';mod.node_group=g;n=g.nodes;l=g.links
        tr=next(q for q in n if q.bl_idname=='GeometryNodeTransform')
        sphere=next(q for q in n if q.bl_idname=='GeometryNodeMeshUVSphere')
        inst=next(q for q in n if q.bl_idname=='GeometryNodeInstanceOnPoints')
        sp=next(q for q in n if q.bl_idname=='GeometryNodeSetPosition')
        assert all(abs(tr.inputs['Scale'].default_value[i]-[.0028,.0028,.075][i])<.00001 for i in range(3))
        tr.inputs['Scale'].default_value=(.0021,.0021,.0024)
        sphere.inputs['Segments'].default_value=24;sphere.inputs['Rings'].default_value=12
        smooth=n.new('GeometryNodeSetShadeSmooth');smooth.domain='FACE';smooth.inputs['Shade Smooth'].default_value=True
        l.new(sphere.outputs['Mesh'],smooth.inputs['Geometry']);l.new(smooth.outputs['Geometry'],tr.inputs['Geometry'])
        # A new lifetime gets a distinct native ID. Do not match a drop at the
        # hit surface with the reborn drop at the top of its clipped trajectory.
        attrs={q.inputs['Name'].default_value:q.outputs['Attribute'] for q in n if q.bl_idname=='GeometryNodeInputNamedAttribute'}
        tm=next(q for q in n if q.bl_idname=='GeometryNodeInputSceneTime')
        phase=node_math(n,l,'ADD',node_math(n,l,'MULTIPLY',tm.outputs['Seconds'],attrs['rain_speed']),attrs['rain_phase'])
        cycle=node_math(n,l,'FLOOR',node_math(n,l,'DIVIDE',phase,attrs['rain_travel']))
        idx=n.new('GeometryNodeInputIndex');ident=node_math(n,l,'ADD',idx.outputs['Index'],node_math(n,l,'MULTIPLY',cycle,len(ob.data.vertices)))
        setid=n.new('GeometryNodeSetID');l.new(sp.outputs['Geometry'],setid.inputs['Geometry']);l.new(ident,setid.inputs['ID']);l.new(setid.outputs['Geometry'],inst.inputs['Points'])
        if hasattr(ob.cycles,'use_motion_blur'):ob.cycles.use_motion_blur=True
        if hasattr(ob.cycles,'motion_steps'):ob.cycles.motion_steps=2
        N=len(ob.data.vertices);stats={'matched':0,'birth_or_death':0,'max_matched_distance':0.0};samples=[]
        for i in range(N):
            attrs=ob.data.attributes;L=attrs['rain_travel'].data[i].value;v=attrs['rain_speed'].data[i].value;p=attrs['rain_phase'].data[i].value
            a=(451-.35)/30*v+p;b=(451+.35)/30*v+p;ia=math.floor(a/L);ib=math.floor(b/L)
            if ia==ib:
                distance=b-a;assert distance<.25;stats['matched']+=1;stats['max_matched_distance']=max(stats['max_matched_distance'],distance)
            else:stats['birth_or_death']+=1
            if i<8:samples.append({'point':i,'lifetime_IDs':[i+N*ia,i+N*ib],'offsets':[a%L,b%L],'speed_m_s':v,'travel':L})
        edits.append({'object':name,'old_prototype_scale':[.0028,.0028,.075],'new_prototype_scale':list(tr.inputs['Scale'].default_value),'prototype_segments':24,'prototype_rings':12,'smooth_normals':True,'cycle_aware_ids':True,'shutter_path_audit':stats,'samples':samples})
    set_motion();after=invariant();assert before==after,'Unrelated source geometry, attributes, motion, fixtures, camera or visibility changed'
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    shutil.copy2(BASE/'build-report.json',OUT/'R03-build-report.json')
    s['g4_revision']=REV;s['g4_r04_parent_sha256']=PARENT;s.frame_set(451);s.camera=bpy.data.objects['G4R03_rain_glass_macro']
    save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
    report={'stage':'G4','revision':'R04','parent_master_sha256':PARENT,'parent_source_checkpoint':'0e0f56888549e27900070a83b9830f81c3313c4b','candidate_sha256':sha(OUT/'g4-full-scene-candidate.blend'),'master_bytes':(OUT/'g4-full-scene-candidate.blend').stat().st_size,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
      'basis':'Actual R03 M01 native image shows sharp black refractive rain spears. Correct optical representation, not add more power, color grading or white-line overlay. R03 material finishes and static attached water kept.',
      'edits':edits,'shutter_fraction':.70,'shutter_seconds':.70/30,'motion_blur_enabled':True,'protected_before':before,'protected_after':after,
      'limits':['Analytic roof-clipped particle paths at parked frame451, not fluid simulation.','Cycle IDs are lifetime bookkeeping; rendered image still decides whether native motion integration is satisfactory.','Glass adhesion remains static. Other source material/geometry issues not closed by this optical correction.'],
      'queue_decision':'Pending R03 proof34148751768 intentionally superseded via existing single-pending concurrency pattern; no known-bad rain movie required. Original failed still and source retained.',
      'g4_stage_pass':False,'human_acceptance':False}
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('R04_ROUND_DROP_SOURCE_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g4-full-scene-candidate.blend';r=json.loads((OUT/'build-report.json').read_text());expected=r['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    for n in json.loads(s['g3_neutral_lights']):bpy.data.objects[n].data.energy=0
    assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX';set_motion()
    s.cycles.max_bounces=10;s.cycles.transmission_bounces=8;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=24;s.cycles.adaptive_threshold=.025
    metrics=[]
    jobs=[('G4R03_rain_glass_macro','M01-rain-glass.png',(1600,1000),96,451),('C03_hall_to_platform','C03-hall-rain.png',(1440,900),64,451)] if MODE=='hero' else []
    if MODE=='motion':
        (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.06
        jobs=[('G4R03_rain_glass_macro',f'motion/{j:04d}.png',(640,400),24,f) for j,f in enumerate(range(451,511,3))]
    for cam,name,res,samples,frame in jobs:
        assert time.time()<float(os.environ['G4_OPTICS_DEADLINE']),'Finite optics request exhausted'
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame)
        row.update(native_render=True,master_sha256=expected,motion_blur=True,shutter_fraction=.70,proof_not_final_film=(MODE=='motion'))
        metrics.append(row);(OUT/f'{MODE}-metrics.json').write_text(json.dumps(metrics,indent=2));print('R04_NATIVE_VIEW',name,flush=True)
    assert sha(master)==expected
    (OUT/f'{MODE}-reopen-check.json').write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_frames':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
