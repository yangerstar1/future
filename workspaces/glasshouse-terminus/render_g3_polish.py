"""Fresh-process R04 observations using the existing native Cycles renderer.
No saved geometry/material/camera edits; sparse route images are not a film.
"""
import bpy, json, hashlib, os, sys, time
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path('workspaces/glasshouse-terminus/output/g3-r04').resolve()
MASTER=ROOT/'g3-bay-candidate.blend';s=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==MASTER
assert s.get('g3_revision')=='R04 physical sconces, structural-bay palette and unobstructed witnesses'
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest()
assert sha==json.loads((ROOT/'build-report.json').read_text())['candidate_sha256']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()]
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
                    start=previous+side*lateral+Vector((0,0,h))
                    hit,at,normal,idx,ob,matrix=s.ray_cast(deps,start,direction,distance=step.length+.01)
                    if hit and ob and not ob.name.startswith('QA_'):collisions.append({'frame':frame,'object':ob.name,'height':h,'lateral':lateral})
    if frame%15==1:
        hit,at,normal,idx,ob,matrix=s.ray_cast(deps,Vector((pos.x,pos.y,1.55)),Vector((0,0,-1)),distance=.70)
        floor.append({'frame':frame,'hit':hit,'object':ob.name if ob else None,'z':at.z if hit else None})
    previous=pos
motion=[]
for frame in [301,314,315,330,348,451,660]:
    s.frame_set(frame);motion.append({'frame':frame,'train':list(bpy.data.objects['Train_motion_root'].location),'door':list(bpy.data.objects['Train_door_left'].location),'carriage':list(bpy.data.objects['G3_guide_carriage_left'].location)})
check={'master_sha256':sha,'fresh_process':True,'missing_external_images':missing,'walk_collision_count':len(collisions),'collisions':collisions,'floor':floor,'motion':motion,'visual_acceptance':False,'limit':'Finite ray envelope and sparse stills, not exhaustive collision or a new continuous film'}
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(check,indent=2))
s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights'])
night_power={name:bpy.data.objects[name].data.energy for name in night};bg=s.world.node_tree.nodes['Background']
def lighting(mode):
    for name,p in neutral.items():bpy.data.objects[name].data.energy=p if mode!='night' else 0
    for name,p in night_power.items():bpy.data.objects[name].data.energy=p if mode=='night' else 0
    bg.inputs['Color'].default_value=(.62,.64,.67,1) if mode=='g2-neutral' else ((.16,.19,.23,1) if mode=='neutral' else (.10,.145,.22,1))
    bg.inputs['Strength'].default_value=.18 if mode=='night' else .65
    assert s.view_settings.exposure==0
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
sets={
 'overview':[
  ('G3R03_complete_bay','R04-complete-bay-night.png','night',64,(1440,900),451),
  ('G3R03_complete_bay','R04-complete-bay-neutral.png','neutral',48,(1440,900),451),
  ('G3_bay','G3-bay-night.png','night',64,(1440,900),451)],
 'core':[
  ('G3R04_door_unoccluded','D05-unoccluded-interface.png','night',48,(1280,800),451),
  ('G3R03_roof_node','D01-roof-node.png','night',48,(1280,800),451),
  ('G3_D01','D01-glass-metal.png','night',64,(1280,800),451),
  ('G3_D02','D02-joinery.png','night',64,(1280,800),451),
  ('G3R03_chair_front','D03-front.png','night',48,(1280,800),451)],
 'proof':[
  ('G3_D06','D06-plant.png','night',48,(1280,800),451),
  ('G3_reverse','QA-reverse.png','neutral',32,(1024,640),451),
  ('G3R04_roller_detail','D05-roller-detail.png','neutral',32,(1000,625),348),
  ('G3R04_threshold_detail','D05-threshold-detail.png','neutral',32,(1000,625),348),
  ('C03_hall_to_platform','C03-G2-neutral-baseline.png','g2-neutral',24,(1280,800),451),
  ('G3_D05','D05-original-camera.png','night',48,(1280,800),451)]
}
sets['proof'] += [('G3R04_door_unoccluded',f'QA-door-{f}.png','neutral',16,(640,400),f) for f in [301,330,348]]
sets['proof'] += [('FILM_04_CONTINUOUS_WALK',f'QA-route-{f}.png','neutral',16,(640,360),f) for f in [481,601]]
group=os.environ['G3_POLISH_SET'];assert group in sets
metrics=json.loads((ROOT/'render-metrics.json').read_text()) if (ROOT/'render-metrics.json').exists() else []
for cam,name,mode,samples,res,frame in sets[group]:
    assert time.time()<float(os.environ['G3_PRODUCTION_DEADLINE']),'Production deadline: preserve completed images'
    lighting(mode)
    m=render(s,bpy.data.objects[cam],ROOT/name,res=res,samples=samples,frame=frame)
    m.update(lighting=mode,world_color=list(bg.inputs['Color'].default_value),world_strength=bg.inputs['Strength'].default_value,native_render=True,group=group,adaptive_threshold=s.cycles.adaptive_threshold,adaptive_min_samples=s.cycles.adaptive_min_samples)
    metrics=[p for p in metrics if p['file']!=name]+[m]
    (ROOT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
    print('R04_REAL_VIEW_SAVED',name,flush=True)
assert hashlib.sha256(MASTER.read_bytes()).hexdigest()==sha
check['master_unchanged_after_evidence']=True;check['actual_rendered_files']=[m['file'] for m in metrics]
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(check,indent=2))
print('R04_GROUP_COMPLETE_REVIEW_PENDING',group,flush=True)
