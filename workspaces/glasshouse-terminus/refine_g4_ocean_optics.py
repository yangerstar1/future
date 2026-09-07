"""COAST-R03, based on actual C01/C02 native failures, not guessed beautification.
Change only Ocean_extent and its owned material/node group. All other source
assets, rain, lights, cameras and exposure stay unchanged.
"""
import bpy,json,os,sys,hashlib,shutil,time,math
from pathlib import Path
from array import array
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r02';OUT=ROOT/'output/g4-coast-r03';OUT.mkdir(parents=True,exist_ok=True)
PARENT='b8cea93e7511088f418afbc843b66ddd4dcd0e82f34860b192150341f258ef64';REV='COAST-R03 dielectric closed ocean with graded geometry detail'
MODE=os.environ['G4_OCEAN_MODE'];assert MODE in ['build','exterior','water','motion']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sig():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.name=='Ocean_extent':continue
  h.update(repr((o.name,o.type,o.hide_render,o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.type)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.look,s.view_settings.view_transform)).encode());return h.hexdigest()
def mathn(n,l,op,a,b):
 q=n.new('ShaderNodeMath');q.operation=op
 for i,v in enumerate([a,b]):
  if isinstance(v,(float,int)):q.inputs[i].default_value=v
  else:l.new(v,q.inputs[i])
 return q.outputs[0]

