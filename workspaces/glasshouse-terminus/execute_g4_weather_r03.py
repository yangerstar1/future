"""Small explicit execution adapter for the R03 source, with recorded exact bytes.
Geometry Nodes fields are evaluated on their consuming geometry. Shelter rays must
read the already displaced particle Position, not apply the trajectory a second time.
The glass regression uses the existing G3_D01 camera rather than replacing it.
"""
from pathlib import Path
import hashlib,json,os
root=Path(__file__).resolve().parent
source=root/'enhance_g4_weather_r03.py'
text=source.read_text()
a="link(tree,combine.outputs[0],ray.inputs['Source Position'])"
b="link(tree,pos.outputs['Position'],ray.inputs['Source Position'])"
assert text.count(a)==1,'Source differs from reviewed field correction; stop'
text=text.replace(a,b)
a="('G4R03_wet_glass_detail','D-wet-glass.png'"
b="('G3_D01','D-wet-glass.png'"
assert text.count(a)==1,'Source differs from original-camera regression correction; stop'
text=text.replace(a,b)
out=root/'output/g4-r03-weather';out.mkdir(parents=True,exist_ok=True)
(out/'executed-weather-source.py').write_text(text)
(out/'execution-source.json').write_text(json.dumps({'source_file':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'executed_source_sha256':hashlib.sha256(text.encode()).hexdigest(),'explicit_adaptations':['Shelter ray position reads already-animated particle Position, avoiding double application of a field.','Wet glass evidence uses preserved G3_D01 camera.'],'mode':os.environ['G4_WEATHER_MODE'],'source_commit':os.environ.get('GITHUB_SHA'),'not_a_generated_image':True},indent=2))
exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})
