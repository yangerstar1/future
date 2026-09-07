"""Additional G3 witnesses for G3-V01. Reopen an immutable R02 master.
Never change source geometry/materials/animation or original cameras; do not
replace the old failing angles. New cameras are recorded as extra observations.
"""
import bpy, json, hashlib, sys, os, time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import camera, render
ROOT=Path('workspaces/glasshouse-terminus/output/g3-observations').resolve()
SOURCE=Path('workspaces/glasshouse-terminus/output/g3-r02/g3-bay-candidate.blend').resolve()
EXPECTED='3162ba27fbeb3055c5fbe94a6fc2422cc9cca11f68dda381b06627ebcaf6d680'
assert Path(bpy.data.filepath).resolve()==SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene
assert s.get('phase')=='G3_SAMPLE_NOT_FINAL_SCENE'
assert s.get('g3_revision')=='R02 actual-light-placement and dry/wet correction'
ROOT.mkdir(parents=True,exist_ok=True)
required=['G3_bay','G3_D05','G3_door_track_housing','Car_door_threshold','Train_motion_root',
 'Train_door_left','Train_door_right','G3_guide_carriage_left','GreenChair_01','GreenChair_01.001']
assert all(bpy.data.objects.get(n) for n in required), 'Observed source differs; do not adapt blindly'
original_cameras={o.name:{'matrix':tuple(tuple(r) for r in o.matrix_world),'lens':o.data.lens}
 for o in s.objects if o.type=='CAMERA'}
source_objects=[o.name for o in s.objects if o.type in {'MESH','CURVE'}]

def geometry_signature():
    s.frame_set(451);bpy.context.view_layer.update();h=hashlib.sha256()
    for name in sorted(source_objects):
        ob=bpy.data.objects[name];h.update(name.encode());h.update(repr(tuple(tuple(r) for r in ob.matrix_world)).encode())
        if ob.type=='MESH':
            for v in ob.data.vertices:h.update(repr(tuple(v.co)).encode())
    return h.hexdigest()
prior=geometry_signature()
# Clear the timeline selection only in memory; original master bytes stay intact.
s.timeline_markers.clear()

def points(objects,frame):
    s.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    return [o.evaluated_get(deps).matrix_world@Vector(v) for o in objects for v in o.evaluated_get(deps).bound_box]

def fit(cam,objects,frames):
    assert objects
    s.render.resolution_x=1000;s.render.resolution_y=625;s.render.resolution_percentage=100
    samples={f:points(objects,f) for f in frames}
    for i in range(53):
        cam.data.lens=48-i*.5
        ext=[]
        for f,p in samples.items():
            q=[world_to_camera_view(s,cam,v) for v in p]
            ext.append({'frame':f,'x':[min(v.x for v in q),max(v.x for v in q)],
                        'y':[min(v.y for v in q),max(v.y for v in q)],'depth':min(v.z for v in q)})
        if all(e['depth']>0 and e['x'][0]>=.04 and e['x'][1]<=.96 and e['y'][0]>=.04 and e['y'][1]<=.96 for e in ext):break
    else:raise RuntimeError('Additional framing cannot cover observed objects; stop, no scene movement')
    return {'camera':cam.name,'position':list(cam.location),'rotation':list(cam.rotation_euler),'lens_mm':cam.data.lens,
      'native_frame_fit_resolution':[1000,625],'fit_objects':[o.name for o in objects],'extents':ext}

door_objs=[]
for ob in s.objects:
    if ob.type not in {'MESH','CURVE'}:continue
    if ob.name.startswith(('G3_door_track_','G3_slide_guide_','G3_door_jamb_','G3_door_carriage_','Car_door_threshold')) or (ob.parent and ob.parent.name in ['Train_door_left','Train_door_right']):
        door_objs.append(ob)
assert len(door_objs)>15
wide=camera('QA_G3_door_complete',(-.9,7.1,2.85),(-2,10.70,2.27),48)
framing=[fit(wide,door_objs,[301,330,348])]
bay_objects=[o for o in s.objects if o.type in {'MESH','CURVE'} and o.name.startswith((
 'GreenChair_01','potted_plant_01','G3_walnut_cafe_top','G3_sideboard_','G3_cabinet_',
 'G3_lamp_','G3_table_','G3_turned_','G3_carved_','Platform_portal_'))]
