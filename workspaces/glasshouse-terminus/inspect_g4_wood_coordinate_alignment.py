"""Read-only inspection of the already integrated COAST-R04.
The packed veneer scan was opened externally and has predominantly horizontal
(U-direction) grain. Check actual material links and per-face UV directions;
never infer correctness from earlier variable names saying 'vertical grain'.
"""
import bpy, hashlib, json, os
from pathlib import Path
import numpy as np
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-coast-r04';OUT=ROOT/'output/g4-wood-axis-inspection';OUT.mkdir(parents=True,exist_ok=True)
MASTER=BASE/'g4-full-scene-candidate.blend'
EXPECTED='51a3501edd81f879ba1b5c3e6dd6986e3306968d1319199a624f363667d65a9c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==MASTER and sha(MASTER)==EXPECTED
assert bpy.app.version[:3]==(4,5,13)
s=bpy.context.scene
assert s.get('g4_revision')=='COAST-R04 scanned wool and overcast surface response on native sea geology rain'
assert s.frame_current==451 and s.view_settings.exposure==0
TABLES=['G3_walnut_cafe_top','G4_cafe_G3_walnut_cafe_top','G4_cafe_G3_walnut_cafe_top.001']
CABINET=['G3_sideboard_carcass','G3_cabinet_stile','G3_cabinet_stile.001','G3_cabinet_rail','G3_cabinet_rail.001','G3_cabinet_recessed_panel','G3_cabinet_recessed_panel.001']
EDGE='G4R03_G4_circumferential_edge_veneer';JOINERY='G4R03_G4_walnut_metre_UV'
assert all(n in bpy.data.objects for n in TABLES+CABINET)
report={'stage':'G4','mode':'READ_ONLY_WOOD_AXIS_INSPECTION','master_sha256':EXPECTED,'source_evidence_commit':'def004d60bb37a58a043a3506fb2bbda5c3a0e5c','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'objects':[],'materials':[],'g4_stage_pass':False,'human_acceptance':False}
for name in TABLES+CABINET:
 o=bpy.data.objects[name];assert o.type=='MESH' and o.data.uv_layers.active
 mats=[m.name if m else None for m in o.data.materials]
 target=EDGE if name in TABLES else JOINERY
 assert target in mats,(name,mats)
 active=o.data.uv_layers.active
 row={'name':name,'materials':mats,'active_uv':active.name,'all_uvs':[q.name for q in o.data.uv_layers],'dimensions':list(o.dimensions),'matrix_world':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'faces':[]}
 faces=[p for p in o.data.polygons if o.data.materials[p.material_index].name==target]
 row['affected_faces']=len(faces)
 for p in faces[::max(1,len(faces)//16)][:20]:
  co=np.asarray([o.data.vertices[o.data.loops[li].vertex_index].co[:] for li in p.loop_indices],dtype=float)
  uv=np.asarray([active.data[li].uv[:] for li in p.loop_indices],dtype=float)
  f={'polygon':p.index,'normal':list(p.normal),'material_index':p.material_index,'local_points':co.tolist(),'uv_points':uv.tolist()}
  if name not in TABLES:
   normal_axis=int(np.argmax(np.abs(np.asarray(p.normal))))
   axes=[i for i in range(3) if i!=normal_axis]
   design_axis=1 if name.startswith('G3_cabinet_rail') else 2
   A=np.column_stack([co[:,axes],np.ones(len(co))]);fit=np.linalg.lstsq(A,uv,rcond=None)[0]
   f.update(projected_axes=axes,design_grain_axis=design_axis,local_to_uv_linear=fit.tolist(),max_fit_error=float(np.max(np.abs(A@fit-uv))))
   if design_axis in axes:
    derivative=fit[axes.index(design_axis)]
    f['uv_direction_of_member_length']=derivative.tolist()
    f['member_length_mapped_predominantly_to']='U' if abs(derivative[0])>abs(derivative[1]) else 'V'
  row['faces'].append(f)
 report['objects'].append(row)
for name in [EDGE,JOINERY]:
 m=bpy.data.materials[name];n=m.node_tree.nodes
 row={'name':name,'images':[],'links':[(q.from_node.name,q.from_socket.name,q.to_node.name,q.to_socket.name) for q in m.node_tree.links],
      'normal_maps':[{'node':q.name,'uv_map':q.uv_map,'space':q.space,'strength':q.inputs['Strength'].default_value} for q in n if q.type=='NORMAL_MAP'],
      'vector_multiply':[{'node':q.name,'operand':list(q.inputs[1].default_value)} for q in n if q.type=='VECT_MATH' and q.operation=='MULTIPLY']}
 for q in n:
  if q.type!='TEX_IMAGE' or not q.image:continue
  im=q.image;info={'node':q.name,'name':im.name,'resolution':list(im.size),'packed':bool(im.packed_file),'color_space':im.colorspace_settings.name}
  if q.name=='diff':
   assert im.packed_file,'Use the source packed scan, not external substitute'
   raw=bytes(im.packed_file.data);info['packed_sha256']=hashlib.sha256(raw).hexdigest()
   assert info['packed_sha256']=='c0ba49a1fbc7b6ef93dd87abd83eee21eab611a6b291a0bdc6e4cf67b468158f'
   (OUT/'verified-source-walnut-scan.jpg').write_bytes(raw)
  row['images'].append(info)
 report['materials'].append(row)
assert sha(MASTER)==EXPECTED
report['source_master_unchanged']=True
report['limits']=['No scene edits, no save and no beauty rendering. UV coordinates and scan orientation are diagnostics, not artistic acceptance.','Only the three confirmed tabletops and seven sideboard members inspected; no blanket correction of every wood object implied.']
(OUT/'wood-axis-inspection.json').write_text(json.dumps(report,indent=2))
summary={'master_sha256':EXPECTED,'objects':[{'name':o['name'],'active_uv':o['active_uv'],'affected_faces':o['affected_faces'],'member_mapping_counts':{axis:sum(f.get('member_length_mapped_predominantly_to')==axis for f in o['faces']) for axis in ['U','V']}} for o in report['objects']],'source_master_unchanged':True}
(OUT/'wood-axis-summary.json').write_text(json.dumps(summary,indent=2))
print('READ_ONLY_WOOD_AXIS_INSPECTION_COMPLETE',json.dumps(summary),flush=True)
