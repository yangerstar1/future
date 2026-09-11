"""Encode a contiguous real PNG sequence using Blender's bundled FFmpeg/VSE.
No interpolation, image generation or 3D re-render. Keeps every source-frame hash.
"""
import bpy, os, json, hashlib, struct, time
from pathlib import Path
root=Path(os.environ['FRAME_DIR']).resolve();first=int(os.environ['FRAME_START']);last=int(os.environ['FRAME_END']);assert 1<=first<=last<=192
files=[root/('frame_%04d.png'%f) for f in range(first,last+1)];rows=[];dims=None
for frame,p in zip(range(first,last+1),files):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n',p;d=struct.unpack('>II',b[16:24]);dims=d if dims is None else dims;assert d==dims,p
 rows.append({'frame':frame,'file':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
s=bpy.data.scenes.new('ENCODE_ACTUAL_SOURCE_FRAMES');ed=s.sequence_editor_create()
strips=getattr(ed,'strips',None)
if strips is None:strips=getattr(ed,'sequences',None)
if strips is None:raise RuntimeError('Unsupported VSE API: '+str([p.identifier for p in ed.bl_rna.properties]))
seq=strips.new_image('Actual Cycles or EEVEE rendered frames',str(files[0]),channel=1,frame_start=1)
for p in files[1:]:seq.elements.append(p.name)
seq.blend_type='REPLACE';seq.color_multiply=1.0
s.frame_start=1;s.frame_end=len(files);s.render.fps=24;s.render.fps_base=1.0;s.render.resolution_x=dims[0];s.render.resolution_y=dims[1];s.render.resolution_percentage=100;s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1
s.render.use_sequencer=True;s.render.use_compositing=False
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1;s.sequencer_colorspace_settings.name='sRGB'
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.gopsize=24;s.render.ffmpeg.audio_codec='NONE'
output=root/('skyfold-motion-%03d-%03d.mp4'%(first,last));s.render.filepath=str(output)
t=time.perf_counter();bpy.ops.render.render(animation=True,scene=s.name);elapsed=time.perf_counter()-t
assert output.is_file() and output.stat().st_size>1000
clip=bpy.data.movieclips.load(str(output));assert clip.frame_duration==len(files),(clip.frame_duration,len(files));assert tuple(clip.size)==dims,(tuple(clip.size),dims)
report={'first_source_frame':first,'last_source_frame':last,'frame_count':len(files),'fps':24,'duration_seconds':len(files)/24,'dimensions':dims,'source_frames':rows,'video':output.name,'video_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'blender':bpy.app.version_string,'source_sha':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'encode_seconds':elapsed,'codec':'H264 MP4','color_management':'Input rendered sRGB PNG -> VSE sRGB -> Standard, no second AgX transform','decoded_frame_count_verified':clip.frame_duration,'generated_frames':False,'interpolated_frames':False,'audio':False}
(root/'VIDEO-MANIFEST.json').write_text(json.dumps(report,indent=2));print('ACTUAL_FRAME_VIDEO_VERIFIED',output.name,report['frame_count'],report['duration_seconds'])
