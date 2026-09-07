"""Read-only R07 baseline using the exact additional R08 diagnostic camera.
Import the observed camera only. Never save the parent scene or import art assets.
"""
import bpy,os,hashlib,json
from pathlib import Path
ROOT=Path('workspaces/glasshouse-terminus').resolve()
BASE=ROOT/'output/g4-coast-r07/g4-full-scene-candidate.blend'
CAND=ROOT/'output/g4-coast-r08/g4-full-scene-candidate.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve()==BASE
assert sha(BASE)=='386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396'
q=json.loads((CAND.parent/'build-report.json').read_text());assert sha(CAND)==q['candidate_sha256']
NAME='QA_R08_cab_joinery';assert NAME not in bpy.data.objects
with bpy.data.libraries.load(str(CAND),link=False) as (src,dst):
 assert NAME in src.objects
 dst.objects=[NAME]
cam=dst.objects[0];assert cam is not None and cam.type=='CAMERA' and cam.parent is None
bpy.context.scene.collection.objects.link(cam)
os.environ['G4_CRAFT_MODE']='baseline'
script=ROOT/'refine_g4_r08_craft.py'
exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
assert sha(BASE)=='386ab4bfb0134988962efaa96d03e883ed557b30843aba6c20de0af9d999c396'
