"""Validate and losslessly concatenate the existing R04C render shards.
Does not render new frames, interpolate, grade, or declare artistic qualification.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, shutil, struct, subprocess
from pathlib import Path

SOURCE_SHA = '90363be4ae47d5439b7b91fbc07d859415efcfba'
SCENE_SHA = '831c51340a7c81012e517d4ea0ce0da4a6412a1d86940ad74c7a7f0b1f760261'
RENDER_RUN = 34507267207

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))

def command(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f'{args[0]} failed ({p.returncode}): {p.stderr[-5000:]}')
    return p

def one(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    if len(matches) != 1:
        raise ValueError(f'Expected one {name} in {root.name}, found {len(matches)}')
    return matches[0]

def verify_checksums(folder: Path, role: str) -> dict:
    f = one(folder, 'CHECKSUMS.json'); m = read(f)
    assert m['role'] == role and int(m['run_id']) == RENDER_RUN
    assert m['source_sha'] == SOURCE_SHA and m['exit_code'] == 0
    for rel, item in m['files'].items():
        path = (f.parent / rel).resolve()
        assert path.is_relative_to(f.parent.resolve()), rel
        assert path.is_file() and path.stat().st_size == item['bytes'], rel
        assert digest(path) == item['sha256'], rel
    return {'root': f.parent, 'count': len(m['files'])}

def probe(path: Path) -> dict:
    p = command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)])
    m = json.loads(p.stdout); v = [s for s in m['streams'] if s['codec_type']=='video']
    assert len(v)==1 and not any(s['codec_type']=='audio' for s in m['streams'])
    v=v[0]; assert v['codec_name']=='h264'
    assert (v['width'],v['height'])==(1280,720)
    n,d=map(int,v['avg_frame_rate'].split('/')); assert abs(n/d-24)<1e-6
    return {'frames':int(v['nb_read_frames']), 'duration':float(m['format']['duration']),
            'stream':v, 'sha256':digest(path), 'bytes':path.stat().st_size}

def assemble(incoming: Path, out: Path) -> dict:
    for executable in ['ffmpeg','ffprobe']:
        assert shutil.which(executable), f'Missing {executable}; no hidden installation'
    out.mkdir(parents=True,exist_ok=True)
    folders={k:incoming/f'skyfold-r04c-{k}-{RENDER_RUN}' for k in ['source','stills','motion-a','motion-b']}
    assert all(p.is_dir() for p in folders.values()), str(folders)
    src=one(folders['source'],'skyfold-r04c.blend'); manifest=read(src.with_name('BUILD-MANIFEST.json'))
    assert digest(src)==SCENE_SHA==manifest['scene_sha256'] and manifest['source_sha']==SOURCE_SHA
    checks={'stills':verify_checksums(folders['stills'],'stills')}
    static=read(checks['stills']['root']/'OBSERVATIONS.json')
    expected={'R04_HERO_f001.png':(2560,1440),'R04_SECOND_f001.png':(1920,1080),'R04_GALLERY_CRAFT_f001.png':(1920,1080)}
    assert len(static)==11
    for row in static:
        p=checks['stills']['root']/row['file']; b=p.read_bytes()
        assert b[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II',b[16:24])==tuple(row['dimensions'])
        assert digest(p)==row['sha256'] and row['scene_sha256']==SCENE_SHA
        assert row['scene_source_sha']==SOURCE_SHA and row['render_source_sha']==SOURCE_SHA
        recorded=manifest['cameras'][row['camera']]['matrix']
        assert max(abs(recorded[i][j]-row['camera_matrix'][i][j]) for i in range(4) for j in range(4))<1e-5
        command(['ffmpeg','-v','error','-i',str(p),'-f','null','-'])
    for name,size in expected.items():
        assert struct.unpack('>II',(checks['stills']['root']/name).read_bytes()[16:24])==size
    parts=[]; observations=[]; raw_records=[]; samples=[]
    for key,role,first,last in [('motion-a','motion_a',1,96),('motion-b','motion_b',97,192)]:
        check=verify_checksums(folders[key],role); checks[key]=check; root=check['root']
        v=read(root/'VIDEO-MANIFEST.json'); obs=read(root/'OBSERVATIONS.json'); inp=read(root/'INPUT.json')
        assert inp['scene_sha256']==SCENE_SHA and inp['scene_source_sha']==SOURCE_SHA and inp['render_source_sha']==SOURCE_SHA
        assert v['source_sha']==SOURCE_SHA and int(v['run_id'])==RENDER_RUN
        assert (v['first_source_frame'],v['last_source_frame'],v['frame_count'])==(first,last,96)
        assert v['fps']==24 and v['dimensions']==[1280,720] and v['duration_seconds']==4
        assert v['generated_frames'] is False and v['interpolated_frames'] is False
        assert [r['frame'] for r in v['source_frames']]==list(range(first,last+1))
        assert [r['frame'] for r in obs]==list(range(first,last+1))
        for r,o in zip(v['source_frames'],obs):
            assert r['sha256']==o['sha256'] and r['file']==o['file']
            assert o['scene_sha256']==SCENE_SHA and o['scene_source_sha']==SOURCE_SHA and o['render_source_sha']==SOURCE_SHA
            assert o['dimensions']==[1280,720] and o['camera']=='R04_HERO'
            t=(r['frame']-1)/191; mat=o['ring_matrix']
            angle=math.degrees(math.atan2(mat[0][2],mat[0][0]))
            assert abs(angle-6*t)<1e-4
        video=root/v['video']; assert digest(video)==v['video_sha256']
        info=probe(video); assert info['frames']==96 and abs(info['duration']-4)<.03
        parts.append({'file':video,'probe':info}); observations.extend(obs); raw_records.extend(v['source_frames'])
        by_frame={r['frame']:r for r in v['source_frames']}
        for p in sorted((root/'samples').glob('frame_*.png')):
            frame=int(p.stem.split('_')[1]); assert digest(p)==by_frame[frame]['sha256']
            samples.append((frame,p))
    assert [r['frame'] for r in raw_records]==list(range(1,193))
    assert len({r['sha256'] for r in raw_records})==192
    concatenation=out/'concat.txt'
    assert all("'" not in str(part['file']) for part in parts)
    concatenation.write_text(''.join("file '"+str(part['file'].resolve())+"'\n" for part in parts))
    movie=out/'Skyfold_Dock_R04C_Motion_720p.mp4'
    command(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(concatenation),'-map','0:v:0','-c','copy','-movflags','+faststart',str(movie)])
    result=probe(movie); assert result['frames']==192 and abs(result['duration']-8)<.03
    # Fully decode the result, then independently verify PTS continuity and duplicate frames.
    md5=command(['ffmpeg','-v','error','-i',str(movie),'-map','0:v:0','-f','framemd5','-']).stdout
    (out/'decoded-framemd5.txt').write_text(md5)
    frames=[line for line in md5.splitlines() if line and not line.startswith('#')]
    assert len(frames)==192 and len({l.split(',')[-1].strip() for l in frames})==192
    times=json.loads(command(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(movie)]).stdout)
    pts=[float(f['best_effort_timestamp_time']) for f in times['frames']]
    assert len(pts)==192 and all(abs((b-a)-1/24)<.0001 for a,b in zip(pts,pts[1:]))
    sample_dir=out/'decoded-samples';sample_dir.mkdir(exist_ok=True);ssims=[]
    # Predetermined colour/assembly check, not a subjective or motion-quality score.
    for frame,p in samples:
        dest=sample_dir/f'frame_{frame:04d}.png'
        command(['ffmpeg','-v','error','-y','-i',str(movie),'-vf',f'select=eq(n\\,{frame-1})','-frames:v','1',str(dest)])
        q=command(['ffmpeg','-hide_banner','-i',str(p),'-i',str(dest),'-lavfi','ssim','-f','null','-'])
        val=float(re.findall(r'All:([0-9.]+)',q.stderr)[-1]);ssims.append({'frame':frame,'ssim':val})
        assert val>=.94,(frame,val,'encoding colour or join order differs from source PNG')
    for dirname in ['source','stills']:(out/dirname).mkdir(exist_ok=True)
    shutil.copy2(src,out/'source'/src.name);shutil.copy2(src.with_name('BUILD-MANIFEST.json'),out/'source/BUILD-MANIFEST.json')
    for p in checks['stills']['root'].glob('*.png'):shutil.copy2(p,out/'stills'/p.name)
    report={'render_run_id':RENDER_RUN,'scene_sha256':SCENE_SHA,'scene_source_sha':SOURCE_SHA,
        'assembly':'FFmpeg concat demuxer, H.264 packet copy; no resizing, re-render, interpolation or colour grading',
        'dimensions':[1280,720],'fps':24,'frames':192,'duration_seconds':result['duration'],
        'video_sha256':result['sha256'],'video_bytes':result['bytes'],'audio':False,
        'verified_still_pngs':len(static),'verified_input_files':{k:v['count'] for k,v in checks.items()},
        'source_frame_indices_contiguous':True,'unique_source_frame_hashes':192,
        'decoded_movie_frames':192,'unique_decoded_frames':192,'pts_step_tolerance_seconds':.0001,
        'sample_ssim_minimum_declared':.94,'source_png_sample_comparisons':ssims,
        'ring_rotation_degrees':[0,6],'camera_motion_record_count':len(observations),
        'stills_seconds':sum(r['seconds'] for r in static),'motion_seconds':sum(r['seconds'] for r in observations),
        'technical_result':'PASS_TRANSPORT_DECODE_AND_ASSEMBLY','visual_result':'REVIEW_REQUIRED',
        'contract_P2_1080_pass':False,'auto_qualified':False,
        'limitations':['720p motion study, not 1080p P2 delivery','Selected original PNGs and all frame hashes retained; not all 192 original PNG files','Technical checks do not prove absence of visually noticeable shimmer or professional art quality']}
    (out/'ASSEMBLY-VERIFICATION.json').write_text(json.dumps(report,indent=2))
    (out/'MOTION-OBSERVATIONS.json').write_text(json.dumps(observations,indent=2))
    (out/'SOURCE-FRAME-HASHES.json').write_text(json.dumps(raw_records,indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('incoming',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    print(json.dumps(assemble(args.incoming.resolve(),args.output.resolve()),indent=2))
