"""Continuous Clear display case: smooth loft, hollow cavity, three real ports.

Authored approximation from the registered official Clear photographs. This is
not factory CAD. One browser unit = 10 mm; the exported STEP is in millimetres.
Run from the workspace root with the existing cad/requirements.txt environment.
"""
from pathlib import Path
import hashlib
import json
import cadquery as cq
from OCP.BRepMesh import BRepMesh_IncrementalMesh

if cq.__version__ != '2.8.0':
    raise RuntimeError('Use the locked cad/requirements.txt environment (CadQuery 2.8.0)')

OUT = Path('generated')
OUT.mkdir(exist_ok=True)
# Rolled shoulder and convex flank, within the frozen 44.4 x 57.8 mm envelope.
LEVELS = [
    (-.995, 4.10, 5.44, 3.79, 4.99),
    (-.960, 4.21, 5.56, 3.81, 5.02),
    (-.865, 4.31, 5.66, 3.85, 5.07),
    (-.650, 4.405, 5.75, 3.90, 5.13),
    (-.320, 4.44, 5.78, 3.94, 5.17),
    (.120, 4.42, 5.77, 3.95, 5.19),
    (.430, 4.355, 5.70, 3.94, 5.19),
    (.660, 4.26, 5.60, 3.92, 5.18),
    (.830, 4.145, 5.47, 3.90, 5.17),
    (.905, 4.055, 5.35, 3.88, 5.15),
    (.950, 4.015, 5.29, 3.875, 5.145),
]


def contour(w, h, z):
    """Same eight cubic Bezier arcs as the web's frozen tonneau outline."""
    a, b = w / 2, h / 2
    arcs = [
        [(0,b),(.44*a,b),(.78*a,.97*b),(.88*a,.87*b)],
        [(.88*a,.87*b),(1.01*a,.69*b),(a,.28*b),(a,0)],
        [(a,0),(a,-.32*b),(.99*a,-.74*b),(.84*a,-.88*b)],
        [(.84*a,-.88*b),(.73*a,-.995*b),(.3*a,-b),(0,-b)],
        [(0,-b),(-.3*a,-b),(-.73*a,-.995*b),(-.84*a,-.88*b)],
        [(-.84*a,-.88*b),(-.99*a,-.74*b),(-a,-.32*b),(-a,0)],
        [(-a,0),(-a,.28*b),(-1.01*a,.69*b),(-.88*a,.87*b)],
        [(-.88*a,.87*b),(-.78*a,.97*b),(-.44*a,b),(0,b)],
    ]
    return cq.Wire.assembleEdges([
        cq.Edge.makeBezier([cq.Vector(x, y, z) for x, y in arc])
        for arc in arcs
    ])


print('Lofting the continuous outer and inner walls', flush=True)
outer = cq.Solid.makeLoft([contour(w, h, z) for z,w,h,iw,ih in LEVELS])
inner_sections = [(-1.05,3.79,4.99)] + [(z,iw,ih) for z,w,h,iw,ih in LEVELS] + [(1.00,3.875,5.145)]
inner = cq.Solid.makeLoft([contour(w,h,z) for z,w,h in inner_sections])
case = outer.cut(inner)
# Both separately removable lenses have flat assembly faces. Real recessed
# landings avoid floating curved skins and Boolean overlap with the main shell.
lenses = {
    'front':{'width':3.885,'height':5.15,'surfaceZ':.95,'baseZ':.935,'curved':True},
    'rear':{'width':3.82,'height':5.03,'surfaceZ':-.995,'baseZ':-1.075,'curved':False},
}
for w,h,z,depth in [(3.895,5.16,.934,.30),(3.83,5.04,-1.20,.206)]:
    case = case.cut(cq.Solid.extrudeLinear(contour(w,h,z),[],cq.Vector(0,0,depth)))
ports = []
for x in [-1.11, 0, 1.11]:
    print(f'Cutting the actual crown port at x={x}', flush=True)
    cutter = cq.Solid.makeCylinder(.322, 1.30, cq.Vector(x,-3.50,-.03), cq.Vector(0,1,0))
    case = case.cut(cutter)
    ports.append({'axisOrigin':[x,-3.50,-.03], 'axis':[0,1,0], 'radius':.322, 'length':1.30})
if not case.isValid() or len(case.Solids()) != 1:
    raise RuntimeError('Main sapphire shell must be a single valid connected solid')
case = case.Solids()[0]

