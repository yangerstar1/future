"""Verify actual contiguous tracking renders and packet-copy join their H.264 clips.
Derived from assemble_r04c.py; no rendering, interpolation, resizing or new grading.
Parameters describe an explicit preview, not automatic core-contract acceptance.
"""
from pathlib import Path
import os,json,hashlib,subprocess,shutil,re,math,struct
IN=Path(os.environ['TRACKING_IN']);OUT=Path(os.environ['TRACKING_OUT']);OUT.mkdir(parents=True,exist_ok=True)
SCENE=os.environ['TRACKING_SCENE_SHA'];SOURCE=os.environ['TRACKING_RENDER_SHA'];N=int(os.environ.get('TRACKING_FRAME_COUNT','96'))
assert N in [96,192]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def command(a):
 r=subprocess.run(a,capture_output=True,text=True,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr[-5000:])
 return r
def probe(p):
 j=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]).stdout)
 v=[s for s in j['streams'] if s['codec_type']=='video'];assert len(v)==1 and not any(s['codec_type']=='audio' for s in j['streams']);v=v[0]
 assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080)
 a,b=map(int,v['avg_frame_rate'].split('/'));assert a/b==24
 return {'frames':int(v['nb_read_frames']),'seconds':float(j['format']['duration']),'sha256':digest(p),'bytes':p.stat().st_size}
parts=[];rows=[];hashes=[];samples=[]
for p in IN.rglob('VIDEO-MANIFEST.json'):
 j=read(p);parts.append((j['first_source_frame'],j,p.parent))
parts.sort(key=lambda a:a[0]);assert len(parts)>=2
next_frame=1;clips=[]
for first,j,root in parts:
 assert first==next_frame and j['last_source_frame']>=first
 count=j['last_source_frame']-first+1;next_frame=j['last_source_frame']+1
 assert j['frame_count']==count and j['dimensions']==[1920,1080] and j['fps']==24
 assert j['generated_frames'] is False and j['interpolated_frames'] is False
 assert j['source_sha']==SOURCE
 obs=read(root/'OBSERVATIONS.json');assert len(obs)==count
 assert [r['frame'] for r in obs]==list(range(first,next_frame))
 assert [r['frame'] for r in j['source_frames']]==list(range(first,next_frame))
 for o,h in zip(obs,j['source_frames']):
  assert o['scene_sha256']==SCENE and o['render_source_sha']==SOURCE
  assert o['camera']=='R07B_FLIGHT_TRACK' and o['dimensions']==[1920,1080]
  assert o['sha256']==h['sha256'] and o['file']==h['file']
  if (root/o['file']).is_file():assert digest(root/o['file'])==o['sha256']
 clip=root/j['video'];info=probe(clip);assert info['frames']==count and abs(info['seconds']-count/24)<.03
 assert info['sha256']==j['video_sha256'];clips.append(clip);rows.extend(obs);hashes.extend(j['source_frames'])
 by_frame={r['frame']:r for r in obs}
 for png in sorted((root/'samples').glob('frame_*.png')):
  f=int(png.stem.split('_')[1]);assert digest(png)==by_frame[f]['sha256'];samples.append((f,png))
assert next_frame==N+1 and len(rows)==N and len({r['sha256'] for r in rows})==N
# Frame-source kinematics, not a claim of orbital physics or collision simulation.
for a,b in zip(rows,rows[1:]):
 assert a['ring_matrix']==b['ring_matrix']
 assert abs(b['ship_matrix'][0][3]-a['ship_matrix'][0][3])<.02
 assert b['ship_matrix'][1][3]<a['ship_matrix'][1][3]
 assert abs((a['ship_matrix'][1][3]-b['ship_matrix'][1][3])-640/191)<.03
 assert all(abs(b['ship_matrix'][i][j]-(1. if i==j else 0.))<1e-5 for i in range(3) for j in range(3))
assert len({tuple(r['camera_matrix'][i][3] for i in range(3)) for r in rows})==N
lst=OUT/'concat.txt';lst.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
movie=OUT/'Skyfold_Forward_Flight_1080p.mp4'
command(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(lst),'-map','0:v:0','-c','copy','-movflags','+faststart',str(movie)])
info=probe(movie);assert info['frames']==N and abs(info['seconds']-N/24)<.03
md5=command(['ffmpeg','-v','error','-i',str(movie),'-map','0:v:0','-f','framemd5','-']).stdout
(OUT/'decoded-framemd5.txt').write_text(md5);decoded=[x for x in md5.splitlines() if x and not x.startswith('#')]
assert len(decoded)==N and len({x.split(',')[-1].strip() for x in decoded})==N
before=[]
for p in clips:
 h=command(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-']).stdout
 before.extend(x.split(',')[-1].strip() for x in h.splitlines() if x and not x.startswith('#'))
assert before==[x.split(',')[-1].strip() for x in decoded]
times=json.loads(command(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(movie)]).stdout)
pts=[float(f['best_effort_timestamp_time']) for f in times['frames']];assert len(pts)==N and all(abs(b-a-1/24)<.0001 for a,b in zip(pts,pts[1:]))
comparisons=[];dest=OUT/'samples';dest.mkdir(exist_ok=True)
for f,p in samples:
 q=dest/('frame_%04d.png'%f);command(['ffmpeg','-v','error','-y','-i',str(movie),'-vf','select=eq(n\\,%d)'%(f-1),'-frames:v','1',str(q)])
 r=command(['ffmpeg','-hide_banner','-i',str(p),'-i',str(q),'-lavfi','ssim','-f','null','-']);val=float(re.findall(r'All:([0-9.]+)',r.stderr)[-1]);assert val>=.94,(f,val)
 comparisons.append({'frame':f,'ssim':val,'source_sha256':digest(p),'decoded_sha256':digest(q)})
report={'scene_sha256':SCENE,'render_source_sha':SOURCE,'assembly_source_sha':os.environ['GITHUB_SHA'],'assembly_run_id':os.environ['GITHUB_RUN_ID'],'video':movie.name,**info,'dimensions':[1920,1080],'fps':24,'source_frame_count':N,'first_source_frame':1,'last_source_frame':N,'full_scene_timeline_frames':192,'forward_displacement_m':[rows[-1]['ship_matrix'][i][3]-rows[0]['ship_matrix'][i][3] for i in range(3)],'independent_ship_forward_motion':True,'stationary_habitat':True,'moving_tracking_camera':True,'unique_source_frames':N,'unique_decoded_frames':N,'joined_decoded_frames_match_shards':True,'pts_continuous':True,'ssim_minimum_declared':.94,'source_png_comparisons':comparisons,'audio':False,'assembly':'H264 packet copy only','generated_or_interpolated_frames':False,'technical_result':'PASS_FILE_PROVENANCE_KINEMATICS_AND_ENCODING','artistic_result':'REVIEW_REQUIRED','core_contract_qualified':False,'contract_P2_8_seconds':N==192,'auto_qualified':False}
(OUT/'ASSEMBLY-VERIFICATION.json').write_text(json.dumps(report,indent=2));(OUT/'MOTION-OBSERVATIONS.json').write_text(json.dumps(rows,indent=2));(OUT/'SOURCE-FRAME-HASHES.json').write_text(json.dumps(hashes,indent=2))
print(json.dumps(report,indent=2))
