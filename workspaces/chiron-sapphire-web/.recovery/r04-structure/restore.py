"""Apply the verified R04 structural checkpoint once, without overwriting later work.
Transport is not the deliverable: Actions commits all restored readable files.
"""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
here=Path(__file__).resolve().parent
root=here.parent.parent
manifest=json.loads((here/'manifest.json').read_text())
marker=here/'RESTORED.json'
if marker.exists():
    if json.loads(marker.read_text())['snapshot'] != manifest['sha256']:
        raise SystemExit('Recovery identity changed; do not overwrite current source.')
    print('R04 already restored. Current readable source is left untouched.')
    raise SystemExit(0)
data=base64.b64decode(''.join((here/f'delta-{i:02}.b64').read_text().strip() for i in range(manifest['parts'])),validate=True)
if len(data)!=manifest['compressedBytes'] or hashlib.sha256(data).hexdigest()!=manifest['sha256']:
    raise SystemExit('Compressed checkpoint verification failed.')
raw=lzma.decompress(data)
if len(raw)!=manifest['rawBytes'] or hashlib.sha256(raw).hexdigest()!=manifest['jsonSha256']:
    raise SystemExit('Decoded checkpoint verification failed.')
changes=json.loads(raw)['changes']
if len(changes)!=manifest['files']:
    raise SystemExit('Inventory mismatch.')
prepared={}
for change in changes:
    name=change['path']; rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or name in prepared:
        raise SystemExit('Invalid or duplicate checkpoint path.')
    file=root/name
    if change['before'] is None:
        if file.exists(): raise SystemExit('New-file conflict: '+name)
        text=''
    else:
        if not file.is_file(): raise SystemExit('Missing baseline: '+name)
        source=file.read_bytes()
        if hashlib.sha256(source).hexdigest()!=change['before']:
            raise SystemExit('Baseline changed; reconcile before writing: '+name)
        text=source.decode('utf-8')
    lines=text.splitlines(keepends=True)
    last=len(lines)+1
    for edit in reversed(change['edits']):
        start,end=edit['start'],edit['end']
        if not 0<=start<=end<=len(lines) or end>last:
            raise SystemExit('Invalid edit bounds: '+name)
        lines[start:end]=edit['text'].splitlines(keepends=True);last=start
    result=''.join(lines).encode('utf-8')
    if hashlib.sha256(result).hexdigest()!=change['after']:
        raise SystemExit('Restored-file verification failed: '+name)
    prepared[name]=result
# Only write after EVERY input and output has been checked.
for name,result in prepared.items():
    file=root/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(result)
marker.write_text(json.dumps({'snapshot':manifest['sha256'],'sourceSha256':{n:hashlib.sha256(b).hexdigest() for n,b in prepared.items()}},indent=2)+'\n')
print('Restored',len(prepared),'readable R04 source files. No quality gate is implied.')
