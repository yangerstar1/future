"""Bounded G2 intervention, from exact inspected R00 source; not a generic patcher."""
from pathlib import Path
import hashlib,json,difflib
root=Path(__file__).resolve().parent;base=root/'build_scene.py';old=base.read_text()
assert hashlib.sha256(old.encode()).hexdigest()=='3cd8acd68f766d21ea12997368ae4ae5175c4c8fa663b8349106486917c1548a'
s=old
changes=[]
def replace(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a),count)
 s=s.replace(a,b);changes.append({'old':a,'new':b,'occurrences':count})
replace('WIDTH=3200.0','WIDTH=1800.0')
replace('[480,1040,1600,2160,2720]','[300,700,1100,1500]',2)
replace('[18,800,1600,2400,3182]','[18,450,900,1350,1782]')
replace('min(y+760,3200)','min(y+420,1800)')
replace('range(27)','range(15)')
replace('wrap<.43','wrap<.60')
# Correct a source-audited rail-contact defect, not a retrospective visual PASS.
replace('VX,VY,VZ=-168,-288,18.15','VX,VY,VZ=-168,-288,17.935')
replace('for xx in [-1.20,1.20]:','for xx in [-.72,.72]:')
start=s.index('# Low service route connects into a lift;')
end=s.index('# Hero cart occupies',start)
new_route='''# R01: a continuous 1.44m-gauge service route; elevated near platform joins the dock.
route=[(-688,-374,167.18),(-688,70,167.18),(0,205,162.30),(0,1602,162.30)]
def rail_pair(points):
 pts=[Vector(p) for p in points];offsets=[]
 for i,p in enumerate(pts):
  a=(pts[min(i+1,len(pts)-1)]-p) if i==0 else p-pts[i-1]
  b=p-pts[i-1] if i==len(pts)-1 else pts[i+1]-p
  a=Vector((a.x,a.y,0)).normalized();b=Vector((b.x,b.y,0)).normalized()
  n0=Vector((-a.y,a.x,0));n1=Vector((-b.y,b.x,0));bis=(n0+n1).normalized();den=bis.dot(n0)
  assert den>.3,'Rail corner exceeds explicit miter bound'
  offsets.append(bis*(.72/den))
 for side in [-1,1]:tube('Continuous service rail',[tuple(p+side*d) for p,d in zip(pts,offsets)],.065,SILVER,T)
rail_pair(route)
a=Vector(route[1]);b=Vector(route[2]);beam('Service transfer bridge deck',a-Vector((0,0,.565)),b-Vector((0,0,.565)),8,1,DECK,T)
for k in range(1,9):
 p=a.lerp(b,k/9);ground=R-math.sqrt(R*R-p.x*p.x);top=p.z-1.065
 assert top>ground+4 and 0<=p.y<=WIDTH
 box('Transfer bridge rooted foundation',(p.x,p.y,ground+2),(12,12,4),CONCRETE,T,.20)
 box('Transfer bridge support',(p.x,p.y,(top+ground+4)/2),(3.2,4,top-ground-4),DARK,T,.10)
# Guardrails follow the bridge tangent, preserving 1.1m height rather than a scaled railing.
tangent=Vector((b.x-a.x,b.y-a.y,0)).normalized();side=Vector((-tangent.y,tangent.x,0))
for sign in [-1,1]:
 p=a+side*3.8*sign;q=b+side*3.8*sign
 tube('Transfer bridge guardrail',[tuple(p+Vector((0,0,1.04))),tuple(q+Vector((0,0,1.04)))],.055,ORANGE,T)
 for k in range(0,101):
  v=p.lerp(q,k/100);box('Transfer guardrail post',(v.x,v.y,v.z+.5),(.09,.09,1.1),SILVER,T,.01)
'''
s=s[:start]+new_route+s[end:];changes.append({'range_replaced':'lower-rail/elevator/stair block','reason':'Move maintenance vantage and keep an actually continuous, constant-gauge bridge to dock'})
start=s.index('# Limited left-edge framing,')
end=s.index('# Mid-distance cargo,',start)
s=s[:start]+'''# R01 removes seven optional foreground frame/conduit pieces that occluded the hero.
# Core walkway, guardrails, supports, vehicle and freight route remain real geometry.
'''+s[end:];changes.append({'range_removed':'optional near overhead framing only','reason':'R00 O01 actual image showed excessive foreground occlusion'})
anchor='# Sun and neutral skylight;'
pos=s.index(anchor)
s=s[:pos]+'''# Preserve metre-scale maintenance geometry while changing the still-unfrozen G2 vantage.
for o in COL['05_MAINTENANCE'].objects:o.location+=Vector((-520,0,150))
'''+s[pos:]
replace("hero_pos=Vector((-174,-323,18.75));hero_target=Vector((260,1960,995))","hero_pos=Vector((-694,-323,168.75));hero_target=Vector((200,1650,1200))")
replace("camera('O04_CRAFT',(-179,-308,19.35),(-168,-286,18.5),41)","camera('O04_CRAFT',(-695,-302,169.35),(-688,-286,168.5),41)")
replace("camera('O01_HERO',hero_pos,hero_target,18)","camera('O01_HERO',hero_pos,hero_target,18)\ncamera('O01_R00_FIXED',(-174,-323,18.75),(260,1960,995),18)")
anchor='CAMERAS={}'
replace(anchor,"""# Broad opening skylight approximation exposes the cavity rather than hiding it in fog.
ld=bpy.data.lights.new('Opening diffuse daylight','AREA');ld.energy=70000000;ld.shape='DISK';ld.size=3200;ld.color=(.77,.87,1)
lo=bpy.data.objects.new('Opening diffuse daylight',ld);COL['07_LIGHTS'].objects.link(lo);lo.location=(0,-1700,1450);lo.rotation_euler=(Vector((0,900,1450))-lo.location).to_track_quat('-Z','Y').to_euler()
CAMERAS={} """)
replace("'lift_lower':[0,217,17.3],'lift_upper':[0,217,162.0],",'')
replace('R00_PROVISIONAL','R01_PROVISIONAL',2)
replace('skyfold-r00.blend','skyfold-r01.blend',2)
replace('Skyfold Dock R00:','Skyfold Dock R01:')
replace("'output/r00'","'output/r01'")
compile(s,'build_scene_r01.py','exec')
(root/'build_scene_r01.py').write_text(s)
report={'base_build_sha256':hashlib.sha256(old.encode()).hexdigest(),'revised_build_sha256':hashlib.sha256(s.encode()).hexdigest(),'candidate':'R01_PROVISIONAL','changes':changes,'status':'SOURCE_PREPARED_VISUAL_RETEST_REQUIRED'}
(root/'R01-INTERVENTION.json').write_text(json.dumps(report,indent=2))
(root/'R01-SOURCE.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='build_scene.py',tofile='build_scene_r01.py')))
print(json.dumps({k:report[k] for k in ['base_build_sha256','revised_build_sha256','candidate','status']}))
