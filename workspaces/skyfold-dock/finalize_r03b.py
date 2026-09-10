"""Narrow R03 QA fix: aperture rail termination and camera-manifest synchronization."""
import hashlib,json,os,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'output/r03/skyfold-r03.blend'
OUT=Path(os.environ['SKYFOLD_OUT']);OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='e1f8815c36bb30b8c245715fb56fd9c3a38c77955535ea99b4011170a95d4787'
assert bpy.app.version[:3]==(4,5,13)
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==EXPECTED
SC=bpy.context.scene;bpy.context.view_layer.update()
fixed={o.name:([list(r) for r in o.matrix_world],o.data.lens) for o in bpy.data.collections['08_CAMERAS'].objects}
changed=[]
for o in bpy.data.collections['06_TRANSPORT'].objects:
    if o.type!='CURVE' or not o.name.startswith('Continuous service rail'):continue
    if len(o.data.splines)!=1:continue
    sp=o.data.splines[0]
    if len(sp.points)!=6:continue
    p=sp.points[0]
    if abs(p.co.y-1608)<.01 and abs(p.co.z-512.065)<.01:
        old=list(p.co)
        o.data=o.data.copy();o.data.splines[0].points[0].co.y=1615.25
        changed.append({'object':o.name,'before':old,'after':list(o.data.splines[0].points[0].co),'purpose':'terminate upper landing rail on supported slab, outside open elevator shaft'})
assert len(changed)==2,changed
cam=bpy.data.cameras.new('O05_RETURN_LIFT_DIAGNOSTIC');cam.lens=38;cam.sensor_width=36;cam.clip_start=.08;cam.clip_end=20000
obj=bpy.data.objects.new(cam.name,cam);bpy.data.collections['08_CAMERAS'].objects.link(obj)
obj.location=(-340,1320,410);obj.rotation_euler=(Vector((-46,1608,394))-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
for name,(matrix,lens) in fixed.items():
    o=bpy.data.objects[name]
    assert matrix==[list(r) for r in o.matrix_world] and lens==o.data.lens,name
manifest=json.loads((ROOT/'output/r03/BUILD-MANIFEST.json').read_text())
manifest['inherited_R03_visibility_diagnostic']={k:manifest.pop(k) for k in ['visibility_before','visibility_after']}
manifest.update(candidate='R03B_NEAR_PIER_REPAIR',source_sha=os.environ['GITHUB_SHA'],parent_scene_sha256=EXPECTED,qa_fix=changed,visual_gate='NOT_REVIEWED',auto_qualified=False)
manifest['cameras']={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in bpy.data.collections['08_CAMERAS'].objects}
manifest['tests']['existing_camera_poses_unchanged_in_R03B']=True
manifest['tests']['upper_return_rail_end_outside_aperture']=True
manifest['tests']['camera_manifest_flushed_before_save']=True
manifest['geometry']['objects']=len(SC.objects)
manifest['notes']='R03B does not rerun the inherited R02/R03 sparse visibility rays. Actual R03B image observations are authoritative.'
SC['candidate']=manifest['candidate'];SC['source_sha']=manifest['source_sha'];SC['quality_status']='G2_REVISE_NOT_QUALIFIED'
SC.camera=bpy.data.objects['O01_HERO']
embedded=bpy.data.texts.get('BUILD-MANIFEST.json') or bpy.data.texts.new('BUILD-MANIFEST.json')
embedded.clear();embedded.write(json.dumps({k:v for k,v in manifest.items() if k!='scene_sha256'},indent=2))
path=OUT/'skyfold-r03b.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
manifest['scene_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('R03B_QA_FIXED',manifest['scene_sha256'],'VISUAL_REVIEW_PENDING')
