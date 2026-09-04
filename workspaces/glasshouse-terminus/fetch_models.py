"""Download only two explicitly selected CC0 models after a G3 request.
Powered by Poly Haven. Metadata and glTF dependency URIs are inspected before
fetching; no invented texture paths, bulk crawl, paid assets or brand models.
"""
from pathlib import Path
from urllib.parse import urlparse,urljoin,unquote
import urllib.request,json,hashlib,time,os

ROOT=Path(os.environ.get('MODEL_ROOT','workspaces/glasshouse-terminus/output/g3/models')).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
AGENT='GlasshouseTerminus-Future/1.0 (https://github.com/yangerstar1/future; selected-asset-build)'
HOSTS={'api.polyhaven.com','dl.polyhaven.org','dl.polyhaven.com'}
MAX_TOTAL=180_000_000
used=0

def download(url,limit=60_000_000):
 global used
 parsed=urlparse(url)
 if parsed.scheme!='https' or parsed.hostname not in HOSTS:raise RuntimeError('Unexpected asset origin')
 req=urllib.request.Request(url,headers={'User-Agent':AGENT,'Referer':'https://github.com/yangerstar1/future'})
 with urllib.request.urlopen(req,timeout=60) as r:
  if urlparse(r.url).hostname not in HOSTS:raise RuntimeError('Unexpected redirect origin')
  data=r.read(limit+1)
 if len(data)>limit or used+len(data)>MAX_TOTAL:raise RuntimeError('Model download budget exceeded')
 used+=len(data);time.sleep(.2)
 return data

records=[]
for asset in ['GreenChair_01','potted_plant_01']:
 folder=ROOT/asset;folder.mkdir(exist_ok=True)
 info=json.loads(download('https://api.polyhaven.com/info/'+asset,3_000_000))
 files=json.loads(download('https://api.polyhaven.com/files/'+asset,3_000_000))
 (folder/'source-info.json').write_text(json.dumps(info,indent=2))
 (folder/'source-files.json').write_text(json.dumps(files,indent=2))
 try:variant=files['gltf']['2k']['gltf']
 except (TypeError,KeyError) as e:raise RuntimeError('Observed glTF metadata differs; stop without guessing: '+asset) from e
 if not isinstance(variant,dict) or not isinstance(variant.get('url'),str):raise RuntimeError('Invalid glTF descriptor')
 blob=download(variant['url'])
 if variant.get('md5') and hashlib.md5(blob).hexdigest()!=variant['md5']:raise RuntimeError('glTF integrity mismatch')
 doc=json.loads(blob)
 if doc.get('asset',{}).get('version')!='2.0':raise RuntimeError('Expected glTF 2.0')
 local_name=Path(unquote(urlparse(variant['url']).path)).name
 (folder/local_name).write_bytes(blob)
 record={'asset_id':asset,'source':'https://polyhaven.com/a/'+asset,'license':'CC0-1.0',
  'license_source':'https://polyhaven.com/license','authors':info.get('authors'),
  'upstream_dimensions':info.get('dimensions'),'entry':str((folder/local_name).relative_to(ROOT)),
  'files':[{'path':local_name,'url':variant['url'],'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}]}
 includes=variant.get('include',{})
 urls={}
 def collect(node):
  if isinstance(node,dict):
   for key,value in node.items():
    if isinstance(value,dict) and 'url' in value:urls[key]=value
    collect(value)
  elif isinstance(node,list):
   for value in node:collect(value)
 collect(includes)
 needed={item['uri'] for group in ['buffers','images'] for item in doc.get(group,[]) if 'uri' in item and not item['uri'].startswith('data:')}
 for uri in sorted(needed):
  if urlparse(uri).scheme or urlparse(uri).netloc:raise RuntimeError('Unexpected external glTF URI')
  path=(folder/unquote(uri)).resolve()
  if not path.is_relative_to(folder):raise RuntimeError('Asset dependency escapes its directory')
  descriptor=urls.get(uri)
  url=descriptor['url'] if descriptor else urljoin(variant['url'],uri)
  data=download(url)
  if descriptor and descriptor.get('md5') and hashlib.md5(data).hexdigest()!=descriptor['md5']:raise RuntimeError('Dependency integrity mismatch: '+uri)
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
  record['files'].append({'path':str(path.relative_to(folder)),'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 record['gltf_nodes']=[n.get('name','') for n in doc.get('nodes',[])]
 record['gltf_materials']=[m.get('name','') for m in doc.get('materials',[])]
 records.append(record)
manifest={'credit':'Powered by Poly Haven','assets_license':'CC0-1.0','downloaded_bytes':used,
 'scope':'Selected generic chair and potted plant only; original station/train remain project assets',
 'assets':records}
(ROOT/'MODEL-SOURCES.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
