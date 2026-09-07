"""COAST-R08 construction-first challenger. Actual audited R07 only.
Boundary-anchored cab lofts, sewn upholstery, secondary native wind sea.
No extra lamps, exposure changes, rain rebuild, or scene replacement.
"""
import bpy,math,json,os,sys,time,hashlib,shutil,re
from pathlib import Path
from array import array
from mathutils import Vector,Matrix
import numpy as np
ROOT=Path('workspaces/glasshouse-terminus').resolve();sys.path.insert(0,str(ROOT))
from scene_common import mesh,material,render,save,camera
BASE=ROOT/'output/g4-coast-r07';OUT=ROOT/'output/g4-coast-r08';OUT.mkdir(parents=True,exist_ok=True)
PARENT='386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396'
REV='COAST-R08 anchored cab shells sewn upholstery and layered native wind sea'
MODE=os.environ['G4_CRAFT_MODE'];assert MODE in ['build','baseline','detail','context']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hash_array(h,collection,prop,count,kind='f'):
 a=array(kind,[0])*count;collection.foreach_get(prop,a);h.update(a.tobytes())
def signature(names):
 h=hashlib.sha256()
 for name in sorted(names):
  o=bpy.data.objects[name];h.update(repr((name,o.type,o.parent.name if o.parent else None,o.hide_render,getattr(o,'visible_camera',None),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   hash_array(h,o.data.vertices,'co',len(o.data.vertices)*3);hash_array(h,o.data.loops,'vertex_index',len(o.data.loops),'i');hash_array(h,o.data.polygons,'material_index',len(o.data.polygons),'i')
   for u in o.data.uv_layers:hash_array(h,u.data,'uv',len(u.data)*2)
  if hasattr(o.data,'materials'):h.update(repr([m.name if m else None for m in o.data.materials]).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
  if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.clip_start,o.data.clip_end,o.data.dof.use_dof,o.data.shift_x,o.data.shift_y)).encode())
 for frame in [1,301,451,466,660,840,451]:
  s.frame_set(frame);bpy.context.view_layer.update()
  for name in sorted(names):h.update(repr(tuple(tuple(r) for r in bpy.data.objects[name].matrix_world)).encode())
 h.update(repr((s.world.name,s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.render.motion_blur_shutter)).encode());return h.hexdigest()
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(q[i] for q in p) for i in range(3)],[max(q[i] for q in p) for i in range(3)]]
def curve_local(name,points,parent,mat,radius,closed=True):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);cu.materials.append(mat);return o

def cab_diagnostic():
 # Additional diagnostic camera; every original camera is retained unaltered.
 name='QA_R08_cab_joinery'
 if name in bpy.data.objects:return bpy.data.objects[name]
 o=bpy.data.objects['Cab_complete_roof_loft.001'];lo,hi=bounds(o);mid=(Vector(lo)+Vector(hi))*.5
 return camera(name,(hi[0]+2.6,lo[1]-4.5,hi[2]+1.45),(mid.x-.1,mid.y,mid.z-.43),lens=54)

def rounded_contour(a,b,r,steps=16):
 ps=[]
 for cx,cy,start in [(a-r,b-r,0),(-a+r,b-r,math.pi/2),(-a+r,-b+r,math.pi),(a-r,-b+r,3*math.pi/2)]:
  for j in range(steps):
   t=start+j*math.pi/2/steps;ps.append((cx+r*math.cos(t),cy+r*math.sin(t)))
 return ps

