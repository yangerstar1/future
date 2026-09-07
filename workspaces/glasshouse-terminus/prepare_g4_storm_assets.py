"""Reuse existing selected-asset workflow; official metadata names verified after a stopped preflight.
One bounded recovery: reuse downloaded coastal scan, fetch missing seaside surface maps.
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
  assert urlparse(r.url).hostname in HOSTS;b=r.read(limit+1)
 assert len(b)<=limit and used+len(b)<=MAX_TOTAL,'Finite download cap reached'
 used+=len(b);time.sleep(.2);return b

def write_descriptor(desc,path):
 reused=path.exists()
 b=path.read_bytes() if reused else get(desc['url'])
 assert not desc.get('md5') or hashlib.md5(b).hexdigest()==desc['md5'],'Upstream checksum mismatch'
 if not reused:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
 return {'path':str(path.relative_to(ROOT)),'url':desc['url'],'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'md5_verified':bool(desc.get('md5')),'reused_bytes':reused}

records=[]
for asset in ['coastal_cliff_04','seaside_rock']:
 folder=ROOT/asset;folder.mkdir(exist_ok=True)
 for tag,endpoint in [('source-info','info'),('source-files','files')]:
  path=folder/(tag+'.json')
  if not path.exists():path.write_text(json.dumps(json.loads(get('https://api.polyhaven.com/'+endpoint+'/'+asset,3000000)),indent=2))
 info=json.loads((folder/'source-info.json').read_text());files=json.loads((folder/'source-files.json').read_text())
 record={'asset_id':asset,'source':'https://polyhaven.com/a/'+asset,'authors':info.get('authors'),'license':'CC0-1.0','license_source':'https://polyhaven.com/license','upstream_dimensions':info.get('dimensions'),'files':[]}
 if asset=='coastal_cliff_04':
  variant=files.get('gltf',{}).get('2k',{}).get('gltf');assert variant and 'url' in variant
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
   record['files'].append(write_descriptor(descriptors.get(uri,{'url':urljoin(variant['url'],uri)}),path))
  record['gltf_nodes']=[n.get('name') for n in doc.get('nodes',[])];record['gltf_materials']=[m.get('name') for m in doc.get('materials',[])]
 else:
  # Exact keys read from persisted official source-files.json, not filename guessing.
  for role,key,res in [('diff','Diffuse','4k'),('nor_gl','nor_gl','4k'),('rough','Rough','4k'),('disp','Displacement','2k')]:
   variants=files.get(key,{}).get(res,{})
   fmt='png' if role=='disp' and 'png' in variants else 'jpg'
   assert fmt in variants,(asset,key,res,'Actual descriptor unavailable')
   desc=variants[fmt];path=folder/Path(unquote(urlparse(desc['url']).path)).name
   row=write_descriptor(desc,path);row.update(role=role,resolution=res,metadata_key=key);record['files'].append(row)
 records.append(record)
manifest={'credit':'Powered by Poly Haven','scope':'Selected cliff scan and rock surface only; station/train remain original. No generated image textures.','assets':records,'downloaded_bytes_this_recovery':used,'max_bytes':MAX_TOTAL,'recovery_from':'8a458ecbc1a345189bef0efb99e1caffb5c3ea1f','corrected_failure':'Official channel keys are Diffuse/Rough/Displacement rather than assumed lowercase aliases.'}
(ROOT/'STORM-ASSET-SOURCES.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
