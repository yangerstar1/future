"""One-time verified transport recovery, scoped to this authorized workspace.
The readable source is committed by the workflow before build or validation.
Never overwrite an existing implementation or replay over subsequent edits.
"""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma

here = Path(__file__).resolve().parent
workspace = here.parent.parent
manifest = json.loads((here / 'manifest.json').read_text())
patch_bytes = (here / 'patches.json').read_bytes()
identity = {'snapshot': manifest['sha256'], 'patches': hashlib.sha256(patch_bytes).hexdigest()}
marker = here / 'RESTORED.json'
if marker.exists():
    previous = json.loads(marker.read_text())
    if any(previous.get(k) != v for k, v in identity.items()):
        raise SystemExit('Recovery identity changed: stop; do not overwrite the implementation.')
    print('Already restored; current readable implementation is left unchanged.')
    raise SystemExit(0)
if (workspace / 'main.mjs').exists():
    raise SystemExit('Unregistered existing implementation: stop before writing.')

encoded = ''.join((here / f'part-{i:02}.b64').read_text().strip() for i in range(manifest['parts']))
packed = base64.b64decode(encoded, validate=True)
if hashlib.sha256(packed).hexdigest() != manifest['sha256']:
    raise SystemExit('Compressed snapshot hash mismatch.')
raw = lzma.decompress(packed)
if hashlib.sha256(raw).hexdigest() != manifest['jsonSha256']:
    raise SystemExit('Decoded snapshot hash mismatch.')
files = json.loads(raw)
if set(files) != set(manifest['sourceFiles']) or len(files) != manifest['files']:
    raise SystemExit('Source inventory mismatch.')
for name, text in files.items():
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or not isinstance(text, str):
        raise SystemExit('Invalid recovery path/content.')
    if (workspace / name).exists() and name not in {'package.json', 'PRODUCTION-STATE.md'}:
        raise SystemExit(f'Existing file conflict: {name}')

for patch in json.loads(patch_bytes)['patches']:
    name = patch['path']
    text = files[name]
    if hashlib.sha256(text.encode()).hexdigest() != patch['sha256Before']:
        raise SystemExit(f'Patch base mismatch: {name}')
    for replacement in patch['replacements']:
        if text.count(replacement['before']) != 1:
            raise SystemExit(f'Patch anchor mismatch: {name}')
        text = text.replace(replacement['before'], replacement['after'], 1)
    if hashlib.sha256(text.encode()).hexdigest() != patch['sha256After']:
        raise SystemExit(f'Patch output mismatch: {name}')
    files[name] = text

# No writes occur before the complete inventory and patch verification above.
for name, text in files.items():
    path = workspace / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
identity['sourceSha256'] = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files.items()}
marker.write_text(json.dumps(identity, indent=2) + '\n')
print(f'Restored {len(files)} readable source files, with verified context-recovery repair.')
