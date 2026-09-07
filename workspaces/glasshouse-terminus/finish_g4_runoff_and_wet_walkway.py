"""COAST-R07: two evidence-based interventions on checked integrated R06.
1. Move a subset of existing adhered beads as surface-supported runoff, using
   existing SceneTime/lifetime-ID instances rather than image-space rain.
2. Four shielded plinth fixtures illuminate the actual exterior walkway.
Original sea, scans, glass panes, wool, joinery, camera/exposure and lamps retained.
"""
import bpy,os,sys,json,math,hashlib,shutil,time,random
from pathlib import Path
from array import array
from mathutils import Vector
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import mesh,cube,render,save
BASE=ROOT/'output/g4-coast-r06-checked';OUT=ROOT/'output/g4-coast-r07';OUT.mkdir(parents=True,exist_ok=True)
PARENT='590e6793224219c5245f89fd43f7ab2e9daed08b79429b5f8925d6c7c0e36738'
REV='COAST-R07 supported moving runoff and shielded exterior plinth lighting'
MODE=os.environ['G4_RUNOFF_MODE'];assert MODE in ['build','wet','rain','context','motion']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
def signature(names):
 h=hashlib.sha256()
 for name in sorted(names):
  o=bpy.data.objects[name];h.update(repr((name,o.type,o.hide_render,o.parent.name if o.parent else None,tuple(tuple(v) for v in o.matrix_world),getattr(o,'visible_shadow',None),getattr(o,'visible_camera',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
   for p in o.data.polygons:h.update(repr((tuple(p.vertices),p.material_index,p.use_smooth)).encode())
   for uv in o.data.uv_layers:
    a=array('f',[0])*(2*len(uv.data));uv.data.foreach_get('uv',a);h.update(a.tobytes())
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.type,o.data.clip_start,o.data.clip_end,o.data.dof.use_dof)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.render.motion_blur_shutter)).encode())
 return h.hexdigest()
def first(at,d,length):
 h,p,n,fi,o,m=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(at),Vector(d).normalized(),distance=length)
 return (o,p,n) if h else None

