"""R07 finite photometric-art calibration, not another occlusion guess.
Only two existing R06 projector energies change. All original source blocks retained.
"""
import bpy,sys,os,json,hashlib,shutil,time
from pathlib import Path
from array import array
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import save,render
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g3-r06';OUT=ROOT/'output/g3-r07';OUT.mkdir(parents=True,exist_ok=True)
PARENT='65ef58c38685aa6ef26aa0f2d5116e1535e879f4a2b01975100d71be7cb7de26'
REV='R07 two existing purlin wash powers calibrated after native R06 review'
MODE=os.environ['G3_CALIBRATION_MODE'];assert MODE in ['build','node','context']
s=bpy.context.scene
assert bpy.app.version[:2]==(4,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def invariant():
    h=hashlib.sha256()
    for o in sorted(s.objects,key=lambda x:x.name):
        h.update(repr((o.name,o.type,tuple(tuple(r) for r in o.matrix_world),o.hide_render,getattr(o,'visible_shadow',None),getattr(o,'visible_camera',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None),getattr(o,'visible_diffuse',None))).encode())
        if o.type=='MESH':
            a=array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
            for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.material_index,p.use_smooth)).encode())
        if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
        if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end)).encode())
        if o.type=='LIGHT':h.update(repr((o.data.type,tuple(o.data.color),o.data.energy if not o.name.startswith('G3R06_upper_node_wash') else 'PERMITTED_ENERGY_ONLY',getattr(o.data,'spot_size',None),getattr(o.data,'spot_blend',None),getattr(o.data,'shadow_soft_size',None))).encode())
    for m in sorted(bpy.data.materials,key=lambda x:x.name):
        h.update(m.name.encode())
        if m.use_nodes:
            for n in m.node_tree.nodes:
                for socket in n.inputs:
                    if hasattr(socket,'default_value'):h.update(repr((n.name,socket.name,str(socket.default_value),socket.is_linked)).encode())
    h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.view_settings.gamma)).encode())
    return h.hexdigest()

if MODE=='build':
    parent=BASE/'g3-bay-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
    assert s.get('g3_revision')=='R06 physically supported purlin node wash after measured R05 occlusion'
    prior=json.loads((BASE/'upper-node-report.json').read_text());assert prior['post_fixture_direct_count']==23 and prior['upper_sample_count']==25
    s.frame_set(451);bpy.context.view_layer.update();before=invariant()
    lights=[bpy.data.objects[r['light_object']] for r in prior['specifications']];assert len(lights)==2
    changes=[]
    for o in lights:
        assert o.type=='LIGHT' and o.data.type=='SPOT' and abs(o.data.energy-36)<.001
        changes.append({'object':o.name,'before':36,'after':144,'location':list(o.location),'rotation':list(o.rotation_euler)})
        o.data.energy=144
    after=invariant();assert before==after,'Non-authorized source property changed'
    s['g3_revision']=REV;s['g3_r07_parent_sha256']=PARENT
    for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json')
    shutil.copy2(BASE/'upper-node-report.json',OUT/'R06-upper-node-report.json')
    save(s,OUT/'g3-bay-candidate.blend');assert sha(parent)==PARENT
    report={'stage':'G3','revision':'R07','parent_evidence_commit':'719b77ac1678b0ede8edcc9bd86193e1d0db9362','parent_master_sha256':PARENT,
      'candidate_sha256':sha(OUT/'g3-bay-candidate.blend'),'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],
      'changes':changes,'protected_before':before,'protected_after':after,'no_new_geometry_or_lights':True,
      'basis':'R06 original D01 was actually viewed. 23/25 upper geometric samples have direct paths. Visible web/plate recovered but remain underlit. Local projector power only increased by two stops; global exposure and original floor lamps untouched.',
      'limits':'Two R06 first hits are curved roof glazing; geometric visibility is not full refracted-light transport. Do not claim all 25 paths open, or use power to fix these two paths. This is a bounded visual calibration, no automatic PASS.',
      'parent_master_unchanged':True,'g4_allowed':False,'human_acceptance':False}
    (OUT/'calibration-report.json').write_text(json.dumps(report,indent=2))
    (OUT/'build-report.json').write_text(json.dumps({'stage':'G3_CANDIDATE','revision':'R07','parent_sha256':PARENT,'candidate_sha256':report['candidate_sha256'],'revision_report':'calibration-report.json','blender':bpy.app.version_string},indent=2))
    print('R07_CANDIDATE_SAVED',report['candidate_sha256'],flush=True)
else:
    master=OUT/'g3-bay-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256']
    assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g3_revision')==REV
    missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
    s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
    for n in json.loads(s['g3_neutral_lights']):bpy.data.objects[n].data.energy=0
    bg=s.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.10,.145,.22,1);bg.inputs['Strength'].default_value=.18
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
    jobs=[('G3R03_roof_node','D01-roof-node.png',(1280,800))] if MODE=='node' else [
      ('G3R03_complete_bay','R07-complete-bay-night.png',(1440,900)),('G3_bay','G3-bay-night.png',(1440,900)),('G3_D01','D01-glass-metal.png',(1280,800))]
    metrics=[] if MODE=='node' else json.loads((OUT/'render-metrics.json').read_text())
    for cam,name,res in jobs:
        assert time.time()<float(os.environ['G3_CALIBRATION_DEADLINE']),'Finite calibration time reached'
        assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
        row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=64,frame=451);row.update(lighting='night',native_render=True,source_master_sha256=expected)
        metrics.append(row);(OUT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('R07_VIEW_SAVED',name,flush=True)
    assert sha(master)==expected and sha(BASE/'g3-bay-candidate.blend')==PARENT
    (OUT/('node-reopen-check.json' if MODE=='node' else 'reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'parent_master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_allowed':False,'human_acceptance':False},indent=2))