if MODE=='build':
 p=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==p and sha(p)==PARENT
 assert s.get('g4_revision')=='COAST-R02 native coast with integrated round-drop shutter correction'
 s.frame_set(451);bpy.context.view_layer.update();before=sig();o=bpy.data.objects['Ocean_extent'];old=o.data;om=next(m for m in o.modifiers if m.type=='OCEAN');assert om.geometry_mode=='DISPLACE'
 a=np.empty(len(old.vertices)*3,dtype=np.float32);old.vertices.foreach_get('co',a);a=a.reshape(-1,3)
 assert len(a)==229441 and abs(a[:,2]).max()<.0001 and abs(a[:,0]).max()==20000
 N=int(math.isqrt(len(a)));assert N*N==len(a)
 vertices=a.tolist();faces=[tuple(p.vertices) for p in old.polygons]
 # Close the optical water body with four far-side walls and a planar bottom.
 # Unlike deep Solidify along wave normals, this cannot fold the bottom sideways.
 bottoms=[]
 for x,y in [(-20000,-20000),(20000,-20000),(20000,20000),(-20000,20000)]:bottoms.append(len(vertices));vertices.append((x,y,-90))
 chains=[list(range(N)),[j*N+N-1 for j in range(N)],list(range(N*N-1,(N-1)*N-1,-1)),[j*N for j in range(N-1,-1,-1)]]
 for i,chain in enumerate(chains):faces.append(tuple(list(reversed(chain))+[bottoms[i],bottoms[(i+1)%4]]))
 faces.append(tuple(reversed(bottoms)))
 data=bpy.data.meshes.new('G4COAST_R03_closed_optical_ocean');data.from_pydata(vertices,[],faces);data.update();o.data=data
 for face in data.polygons:face.use_smooth=True
 xyz=np.asarray(vertices,dtype=np.float32);r=np.maximum(abs(xyz[:,0]),abs(xyz[:,1]));w=np.clip((207-r)/(207-137),0,1);w=w*w*(3-2*w)
 rest=data.attributes.new('OceanRestPosition','FLOAT_VECTOR','POINT');rest.data.foreach_set('vector',xyz.reshape(-1));weight=data.attributes.new('OceanGeometryWeight','FLOAT','POINT');weight.data.foreach_set('value',w)
 mod=next(m for m in o.modifiers if m.type=='NODES');g=mod.node_group.copy();g.name='G4COAST_R03_distance_wash_and_far_geometry_transition';mod.node_group=g;n=g.nodes;l=g.links
 inp=next(q for q in n if q.bl_idname=='NodeGroupInput');targets=[v.to_socket for v in list(inp.outputs['Geometry'].links)]
 pos=n.new('GeometryNodeInputPosition');restn=n.new('GeometryNodeInputNamedAttribute');restn.data_type='FLOAT_VECTOR';restn.inputs['Name'].default_value='OceanRestPosition'
 wn=n.new('GeometryNodeInputNamedAttribute');wn.data_type='FLOAT';wn.inputs['Name'].default_value='OceanGeometryWeight'
 sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';l.new(pos.outputs['Position'],sub.inputs[0]);l.new(restn.outputs['Attribute'],sub.inputs[1])
 sc=n.new('ShaderNodeVectorMath');sc.operation='SCALE';l.new(sub.outputs[0],sc.inputs[0]);l.new(wn.outputs['Attribute'],sc.inputs['Scale'])
 add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(restn.outputs['Attribute'],add.inputs[0]);l.new(sc.outputs[0],add.inputs[1])
 sp=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],sp.inputs['Geometry']);l.new(add.outputs[0],sp.inputs['Position'])
 for target in targets:l.new(sp.outputs['Geometry'],target)
 original=bpy.data.materials['G4COAST_deep_water_and_foam'];m=original.copy();m.name='G4COAST_R03_dielectric_water_and_whitewater';data.materials.append(m);n=m.node_tree.nodes;l=m.node_tree.links;pbr=n['Principled BSDF']
 assert abs(pbr.inputs['Transmission Weight'].default_value-.22)<.001
 pbr.inputs['Transmission Weight'].default_value=1;pbr.inputs['Base Color'].default_value=(.75,.92,.94,1);pbr.inputs['Roughness'].default_value=.105;pbr.inputs['IOR'].default_value=1.333;pbr.inputs['Metallic'].default_value=0;pbr.inputs['Coat Weight'].default_value=0
 vol=n.new('ShaderNodeVolumeAbsorption');vol.name='90m bounded deep-water optical absorption';vol.inputs['Color'].default_value=(.07,.30,.37,1);vol.inputs['Density'].default_value=.035;l.new(vol.outputs['Volume'],n['Material Output'].inputs['Volume'])
 geom=next(q for q in n if q.type=='NEW_GEOMETRY');oldnormal=pbr.inputs['Normal'].links[0].from_socket
 tex=n.new('ShaderNodeTexNoise');tex.name='Secondary capillary-wave surface, including distant LOD';tex.noise_dimensions='4D';tex.inputs['Scale'].default_value=.27;tex.inputs['Detail'].default_value=4;tex.inputs['Roughness'].default_value=.65;tex.inputs['W'].driver_add('default_value').driver.expression='frame/85.0';l.new(geom.outputs['Position'],tex.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.name='Sub-geometry irregular water surface';bump.inputs['Distance'].default_value=.18;bump.inputs['Strength'].default_value=.32;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(oldnormal,bump.inputs['Normal']);l.new(bump.outputs['Normal'],pbr.inputs['Normal'])
 # Coarse distant vertices must not interpolate isolated high-foam samples into stripes.
 attr=next(q for q in n if q.type=='ATTRIBUTE' and q.attribute_name=='OceanFoam');outs=[v.to_socket for v in list(attr.outputs['Fac'].links)]
 fade=n.new('ShaderNodeAttribute');fade.attribute_name='OceanGeometryWeight';product=mathn(n,l,'MULTIPLY',attr.outputs['Fac'],fade.outputs['Fac'])
 for target in outs:l.new(product,target)
 report={'stage':'G4','revision':'COAST-R03','parent_master_sha256':PARENT,'parent_evidence_commit':'071ba6959335f094209fbc4537d2ce2b1246d2dc','reviewed_native_artifact':10029611593,'reviewed_zip_sha256':'4f3fa0c03fdff1be15465163367fa8d91f90d037f5c858f24b14659b19f9e0dc','observations':['Native C01/C02 show long distant triangles from sparse displaced grid, not realistic sea.','Water looked plastic because surface had78percent diffuse rather than a dielectric optical body.'],'changes':['Only Ocean_extent geometry, owned node group and water shader. No station/cliff/rain/material/light/camera/exposure changes.','Native spectral geometry full within max-XY137m, smooth137..207m transition. Farther water uses continuous animated surface normals, not camera-dependent hiding.','Closed90m deep optical body, full dielectric transmission/IOR1.333 and absorption, retained non-emissive crest/coastal foam.'],'motion':[],'g4_stage_pass':False,'human_acceptance':False,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID']}
 hashes=[]
 for frame in [451,460,451]:
  s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();out=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',out);out=out.reshape(-1,3);near=(np.maximum(abs(xyz[:,0]),abs(xyz[:,1]))<130);far=(r>=207)&(xyz[:,2]==0)
  assert abs(out[far,2]).max()<.001,'Coarse distant water still displaced';h=hashlib.sha256(out[near].tobytes()).hexdigest();hashes.append(h)
  report['motion'].append({'frame':frame,'near_z_range':[float(out[near,2].min()),float(out[near,2].max())],'far_top_max_abs_z':float(abs(out[far,2]).max()),'near_position_sha256':h,'closed_optical_boundary':len(me.polygons)==len(old.polygons)+5});ev.to_mesh_clear()
 assert hashes[0]==hashes[2] and hashes[0]!=hashes[1]
 s.frame_set(451);bpy.context.view_layer.update();report['protected_before']=before;report['protected_after']=sig();assert before==report['protected_after']
 for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json','STORM-ASSET-SOURCES.json','ASSET-AND-API-PROBE.json','PARENT-R03-build-report.json','COAST-R01-build-report.json']:
  if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
 (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json');shutil.copy2(BASE/'build-report.json',OUT/'COAST-R02-build-report.json')
 s['g4_revision']=REV;s['ocean_detail_scope']='137m full geometry, smooth transition to207m, distant procedural normal detail; not uniform40km simulation';s.camera=bpy.data.objects['C01_exterior_hero'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(BASE/'g4-full-scene-candidate.blend')==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size;(OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('COAST_R03_SOURCE_SAVED_NOT_ART_PASS',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 jobs={'exterior':[('C01_exterior_hero','C01-dielectric-coast.png',(1440,900),48,451),('C02_reverse_exterior','C02-dielectric-reverse.png',(1280,800),40,451)],'water':[('G4COAST_ocean_close','E02-real-water.png',(1440,900),64,451),('G4COAST_rock_water_close','E01-rock-water.png',(1440,900),64,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.08
  jobs=[('G4COAST_ocean_close',f'motion/{j:04d}.png',(640,400),16,f) for j,f in enumerate(range(451,481,3))]
 metrics=[]
 for cam,name,res,samples,frame in jobs:
  assert time.time()<float(os.environ['G4_OCEAN_DEADLINE']),'Finite ocean correction deadline reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame);row.update(native_render=True,master_sha256=expected,max_bounces=10,transmission_bounces=8,revision='COAST-R03',proof_only=MODE=='motion');metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2));print('COAST_R03_NATIVE_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