def replace_cushion(o,pipe_mat):
 old=o.data;assert len(old.vertices)==8 and len(old.polygons)==6 and len(old.materials)==1
 assert old.materials[0].name=='G4COAST_R04_scanned_moss_wool'
 coords=np.array([v.co[:] for v in old.vertices]);lo=coords.min(0);hi=coords.max(0);center=(lo+hi)/2;half=(hi-lo)/2
 assert np.max(abs(center))<1e-5 and np.allclose(o.scale,(1,1,1))
 back=o.name.startswith('Car_seat_back');axes=(1,2,0) if back else (0,1,2);u,v,d=axes;a,b,h=[float(half[i]) for i in axes]
 r=min(.07,a*.23,b*.23);contour=rounded_contour(a,b,r);N=len(contour)
 # Deliberate side boxing, top/bottom fabric panels and a restrained crown.
 rings=[(.91,-1),(.978,-.79),(1,-.42),(1,.12),(.986,.48),(.954,.70),(.87,.84),(.68,.94),(.43,.985),(.17,1)]
 vertices=[]
 for ri,(scale,depth) in enumerate(rings):
  for x,y in contour:
   co=[0.,0.,0.];co[u]=x*scale;co[v]=y*scale
   # Millimetric edge gathering tied to the seam, not all-over noise.
   gather=.0010*math.sin(x*45+.7)*math.sin(y*31)*math.exp(-((scale-.94)/.055)**2)
   co[d]=h*depth+gather;vertices.append(co)
 bottom=len(vertices);vertices.append([0,0,0]);vertices[-1][d]=-h
 top=len(vertices);vertices.append([0,0,0]);vertices[-1][d]=h
 faces=[]
 for ring in range(len(rings)-1):
  for j in range(N):faces.append((ring*N+j,ring*N+(j+1)%N,(ring+1)*N+(j+1)%N,(ring+1)*N+j))
 for j in range(N):faces.append((bottom,(j+1)%N,j));faces.append(((len(rings)-1)*N+j,(len(rings)-1)*N+(j+1)%N,top))
 me=bpy.data.meshes.new('R08_sewn_'+o.name);me.from_pydata(vertices,[],faces);me.update();me.materials.append(old.materials[0])
 for f in me.polygons:f.use_smooth=True
 uv=me.uv_layers.new(name='ClothPhysicalMeters');me.uv_layers.active=uv;uv.active_render=True
 lengths=[0.]
 for i in range(1,N):lengths.append(lengths[-1]+math.dist(contour[i-1],contour[i]))
 perimeter=lengths[-1]+math.dist(contour[-1],contour[0])
 for f in me.polygons:
  side=(f.index//N)<5 and f.index<(len(rings)-1)*N
  js=[me.loops[i].vertex_index%N for i in f.loop_indices];wrap=0 in js and N-1 in js
  for li in f.loop_indices:
   vi=me.loops[li].vertex_index;co=me.vertices[vi].co
   if side:
    j=vi%N;uv.data[li].uv=(perimeter if wrap and j==0 else lengths[j],co[d])
   else:uv.data[li].uv=(co[u],co[v])
 old.use_fake_user=True;o.data=me;o.modifiers.clear()
 # Welt lies on the actual outer boxing. New geometry inherits the same moving object.
 points=[]
 for x,y in contour:
  co=[0.,0.,0.];co[u]=x;co[v]=y;co[d]=h*.12;points.append(co)
 welt=curve_local('R08_tailored_welt_'+o.name,points,o,pipe_mat,.0020)
 # Seam stitches are curve segments on the welt, at physical spacing; bounded density.
 cu=bpy.data.curves.new('R08_stitch_'+o.name,'CURVE');cu.dimensions='3D';cu.bevel_depth=.00026;cu.bevel_resolution=1
 for i in range(N):
  p0=Vector(points[i]);p1=Vector(points[(i+1)%N]);L=(p1-p0).length;pieces=max(1,int(L/.009))
  for k in range(pieces):
   a0=p0.lerp(p1,(k+.16)/pieces);a1=p0.lerp(p1,(k+.58)/pieces);a0[d]+=.0018;a1[d]+=.0018
   sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a0,1);sp.points[1].co=(*a1,1)
 ob=bpy.data.objects.new('R08_seam_stitches_'+o.name,cu);bpy.context.collection.objects.link(ob);ob.parent=o;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4);cu.materials.append(pipe_mat)
 out=np.array(vertices);assert np.all(out.max(0)<=hi+.0015) and np.all(out.min(0)>=lo-.0015)
 # Mesh is a closed sewn envelope with consistent winding, no disconnected floating panels.
 edge_counts={}
 for f in faces:
  for x,y in zip(f,f[1:]+f[:1]):key=tuple(sorted((x,y)));edge_counts[key]=edge_counts.get(key,0)+1
 assert set(edge_counts.values())=={2}
 return {'object':o.name,'before_vertices':8,'after_vertices':len(vertices),'closed_edges':True,'original_parent':o.parent.name if o.parent else None,'physical_tile_metres':.30,'welt_radius':.002,'stitch_radius':.00026,'shape':'Sewn side boxing, crowned fabric panel, slight edge gathering. Not a simulated cloth drape.','old_mesh_retained':old.name,'outer_envelope_preserved_mm':1.5}

