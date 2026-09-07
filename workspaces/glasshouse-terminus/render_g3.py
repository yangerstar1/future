"""Fresh-process G3 evidence. No geometry changes; never overwrites the master.
Legacy all/overview/details remain available. R03 prioritizes missing proof before
revisiting legacy closeups. Adaptive sampling is explicitly recorded, not hidden.
"""
import bpy,json,sys,time,hashlib,os
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render
ROOT=Path(os.environ.get('G3_OUTPUT_ROOT','workspaces/glasshouse-terminus/output/g3')).resolve()
assert ROOT.is_relative_to(Path('workspaces/glasshouse-terminus/output').resolve()),'Unapproved evidence root'
MASTER=ROOT/'g3-bay-candidate.blend'
s=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==MASTER and s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE'
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest()
assert sha==json.loads((ROOT/'build-report.json').read_text())['candidate_sha256']
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
report={'master_sha256':sha,'fresh_process':True,'missing_external_images':missing,'walk_collision_count':len(collisions),'collisions':collisions,'floor':floor,'motion':motion,'source_frames_checked':[391,660],'visual_status':'PENDING_NOT_AUTO_PASS','diagnostic_limit':'Finite ray samples supplement actual images; not an exhaustive human collision solver'}
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(report,indent=2))
s.timeline_markers.clear()
neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights'])
night_power={n:bpy.data.objects[n].data.energy for n in night};bg=s.world.node_tree.nodes.get('Background')

def lighting(mode):
    assert mode in ['neutral','night','g2-neutral']
    for n,power in neutral.items():bpy.data.objects[n].data.energy=power if mode!='night' else 0
    for n,power in night_power.items():bpy.data.objects[n].data.energy=power if mode=='night' else 0
    bg.inputs['Color'].default_value=(.62,.64,.67,1) if mode=='g2-neutral' else ((.16,.19,.23,1) if mode=='neutral' else (.10,.145,.22,1))
    bg.inputs['Strength'].default_value=.18 if mode=='night' else .65
    s.view_settings.exposure=0

legacy=[('G3_bay','G3-bay-night.png','night',64,(1440,900),451),
 ('G3_bay','G3-bay-neutral.png','neutral',48,(1440,900),451),
 ('C03_hall_to_platform','C03-neutral-context.png','neutral',24,(1280,800),451),
 ('G3_D01','D01-glass-metal.png','night',64,(1280,800),451),
 ('G3_D02','D02-joinery.png','night',64,(1280,800),451),
 ('G3_D03','D03-upholstery.png','night',64,(1280,800),451),
 ('G3_D05','D05-door-interface.png','night',64,(1280,800),451),
 ('G3_D06','D06-plant.png','night',48,(1280,800),451),
 ('G3_reverse','QA-reverse.png','neutral',32,(1024,640),451)]
group=os.environ.get('G3_RENDER_SET','all')
assert group in ['all','overview','details','r03-overview','r03-proof','r03-legacy']
if group=='r03-overview':
    jobs=[('G3R03_complete_bay','R03-complete-bay-night.png','night',64,(1440,900),451),
      ('G3R03_complete_bay','R03-complete-bay-neutral.png','neutral',48,(1440,900),451),legacy[0]]
elif group=='r03-proof':
    jobs=[('G3R03_chair_front','D03-front.png','night',48,(1280,800),451),
      ('G3R03_full_door','D05-full-interface.png','night',48,(1280,800),451),
      legacy[7],legacy[8],
      ('G3R03_roof_node','D01-roof-node.png','night',48,(1280,800),451),
      ('C03_hall_to_platform','C03-G2-neutral-baseline.png','g2-neutral',24,(1280,800),451)]
    jobs += [('G3R03_full_door',f'QA-full-door-{f}.png','neutral',16,(640,400),f) for f in [301,330,348]]
    jobs += [('FILM_04_CONTINUOUS_WALK',f'QA-route-{f}.png','neutral',16,(640,360),f) for f in [391,421,451,481,511,541,571,601,631,660]]
elif group=='r03-legacy':jobs=[legacy[1],legacy[2]]+legacy[3:7]
else:
    jobs=legacy[:3] if group=='overview' else (legacy[3:] if group=='details' else legacy)
    if group!='overview':jobs += [('G3_D05',f'QA-door-{f}.png','neutral',16,(640,400),f) for f in [301,330,348]]
mode=os.environ.get('G3_SAMPLING','saved')
assert mode in ['saved','adaptive-review']
if mode=='adaptive-review':
    s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.04;s.cycles.adaptive_min_samples=16
sampling={'mode':mode,'adaptive':s.cycles.use_adaptive_sampling,'threshold':s.cycles.adaptive_threshold,'min_samples':s.cycles.adaptive_min_samples,'denoising':s.cycles.use_denoising}
metrics=json.loads((ROOT/'render-metrics.json').read_text()) if (ROOT/'render-metrics.json').exists() else []
for cam,name,light,samples,res,frame in jobs:
    lighting(light)
    m=render(s,bpy.data.objects[cam],ROOT/name,res=res,samples=samples,frame=frame)
    m.update({'lighting':light,'world_color':list(bg.inputs['Color'].default_value),'world_strength':bg.inputs['Strength'].default_value,'native_render':True,'sampling':sampling,'group':group})
    metrics=[old for old in metrics if old['file']!=name]+[m]
    (ROOT/'render-metrics.json').write_text(json.dumps(metrics,indent=2))
    print('G3_VIEW_COMPLETE',name,flush=True)
assert hashlib.sha256(MASTER.read_bytes()).hexdigest()==sha
report['rendered_views']=[m['file'] for m in metrics];report['master_unchanged_after_evidence']=True
report['route_images_scope']='Ten sparse Cycles observations, not a new complete continuous film' if group.startswith('r03') else 'No new continuous film'
(ROOT/'reopen-and-space-check.json').write_text(json.dumps(report,indent=2))
print('G3_EVIDENCE_COMPLETE_REQUIRES_IMAGE_REVIEW',len(metrics),'COLLISIONS',len(collisions),flush=True)
