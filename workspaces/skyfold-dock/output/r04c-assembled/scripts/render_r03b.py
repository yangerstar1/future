"""Original R02 presets, now verifying every camera against the flushed manifest."""
import hashlib,os
from pathlib import Path
root=Path(__file__).resolve().parent
source=(root/'render_r02.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='759ef7259d97df021fd5e1b52fae917dc0979646d78c8e8926b8ea181f4acbb5'
text=source.decode().replace('R02_SPATIAL_STUDY','R03B_NEAR_PIER_REPAIR').replace('skyfold-r02.blend','skyfold-r03b.blend')
old="('O05_LIFT',960,20,False)]";assert text.count(old)==1
text=text.replace(old,"('O05_LIFT',960,20,False),('O05_LIFT_R03_DIAGNOSTIC',960,20,False),('O05_RETURN_LIFT_DIAGNOSTIC',960,20,False)]")
anchor=" label='O02_NEUTRAL' if clay else name"
assert text.count(anchor)==1
check="\n assert max(abs(bpy.data.objects[name].matrix_world[r][c]-man['cameras'][name]['matrix'][r][c]) for r in range(4) for c in range(4))<1e-5,name\n assert abs(bpy.data.objects[name].data.lens-man['cameras'][name]['lens'])<1e-5,name"
text=text.replace(anchor,anchor+check).replace('R02_OBSERVATIONS_SAVED','R03B_OBSERVATIONS_SAVED')
compile(text,'render-resolved.py','exec')
(Path(os.environ['SKYFOLD_OUT'])/'render-resolved.py').write_text(text)
exec(compile(text,'render-resolved.py','exec'),globals())