if MODE=='build':
 master=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==master and sha(master)==PARENT
 assert s.get('g4_revision')=='COAST-R06 surface-bound weather on preserved sea geology scanned wool and aligned wood'
 prior=json.loads((BASE/'build-report.json').read_text());assert prior['normal_preflight']['all_closed_cap_volumes_positive']
 audit=json.loads((ROOT/'output/g4-r06-optical-audit/wet-optical-audit.json').read_text());assert audit['master_sha256']==PARENT and audit['source_unchanged']
 assert sum(q.get('reflected_first_hit',{}).get('object')=='Hall_plinth' for q in audit['camera_rays'] if q.get('reflected_first_hit'))==36
 s.frame_set(451);bpy.context.view_layer.update()
 source=bpy.data.objects['G4R03_convex_glass_water_beads'];assert len(source.data.vertices)==276192 and not source.modifiers
 originals=[o.name for o in s.objects if o!=source];before=signature(originals)
 report={'stage':'G4','revision':'COAST-R07','parent_master_sha256':PARENT,'parent_evidence_commit':'8edab03563070bc62a1a768aaf1f6389d72a68f6','diagnosis_evidence_commit':'fa5eadee301d2fd38f97990c5c22bfd05a51f634','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'basis':['Actually opened all five completed R06 originals and verified43 manifest entries. R06 missing wood/node witnesses handled separately from the same master.','Wet macro54/54 camera normals front-facing;36/54 reflected centre rays hit the dark Hall_plinth. Do not solve by flipping normals, global exposure or making water diffuse.','Adhered rain exists but is static; preserve most existing beads and move a bounded subset on their real supporting panes.'],'g4_stage_pass':False,'human_acceptance':False}
 c=bpy.data.collections.new('G4COAST_R07_runoff_and_walkway');s.collection.children.link(c);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
 # Choose complete existing water caps, never separate vertices of a single drop.
 co=[v.co.copy() for v in source.data.vertices];per=72;N=len(co)//per
 assert N==3836 and all(len({i//per for i in p.vertices})==1 for p in source.data.polygons)
 panels=[o for o in s.objects if o.type=='MESH' and o.name.startswith('Side_wall_glass') and bounds(o)[1][1]<-6]
 selected=set(range(0,N,7));rng=random.Random(731907);origins=[];travels=[];phases=[];speeds=[];sizes=[];support=[]
 for index in sorted(selected):
  ps=co[index*per:(index+1)*per];center=sum(ps[:12],Vector())/12
  matches=[o for o in panels if bounds(o)[0][0]<center.x<bounds(o)[1][0] and bounds(o)[0][2]<center.z<bounds(o)[1][2]];assert len(matches)==1,(index,list(center))
  panel=matches[0];lo,hi=bounds(panel);radius=max(abs(p.x-center.x) for p in ps)
  assert .0013<radius<.0067 and abs(lo[1]+6.5)<.001
  top=hi[2]-.10;bottom=lo[2]+.065;assert top>bottom and top+9*radius<hi[2]-.012
  at=(center.x,lo[1]-.000025,top);origins.append(at);travels.append(top-bottom);sizes.append(radius);speed=rng.uniform(.09,.22);speeds.append(speed)
  # Start at the original bead height when it fits the safe movement interval.
  start=min(max(center.z,bottom+.004),top-.004);phases.append(((top-start)-451/30*speed)%(top-bottom))
  support.append({'source_bead':index,'pane':panel.name,'surface_y':lo[1],'x':center.x,'z_min':bottom,'z_max':top,'radius':radius})
 # Keep unselected static caps byte-identical in position and polygon winding.
 ids=[i for i in range(len(co)) if i//per not in selected];mapping={old:new for new,old in enumerate(ids)}
 faces=[tuple(mapping[i] for i in p.vertices) for p in source.data.polygons if p.vertices[0]//per not in selected]
 data=bpy.data.meshes.new('G4COAST_R07_retained_static_beads');data.from_pydata([tuple(co[i]) for i in ids],[],faces);data.update()
 for p in data.polygons:p.use_smooth=True
 for mat in source.data.materials:data.materials.append(mat)
 old_static=source.data;source.data=data
 # Closed droplet head with a narrow trailing film; local exterior is -Y.
 # Prototype is a hidden source asset; its visible native instances carry the water.
 zs=[-1.6,-1.4,-1.0,-.5,0,.5,1,1.5,2,3,5,7,9]
 widths=[.035,.38,.76,.96,1,.87,.65,.38,.19,.15,.12,.08,.025]
 heights=[.012,.16,.37,.50,.54,.43,.28,.15,.070,.055,.042,.025,.010]
 xs=[-1,-.92,-.71,-.38,0,.38,.71,.92,1];vv=[]
 for bottom_layer in [False,True]:
  for z,w,h in zip(zs,widths,heights):
   for x in xs:vv.append((x*w,0 if bottom_layer else -(h*math.sqrt(max(0,1-x*x))+.010),z))
 rows=len(zs);cols=len(xs);layer=rows*cols;ff=[]
 for side in [0,1]:
  off=side*layer
  for j in range(rows-1):
   for k in range(cols-1):
    face=(off+j*cols+k,off+j*cols+k+1,off+(j+1)*cols+k+1,off+(j+1)*cols+k)
    ff.append(face if side==0 else tuple(reversed(face)))
 edge=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(range(layer-2,layer-cols-1,-1))+[j*cols for j in range(rows-2,0,-1)]
 for j,a in enumerate(edge):b=edge[(j+1)%len(edge)];ff.append((a,b,b+layer,a+layer))
 def volume(faces):
  return sum(Vector(vv[f[0]]).dot(Vector(vv[f[j]]).cross(Vector(vv[f[j+1]])))/6 for f in faces for j in range(1,len(f)-1))
 if volume(ff)<0:ff=[tuple(reversed(f)) for f in ff]
 assert volume(ff)>0
 counts={}
 for f in ff:
  for a,b in zip(f,f[1:]+f[:1]):k=tuple(sorted((a,b)));counts[k]=counts.get(k,0)+1
 assert set(counts.values())=={2},'Runoff prototype is not closed'
 water=bpy.data.materials['G4R03_actual_water'];proto=mesh('G4COAST_R07_runoff_source_cap',vv,ff,water,smooth=True);proto.hide_render=True
 rain=mesh('G4COAST_R07_surface_runoff',origins,[])
 for name,values in [('rain_travel',travels),('rain_phase',phases),('rain_speed',speeds),('rain_size',sizes)]:rain.data.attributes.new(name,'FLOAT','POINT').data.foreach_set('value',values)
 original_group=next(m.node_group for m in bpy.data.objects['G4R03_roof_clipped_rain'].modifiers if m.type=='NODES');group=original_group.copy();group.name='G4COAST_R07_adhered_runoff_stable_ID'
 n=group.nodes;l=group.links;tr=next(q for q in n if q.bl_idname=='GeometryNodeTransform');tr.inputs['Scale'].default_value=(1,1,1);tr.inputs['Rotation'].default_value=(0,0,0)
 info=n.new('GeometryNodeObjectInfo');info.transform_space='ORIGINAL';info.inputs['Object'].default_value=proto;info.inputs['As Instance'].default_value=False;l.new(info.outputs['Geometry'],tr.inputs['Geometry'])
 changed=0;directions=0
 for q in n:
  if q.bl_idname=='ShaderNodeVectorMath' and q.operation=='SCALE' and not q.inputs[0].is_linked:q.inputs[0].default_value=(0,0,-1);directions+=1
  if q.bl_idname=='ShaderNodeMath' and q.operation=='MULTIPLY':
   for v in q.inputs:
    if not v.is_linked and abs(v.default_value-28000)<.01:v.default_value=len(origins);changed+=1
 assert changed==1 and directions==1
 rain.modifiers.new('Supported runoff with native SceneTime and lifetime ID','NODES').node_group=group;rain.cycles.use_motion_blur=True;rain.cycles.motion_steps=2
 report['runoff']={'reused_source':'Existing R04 round-rain SceneTime/SetID graph; original source bead subset','moving_drops':len(origins),'static_beads_retained':N-len(origins),'support':support,'prototype_closed':True,'prototype_positive_volume':volume(ff),'prototype_hidden_source_only':True,'surface_gap_metres':.000025,'not_fluid_simulation':True}
 # Real installation on the ray-verified plinth, not invisible off-camera fill.
 paint=bpy.data.materials['G4R03_G3R05_satin_column_paint'];trim=bpy.data.materials['G4R03_G3_satin_aged_brass'];fixtures=[]
 for x in [-12.,-4.,4.,12.]:
  hit=first((x,-7.2,.65),(0,1,0),.7);assert hit and hit[0].name=='Hall_plinth' and hit[2].y<-.9,('Plinth installation differs',x,hit)
  surface=hit[1];plate=cube('G4COAST_R07_plinth_fixture_back',(x,surface.y-.008,.65),(.20,.020,.115),paint,.006)
  body=cube('G4COAST_R07_shielded_step_light',(x,surface.y-.044,.654),(.19,.063,.084),paint,.008)
  cube('G4COAST_R07_step_light_bezel',(x,surface.y-.059,.610),(.16,.032,.011),trim,.002)
  data=bpy.data.lights.new('G4COAST_R07_walkway_wash','AREA');data.shape='RECTANGLE';data.size=.14;data.size_y=.025;data.energy=18;data.color=(1,.89,.74)
  ob=bpy.data.objects.new(data.name,data);c.objects.link(ob);ob.location=(x,surface.y-.075,.597);axis=Vector((0,-.65,-1)).normalized();ob.rotation_euler=axis.to_track_quat('-Z','Y').to_euler()
  # Light leaves below the hood. Confirm a useful centre ray reaches the wet terrace.
  target=Vector((x,surface.y-.80,-.025));h=first(ob.location,target-ob.location,2);assert h and (h[0].name=='Load_bearing_masonry_terrace' or h[0].name.startswith('G4R03_shallow_rain_puddle')),('Fixture self-shadow',x,h)
  fixtures.append({'light':ob.name,'mount':plate.name,'body':body.name,'support_object':hit[0].name,'support_point':list(surface),'position':list(ob.location),'energy_native_blender_W':18,'axis':list(axis),'useful_ray_first_hit':h[0].name})
 report['fixtures']=fixtures
 # Verify actual evaluated runoff translations, repeatability and surface boundary.
 snapshots=[]
 for f in [451,466,481,451]:
  s.frame_set(f);bpy.context.view_layer.update();pts=[]
  for it in bpy.context.evaluated_depsgraph_get().object_instances:
   if it.is_instance and it.parent and it.parent.original.name==rain.name:pts.append(tuple(round(v,6) for v in it.matrix_world.translation))
  assert len(pts)==len(origins),(f,len(pts),len(origins))
  assert all(abs(p[1]+6.500025)<.00001 for p in pts)
  snapshots.append({'frame':f,'count':len(pts),'positions_sha256':hashlib.sha256(repr(pts).encode()).hexdigest(),'first_points':pts[:8]})
 assert snapshots[0]['positions_sha256']==snapshots[-1]['positions_sha256']!=snapshots[1]['positions_sha256']
 s.frame_set(451);bpy.context.view_layer.update();report['protected_before']=before;report['protected_after']=signature(originals);assert before==report['protected_after'],'Original sea/geology/panes/wood/wool/lights/cameras or exposure changed'
 report['motion_probe']=snapshots
 for p in BASE.iterdir():
  if p.name in ['assets','models'] and p.is_dir():shutil.copytree(p,OUT/p.name,dirs_exist_ok=True)
  elif p.suffix in ['.json','.txt'] and p.name not in ['DELIVERY.json','build-report.json','MASTER-PARTS.json','MASTER-RESTORE.txt','FINITE-REQUEST.txt']:shutil.copy2(p,OUT/p.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R06-build-report.json')
 s['g4_revision']=REV;s['g4_r07_parent_sha256']=PARENT;s['surface_runoff_scope']='Supported analytic sliding water caps, lifetime-aware IDs; not coalescence simulation';s.camera=bpy.data.objects['C03_hall_to_platform'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(master)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
 report['limits']=['Only windward wall subset slides; roof caps and other small beads remain static. No claimed full fluid/coalescence solver.','New practical fixtures are a disclosed art variable. Original light sources, exposure and world untouched.','Sea smoothness/coastal foam, rock dark areas and moving-train rain collision remain separate open issues.']
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('R07_SUPPORTED_RUNOFF_AND_WALKWAY_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 jobs={'wet':[('G4R03_wet_stone_macro','M03-lit-wet-stone.png',(1440,900),64,451)],'rain':[('G4R03_rain_glass_macro','M01-moving-surface-rain.png',(1600,1000),64,451)],'context':[('C03_hall_to_platform','C03-runoff-hall.png',(1440,900),64,451),('C01_exterior_hero','C01-runoff-coast.png',(1440,900),48,451)],'motion':[]}[MODE]
 if MODE=='motion':
  (OUT/'motion').mkdir(exist_ok=True);s.cycles.adaptive_min_samples=8;s.cycles.adaptive_threshold=.065
  jobs=[('G4R03_rain_glass_macro',f'motion/{j:04d}.png',(640,400),24,f) for j,f in enumerate(range(451,481,3))]
 metrics=[]
 for cam,name,res,samples,frame in jobs:
  assert time.time()<float(os.environ['G4_RUNOFF_DEADLINE']),'Finite runoff production deadline reached'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=frame);row.update(native_render=True,master_sha256=expected,proof_only=MODE=='motion');metrics.append(row);(OUT/(MODE+'-metrics.json')).write_text(json.dumps(metrics,indent=2));print('R07_NATIVE_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen.json')).write_text(json.dumps({'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'fresh_process':True,'new_frames':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