# Test actual CAD intersections with all three metal collars/tubes. Their
# positions/radii are the existing production crown interfaces, not guesses
# inferred merely from coincident parents.
clearances=[]
print('Checking solid intersections with all three crown interfaces', flush=True)
for i,x in enumerate([-1.11,0,1.11]):
    cy=-3.18 if i==1 else -3.065
    collar=cq.Solid.makeCylinder(.305,.14,cq.Vector(x,cy+.13,-.03),cq.Vector(0,1,0))
    tube=cq.Solid.makeCylinder(.072,-2.59-(cy+.2),cq.Vector(x,cy+.2,-.03),cq.Vector(0,1,0))
    overlaps=[case.intersect(s).Volume() for s in [collar,tube]]
    if max(overlaps)>1e-8:
        raise RuntimeError(f'Crown {i} intersects the sapphire shell: {overlaps}')
    clearances.append({'crown':i,'collarOverlapVolume':overlaps[0],'tubeOverlapVolume':overlaps[1],'portRadius':.322,'collarRadius':.305,'nominalRadialClearanceMm':.17})
print('Checking the complete lens envelopes against the recessed seats', flush=True)
lens_clearances = []
for name, data in lenses.items():
    top = data['surfaceZ'] + (.125 if data['curved'] else 0)
    envelope = cq.Solid.extrudeLinear(contour(data['width'],data['height'],data['baseZ']),[],cq.Vector(0,0,top-data['baseZ']))
    overlap = case.intersect(envelope).Volume()
    if overlap > 1e-8:
        raise RuntimeError(f'{name} lens intersects the main shell: {overlap}')
    bounds = envelope.BoundingBox()
    lens_clearances.append({'lens':name,'envelopeOverlapVolume':overlap,'axialSeatClearanceMm':.01,'envelopeBounds':[[bounds.xmin,bounds.ymin,bounds.zmin],[bounds.xmax,bounds.ymax,bounds.zmax]]})
bb = case.BoundingBox()

# Absolute chordal deflection avoids massive over-tessellation of the small
# Boolean faces. Keep exact analytic surface normals at every exported vertex.
deflection, angle = .005, .2
print('Meshing with 0.05 mm absolute chordal deflection', flush=True)
BRepMesh_IncrementalMesh(case.wrapped, deflection, False, angle, True)
position, normal, uv, index = [], [], [], []
for face in case.Faces():
    vertices, triangles = face.tessellate(deflection, angle)
    base = len(position)//3
    for v in vertices:
        position.extend(round(a,7) for a in (v.x,v.y,v.z))
        n = face.normalAt(v)
        normal.extend(round(a,7) for a in (n.x,n.y,n.z))
        uv.extend([round(v.x/4.44+.5,7),round(v.y/5.78+.5,7)])
    for t in triangles:
        index.extend(base+i for i in t)
mesh = {'id':'continuous-bored-sapphire-case', 'lenses':lenses, 'position':position, 'normal':normal, 'uv':uv, 'index':index}
mesh_path = OUT/'sapphire-main-case.json'
mesh_path.write_text(json.dumps(mesh,separators=(',',':')))
step_path = OUT/'sapphire-main-case.step'
cq.exporters.export(case.scale(10),str(step_path))
audit = {
    'cadquery':cq.__version__, 'units':'browser: 10 mm per unit; STEP: millimetres',
    'status':'AUTHORED_DISPLAY_GEOMETRY_NOT_FACTORY_CAD',
    'valid':case.isValid(), 'solids':len(case.Solids()), 'volume':case.Volume(),
    'boundsMm':[bb.xlen*10,bb.ylen*10,bb.zlen*10], 'faces':len(case.Faces()),
    'triangles':len(index)//3, 'allEdgeFilletApplied':False,
    'tessellation':{'deflectionMm':deflection*10,'angularToleranceRadians':angle,'relative':False,'normals':'analytic per CAD face'},
    'ports':ports, 'crownIntersections':clearances, 'lensEnvelopeIntersections':lens_clearances,
    'generatorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'meshSha256':hashlib.sha256(mesh_path.read_bytes()).hexdigest(),
    'stepSha256':hashlib.sha256(step_path.read_bytes()).hexdigest(),
    'limitations':['Visible-shape approximation, not OEM manufacturing tolerance','Intersection checks cover crown collars/tubes and conservative lens envelopes only','Web front and rear lenses complete the 21.5 mm frozen measurement boundary','Crown port edges are not filleted; visual inspection remains required'],
}
(OUT/'sapphire-main-case-audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit),flush=True)
