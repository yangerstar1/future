"""COAST-R06. Native weather surfaces on the verified integrated R05.
No image generation, no old R02 restoration, no replacement of ocean or scan geometry.
Surface water is an artist-controlled layered shader plus attached cap geometry;
falling rain reuses the inspected round-drop/SceneTime/SetID graph. Not fluid sim.
"""
import bpy, os, sys, math, random, json, hashlib, shutil, time
from pathlib import Path
from array import array
from collections import Counter
from mathutils import Vector
import numpy as np
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import mesh,render,save
BASE=ROOT/'output/g4-coast-r05';OUT=ROOT/'output/g4-coast-r06';OUT.mkdir(parents=True,exist_ok=True)
PARENT='232a602326d2519d8f3bb5fe125a416c4d36149885173563df1297092e493445'
REV='COAST-R06 surface-bound weather on preserved sea geology scanned wool and aligned wood'
MODE=os.environ['G4_CONTACT_MODE'];assert MODE in ['build','context','details','motion']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mn(n,l,op,a,b=None):
 q=n.new('ShaderNodeMath');q.operation=op
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):q.inputs[i].default_value=v
  else:l.new(v,q.inputs[i])
 return q.outputs[0]
def maprange(n,l,source,a,b):
 q=n.new('ShaderNodeMapRange');q.clamp=True;q.inputs['To Min'].default_value=a;q.inputs['To Max'].default_value=b;l.new(source,q.inputs['Value']);return q.outputs['Result']
def signature(names,glass_names,puddles):
 h=hashlib.sha256()
 for name in sorted(names):
  o=bpy.data.objects[name];h.update(repr((name,o.type,o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_camera',None),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH' and name not in puddles:
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(repr([(tuple(p.vertices),p.use_smooth) for p in o.data.polygons]).encode())
   for uv in o.data.uv_layers:
    if uv.name=='RainFilmMetric':continue
    a=array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
  if hasattr(o.data,'materials') and name not in glass_names and name not in puddles and name!='Load_bearing_masonry_terrace':h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='LIGHT':h.update(repr((o.data.energy,tuple(o.data.color),o.data.type)).encode())
  if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.clip_start,o.data.clip_end,o.data.dof.use_dof)).encode())
 for f in [451,457,451]:
  s.frame_set(f);bpy.context.view_layer.update()
  for name in sorted(names):h.update(repr(tuple(tuple(r) for r in bpy.data.objects[name].matrix_world)).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.look,s.view_settings.view_transform,s.render.motion_blur_shutter)).encode());return h.hexdigest()
def collection(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name];return c

