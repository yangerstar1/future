"""Native coast on preserved rain/material master. No generated images.
Ocean spectrum plus 3D proximity wash; not a coastal fluid-impact simulation.
"""
import bpy,math,json,os,sys,hashlib,shutil,time
from pathlib import Path
from mathutils import Vector,Matrix
from array import array
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import material,mesh,camera,render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve();Q=json.loads((ROOT/'g4-coastal-environment-request.json').read_text())
BASE=ROOT/Q['parent_directory'];ASSETS=ROOT/'output/g4-storm-assets';OUT=ROOT/'output/g4-coast-r01';OUT.mkdir(parents=True,exist_ok=True)
MODE=os.environ['G4_COAST_MODE'];assert MODE in ['build','preview','detail','motion']
s=bpy.context.scene;assert bpy.app.version[:2]==(4,5)
REV='COAST-R01 native ocean and adapted licensed coast scan on rain master'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
 ps=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
def coll(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name];return c

def mn(n,l,op,a,b=None):
 v=n.new('ShaderNodeMath');v.operation=op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,(float,int)):v.inputs[i].default_value=x
  else:l.new(x,v.inputs[i])
 return v.outputs[0]
def scale(n,l,v,k):
 nd=n.new('ShaderNodeVectorMath');nd.operation='SCALE';l.new(v,nd.inputs[0]);nd.inputs['Scale'].default_value=k;return nd.outputs[0]
def noise(n,l,v,frequency,detail=3,animated=False):
 nd=n.new('ShaderNodeTexNoise');nd.inputs['Scale'].default_value=frequency;nd.inputs['Detail'].default_value=detail;l.new(v,nd.inputs['Vector'])
 if animated:nd.noise_dimensions='4D';nd.inputs['W'].driver_add('default_value').driver.expression='frame/180'
 return nd.outputs['Fac']
def remap(n,l,v,a,b,lo=0,hi=1):
 nd=n.new('ShaderNodeMapRange');nd.clamp=True;nd.inputs['From Min'].default_value=lo;nd.inputs['From Max'].default_value=hi;nd.inputs['To Min'].default_value=a;nd.inputs['To Max'].default_value=b;l.new(v,nd.inputs['Value']);return nd.outputs['Result']
def bump(n,l,height,old,distance,strength):
 nd=n.new('ShaderNodeBump');nd.inputs['Distance'].default_value=distance;nd.inputs['Strength'].default_value=strength;l.new(height,nd.inputs['Height'])
 if old is not None:l.new(old,nd.inputs['Normal'])
 return nd.outputs['Normal']
