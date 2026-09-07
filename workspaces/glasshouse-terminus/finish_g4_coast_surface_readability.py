"""Native surface response candidate, not image generation or a scene replacement.
Reuse two selected CC0 assets. Preserve sea/geology geometry and original cameras.
"""
import bpy,json,hashlib,math,os,sys,time,shutil,urllib.request
from pathlib import Path
from urllib.parse import urlparse,unquote
from array import array
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_common import render,save
ROOT=Path('workspaces/glasshouse-terminus').resolve();BASE=ROOT/'output/g4-coast-r03';OUT=ROOT/'output/g4-coast-r04';OUT.mkdir(parents=True,exist_ok=True)
PARENT='1ed77cc2acaabe09a921aaae5443256b6ffb9674d6912bcdbe754d3290d0990b';REV='COAST-R04 scanned wool and overcast surface response on native sea geology rain'
MODE=os.environ['G4_SURFACE_MODE'];assert MODE in ['build','context','closeups']
s=bpy.context.scene;assert bpy.app.version[:3]==(4,5,13)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def protect():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  h.update(repr((o.name,o.type,o.parent.name if o.parent else None,o.hide_render,tuple(tuple(r) for r in o.matrix_world),getattr(o,'visible_shadow',None),getattr(o,'visible_glossy',None),getattr(o,'visible_transmission',None))).encode())
  if o.type=='MESH':
   a=array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(repr([(len(p.vertices),p.use_smooth) for p in o.data.polygons]).encode())
  if o.type=='CAMERA':h.update(repr((o.data.lens,o.data.clip_start,o.data.clip_end,o.data.type,o.data.shift_x,o.data.shift_y)).encode())
  if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,tuple(o.data.color))).encode())
 h.update(repr((s.view_settings.exposure,s.view_settings.view_transform,s.view_settings.look,s.render.motion_blur_shutter)).encode());return h.hexdigest()

def get(url,cap):
 assert urlparse(url).scheme=='https' and urlparse(url).hostname in ['api.polyhaven.com','dl.polyhaven.org','dl.polyhaven.com']
 q=urllib.request.Request(url,headers={'User-Agent':'GlasshouseTerminus-Future/1.0 (https://github.com/yangerstar1/future; selected-asset reuse)','Referer':'https://github.com/yangerstar1/future'})
 with urllib.request.urlopen(q,timeout=90) as response:
  assert urlparse(response.url).hostname in ['api.polyhaven.com','dl.polyhaven.org','dl.polyhaven.com'];data=response.read(cap+1)
 assert len(data)<=cap;time.sleep(.25);return data

def asset(asset_id,roles):
 folder=OUT/'assets'/asset_id;folder.mkdir(parents=True,exist_ok=True)
 meta=json.loads(get('https://api.polyhaven.com/files/'+asset_id,3000000));info=json.loads(get('https://api.polyhaven.com/info/'+asset_id,3000000))
 (folder/'upstream-files.json').write_text(json.dumps(meta,indent=2));(folder/'upstream-info.json').write_text(json.dumps(info,indent=2))
 row={'asset_id':asset_id,'authors':info.get('authors'),'license':'CC0-1.0','license_source':'https://polyhaven.com/license','source':'https://polyhaven.com/a/'+asset_id,'files':{}}
 for role,aliases,res,fmt in roles:
  choices=[key for key in meta if key.lower() in [a.lower() for a in aliases]];assert len(choices)==1,(asset_id,role,list(meta))
  key=choices[0];d=meta[key][res][fmt];p=folder/Path(unquote(urlparse(d['url']).path)).name
  data=get(d['url'],45000000);assert not d.get('md5') or hashlib.md5(data).hexdigest()==d['md5'];p.write_bytes(data)
  image=bpy.data.images.load(str(p),check_existing=True);assert image.size[0]>=2048
  if role not in ['diff','environment']:image.colorspace_settings.name='Non-Color'
  row['files'][role]={'file':str(p.relative_to(OUT)),'url':d['url'],'bytes':len(data),'sha256':sha(p),'native_resolution':list(image.size),'color_space':image.colorspace_settings.name,'image_name':image.name,'metadata_key':key}
 return row

