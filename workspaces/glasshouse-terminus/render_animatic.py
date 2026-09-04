"""G2 low-cost animatic, explicitly 640x360 / 10 FPS, NOT FINAL FILM.
Run in a new Blender process with g2-complete-whitebox.blend already loaded.
Saved source keeps 840 frames / 30 FPS and all camera markers.
"""
import bpy, json, math, os, time
from pathlib import Path
from mathutils import Vector

s=bpy.context.scene
assert s.get('phase')=='G2_WHITEBOX_NOT_FINAL_ART', 'Wrong source stage'
root=Path('workspaces/glasshouse-terminus/output/g2').resolve()
out=root/'animatic-frames';out.mkdir(parents=True,exist_ok=True)
qa=bpy.data.collections.get('QA_scale_and_route')
if qa:
    for ob in qa.objects:ob.hide_render=True;ob.hide_viewport=True

# Inspect evaluated geometry instead of treating declared route points as collision proof.
walk=bpy.data.objects.get('FILM_04_CONTINUOUS_WALK')
train=bpy.data.objects.get('Train_motion_root')
assert walk and train
collisions=[];floor_checks=[];previous=None
for frame in range(391,661,3):
    s.frame_set(frame)
    deps=bpy.context.evaluated_depsgraph_get()
    position=walk.matrix_world.translation.copy()
    if previous is not None:
        step=position-previous
        if step.length>.00001:
            forward=step.normalized();side=Vector((-forward.y,forward.x,0)).normalized()
            # Five-height capsule envelope, radius 0.20 m, lower samples avoid the ground.
            for height in [-1.38,-.95,-.4,0,.10]:
                for lateral in [-.20,0,.20]:
                    start=previous+side*lateral+Vector((0,0,height))
                    hit,where,normal,index,obj,matrix=s.ray_cast(deps,start,forward,distance=step.length+.015)
                    if hit and obj and not obj.name.startswith('QA_'):
                        collisions.append({'frame':frame,'object':obj.name,'height_offset':height,'lateral_offset':lateral,'point':list(where)})
    if frame%15==1:
        origin=Vector((position.x,position.y,1.55))
        hit,where,normal,index,obj,matrix=s.ray_cast(deps,origin,Vector((0,0,-1)),distance=.70)
        floor_checks.append({'frame':frame,'hit':hit,'object':obj.name if obj else None,'height':float(where.z) if hit else None})
    previous=position

motion=[]
previous_location=None
for frame in [1,211,298,301,310,314,315,330,348,390,451,660,840]:
    s.frame_set(frame)
    t=(frame-1)/30
    position=train.matrix_world.translation.copy()
    door=bpy.data.objects['Train_door_left']
    motion.append({'frame':frame,'seconds':t,'body_position':list(position),'door_local_position':list(door.location)})
(root/'evaluated-space-check.json').write_text(json.dumps({'source_blend':'g2-complete-whitebox.blend','fresh_process':True,
    'collision_method':'scene.ray_cast on evaluated geometry along actual animated camera centreline and 0.20m horizontal envelope at five heights; diagnostic proxies hidden',
    'walk_source_frames':[391,660],'collisions':collisions,'floor_checks':floor_checks,'motion':motion,
    'limitation':'This deterministic geometry check supplements but does not replace full-size C views and human viewing of continuous animation.'},indent=2))

s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4
s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=False
s.cycles.max_bounces=6;s.cycles.transmission_bounces=5
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=4
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.use_persistent_data=True
records=[]
for i,frame in enumerate(range(1,841,3)):
    s.frame_set(frame)
    assert s.camera is not None
    s.render.filepath=str(out/f'{i:04d}.png')
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    records.append({'output_index':i,'source_frame':frame,'source_seconds':(frame-1)/30,
                    'camera':s.camera.name,'camera_position':list(s.camera.matrix_world.translation),'seconds':time.monotonic()-start})
    if i%20==0:
        (root/'animatic-progress.json').write_text(json.dumps({'last_index':i,'frames_rendered':len(records),'status':'INCOMPLETE_PREVIEW'},indent=2))
(root/'animatic-metrics.json').write_text(json.dumps({'scope':'G2 WHITEBOX PREVIEW; NOT FINAL 4K30 FILM',
    'source_fps':30,'source_frames':840,'preview_fps':10,'preview_frames':280,'duration_seconds':28,
    'native_resolution':[640,360],'samples':4,'no_generated_or_interpolated_frames':True,
    'continuous_walk_interval_seconds':[13,22],'frames':records},indent=2))
print('G2_ANIMATIC_RENDERED',len(records),'COLLISION_OBSERVATIONS',len(collisions))