if MODE=='build':
 master=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==master and sha(master)==PARENT
 assert s.get('g4_revision')=='COAST-R07 supported moving runoff and shielded exterior plinth lighting'
 audit=json.loads((ROOT/'output/g4-r07-craft-audit/craft-audit.json').read_text());assert audit['source_master_sha256']==PARENT and audit['source_unchanged']
 s.frame_set(451);bpy.context.view_layer.update();originals=[o.name for o in s.objects]
 roofs=[bpy.data.objects[n] for n in ['Cab_complete_roof_loft','Cab_complete_roof_loft.001']]
 seats=sorted([o for o in s.objects if re.fullmatch(r'(Car_seat_(cushion|back)|G4_bench_seat_cushion)(\.\d+)?',o.name)],key=lambda o:o.name)
 assert len(seats)==32,('Audited cushion set differs',len(seats))
 allowed={o.name for o in roofs+seats}|{'Ocean_extent'};protected=[n for n in originals if n not in allowed];before=signature(protected)
 c=bpy.data.collections.new('G4COAST_R08_craft');s.collection.children.link(c);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[c.name]
 report={'stage':'G4','revision':'COAST-R08','parent_master_sha256':PARENT,'parent_evidence_commit':'91b5bcc932c58e5a43b20061299bb6a6f606aaaa','audit_evidence_commit':'fabf97ac9fa264a741429c0dc01c75e63f322381','audit_run':34164882942,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'roofs':[],'upholstery':[],'g4_stage_pass':False,'human_acceptance':False}
 for o in roofs:
  old=o.data;assert len(old.vertices)==50 and len(old.polygons)==24 and sum(p.use_smooth for p in old.polygons)==0
  assert len(o.modifiers)==1 and o.modifiers[0].type=='SOLIDIFY' and abs(o.modifiers[0].thickness-.07)<1e-5
  A=[v.co.copy() for v in old.vertices[:25]];B=[v.co.copy() for v in old.vertices[25:]];V=[];faces=[];cross=96;long=16
  def sample(row,v,smooth):
   k=min(23,int(v));f=v-k;p0=row[max(0,k-1)];p1=row[k];p2=row[k+1];p3=row[min(24,k+2)]
   linear=p1.lerp(p2,f);cubic=.5*((2*p1)+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f*f*f)
   return linear.lerp(cubic,smooth)
  for it in range(long+1):
   t=it/long
   for j in range(cross+1):
    a=sample(A,j*24/cross,math.sin(math.pi*t)**2);b=sample(B,j*24/cross,math.sin(math.pi*t)**2);p=a.lerp(b,t)
    p.z=a.z+(b.z-a.z)*t*t;V.append(tuple(p))
  for it in range(long):
   for j in range(cross):
    a=it*(cross+1)+j;faces.append((a,a+1,a+cross+2,a+cross+1))
  mid=faces[(long//2)*cross+cross//2];nz=(Vector(V[mid[1]])-Vector(V[mid[0]])).cross(Vector(V[mid[2]])-Vector(V[mid[0]])).z
  if nz<0:faces=[tuple(reversed(f)) for f in faces]
  me=bpy.data.meshes.new('R08_boundary_anchored_'+o.name);me.from_pydata(V,[],faces);me.update()
  for m in old.materials:me.materials.append(m)
  for f in me.polygons:f.use_smooth=True
  assert min(p.normal.z for p in me.polygons)>-.001
  # Keep the actual 50 original interface vertices exactly, not camera-space approximations.
  error=max((Vector(V[it*(cross+1)+j*4])-row[j]).length for it,row in [(0,A),(long,B)] for j in range(25));assert error<1e-6
  old.use_fake_user=True;o.data=me;o.modifiers[0].use_quality_normals=True;o.modifiers[0].use_even_offset=True
  lip=V[long*(cross+1):(long+1)*(cross+1)];curve_local('R08_rolled_cab_lip_'+o.name,lip,o,me.materials[0],.0032,False)
  report['roofs'].append({'object':o.name,'before_faces':24,'after_quads':len(faces),'source_normals_mean_z':sum(p.normal.z for p in old.polygons)/24,'new_mean_z':sum(p.normal.z for p in me.polygons)/len(me.polygons),'interface_max_error_m':error,'thickness_m':.07,'old_mesh_retained':old.name,'method':'Anchored cross-section quad loft, longitudinal tangent easing and explicit outward normals; all original boundary samples preserved.'})
 pipe=material('R08_moss_wool_seam',(.062,.080,.060),rough=.69);pipe.node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value=.23
 for o in seats:report['upholstery'].append(replace_cushion(o,pipe))
 ocean=bpy.data.objects['Ocean_extent'];assert [m.type for m in ocean.modifiers]==['OCEAN','NODES'];primary=ocean.modifiers[0]
 assert len(ocean.data.vertices)==229445 and abs(primary.choppiness-1.2)<.001 and primary.spatial_size==100
 extra=ocean.modifiers.new('R08 short-fetch wind wave spectrum','OCEAN');extra.geometry_mode='DISPLACE';extra.spectrum='PHILLIPS';extra.resolution=16;extra.viewport_resolution=12;extra.spatial_size=35;extra.wind_velocity=8;extra.wave_scale=.38;extra.wave_scale_min=.50;extra.choppiness=.8;extra.wave_alignment=.35;extra.wave_direction=math.radians(48);extra.random_seed=73;extra.use_foam=False;extra.time=451/30;extra.driver_add('time').driver.expression='frame/30.0'
 bpy.context.view_layer.objects.active=ocean;bpy.ops.object.modifier_move_up(modifier=extra.name)
 assert [m.type for m in ocean.modifiers]==['OCEAN','OCEAN','NODES']
 # Existing GN distance taper runs AFTER both physical spectra; the distant sparse grid stays flat.
 primary.choppiness=1.4
 src=ocean.active_material;m=src.copy();m.name='R08_multiscale_dielectric_sea';ocean.data=ocean.data.copy();ocean.data.materials[0]=m;n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
 geo=n['Geometry'];oldnormal=n['Bump'].outputs['Normal'];waveheight=None;specs=[]
 for wavelength,amplitude,angle in [(.11,.0008,25),(.17,.0011,63),(.29,.0017,112),(.51,.0025,31)]:
  k=math.tau/wavelength;theta=math.radians(angle);dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(math.cos(theta)*k,math.sin(theta)*k,0);l.new(geo.outputs['Position'],dot.inputs[0])
  phase=n.new('ShaderNodeMath');phase.operation='ADD';l.new(dot.outputs['Value'],phase.inputs[0]);phase.inputs[1].driver_add('default_value').driver.expression=f'-{math.sqrt(9.81*k):.9f}*frame/30.0'
  sine=n.new('ShaderNodeMath');sine.operation='SINE';l.new(phase.outputs[0],sine.inputs[0]);amp=n.new('ShaderNodeMath');amp.operation='MULTIPLY';amp.inputs[1].default_value=amplitude;l.new(sine.outputs[0],amp.inputs[0])
  if waveheight is None:waveheight=amp.outputs[0]
  else:
   add=n.new('ShaderNodeMath');add.operation='ADD';l.new(waveheight,add.inputs[0]);l.new(amp.outputs[0],add.inputs[1]);waveheight=add.outputs[0]
  specs.append({'wavelength_m':wavelength,'amplitude_m':amplitude,'direction_degrees':angle})
 bn=n.new('ShaderNodeBump');bn.name='R08 metric wind-ripple slopes';bn.inputs['Distance'].default_value=1;bn.inputs['Strength'].default_value=.65;l.new(waveheight,bn.inputs['Height']);l.new(oldnormal,bn.inputs['Normal']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
 assert p.inputs['Transmission Weight'].default_value==1 and p.inputs['Emission Strength'].default_value==0
 rest=ocean.data.attributes['OceanRestPosition'];xyz=np.empty(len(rest.data)*3,dtype=np.float32);rest.data.foreach_get('vector',xyz);xyz=xyz.reshape(-1,3);r=np.max(abs(xyz[:,:2]),axis=1);far=(r>=207)&(xyz[:,2]==0);near=r<130;hs=[];observed=[]
 for f in [451,466,451]:
  s.frame_set(f);bpy.context.view_layer.update();ev=ocean.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();co=np.empty(len(em.vertices)*3,dtype=np.float32);em.vertices.foreach_get('co',co);co=co.reshape(-1,3)
  assert len(co)==len(xyz) and np.isfinite(co).all() and abs(co[far,2]).max()<.001
  h=hashlib.sha256(co[near].tobytes()).hexdigest();hs.append(h);observed.append({'frame':f,'near_z_min_max':[float(co[near,2].min()),float(co[near,2].max())],'far_displacement_max':float(abs(co[far,2]).max()),'position_sha256':h});ev.to_mesh_clear()
 assert hs[0]==hs[2] and hs[0]!=hs[1]
 report['ocean']={'retained':'Original 100m dominant spectrum, closed optical body, original foam and shore-distance field,207m taper. No new flat sea or duplicate water sheet.','primary_choppiness':[1.2,1.4],'secondary_spectrum':'35m short-fetch Phillips,wind8m/s,scale0.38,seed73; art-directed superposition not coastal-impact fluid simulation','metric_ripples':specs,'replay':observed}
 report['protected_before']=before;report['protected_after']=signature(protected);assert before==report['protected_after'],'Unrelated saved source geometry, original UV, camera, lights or motion changed'
 s.frame_set(451);bpy.context.view_layer.update();diagnostic=cab_diagnostic();s.camera=diagnostic
 for p0 in BASE.iterdir():
  if p0.name in ['g4-full-scene-candidate.blend','master-parts','MASTER-PARTS.json','MASTER-RESTORE.txt','restore_master.py','build-report.json','build.log','provision-source.log','FINITE-REQUEST.txt']:continue
  if p0.is_dir():shutil.copytree(p0,OUT/p0.name,dirs_exist_ok=True)
  elif p0.suffix in ['.json','.txt']:shutil.copy2(p0,OUT/p0.name)
 shutil.copy2(BASE/'build-report.json',OUT/'COAST-R07-build-report.json')
 s['g4_revision']=REV;s['g4_craft_parent']=PARENT;save(s,OUT/'g4-full-scene-candidate.blend');assert sha(master)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size
 report['limits']=['All modifications are challenger art, not commercial certification.','Rain/runoff, cliff geometry, glass, wood, lights and world are inherited unchanged. R07 wet-stone still fails readability and is not claimed fixed here.','No new full-event train collision or final film validation. Reversed, original wide and close camera observations remain required.']
 (OUT/'build-report.json').write_text(json.dumps(report,indent=2));print('R08_CRAFT_SOURCE_SAVED_NOT_ART_PASS',report['candidate_sha256'],flush=True)
else:
 isbase=MODE=='baseline';master=(BASE if isbase else OUT)/'g4-full-scene-candidate.blend';expected=PARENT if isbase else json.loads((OUT/'build-report.json').read_text())['candidate_sha256']
 assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected
 if not isbase:assert s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.frame_set(451);bpy.context.view_layer.update();cab=cab_diagnostic();s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False
 s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 assert s.view_settings.exposure==0 and s.view_settings.view_transform=='AgX'
 jobs={'baseline':[(cab.name,'BEFORE-cab.png',(1280,800),64),('G4R03_textile_macro','BEFORE-upholstery.png',(1280,800),64)],'detail':[(cab.name,'AFTER-cab.png',(1280,800),64),('G4R03_textile_macro','AFTER-upholstery.png',(1280,800),64)],'context':[('C09_car_aisle_failure_check','C09-tailored-interior.png',(1280,800),48),('C01_exterior_hero','C01-craft-coast.png',(1440,900),48),('G4COAST_ocean_close','E02-wind-sea.png',(1280,800),48)]}[MODE]
 metrics=[]
 for cam,name,res,samples in jobs:
  assert time.time()<float(os.environ['G4_CRAFT_DEADLINE']),'Finite craft rendering budget reached'
  q=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451);q.update(master_sha256=expected,native_render=True,revision='R07' if isbase else 'R08');metrics.append(q)
  (OUT/(MODE+'-metrics.json')).write_text(json.dumps(metrics,indent=2));print('R08_NATIVE_VIEW_SAVED',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