def water_film(source,name,coverage):
 m=source.copy();m.name=name;n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
 uv=n.new('ShaderNodeUVMap');uv.uv_map='RainFilmMetric';uv.name='Real panel metric UV, not camera coordinates'
 scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(70,48,0);l.new(uv.outputs['UV'],scale.inputs[0])
 v=n.new('ShaderNodeTexVoronoi');v.voronoi_dimensions='2D';v.feature='F1';v.distance='EUCLIDEAN';v.inputs['Scale'].default_value=1;l.new(scale.outputs[0],v.inputs['Vector'])
 color=n.new('ShaderNodeSeparateColor');l.new(v.outputs['Color'],color.inputs[0])
 radius=maprange(n,l,color.outputs[0],.10,.24)
 ratio=mn(n,l,'DIVIDE',v.outputs['Distance'],radius)
 cap=mn(n,l,'MAXIMUM',mn(n,l,'SUBTRACT',1,mn(n,l,'MULTIPLY',ratio,ratio)),0)
 present=mn(n,l,'LESS_THAN',color.outputs[1],coverage)
 cap=mn(n,l,'MULTIPLY',cap,present)
 sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0])
 bend=mn(n,l,'MULTIPLY',mn(n,l,'SINE',mn(n,l,'MULTIPLY',sep.outputs['Y'],8.2)),.0027)
 x=mn(n,l,'ADD',sep.outputs['X'],bend)
 channel=mn(n,l,'ABSOLUTE',mn(n,l,'SUBTRACT',mn(n,l,'FRACT',mn(n,l,'MULTIPLY',x,2.9)),.5))
 channel=mn(n,l,'MAXIMUM',mn(n,l,'SUBTRACT',1,mn(n,l,'DIVIDE',channel,.008)),0)
 flow=n.new('ShaderNodeTexNoise');flow.name='Slow film variation; controlled shader motion, not fluid simulation';flow.noise_dimensions='4D';flow.inputs['Scale'].default_value=3.0;flow.inputs['Detail'].default_value=2;flow.inputs['W'].driver_add('default_value').driver.expression='frame/500.0';l.new(uv.outputs[0],flow.inputs['Vector'])
 channel=mn(n,l,'MULTIPLY',channel,maprange(n,l,flow.outputs['Fac'],.15,.85))
 height=mn(n,l,'MAXIMUM',mn(n,l,'MULTIPLY',cap,.00105),mn(n,l,'MULTIPLY',channel,.00055))
 bump=n.new('ShaderNodeBump');bump.name='Submillimetre adhered-water profile';bump.inputs['Distance'].default_value=1;bump.inputs['Strength'].default_value=.55;l.new(height,bump.inputs['Height'])
 l.new(bump.outputs['Normal'],p.inputs['Normal']);l.new(bump.outputs['Normal'],p.inputs['Coat Normal'])
 p.inputs['Coat IOR'].default_value=1.333;p.inputs['Coat Roughness'].default_value=.055
 l.new(maprange(n,l,mn(n,l,'MAXIMUM',cap,channel),.10,.72),p.inputs['Coat Weight'])
 p.inputs['Transmission Weight'].default_value=1;p.inputs['Roughness'].default_value=.024
 m['scope']='Surface-linked rain microprofile and water coating; original physical glass thickness retained. Not a screen-space layer.'
 return m