assert len(bay_objects)>15
bay=camera('QA_G3_bay_complete',(1.5,-2.5,3.3),(-2,4.8,2.30),48)
framing.append(fit(bay,bay_objects+door_objs,[451]))
rail=camera('QA_G3_door_roller',(-2.40,9.25,3.67),(-2.96,10.59,3.40),55)
threshold=camera('QA_G3_threshold',(-.9,8.75,2.20),(-2,10.73,1.19),50)

neutral=json.loads(s['g3_neutral_lights']);night=json.loads(s['g3_night_lights'])
night_power={n:bpy.data.objects[n].data.energy for n in night}
bg=s.world.node_tree.nodes.get('Background')
def lighting(mode):
    for n,p in neutral.items():bpy.data.objects[n].data.energy=p if mode=='neutral' else 0
    for n,p in night_power.items():bpy.data.objects[n].data.energy=p if mode=='night' else 0
    # Match the R01/R02 diagnostic settings, not falsely label this G2 lighting.
    bg.inputs['Color'].default_value=(.16,.19,.23,1) if mode=='neutral' else (.10,.145,.22,1)
    bg.inputs['Strength'].default_value=.65 if mode=='neutral' else .18
    s.view_settings.exposure=0

report={'stage':'G3','status':'EXTRA_OBSERVATIONS_NOT_ACCEPTANCE','source_commit':'87d75e3b90d6b330fb378d1fc2200f5d1a52e418',
 'source_master_sha256':EXPECTED,'source_root':str(SOURCE.relative_to(Path.cwd())),
 'issue':'G3-V01','purpose':'Supplement, not replace, old G3 bay and D05 framing. No G4 work.',
 'geometry_signature_before':prior,'framing':framing,'original_cameras':original_cameras,'views':[],
 'limitation':'Native still observations of evaluated states; not a continuous new film or final 4K media.',
 'neutral_lighting':'Matches R01/R02, not the G2 original world color','human_acceptance':False,'g4_allowed':False}
(ROOT/'observation-report.json').write_text(json.dumps(report,indent=2))
jobs=[(bay,'W01-complete-bay-night.png','night',451,32,(1000,625)),
      (wide,'W02-complete-door-night.png','night',451,32,(1000,625)),
      (wide,'W03-door-closed.png','neutral',301,16,(640,400)),
      (wide,'W04-door-moving.png','neutral',330,16,(640,400)),
      (wide,'W05-door-open.png','neutral',348,16,(640,400)),
      (rail,'W06-guide-roller.png','neutral',348,32,(1000,625)),
      (threshold,'W07-threshold.png','neutral',348,32,(1000,625))]
for cam,name,light,frame,samples,res in jobs:
    if time.time()>float(os.environ.get('G3_OBSERVATION_DEADLINE','inf')):raise TimeoutError('Production deadline; preserve completed evidence')
    lighting(light)
    m=render(s,cam,ROOT/name,res=res,samples=samples,frame=frame);m['lighting']=light
    m['train_position']=list(bpy.data.objects['Train_motion_root'].location)
    m['door_position']=list(bpy.data.objects['Train_door_left'].location)
    m['carriage_position']=list(bpy.data.objects['G3_guide_carriage_left'].location)
    report['views'].append(m)
    (ROOT/'observation-report.json').write_text(json.dumps(report,indent=2))
assert geometry_signature()==prior,'Unexpected geometry or transform change'
for name,expected in original_cameras.items():
    ob=bpy.data.objects[name]
    assert tuple(tuple(r) for r in ob.matrix_world)==expected['matrix'] and ob.data.lens==expected['lens']
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
report['geometry_signature_after']=prior;report['master_bytes_unchanged']=True;report['original_cameras_unchanged']=True
report['status']='EXTRA_OBSERVATIONS_RENDERED_REVIEW_PENDING'
(ROOT/'observation-report.json').write_text(json.dumps(report,indent=2))
print('G3_EXTRA_OBSERVATIONS_COMPLETE',len(report['views']),flush=True)
