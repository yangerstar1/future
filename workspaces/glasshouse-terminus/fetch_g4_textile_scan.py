"""Download one selected CC0 Poly Haven textile, not website preview renders.
URLs are the actual 4K JPG asset links on the official asset page.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image
import json,hashlib,time
ROOT=Path('workspaces/glasshouse-terminus/output/g4-r05/assets');ROOT.mkdir(parents=True,exist_ok=True)
asset='poly_wool_herringbone';MAX_FILE=20000000;MAX_TOTAL=55000000;total=0
report={'provider':'Poly Haven','credit':'Powered by Poly Haven','asset_id':asset,'asset_page':'https://polyhaven.com/a/poly_wool_herringbone','license':'CC0-1.0','license_source':'https://polyhaven.com/license','authors':{'Rico Cilliers':'Processing','colormass':'Photography'},'intended_surface':'Moss-tinted wool-blend herringbone upholstery in existing station/vehicle. Original image bytes unchanged; tint only in shader.','physical_tile_metres':.30,'physical_scale_note':'Approximate0.3m published asset height, not a laboratory measurement by this project.','files':{}}
for role in ['diff','nor_gl','rough']:
 name=f'{asset}_{role}_4k.jpg';url=f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/{asset}/{name}';dest=ROOT/name
 assert not dest.exists(),'Do not silently overwrite an existing downloaded asset'
 request=Request(url,headers={'User-Agent':'GlasshouseTerminus-ArtStudy/1.0 (public CC0 asset reuse)'})
 try:
  with urlopen(request,timeout=120) as response, dest.open('wb') as out:
   amount=0
   while True:
    chunk=response.read(1048576)
    if not chunk:break
    amount+=len(chunk);total+=len(chunk)
    if amount>MAX_FILE or total>MAX_TOTAL:raise RuntimeError('Finite selected-asset download limit reached')
    out.write(chunk)
 except Exception:
  if dest.exists():dest.unlink()
  raise
 im=Image.open(dest);im.verify();im=Image.open(dest);assert im.size==(4096,4096),(role,im.size)
 record={'file':name,'url':url,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'native_resolution':[4096,4096],'upscaled':False}
 report['files'][role]=record
 if role=='diff':
  vals=list(im.convert('RGB').resize((128,128)).getdata())
  def linear(c):
   v=c/255.;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
  report['linear_rgb_mean']=[sum(linear(p[c]) for p in vals)/len(vals) for c in range(3)]
 report['downloaded_bytes']=total
 (ROOT/'PH-TEXTILE-SOURCE.json').write_text(json.dumps(report,indent=2))
 print('VERIFIED_NATIVE_CC0_SCAN',role,record,flush=True)
 time.sleep(.25)
