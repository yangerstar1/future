"""Fresh-process G3 evidence. No geometry changes; never overwrites the master."""
import bpy,json,sys,time,hashlib,os
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path(os.environ.get('G3_OUTPUT_ROOT','workspaces/glasshouse-terminus/output/g3')).resolve()
assert ROOT.is_relative_to(Path('workspaces/glasshouse-terminus/output').resolve()),'Unapproved evidence root'
MASTER=ROOT/'g3-bay-candidate.blend'
s=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==MASTER
assert s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE'
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest()
assert sha==json.loads((ROOT/'build-report.json').read_text())['candidate_sha256']
missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
assert not missing,missing
# Reuse the evaluated walking check, now at every source frame in the continuous shot.
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
                    hit,where,normal,idx,ob,matrix=s.ray_cast(deps,start,direction,distance=step.length+.01)
                    if hit and ob and not ob.name.startswith('QA_'):collisions.append({'frame':frame,'object':ob.name,'height':h,'lateral':lateral,'point':list(where)})
    if frame%15==1:
        hit,where,normal,idx,ob,matrix=s.ray_cast(deps,Vector((pos.x,pos.y,1.55)),Vector((0,0,-1)),distance=.70)
        floor.append({'frame':frame,'hit':hit,'object':ob.name if ob else None,'z':where.z if hit else None})
    previous=pos
motion=[]
for f in [1,211,298,301,314,315,330,348,451,660,840]:
    s.frame_set(f);motion.append({'frame':f,'train':list(bpy.data.objects['Train_motion_root'].location),'door_left':list(bpy.data.objects['Train_door_left'].location),'carriage':list(bpy.data.objects['G3_guide_carriage_left'].location)})
report={'master_sha256':sha,'fresh_process':True,'missing_external_images':missing,'walk_collision_count':len(collisions),'collisions':collisions,'floor':floor,'motion':motion,'source_frames_checked':[391,660],'visual_status':'PENDING_NOT_AUTO_PASS','diagnostic_limit':'Ray samples supplement visual review; not an exhaustive human collision solver'}
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(report,indent=2))
# Clear only in memory so timeline markers do not override diagnostic cameras.
s.timeline_markers.clear()
neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights'])
night_power={n:bpy.data.objects[n].data.energy for n in night}
bg=s.world.node_tree.nodes.get('Background')

def lighting(mode):
    for n,power in neutral.items():bpy.data.objects[n].data.energy=power if mode=='neutral' else 0
    for n,power in night_power.items():bpy.data.objects[n].data.energy=power if mode=='night' else 0
    bg.inputs['Color'].default_value=(.16,.19,.23,1) if mode=='neutral' else (.10,.145,.22,1)
    bg.inputs['Strength'].default_value=.65 if mode=='neutral' else .18
    s.view_settings.exposure=0

jobs=[('G3_bay','G3-bay-night.png','night',64,(1440,900),451),
      ('G3_bay','G3-bay-neutral.png','neutral',48,(1440,900),451),
      ('C03_hall_to_platform','C03-neutral-context.png','neutral',24,(1280,800),451),
      ('G3_D01','D01-glass-metal.png','night',64,(1280,800),451),
      ('G3_D02','D02-joinery.png','night',64,(1280,800),451),
      ('G3_D03','D03-upholstery.png','night',64,(1280,800),451),
      ('G3_D05','D05-door-interface.png','night',64,(1280,800),451),
      ('G3_D06','D06-plant.png','night',48,(1280,800),451),
      ('G3_reverse','QA-reverse.png','neutral',32,(1024,640),451)]
group=os.environ.get('G3_RENDER_SET','all')
assert group in ['all','overview','details']
jobs=jobs[:3] if group=='overview' else (jobs[3:] if group=='details' else jobs)
metrics=json.loads((ROOT/'render-metrics.json').read_text()) if (ROOT/'render-metrics.json').exists() else []
for cam,name,light,samples,res,frame in jobs:
    lighting(light)
    m=render(s,bpy.data.objects[cam],ROOT/name,res=res,samples=samples,frame=frame)
    m['lighting']=light;m['native_render']=True
    metrics.append(m)
    (ROOT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
    print('G3_VIEW_COMPLETE',name,flush=True)
# Evaluate saved door animation, never manually pose leaves for a convenient frame.
lighting('neutral')
for frame in ([] if group=='overview' else [301,330,348]):
    m=render(s,bpy.data.objects['G3_D05'],ROOT/f'QA-door-{frame}.png',res=(640,400),samples=16,frame=frame)
    m['lighting']='neutral';m['native_render']=True;metrics.append(m)
    (ROOT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
assert hashlib.sha256(MASTER.read_bytes()).hexdigest()==sha
report['rendered_views']=[m['file'] for m in metrics]
report['master_unchanged_after_evidence']=True
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(report,indent=2))
print('G3_EVIDENCE_COMPLETE_REQUIRES_IMAGE_REVIEW',len(metrics),'COLLISIONS',len(collisions))
