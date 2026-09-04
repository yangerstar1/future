"""Selected Poly Haven assets, not a site scraper. Run with system Python.
Live API requests are visibly credited here: Powered by Poly Haven.
No authentication, subscriptions, paid generation, or unlicensed reference images.
"""
from pathlib import Path
import hashlib, json, os, time, urllib.request, urllib.parse

ROOT = Path(os.environ.get('ASSET_ROOT', 'workspaces/glasshouse-terminus/output/g1/assets'))
ROOT.mkdir(parents=True, exist_ok=True)
AGENT = 'GlasshouseTerminus-Future/1.0 (https://github.com/yangerstar1/future; selected-asset-build)'
MAX_TOTAL = 120_000_000
used = 0

def fetch(url, limit=30_000_000):
    global used
    host = urllib.parse.urlparse(url).hostname
    if host not in {'api.polyhaven.com','dl.polyhaven.org','dl.polyhaven.com'}:
        raise RuntimeError('Unexpected asset host: '+str(host))
    req = urllib.request.Request(url, headers={'User-Agent':AGENT, 'Referer':'https://github.com/yangerstar1/future'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read(limit+1)
    if len(data)>limit or used+len(data)>MAX_TOTAL:
        raise RuntimeError('Asset download budget exceeded')
    used += len(data)
    return data

records=[]
for asset, maps in [('american_walnut_veneer',['diff','nor_gl','rough']), ('slate_floor',['diff','nor_gl','rough'])]:
    info=json.loads(fetch('https://api.polyhaven.com/info/'+asset,2_000_000))
    files=json.loads(fetch('https://api.polyhaven.com/files/'+asset,3_000_000))
    (ROOT/(asset+'-info.json')).write_text(json.dumps(info,indent=2))
    (ROOT/(asset+'-files.json')).write_text(json.dumps(files,indent=2))
    if info.get('vaulted') is True or info.get('locked') is True:
        raise RuntimeError('Selected asset is not publicly unlocked: '+asset)
    record={'asset':asset,'source':'https://polyhaven.com/a/'+asset,'license':'CC0-1.0',
            'license_source':'https://polyhaven.com/license','author':info.get('authors',info.get('author','SEE_INFO_JSON')),
            'downloads':{}}
    for role in maps:
        try: variant=files[role]['2k']['jpg']
        except (KeyError,TypeError):
            raise RuntimeError('Selected map unavailable; no silent substitution: '+asset+' '+role)
        url=variant['url']; data=fetch(url)
        if variant.get('md5') and hashlib.md5(data).hexdigest()!=variant['md5']:
            raise RuntimeError('Upstream MD5 mismatch: '+asset+' '+role)
        path=ROOT/(asset+'_'+role+'_2k.jpg');path.write_bytes(data)
        record['downloads'][role]={'path':path.name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        time.sleep(.25)
    records.append(record)
    time.sleep(1)
manifest={'provider':'Poly Haven','credit':'Powered by Poly Haven','assets_license':'CC0-1.0',
          'notice':'Only downloaded asset maps are reused; website previews and third-party reference photos are not redistributed.',
          'downloaded_bytes':used,'assets':records}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
