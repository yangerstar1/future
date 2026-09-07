"""Read-only inventory for the user-authorized G4 continuation, not G0/G2.
No master save, mutation of geometry, materials, lamps or cameras.
"""
import bpy,json,hashlib,os,collections
from pathlib import Path
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g3-r07-recovered';OUT=ROOT/'output/g4-inventory';OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='1680bcbcc8f8c0911c3c3486f7fc5da5d849b4a7016e87fad67f4233beb14d5e'
master=BASE/'g3-bay-candidate.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==master and sha(master)==EXPECTED
assert bpy.app.version[:2]==(4,5)
s=bpy.context.scene;s.frame_set(451);bpy.context.view_layer.update()
def bounds(o):
    if o.type not in ['MESH','CURVE','FONT','SURFACE']:return None
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
def simple(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    try:return list(v)
    except:return str(v)
objects=[]
for o in sorted(s.objects,key=lambda x:x.name):
    r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'data':o.data.name if o.data else None,
      'location':list(o.location),'world_location':list(o.matrix_world.translation),'rotation':list(o.rotation_euler),
      'scale':list(o.scale),'bounds':bounds(o),'matrix_world':[list(row) for row in o.matrix_world],
      'hide_render':o.hide_render,'visible_camera':getattr(o,'visible_camera',None),
      'collections':[c.name for c in o.users_collection],
      'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],
      'modifiers':[{'name':m.name,'type':m.type,'show_render':m.show_render} for m in o.modifiers]}
    if o.type=='MESH':
        r.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),uv_layers=[u.name for u in o.data.uv_layers])
    if o.type=='LIGHT':
        r['light']={k:simple(getattr(o.data,k,None)) for k in ['type','energy','color','size','size_y','shape','spot_size','spot_blend','shadow_soft_size']}
    if o.type=='CAMERA':
        r['camera']={k:simple(getattr(o.data,k,None)) for k in ['type','lens','clip_start','clip_end','ortho_scale','shift_x','shift_y']}
        r['camera']['dof']=o.data.dof.use_dof
    if o.animation_data:r['action']=o.animation_data.action.name if o.animation_data.action else None
    objects.append(r)
materials=[]
for m in bpy.data.materials:
    r={'name':m.name,'diffuse_color':list(m.diffuse_color),'users':m.users,'nodes':[],'links':[]}
    if m.use_nodes:
        for n in m.node_tree.nodes:
            x={'name':n.name,'type':n.type,'inputs':{q.name:simple(q.default_value) for q in n.inputs if hasattr(q,'default_value')},'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None}
            if n.type=='TEX_IMAGE':x.update(projection=n.projection,extension=n.extension)
            if n.type=='UVMAP':x['uv_map']=n.uv_map
            r['nodes'].append(x)
        r['links']=[{'from_node':l.from_node.name,'from_socket':l.from_socket.name,'to_node':l.to_node.name,'to_socket':l.to_socket.name} for l in m.node_tree.links]
    materials.append(r)
source={str(p.relative_to(ROOT.parent.parent)):p.read_text() for p in ROOT.iterdir() if p.suffix in ['.py','.sh']}
source.update({str(p):p.read_text() for p in Path('.github/workflows').glob('glasshouse*.yml')})
(OUT/'source-snapshot.json').write_text(json.dumps(source,indent=2))
report={'stage':'G4_READ_ONLY_EXTENSION_INVENTORY','user_authorization':'Direct G4 requested after disclosure that G3 craft review remains unmet. Scope-order exception only, not artistic acceptance.',
 'source_master_sha256':EXPECTED,'source_evidence_commit':'192eba1352585df211f1aa2447a193eec949f6be','run_id':os.environ['GITHUB_RUN_ID'],'source_sha':os.environ['GITHUB_SHA'],
 'blender':bpy.app.version_string,'engine':s.render.engine,'objects':objects,'materials':materials,
 'scene_properties':{k:simple(s[k]) for k in s.keys()},'collections':[{'name':c.name,'objects':len(c.objects),'children':[v.name for v in c.children]} for c in bpy.data.collections],
 'images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images],
 'source_master_unchanged':sha(master)==EXPECTED,'human_acceptance':False}
assert report['source_master_unchanged']
(OUT/'R07-extension-inventory.json').write_text(json.dumps(report,indent=2))
print('G4_INVENTORY_COMPLETE_SOURCE_UNCHANGED',len(objects),len(materials),flush=True)
