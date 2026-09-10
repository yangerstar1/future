"""Minor presentation preparation of the visually inspected R04C, not a core quality pass."""
import bpy,json,hashlib,os
from pathlib import Path
base=Path(bpy.data.filepath);parent='abe8683a5b5ffad31f3da5b0ff04a367b583c0016573a4be15d96fb384678307';assert hashlib.sha256(base.read_bytes()).hexdigest()==parent
assert bpy.app.version[:3]==(4,5,13)
out=Path(os.environ['SKYFOLD_OUT']);out.mkdir(parents=True,exist_ok=True);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();meta=json.loads((base.parent/'BUILD-MANIFEST.json').read_text());changed=[]
for o in bpy.data.collections['10_R04_GALLERY'].objects:
 if o.type!='MESH' or not o.name.startswith('R04 mobile diagnostic trolley'):continue
 for i,slot in enumerate(o.material_slots):
  if slot.material and slot.material.name=='Pearl ceramic-coated alloy' and any(p.material_index==i for p in o.data.polygons):
   slot.link='OBJECT';slot.material=bpy.data.materials['Structural graphite steel'];changed.append(o.name)
assert changed,'Expected visible cabinet material was not found'
s.camera=bpy.data.objects['R04_HERO'];s.render.engine='CYCLES';s.cycles.device='CPU'
s.render.use_persistent_data=True;s['candidate']='R04C_PRESENTATION_V1';s['source_sha']=os.environ['GITHUB_SHA'];s['auto_qualified']=False
meta.update({'candidate':s['candidate'],'source_sha':os.environ['GITHUB_SHA'],'geometry_source_sha':meta['source_sha'],'parent_scene_sha256':parent,'material_adjustment':{'objects':changed,'reason':'Darken foreground cabinet so it does not outshine the docked ship','geometry_changed':False},'presentation_targets':{'hero':[2560,1440],'second':[1920,1080],'craft':[1920,1080],'motion_preview':{'dimensions':[1280,720],'frames':192,'fps':24,'duration_seconds':8,'contract_P2_1080_pass':False}},'cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens} for o in bpy.data.collections['08_CAMERAS'].objects},'render_status':'NOT_RENDERED','gate':'NOT_AUTO_QUALIFIED'})
p=out/'skyfold-r04c.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);meta['scene_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(out/'BUILD-MANIFEST.json').write_text(json.dumps(meta,indent=2));print('R04C_PRESENTATION_SAVED',meta['scene_sha256'])