def protected(names):
 h=hashlib.sha256()
 for name in sorted(names):
  o=bpy.data.objects[name];h.update(repr((name,o.type,o.parent.name if o.parent else None,o.hide_render,tuple(tuple(v) for v in o.matrix_world),getattr(o,'visible_camera',None),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(repr([(len(p.vertices),p.use_smooth) for p in o.data.polygons]).encode())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.type)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 return h.hexdigest()
def image_map(n,l,vector,row):
 im=bpy.data.images.load(str(ASSETS/row['path']),check_existing=True)
 if row['role']!='diff':im.colorspace_settings.name='Non-Color'
 tex=n.new('ShaderNodeTexImage');tex.name='Licensed seaside '+row['role'];tex.image=im;tex.projection='BOX';tex.projection_blend=.22;l.new(vector,tex.inputs['Vector']);return tex

def rock_finish(source,scan_material=None):
 m=scan_material.copy() if scan_material else material('G4COAST_scanned_core',(.14,.16,.16),rough=.5)
 m.name='G4COAST_scanned_cliff_wet' if scan_material else 'G4COAST_scanned_core'
 n=m.node_tree.nodes;l=m.node_tree.links;p=next(x for x in n if x.type=='BSDF_PRINCIPLED');tc=n.new('ShaderNodeTexCoord');v=scale(n,l,tc.outputs['Object'],.5)
 maps={r['role']:r for r in source['files']};diff=image_map(n,l,v,maps['diff']);height=image_map(n,l,v,maps['disp']);rough=image_map(n,l,v,maps['rough'])
 if not scan_material:
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.67,.70,.70,1);l.new(diff.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
 else:
  base=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
  if base:
   mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.25;l.new(base,mix.inputs[1]);l.new(diff.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
 old=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
 l.new(bump(n,l,height.outputs['Color'],old,.045,.38),p.inputs['Normal']);l.new(remap(n,l,rough.outputs['Color'],.26,.57),p.inputs['Roughness'])
 p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=.17;p.inputs['Coat Roughness'].default_value=.22
 m['source_license']='CC0-1.0';m['source_detail']='https://polyhaven.com/a/seaside_rock';m['texture_width_metres']=2.0
 return m

def coast_distance_modifier(o,rocks):
 g=bpy.data.node_groups.new('G4COAST_surface_distance_wash','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 n=g.nodes;l=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput')
 info=n.new('GeometryNodeCollectionInfo');info.inputs['Collection'].default_value=rocks;info.transform_space='RELATIVE'
 real=n.new('GeometryNodeRealizeInstances');l.new(info.outputs['Instances'],real.inputs['Geometry'])
 prox=n.new('GeometryNodeProximity');prox.target_element='FACES';l.new(real.outputs['Geometry'],prox.inputs['Target'])
 weight=remap(n,l,prox.outputs['Distance'],1,0,.25,3.4)
 store=n.new('GeometryNodeStoreNamedAttribute');store.data_type='FLOAT';store.domain='POINT';store.inputs['Name'].default_value='CoastalWash';l.new(inp.outputs['Geometry'],store.inputs['Geometry']);l.new(weight,store.inputs['Value']);l.new(store.outputs['Geometry'],out.inputs['Geometry'])
 mod=o.modifiers.new('Geometry-bound shoreline wash, not fluid solver','NODES');mod.node_group=g

def ocean_surface():
 m=material('G4COAST_deep_water_and_foam',(.018,.051,.063),rough=.20,transmission=.22)
 n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF'];p.inputs['IOR'].default_value=1.333;p.inputs['Coat Weight'].default_value=0
 geo=n.new('ShaderNodeNewGeometry');small=noise(n,l,geo.outputs['Position'],3.3,3,True);l.new(bump(n,l,small,None,.028,.35),p.inputs['Normal'])
 a=n.new('ShaderNodeAttribute');a.attribute_name='OceanFoam';b=n.new('ShaderNodeAttribute');b.attribute_name='CoastalWash'
 native=remap(n,l,a.outputs['Fac'],0,.70,.12,.75)
 spatial=noise(n,l,geo.outputs['Position'],1.6,3,True);shore=mn(n,l,'MULTIPLY',b.outputs['Fac'],remap(n,l,spatial,0,.83,.34,.67));mask=mn(n,l,'MAXIMUM',native,shore)
 foam=n.new('ShaderNodeBsdfPrincipled');foam.name='Whitewater microbubble layer';foam.inputs['Base Color'].default_value=(.48,.53,.52,1);foam.inputs['Roughness'].default_value=.70
 l.new(bump(n,l,noise(n,l,geo.outputs['Position'],18,2,True),None,.008,.28),foam.inputs['Normal'])
 mix=n.new('ShaderNodeMixShader');l.new(mask,mix.inputs[0]);l.new(p.outputs['BSDF'],mix.inputs[1]);l.new(foam.outputs['BSDF'],mix.inputs[2]);l.new(mix.outputs[0],n['Material Output'].inputs['Surface'])
 return m

if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==Q['parent_master_sha256']
 assert s.get('g4_revision')==Q['parent_revision'];assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 original_names=[o.name for o in s.objects];protected_names=[n for n in original_names if n not in {'Complete_cliff_mass','Ocean_extent'}]
 s.frame_set(451);bpy.context.view_layer.update();before=protected(protected_names)
 manifest=json.loads((ASSETS/'STORM-ASSET-SOURCES.json').read_text());probe=json.loads((ASSETS/'ASSET-AND-API-PROBE.json').read_text())
 for r in manifest['assets']:
  for f in r['files']:assert sha(ASSETS/f['path'])==f['sha256']
 assert probe['scan']['objects'][0]['name']=='coastal_cliff_04' and 'JONSWAP' in probe['api']['spectrum']['enum']
 report={'stage':'G4','revision':'COAST-R01','status':'CHALLENGER_NOT_ART_PASS','parent_master_sha256':Q['parent_master_sha256'],'parent_evidence_commit':Q['parent_evidence_commit'],'asset_evidence_commit':Q['asset_evidence_commit'],'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'scope':'Real marine waves and rock geometry on native rain/material master; no generated imagery.','g4_stage_pass':False,'human_acceptance':False,'cliff':{},'ocean':{},'far_clip_extensions':[]}
 rocksource=next(a for a in manifest['assets'] if a['asset_id']=='seaside_rock');core=bpy.data.objects['Complete_cliff_mass'];report['cliff']['core_before']=bounds(core)
 core.data=core.data.copy();core.data.materials.clear();core.data.materials.append(rock_finish(rocksource))
 for p in core.data.polygons:p.use_smooth=True
 for md in core.modifiers:
  if md.type=='SUBSURF':md.subdivision_type='SIMPLE';md.levels=4;md.render_levels=4
  if md.type=='DISPLACE':md.strength=1.20
 rock_collection=coll('G4COAST_licensed_rock_surfaces');record=next(a for a in manifest['assets'] if a['asset_id']=='coastal_cliff_04');old=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(ASSETS/record['entry']));scans=[o for o in bpy.data.objects if o not in old and o.type=='MESH'];assert len(scans)==1
 ob=scans[0];ob.data=ob.data.copy();ob.data.transform(ob.matrix_world);ob.parent=None;ob.matrix_world=Matrix.Identity(4)
 for c in list(ob.users_collection):c.objects.unlink(ob)
 rock_collection.objects.link(ob);ob.name='G4COAST_adapted_scanned_cliff_ring'
 lo,hi=bounds(ob);assert abs((hi[0]-lo[0])-86.77198)<.01 and abs((hi[2]-lo[2])-10.999709)<.01,'Scan differs from measured probe'
 # Deterministically bend the continuous scanned face around existing bedrock.
 # Real scan strata/erosion and UVs remain; this is disclosed landscape adaptation.
 arr=np.empty(len(ob.data.vertices)*3,dtype=np.float32);ob.data.vertices.foreach_get('co',arr);v=arr.reshape(-1,3).copy()
 theta=(v[:,0]-lo[0])/(hi[0]-lo[0])*(2*math.pi+.055)+math.pi*.72;radial=-(v[:,1]+2.0)*.48
 arr=arr.reshape(-1,3);arr[:,0]=-1+(29.0+radial)*np.cos(theta);arr[:,1]=-2.5+(24.5+radial)*np.sin(theta);arr[:,2]=v[:,2]*1.95-21.10
 ob.data.vertices.foreach_set('co',arr.reshape(-1));ob.data.update()
 if ob.data.has_custom_normals:ob.data.normals_split_custom_set_from_vertices([(0.0,0.0,0.0)]*len(ob.data.vertices))
 for i,m in enumerate(list(ob.data.materials)):ob.data.materials[i]=rock_finish(rocksource,m)
 for p in ob.data.polygons:p.use_smooth=True
 dec=ob.modifiers.new('Bounded scanned detail LOD, original source archived','DECIMATE');dec.ratio=.52;dec.use_collapse_triangulate=True
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=dec.name)
 report['cliff'].update(scan_object=ob.name,source_dimensions=[hi[i]-lo[i] for i in range(3)],source_vertices=probe['scan']['objects'][0]['vertices'],source_triangles=probe['scan']['objects'][0]['polygons'],adapted_vertices=len(ob.data.vertices),adapted_triangles=len(ob.data.polygons),deformation='Single licensed face bent around elliptical bedrock, 1.95 vertical scale; original archived. Not real-location reconstruction.',scan_bounds=bounds(ob),scan_lod_ratio=.52)
 proximity=bpy.data.collections.new('G4COAST_water_contact_geometry');s.collection.children.link(proximity);proximity.objects.link(core);proximity.objects.link(ob)
 for o in list(s.objects):
  if o.name.startswith(('Viaduct_pier','Viaduct_bedrock_footing')):proximity.objects.link(o)
 sea=bpy.data.objects['Ocean_extent'];report['ocean']['old_bounds']=bounds(sea)
 axis=sorted(set([i*.9 for i in range(-230,231)]+[-20000,-10000,-5000,-2500,-1200,-700,-450,-300,-240,240,300,450,700,1200,2500,5000,10000,20000]))
 N=len(axis);verts=[(x,y,0) for y in axis for x in axis];faces=[(j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for j in range(N-1) for i in range(N-1)]
 data=bpy.data.meshes.new('G4COAST_graded_open_ocean_grid');data.from_pydata(verts,[],faces);data.update();sea.data=data;sea.location=(0,0,-22.15)
 for p in data.polygons:p.use_smooth=True
 data.materials.append(ocean_surface());om=sea.modifiers.new('Native spectral storm ocean','OCEAN');om.geometry_mode='DISPLACE';om.resolution=16;om.viewport_resolution=16;om.spatial_size=100;om.size=1
 om.spectrum='JONSWAP';om.wave_scale=1.8;om.choppiness=1.2;om.wind_velocity=18;om.depth=200;om.wave_scale_min=.035;om.wave_alignment=.4;om.wave_direction=math.radians(25);om.random_seed=23;om.use_foam=True;om.foam_layer_name='OceanFoam';om.foam_coverage=.15
 om.driver_add('time').driver.expression='frame/30.0';coast_distance_modifier(sea,proximity)
 s.frame_set(451);bpy.context.view_layer.update()
 report['ocean'].update(method='Native JONSWAP Ocean DISPLACE and true geometry-proximity art wash, not coastal fluid solver.',grid_vertices=len(data.vertices),grid_faces=len(data.polygons),extent_metres=40000,near_grid_metres=.9,settings={k:getattr(om,k) for k in ['resolution','spatial_size','wind_velocity','wave_scale','choppiness','foam_coverage','spectrum']},proximity_objects=len(proximity.objects),motion=[])
 sigs=[]
 for frame in [451,460,451]:
  s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=sea.evaluated_get(dg);me=ev.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3)
  near=a[(abs(a[:,0])<150)&(abs(a[:,1])<150)];sig=hashlib.sha256(near.tobytes()).hexdigest();sigs.append(sig)
  report['ocean']['motion'].append({'frame':frame,'native_time':om.time,'positions_sha256':sig,'near_z_range':[float(near[:,2].min()),float(near[:,2].max())],'attributes':[(at.name,at.data_type,at.domain) for at in me.attributes]})
  assert 'OceanFoam' in me.attributes and 'CoastalWash' in me.attributes,'Native foam/contact attribute missing'
  assert float(near[:,2].max()-near[:,2].min())>.5,'Real waves not evaluated';ev.to_mesh_clear()
 assert sigs[0]==sigs[2] and sigs[0]!=sigs[1],'Native time fails replay'
 for name in original_names:
  o=bpy.data.objects[name]
  if o.type=='CAMERA':
   report['far_clip_extensions'].append({'camera':name,'before':o.data.clip_end,'after':50000,'reason':'Render physical distant sea rather than old finite edge; transform/lens/near clip unchanged.'});o.data.clip_end=50000
 coll('G4COAST_additional_observations')
 for name,pos,target,lens in [('G4COAST_rock_water_close',(38,39,-9),(13,17,-15),52),('G4COAST_ocean_close',(-33,38,-13),(-43,18,-22),48)]:
  c=camera(name,pos,target,lens);c.data.clip_end=50000
 s.frame_set(451);bpy.context.view_layer.update();report['protected_before']=before;report['protected_after']=protected(protected_names);assert before==report['protected_after'],'Protected building/train/rain/material/camera changed'
 for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json']:
  if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
 (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json');shutil.copy2(ASSETS/'STORM-ASSET-SOURCES.json',OUT/'STORM-ASSET-SOURCES.json');shutil.copy2(BASE/'build-report.json',OUT/'PARENT-R03-build-report.json');shutil.copy2(ASSETS/'ASSET-AND-API-PROBE.json',OUT/'ASSET-AND-API-PROBE.json')
 s['g4_revision']=REV;s['g4_coast_parent_sha256']=Q['parent_master_sha256'];s['coastal_wave_limit']='Native deep-water spectrum and art-directed proximity wash, not fluid impact simulation';s.camera=bpy.data.objects['C01_exterior_hero'];s.frame_set(451)
 save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==Q['parent_master_sha256']
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size;(OUT/'build-report.json').write_text(json.dumps(report,indent=2));assert report['master_bytes']<98000000,'Git file budget exceeded'
 print('COAST_R01_SAVED_REVIEW_PENDING',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.045;s.cycles.adaptive_min_samples=16
 jobs={'preview':[('C01_exterior_hero','C01-coast-rain.png',(1440,900),48),('C02_reverse_exterior','C02-reverse-coast.png',(1280,800),40)],'detail':[('G4COAST_rock_water_close','E01-rock-and-water.png',(1440,900),64),('G4COAST_ocean_close','E02-wave-and-foam.png',(1440,900),64),('C03_hall_to_platform','C03-rain-hall-regression.png',(1440,900),64)],'motion':[]}[MODE]
 metrics=[]
 for cam,name,res,samples in jobs:
  assert time.time()<float(os.environ['G4_COAST_DEADLINE']),'Finite render deadline reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451);row.update(source_master_sha256=expected,native_render=True,revision='COAST-R01');metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2));print('COAST_NATIVE_VIEW_SAVED',name,flush=True)
 if MODE=='motion':
  d=OUT/'motion';d.mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.08
  for j,f in enumerate(range(451,481,3)):
   assert time.time()<float(os.environ['G4_COAST_DEADLINE'])
   row=render(s,bpy.data.objects['G4COAST_ocean_close'],d/f'{j:04d}.png',res=(640,400),samples=16,frame=f);row.update(source_master_sha256=expected,native_render=True,proof_only=True);metrics.append(row);(OUT/'motion-render-metrics.json').write_text(json.dumps(metrics,indent=2))
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
