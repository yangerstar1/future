"""Adapt the existing fetch_models.py selected-asset workflow, never crawl a library.
Powered by Poly Haven. One coastal cliff scan plus one coastal rock material.
"""
import json,hashlib,time,urllib.request
from pathlib import Path
from urllib.parse import urlparse,urljoin,unquote
ROOT=Path('workspaces/glasshouse-terminus/output/g4-storm-assets').resolve();ROOT.mkdir(parents=True,exist_ok=True)
HOSTS={'api.polyhaven.com','dl.polyhaven.org','dl.polyhaven.com'}
AGENT='GlasshouseTerminus-Future/1.0 (https://github.com/yangerstar1/future; selected-asset-build)'
used=0;MAX_TOTAL=180000000

def get(url,limit=80000000):
 global used
 u=urlparse(url);assert u.scheme=='https' and u.hostname in HOSTS,url
 req=urllib.request.Request(url,headers={'User-Agent':AGENT,'Referer':'https://github.com/yangerstar1/future'})
 with urllib.request.urlopen(req,timeout=90) as r:
  assert urlparse(r.url).hostname in HOSTS
  b=r.read(limit+1)
 assert len(b)<=limit and used+len(b)<=MAX_TOTAL,'Finite download cap reached'
 used+=len(b);time.sleep(.2);return b

def write_descriptor(desc,path):
 b=get(desc['url']);assert not desc.get('md5') or hashlib.md5(b).hexdigest()==desc['md5'],'Upstream checksum mismatch'
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
 return {'path':str(path.relative_to(ROOT)),'url':desc['url'],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'md5_verified':bool(desc.get('md5'))}

records=[]
for asset in ['coastal_cliff_04','seaside_rock']:
 folder=ROOT/asset;folder.mkdir(exist_ok=True)
 info=json.loads(get('https://api.polyhaven.com/info/'+asset,3000000));files=json.loads(get('https://api.polyhaven.com/files/'+asset,3000000))
 (folder/'source-info.json').write_text(json.dumps(info,indent=2));(folder/'source-files.json').write_text(json.dumps(files,indent=2))
 record={'asset_id':asset,'source':'https://polyhaven.com/a/'+asset,'authors':info.get('authors'),'license':'CC0-1.0','license_source':'https://polyhaven.com/license','upstream_dimensions':info.get('dimensions'),'files':[]}
 if asset=='coastal_cliff_04':
  variant=files.get('gltf',{}).get('2k',{}).get('gltf');assert variant and 'url' in variant,'No observed 2k glTF descriptor; stop, do not guess'
  name=Path(unquote(urlparse(variant['url']).path)).name
  record['files'].append(write_descriptor(variant,folder/name));record['entry']=str((folder/name).relative_to(ROOT))
  doc=json.loads((folder/name).read_text());assert doc['asset']['version']=='2.0'
  descriptors={}
  def collect(n):
   if isinstance(n,dict):
    for k,v in n.items():
     if isinstance(v,dict) and 'url' in v:descriptors[k]=v
     collect(v)
   elif isinstance(n,list):
    for v in n:collect(v)
  collect(variant.get('include',{}))
  needed={r['uri'] for key in ['buffers','images'] for r in doc.get(key,[]) if 'uri' in r and not r['uri'].startswith('data:')}
  for uri in sorted(needed):
   assert not urlparse(uri).scheme and not urlparse(uri).netloc
   path=(folder/unquote(uri)).resolve();assert path.is_relative_to(folder)
   desc=descriptors.get(uri,{'url':urljoin(variant['url'],uri)})
   record['files'].append(write_descriptor(desc,path))
  record['gltf_nodes']=[n.get('name') for n in doc.get('nodes',[])];record['gltf_materials']=[m.get('name') for m in doc.get('materials',[])]
 else:
  for role,res in [('diff','4k'),('nor_gl','4k'),('rough','4k'),('disp','2k')]:
   variants=files.get(role,{}).get(res,{})
   fmt='png' if role=='disp' and 'png' in variants else 'jpg'
   assert fmt in variants,(asset,role,res,'Actual descriptor unavailable')
   desc=variants[fmt];path=folder/Path(unquote(urlparse(desc['url']).path)).name
   row=write_descriptor(desc,path);row.update(role=role,resolution=res);record['files'].append(row)
 records.append(record)
manifest={'credit':'Powered by Poly Haven','scope':'Selected cliff scan and rock surface only, station/train remain original project geometry. No generated image textures.','assets':records,'downloaded_bytes':used,'max_bytes':MAX_TOTAL}
(ROOT/'STORM-ASSET-SOURCES.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
