"""Reuse the exact R02 observation renderer with explicit version substitutions."""
import hashlib, os
from pathlib import Path
root = Path(__file__).resolve().parent
source = (root/'render_r02.py').read_bytes()
assert hashlib.sha256(source).hexdigest() == '759ef7259d97df021fd5e1b52fae917dc0979646d78c8e8926b8ea181f4acbb5'
text = source.decode().replace('R02_SPATIAL_STUDY', 'R03_NEAR_PIER_REPAIR').replace('skyfold-r02.blend', 'skyfold-r03.blend')
old = "('O05_LIFT',960,20,False)]"
assert text.count(old) == 1
text = text.replace(old, "('O05_LIFT',960,20,False),('O05_LIFT_R03_DIAGNOSTIC',960,20,False)]")
text = text.replace('R02_OBSERVATIONS_SAVED', 'R03_OBSERVATIONS_SAVED')
compile(text, 'render-resolved.py', 'exec')
(Path(os.environ['SKYFOLD_OUT'])/'render-resolved.py').write_text(text)
exec(compile(text, 'render-resolved.py', 'exec'), globals())