if MODE=='build':
 parent=BASE/'g4-full-scene-candidate.blend';assert Path(bpy.data.filepath).resolve()==parent and sha(parent)==PARENT and s.get('g4_revision')=='COAST-R03 dielectric closed ocean with graded geometry detail'
 assert s.view_settings.exposure==0
 s.frame_set(451);bpy.context.view_layer.update();before=protect()
 old=bpy.data.materials['G4R03_G4_moss_woven_upholstery'];targets=[o for o in s.objects if o.type=='MESH' and old in list(o.data.materials)]
 assert 40<=len(targets)<=50 and all(o.name.startswith(('Car_seat_','Cab_driver_seat','Rear_luggage_bench','G4_bench_')) for o in targets),'Actual upholstery target scope differs'
 hdr=asset('kloofendal_overcast_puresky',[('environment',['hdri'],'2k','hdr')])
 textile=asset('poly_wool_herringbone',[('diff',['diff','Diffuse'],'4k','jpg'),('normal',['nor_gl'],'4k','jpg'),('rough',['rough','Rough'],'4k','jpg')])
 report={'stage':'G4','revision':'COAST-R04','parent_master_sha256':PARENT,'parent_evidence_commit':'563ecf127826cf0b93faf72443c19e6a271401d9','source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'assets':[hdr,textile],'credit':'Powered by Poly Haven','basis':'Actually viewed COAST-R02 E01: rock relief exists but near-black; R03 M04: cloth response nearly uniform. Use licensed measured overcast directional environment and scanned fabric surface, not more noise or generated image enhancement.','g4_stage_pass':False,'human_acceptance':False,'edits':[]}
 # Source HDRI is a daylight overcast measurement, artistically adapted to this night.
 # Calibrate the upper-hemisphere mean, never scene exposure or ray-specific output.
 im=bpy.data.images[hdr['files']['environment']['image_name']];assert im.is_float
 width,height=im.size;pixels=np.empty(width*height*4,dtype=np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(height,width,4)
 tint=np.array([.78,.88,1.0],dtype=np.float32);sample=pixels[height//2::4,::4,:3]*tint
 alt=(np.arange(height//2,height,4)+.5-height*.5)/(height*.5)*(math.pi/2);weights=np.cos(alt)[:,None]
 luminance=sample@np.array([.2126,.7152,.0722]);average=float((luminance*weights).sum()/(weights.sum()*sample.shape[1]));assert math.isfinite(average) and average>.0001
 power=.36/average;assert .001<power<100
 previous=s.world;s.world=bpy.data.worlds.new('G4COAST_R04_adapted_overcast_sky');s.world.use_nodes=True;n=s.world.node_tree.nodes;l=s.world.node_tree.links
 env=n.new('ShaderNodeTexEnvironment');env.image=im;env.interpolation='Linear';tc=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=.35;l.new(tc.outputs['Normal'],mapping.inputs['Vector']);l.new(mapping.outputs['Vector'],env.inputs['Vector'])
 tone=n.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1;tone.inputs[2].default_value=(*tint,1);l.new(env.outputs['Color'],tone.inputs[1]);l.new(tone.outputs[0],n['Background'].inputs['Color']);n['Background'].inputs['Strength'].default_value=power
 report['environment']={'old_world':previous.name,'new_world':s.world.name,'source_upper_hemisphere_tinted_mean':average,'design_target_mean':.36,'strength':power,'tint':tint.tolist(),'rotation_radians':.35,'shared_camera_lighting_reflections':True,'not_daylight_or_measured_night_claim':'The source is an overcast daylight HDRI; strength and tint are an artistic night adaptation, not a calibrated moonlight simulation.','no_global_exposure_change':True}
 del pixels,sample,luminance
 cloth=old.copy();cloth.name='G4COAST_R04_scanned_moss_wool';n=cloth.node_tree.nodes;l=cloth.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED')
 uv=n.new('ShaderNodeUVMap');uv.uv_map='ClothPhysicalMeters';sc=n.new('ShaderNodeVectorMath');sc.operation='SCALE';sc.inputs['Scale'].default_value=1/.30;l.new(uv.outputs['UV'],sc.inputs[0])
 images={}
 for role in ['diff','normal','rough']:
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images[textile['files'][role]['image_name']];tex.name='Licensed wool '+role;l.new(sc.outputs[0],tex.inputs['Vector']);images[role]=tex
 tone=n.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1;tone.inputs[2].default_value=(.78,.96,.64,1);l.new(images['diff'].outputs['Color'],tone.inputs[1]);l.new(tone.outputs[0],p.inputs['Base Color'])
 normal=n.new('ShaderNodeNormalMap');normal.uv_map='ClothPhysicalMeters';normal.inputs['Strength'].default_value=.7;l.new(images['normal'].outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs['Normal'])
 rough=n.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.50;rough.inputs['To Max'].default_value=.82;l.new(images['rough'].outputs['Color'],rough.inputs['Value']);l.new(rough.outputs['Result'],p.inputs['Roughness'])
 p.inputs['Sheen Weight'].default_value=.32;p.inputs['Sheen Roughness'].default_value=.48;p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=0
 for o in targets:
  o.data=o.data.copy();uvlayer=o.data.uv_layers.new(name='ClothPhysicalMeters');world_scale=o.matrix_world.to_scale()
  assert min(world_scale)>.5 and max(world_scale)<2,(o.name,list(world_scale))
  for face in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(face.normal[i]));axes={0:(1,2),1:(0,2),2:(0,1)}[axis]
   for li in face.loop_indices:
    co=o.data.vertices[o.data.loops[li].vertex_index].co;uvlayer.data[li].uv=(co[axes[0]]*world_scale[axes[0]],co[axes[1]]*world_scale[axes[1]])
  for i,m in enumerate(o.data.materials):
   if m==old:o.data.materials[i]=cloth
  report['edits'].append({'object':o.name,'old_material':old.name,'new_material':cloth.name,'added_UV':'ClothPhysicalMeters','original_UV_retained':True,'physical_tile_metres':.30,'geometry_unchanged':True})
 cloth['source']='https://polyhaven.com/a/poly_wool_herringbone';cloth['license']='CC0-1.0';cloth['reference_tile_metres']=.30
 s.frame_set(451);bpy.context.view_layer.update();report['protected_before']=before;report['protected_after']=protect();assert before==report['protected_after'],'Protected geometry, placement, rays, cameras, lights or exposure changed'
 for name in ['G1-manifest.json','G1-FINISH-RECIPES.json','G1-DERIVATION.txt','SOURCE-RECOVERY.json','STORM-ASSET-SOURCES.json','ASSET-AND-API-PROBE.json','PARENT-R03-build-report.json','COAST-R01-build-report.json','COAST-R02-build-report.json']:
  if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
 (OUT/'models').mkdir(exist_ok=True);shutil.copy2(BASE/'models/MODEL-SOURCES.json',OUT/'models/MODEL-SOURCES.json');shutil.copy2(BASE/'build-report.json',OUT/'COAST-R03-build-report.json')
 s['g4_revision']=REV;s['g4_coast_surface_parent']=PARENT;s.camera=bpy.data.objects['C01_exterior_hero'];save(s,OUT/'g4-full-scene-candidate.blend');assert sha(parent)==PARENT
 report['candidate_sha256']=sha(OUT/'g4-full-scene-candidate.blend');report['master_bytes']=(OUT/'g4-full-scene-candidate.blend').stat().st_size;(OUT/'build-report.json').write_text(json.dumps(report,indent=2));(OUT/'SURFACE-ASSET-SOURCES.json').write_text(json.dumps({'credit':report['credit'],'assets':report['assets']},indent=2));print('COAST_R04_NATIVE_SURFACE_SOURCE_SAVED',report['candidate_sha256'],flush=True)
else:
 master=OUT/'g4-full-scene-candidate.blend';expected=json.loads((OUT/'build-report.json').read_text())['candidate_sha256'];assert Path(bpy.data.filepath).resolve()==master and sha(master)==expected and s.get('g4_revision')==REV
 missing=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()];assert not missing,missing
 s.timeline_markers.clear();s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=16;s.cycles.adaptive_threshold=.04;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
 jobs={'context':[('C01_exterior_hero','C01-native-surface-coast.png',(1440,900),48),('G4COAST_rock_water_close','E01-native-wet-rock.png',(1440,900),64)],'closeups':[('G4R03_textile_macro','M04-scanned-wool.png',(1440,900),64),('G4R03_rain_glass_macro','M01-native-rain-glass.png',(1600,1000),64),('C03_hall_to_platform','C03-native-rain-hall.png',(1440,900),64)]}[MODE]
 metrics=[]
 for cam,name,res,samples in jobs:
  assert time.time()<float(os.environ['G4_SURFACE_DEADLINE']),'Finite surface request ended'
  row=render(s,bpy.data.objects[cam],OUT/name,res=res,samples=samples,frame=451);row.update(native_render=True,master_sha256=expected,revision='COAST-R04',max_bounces=10,transmission_bounces=8);metrics.append(row);(OUT/(MODE+'-render-metrics.json')).write_text(json.dumps(metrics,indent=2));print('COAST_R04_NATIVE_VIEW',name,flush=True)
 assert sha(master)==expected
 (OUT/(MODE+'-reopen-check.json')).write_text(json.dumps({'fresh_process':True,'master_sha256':expected,'master_unchanged':True,'missing_external_images':missing,'native_images':len(metrics),'g4_stage_pass':False,'human_acceptance':False},indent=2))
