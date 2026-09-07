"""Fetch one bounded, explicitly identified Poly Haven rock texture family.
Records the exact API-selected asset, source URLs, returned sizes/hashes and license.
No paid APIs, scraping, models, or whole-scene replacement. Does not create evidence
from the unrelated generated concept images.
"""
import urllib.request,json,hashlib,os,time
from pathlib import Path
OUT=Path('workspaces/glasshouse-terminus/output/g4-r03-weather/assets')
OUT.mkdir(parents=True,exist_ok=True)
BUDGET=55000000
used=0

def get(url,limit=10000000):
    global used
    req=urllib.request.Request(url,headers={'User-Agent':'GlasshouseTerminus-asset-reuse/1.0'})
    with urllib.request.urlopen(req,timeout=45) as response:
        if response.headers.get('Content-Length') and int(response.headers['Content-Length'])>limit:raise RuntimeError('Download size exceeds finite bound')
        data=response.read(limit+1)
    if len(data)>limit:raise RuntimeError('Response exceeds finite bound')
    used+=len(data)
    if used>BUDGET:raise RuntimeError('Asset download budget reached')
    return data

catalog=json.loads(get('https://api.polyhaven.com/assets?type=textures'))
assert isinstance(catalog,dict)
def score(item):
    key,meta=item;text=(key+' '+str(meta.get('name',''))).lower()
    if 'rock' not in text and 'cliff' not in text:return -1000
    if any(w in text for w in ['aerial','floor','cobble','pavement','ground','gravel','pebble']):return -1000
    return sum(v for word,v in [('cliff',9),('rock_face',8),('rock_wall',6),('rock_boulder',4),('cracked',3),('moss',-2)] if word in text)
candidates=sorted([(k,v) for k,v in catalog.items() if score((k,v))>0],key=lambda kv:(-score(kv),kv[0]))
assert candidates,'No appropriate official rock texture found; do not substitute random assets'
selection=None
for asset,meta in candidates[:3]:
    files=json.loads(get('https://api.polyhaven.com/files/'+asset))
    maps={}
    for role in ['diff','rough','nor_gl']:
        version=files.get(role,{}).get('2k',{})
        fmt='jpg' if 'jpg' in version else 'png' if 'png' in version else None
        if fmt:maps[role]=(fmt,version[fmt])
    if 'diff' in maps and 'rough' in maps:selection=(asset,meta,maps);break
assert selection,'Selected official rock families lack usable 2K diffuse/roughness maps'
asset,meta,maps=selection
record={'asset':asset,'asset_name':meta.get('name'),'authors':meta.get('authors'),'source':'https://polyhaven.com/a/'+asset,'api':'https://api.polyhaven.com/files/'+asset,'license':'CC0-1.0','license_source':'https://polyhaven.com/license','selection_scope':'One actual official rock texture family. Existing furniture, plants, glass, floor and wood assets reused.','maps':{}}
for role,(fmt,entry) in maps.items():
    data=get(entry['url'],18000000)
    if entry.get('size'):assert len(data)==entry['size'],(asset,role,'size mismatch')
    if entry.get('md5'):assert hashlib.md5(data).hexdigest()==entry['md5'],(asset,role,'MD5 mismatch')
    name=asset+'_'+role+'_2k.'+fmt;(OUT/name).write_bytes(data)
    record['maps'][role]={'file':name,'url':entry['url'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'returned_md5':entry.get('md5')}
record['total_download_bytes_including_metadata']=used
(OUT/'rock-sources.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
