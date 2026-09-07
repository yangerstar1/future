"""R04 native art evidence using existing scene_common.render. No saved edits.
Legacy render_g3.py stays untouched. All comparisons retain the old cameras.
"""
import bpy,json,hashlib,sys,os,time
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path('workspaces/glasshouse-terminus/output/g3-r04').resolve();MASTER=ROOT/'g3-bay-candidate.blend'
s=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==MASTER and bpy.app.version[:2]==(4,5)
assert s.get('g3_revision')=='R04 motivated illumination and completed arch bay'
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest()
assert sha==json.loads((ROOT/'art-report.json').read_text())['candidate_sha256']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
assert not missing,missing
walk=bpy.data.objects['FILM_04_CONTINUOUS_WALK'];previous=None;collisions=[];floor=[]
for frame in range(391,661):
    s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();pos=walk.matrix_world.translation.copy()
    if previous is not None:
        step=pos-previous
        if step.length>1e-6:
            direction=step.normalized();side=Vector((-direction.y,direction.x,0)).normalized()
            for h in [-1.38,-.95,-.4,0,.10]:
                for lateral in [-.20,0,.20]:
                    hit,where,normal,index,ob,matrix=s.ray_cast(deps,previous+side*lateral+Vector((0,0,h)),direction,distance=step.length+.01)
                    if hit and ob and not ob.name.startswith('QA_'):collisions.append({'frame':frame,'object':ob.name,'height':h,'lateral':lateral})
    if frame%15==1:
        hit,where,normal,index,ob,matrix=s.ray_cast(deps,Vector((pos.x,pos.y,1.55)),Vector((0,0,-1)),distance=.70)
        floor.append({'frame':frame,'hit':hit,'object':ob.name if ob else None,'z':where.z if hit else None})
    previous=pos
motion=[]
for f in [1,298,301,314,315,330,348,451,660,840]:
    s.frame_set(f);motion.append({'frame':f,'train':list(bpy.data.objects['Train_motion_root'].location),'door':list(bpy.data.objects['Train_door_left'].location),'carriage':list(bpy.data.objects['G3_guide_carriage_left'].location)})
check={'source_master_sha256':sha,'fresh_process':True,'missing_images':missing,'collisions':collisions,'floor':floor,'motion':motion,'limitation':'Finite route envelope, not exhaustive collision or automatic art acceptance'}
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(check,indent=2))
assert not collisions and all(v['hit'] for v in floor),'Added sample hardware obstructs protected walking path'
s.timeline_markers.clear();neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights'])
powers={n:bpy.data.objects[n].data.energy for n in night};bg=s.world.node_tree.nodes['Background']
def lighting(mode):
    for n,p in neutral.items():bpy.data.objects[n].data.energy=p if mode!='night' else 0
    for n,p in powers.items():bpy.data.objects[n].data.energy=p if mode=='night' else 0
    bg.inputs['Color'].default_value=(.10,.145,.22,1) if mode=='night' else ((.62,.64,.67,1) if mode=='g2-neutral' else (.16,.19,.23,1))
    bg.inputs['Strength'].default_value=.18 if mode=='night' else .65
    s.view_settings.exposure=0
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.035;s.cycles.adaptive_min_samples=16
s.render.resolution_percentage=100;s.render.use_border=False
sampling={'threshold':.035,'min_samples':16,'denoise':s.cycles.use_denoising,'note':'Native review renders, not final 4K film'}
group=os.environ.get('R04_RENDER_SET','overview');assert group in ['overview','details']
if group=='overview':
    jobs=[('G3R03_complete_bay','R04-complete-bay-night.png','night',64,(1440,900),451),
          ('G3R03_complete_bay','R04-complete-bay-neutral.png','neutral',48,(1440,900),451),
          ('G3_bay','R04-original-bay-night.png','night',64,(1440,900),451)]
else:
    jobs=[('G3R03_roof_node','D01-roof-node.png','night',48,(1280,800),451),
          ('G3_D01','D01-glass-metal.png','night',48,(1280,800),451),
          ('G3_D02','D02-joinery.png','night',48,(1280,800),451),
          ('G3R03_chair_front','D03-front.png','night',48,(1280,800),451),
          ('G3R04_unobstructed_interface','D05-unobstructed-interface.png','night',48,(1280,800),451),
          ('G3R04_threshold_detail','D05-threshold-detail.png','neutral',32,(1000,625),451),
          ('G3R04_roller_detail','D05-roller-detail.png','neutral',32,(1000,625),348),
          ('G3_D06','D06-plant.png','night',48,(1280,800),451),
          ('G3_reverse','QA-reverse.png','neutral',32,(1024,640),451),
          ('C03_hall_to_platform','C03-G2-neutral-baseline.png','g2-neutral',24,(1280,800),451)]
    jobs += [('G3R04_unobstructed_interface',f'QA-door-{f}.png','neutral',16,(640,400),f) for f in [301,330,348]]
    jobs += [('FILM_04_CONTINUOUS_WALK',f'QA-route-{f}.png','neutral',16,(640,360),f) for f in [421,481,601]]
metrics=json.loads((ROOT/'render-metrics.json').read_text()) if (ROOT/'render-metrics.json').exists() else []
for cam,name,mode,samples,res,frame in jobs:
    if time.time()>float(os.environ.get('G3_ART_DEADLINE','inf')):raise TimeoutError('Production bound reached; preserve partial art honestly')
    lighting(mode);m=render(s,bpy.data.objects[cam],ROOT/name,res=res,samples=samples,frame=frame)
    m.update(lighting=mode,sampling=sampling,native_render=True,world_color=list(bg.inputs['Color'].default_value),world_strength=bg.inputs['Strength'].default_value)
    metrics=[v for v in metrics if v['file']!=name]+[m]
    (ROOT/'render-metrics.json').write_text(json.dumps(metrics,indent=2));print('R04_NATIVE_VIEW',name,flush=True)
assert hashlib.sha256(MASTER.read_bytes()).hexdigest()==sha
check.update(master_unchanged=True,completed_render_group=group,rendered_views=[v['file'] for v in metrics],visual_gate='REVIEW_REQUIRED_NOT_AUTOPASS')
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(check,indent=2))
print('R04_GROUP_RENDERED',group,len(jobs),flush=True)