if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT
 assert s.get('g4_revision')=='COAST-R05 verified horizontal veneer aligned to actual joinery and curved rims'
 audit=json.loads((ROOT/'output/g4-wet-surface-audit/integrated-r05-wet-audit.json').read_text());assert audit['master_sha256']==PARENT and audit['source_unchanged']
 s.frame_set(451);bpy.context.view_layer.update();originals=[o.name for o in s.objects]
 glass=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('Curved_roof_glazing','Side_wall_glass','Platform_canopy_glass'))]
 assert len(glass)==516,('Audited glazing scope changed',len(glass))
 glass_names={o.name for o in glass};puddles={o.name for o in s.objects if o.name.startswith('G4R03_shallow_rain_puddle')};assert len(puddles)==5
 before=signature(originals,glass_names,puddles);rng=random.Random(26090806)
 report={'stage':'G4','revision':'COAST-R06','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'parent_master_sha256':PARENT,'parent_evidence_commit':'3bb182b7b9b1860b3e410f98fc3a098331455fce','audit_evidence_commit':'8c9af5ae59ebd0283941840c8708487cbb9da26e','basis':['Read-only R05 verified 384 roof and128 wall panes; most only have the legacy weak stretched noise normal. Existing physical adhered drops occupy the negative-Y wall only.','Native R04 macro recovered and actually viewed: adhered drops exist but full hall/roof coverage is absent. Existing airborne rain already has round geometry, shutter and stable SetID; do not repeat that correction.','Existing5 puddles stand above the terrace with constant-depth edges; retain footprints but taper the meniscus and reuse the actual slate scan on exposed terrace tops.'],'edits':{},'g4_stage_pass':False,'human_acceptance':False}
 # Read actual evaluated outside faces before changing any materials or adding objects.
 dg=bpy.context.evaluated_depsgraph_get();surface_triangles={}
 for o in glass:
  if not o.name.startswith('Curved_roof_glazing') and not (o.name.startswith('Side_wall_glass') and o.matrix_world.translation.y>0):
   # Mesh helpers may bake world coordinates into local vertices; use actual bounds below.
   ys=[(o.matrix_world@v.co).y for v in o.data.vertices]
   if not (o.name.startswith('Side_wall_glass') and min(ys)>6):continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri=[]
  for t in me.loop_triangles:
   pts=[o.matrix_world@me.vertices[i].co for i in t.vertices];normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]);area=normal.length*.5
   if area<.002:continue
   normal.normalize();mid=sum(pts,Vector())/3
   exterior=Vector((0,mid.y/6.5,(mid.z-5.03)/5.1)) if o.name.startswith('Curved_roof_glazing') else Vector((0,1,0))
   if normal.dot(exterior)<.3:continue
   tri.append((pts,normal,area))
  ev.to_mesh_clear()
  if tri:surface_triangles[o.name]=tri
 # Arc-length coordinates from the actual roof profile, not its bounding-box projection.
 profile=sorted({(round((o.matrix_world@v.co).y,6),round((o.matrix_world@v.co).z,6)) for o in glass if o.name.startswith('Curved_roof_glazing') for v in o.data.vertices})
 ys=np.asarray([q[0] for q in profile]);arcs=np.zeros(len(profile))
 for i in range(1,len(profile)):arcs[i]=arcs[i-1]+math.dist(profile[i],profile[i-1])
 src=bpy.data.materials['G3_exterior_rivulet_glass'];roofmat=water_film(src,'G4COAST_R06_exposed_roof_water',.60);windmat=water_film(src,'G4COAST_R06_windward_glass_water',.55);sheltermat=water_film(src,'G4COAST_R06_sheltered_glass_water',.25)
 assigned=[]
 for o in glass:
  o.data=o.data.copy();uv=o.data.uv_layers.new(name='RainFilmMetric')
  points=[o.matrix_world@v.co for v in o.data.vertices];isroof=o.name.startswith('Curved_roof_glazing');iscanopy=o.name.startswith('Platform_canopy_glass');wind=sum(p.y for p in points)/len(points)<0
  for loop in o.data.loops:
   v=points[loop.vertex_index];uv.data[loop.index].uv=(v.x,float(np.interp(v.y,ys,arcs)) if isroof else v.y if iscanopy else v.z)
  mat=roofmat if isroof or iscanopy else windmat if wind else sheltermat
  for i,m in enumerate(o.data.materials):
   if m and m.name in ['G3_exterior_rivulet_glass','G3_clear_6mm_glass']:o.data.materials[i]=mat
  assigned.append({'object':o.name,'material':mat.name,'UV':'RainFilmMetric','original_vertices_and_UV_preserved':True})
 report['edits']['surface_films']=assigned
 # Larger sparse water caps are actual closed 3D geometry supported by evaluated faces.
 collection('G4COAST_R06_supported_surface_water');verts=[];faces=[];support=[];water=bpy.data.materials['G4R03_actual_water']
 def addcap(p,normal,radius,elong):
  tangent=normal.cross(Vector((1,0,0)))
  if tangent.length<.01:tangent=normal.cross(Vector((0,1,0)))
  tangent.normalize();across=normal.cross(tangent).normalized();base=len(verts);seg=10;rings=4
  for j in range(rings):
   a=(math.pi/2-.035)*j/(rings-1)
   for k in range(seg):
    t=k*math.tau/seg;v=p+across*(radius*math.cos(a)*math.cos(t))+tangent*(radius*elong*math.cos(a)*math.sin(t))+normal*(.000025+radius*.42*math.sin(a));verts.append(tuple(v))
  for j in range(rings-1):
   for k in range(seg):faces.append((base+j*seg+k,base+j*seg+(k+1)%seg,base+(j+1)*seg+(k+1)%seg,base+(j+1)*seg+k))
  faces.append(tuple(base+k for k in reversed(range(seg))));faces.append(tuple(base+(rings-1)*seg+k for k in range(seg)))
 for name,tris in surface_triangles.items():
  count=6 if name.startswith('Curved_roof_glazing') else 7
  for _ in range(count):
   pts,n,area=rng.choices(tris,weights=[t[2] for t in tris],k=1)[0];a=rng.uniform(.08,.82);b=rng.uniform(.08,.82)
   if a+b>.9:a,b=.9-a,.9-b
   p=pts[0]*(1-a-b)+pts[1]*a+pts[2]*b;addcap(p,n,rng.uniform(.0018,.0045),rng.uniform(1.0,1.7))
  support.append({'object':name,'beads':count,'basis':'Evaluated outside face, geometric contact within25micrometres; no camera projection.'})
 assert len(verts)>40000,'Expected actual supporting glazing faces missing'
 caps=mesh('G4COAST_R06_roof_and_leeward_water_caps',verts,faces,water,smooth=True);report['edits']['coarse_water_caps']={'count':sum(q['beads'] for q in support),'support':support,'object':caps.name}
 # Exposed terrace top reuses the packed honed-slate scan. Interior stays dry.
 terrace=bpy.data.objects['Load_bearing_masonry_terrace'];wet=bpy.data.objects['Hall_continuous_floor'].active_material.copy();wet.name='G4COAST_R06_rain_darkened_exterior_slate';n=wet.node_tree.nodes;l=wet.node_tree.links;p=n['Principled BSDF']
 geo=n.new('ShaderNodeNewGeometry');no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=.8;no.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],no.inputs['Vector'])
 l.new(maprange(n,l,no.outputs['Fac'],.19,.45),p.inputs['Roughness']);p.inputs['Coat IOR'].default_value=1.333;p.inputs['Coat Weight'].default_value=.38;p.inputs['Coat Roughness'].default_value=.10
 original_color=p.inputs['Base Color'].links[0].from_socket;mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.67,.70,.72,1);l.new(original_color,mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
 terrace.data=terrace.data.copy();terrace.data.materials.append(wet);slot=len(terrace.data.materials)-1;top_faces=[]
 for face in terrace.data.polygons:
  if face.normal.z>.9:face.material_index=slot;top_faces.append(face.index)
 assert top_faces
 report['edits']['terrace']={'object':terrace.name,'only_top_faces':top_faces,'material':wet.name,'maps':'Packed slate scan retained, no new download','hall_floor_unchanged':True}
 for name in sorted(puddles):
  o=bpy.data.objects[name];old=o.data;assert len(old.vertices)==97
  c=old.vertices[0].co.copy();edge=[v.co.copy() for v in list(old.vertices)[1:]];vv=[tuple(c)];ff=[];ratios=[.32,.68,.89,.975,1.0]
  for ratio in ratios:
   z=c.z-.00155*max(0,(ratio-.68)/.32)**2
   for v in edge:vv.append((c.x+(v.x-c.x)*ratio,c.y+(v.y-c.y)*ratio,z))
  for i in range(96):ff.append((0,1+i,1+(i+1)%96))
  for j in range(4):
   for i in range(96):a=1+j*96+i;b=1+j*96+(i+1)%96;ff.append((a,a+96,b+96,b))
  data=bpy.data.meshes.new('G4COAST_R06_tapered_puddle');data.from_pydata(vv,[],ff);data.materials.append(water);data.update();o.data=data
  for p in data.polygons:p.use_smooth=True
  for mod in o.modifiers:
   if mod.type=='SOLIDIFY':mod.thickness=.0001
 report['edits']['puddle_contacts']={'objects':sorted(puddles),'unchanged_footprints':True,'edge_lift_metres':.00005,'method':'Five concentric geometry rings taper the edge to the stone; no alpha feather or screen overlay.'}
 # Extend precipitation in actual exterior perimeter volumes. Reuse inspected round-drop graph.
 collection('G4COAST_R06_exterior_precipitation');dg=bpy.context.evaluated_depsgraph_get();origins=[];travel=[];phases=[];speeds=[];sizes=[];hits=Counter();d=Vector((-.06,.12,-1)).normalized()
 def ray(origin,direction,limit=70):
  at=origin.copy()
  for _ in range(24):
   h,p,n,face,o,m=s.ray_cast(dg,at,direction,distance=max(.001,limit-(at-origin).length))
   if not h:return None
   if not o.hide_render and not o.name.startswith(('G4R03_roof_clipped_rain','G4R03_eave_drips','G4COAST_R06')):return o.name,p
   at=p+direction*.006
  return None
 for i in range(7200):
  band=i%4
  if band==0:x,y=rng.uniform(-21,21),rng.uniform(-13,-7.2)
  elif band==1:x,y=rng.uniform(-21,21),rng.uniform(15.7,24)
  elif band==2:x,y=rng.uniform(-23,-18),rng.uniform(-7.2,15.7)
  else:x,y=rng.uniform(18,23),rng.uniform(-7.2,15.7)
  at=Vector((x,y,rng.uniform(12.0,18.0)));hit=ray(at,d)
  if not hit:continue
  name,p=hit;length=(p-at).length-.12
  if length<.3:continue
  origins.append(tuple(at));travel.append(length);phases.append(rng.uniform(0,length));speeds.append(rng.uniform(6.5,10.5));sizes.append(rng.uniform(.65,1.15));hits[name]+=1
 assert len(origins)>5000
 rain=mesh('G4COAST_R06_exterior_round_rain',origins,[])
 for name,values in [('rain_travel',travel),('rain_phase',phases),('rain_speed',speeds),('rain_size',sizes)]:rain.data.attributes.new(name,'FLOAT','POINT').data.foreach_set('value',values)
 g=next(m.node_group for m in bpy.data.objects['G4R03_roof_clipped_rain'].modifiers if m.type=='NODES').copy();g.name='G4COAST_R06_stable_lifetime_exterior_rain'
 counts=0
 for n in g.nodes:
  if n.bl_idname=='ShaderNodeMath' and n.operation=='MULTIPLY':
   for input in n.inputs:
    if not input.is_linked and abs(input.default_value-28000)<.01:input.default_value=len(origins);counts+=1
 assert counts==1,'Lifetime-ID multiplier differs from audited graph'
 rain.modifiers.new('Original round rain and stable lifetime ID','NODES').node_group=g
 report['edits']['exterior_rain']={'object':rain.name,'additional_paths':len(origins),'first_hits':dict(hits),'direction':list(d),'reuse':'R04 round drops, native SceneTime and stable lifetime SetID, no emissive streaks or screen particles','parked_collider_frame':451,'moving_train_collision_not_validated':True}
 bpy.context.view_layer.update();report['protected_before']=before;report['protected_after']=signature(originals,glass_names,puddles);assert before==report['protected_after'],'Protected original geometry/old UV/motion/material family/camera/light/exposure changed'
 for file in BASE.iterdir():
  if file.name in ['g4-full-scene-candidate.blend','master-parts','MASTER-PARTS.json','MASTER-RESTORE.txt','restore_master.py','build-report.json','build.log','provision-source.log','FINITE-REQUEST.txt']:continue
  if file.is_dir():shutil.copytree(file,OUT/file.name,dirs_exist_ok=True)
  elif file.suffix in ['.json','.txt']:shutil.copy2(file,OUT/file.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R05-build-report.json')
 s['g4_revision']=REV;s['g4_water_contact_parent']=PARENT;s.camera=bpy.data.objects['C03_hall_to_platform'];s.frame_set(451);save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
 report['limits']=['Controlled layered surface weather, not a full water-film solver. Existing water-bead fields retained; geometry caps are static.','The native ocean, scanned coast, aligned timber, wool and original practical lights remain in this same file. They are not automatically accepted by this weather edit.','Rain contact is evaluated at stopped frame451. Full incoming-train weather collision and final film remain unverified.']
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('COAST_R06_COMBINED_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 jobs={'context':[('C03_hall_to_platform','C03-surface-rain-hall.png',(1440,900),64,451),('C01_exterior_hero','C01-surface-rain-coast.png',(1440,900),64,451)],'details':[('G4R03_rain_glass_macro','M01-attached-rain.png',(1600,1000),80,451),('G4R03_wet_stone_macro','M03-contact-wet-stone.png',(1440,900),64,451),('G4R03_textile_macro','M04-scanned-wool.png',(1440,900),64,451),('G3_D02','M02-aligned-walnut.png',(1600,1000),80,451),('G3R03_roof_node','D01-node-regression.png',(1280,800),64,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.065
  jobs=[('C03_hall_to_platform',f'motion/{j:04d}.png',(768,480),24,f) for j,f in enumerate(range(451,475,3))]
 metrics=[]
 for cam,name,res,samples,frame in jobs:
  assert time.time()<float(os.environ['G4_CONTACT_DEADLINE']),'Finite wet-contact budget reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame);row.update(master_sha256=expected,native_render=True,revision='COAST-R06',proof_only=MODE=='motion');metrics.append(row);(OUT/(MODE+'-metrics.json')).write_text(json.dumps(metrics,indent=2));print('COAST_R06_NATIVE_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
