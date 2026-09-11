"""R04 continuous sapphire cylinder blocks with sixteen actual radial bores.

The cylinder axes reuse the browser's documented kinematic approximation. This is
original, dimensioned digital CAD; it is not manufacturer geometry or machining data.
CadQuery 2.8.0 / OpenCascade. Run from the workspace root.
"""
from pathlib import Path
import math, json, hashlib, time
import cadquery as cq
from scipy.spatial import ConvexHull

OUT=Path('generated');OUT.mkdir(exist_ok=True)
S=math.sin;C=math.cos
parts=[];checks=[]
for side in [-1,1]:
    pts=[]
    for angle in [.43,1.0]:
        for r in [.29,.657]:
            for t in [-.139,.139]:
                pts.append((r*S(angle)+t*C(angle),r*C(angle)-t*S(angle)))
    # Common continuous wedge between the two bank faces, not two floating boards.
    hull=ConvexHull(pts);profile=[pts[i] for i in hull.vertices]
    blank=cq.Workplane('XZ').polyline(profile).close().extrude(.90,both=True)
    # The inlet's two planar faces maintain clearance to the crank and the other bank.
    clip=cq.Workplane('XY').box(.82,2.1,1.4).translate((.51,0,.30))
    blank=blank.intersect(clip)
    blank=blank.edges('|Y').fillet(.012)
    if side<0:
        blank=blank.mirror('YZ')
    source_volume=blank.val().Volume()
    holes=[]
    for station in range(8):
        angle=side*(1.00 if station%2==0 else .43)
        y=(station-3.5)*.205+side*.028
        u=(S(angle),0,C(angle));o=(u[0]*.12,y,u[2]*.12)
        cutter=cq.Solid.makeCylinder(.089,.71,cq.Vector(*o),cq.Vector(*u))
        blank=blank.cut(cutter)
        holes.append({'station':station,'axis':u,'origin':[0,y,0],'radius':.089})
    # The end-face clamping pins have real shallow bores aligned with the framework.
    for angle in [.43,1.0]:
        for sy in [-1,1]:
            x=side*S(angle)*.62;z=C(angle)*.62
            blank=blank.cut(cq.Solid.makeCylinder(.027,.12,cq.Vector(x,sy*.94,z),cq.Vector(0,-sy,0)))
    solid=blank.val()
    if not solid.isValid() or len(solid.Solids())!=1:
        raise RuntimeError(f'Invalid/disconnected block on side {side}')
    # Tessellate each CAD face separately and use analytic face normals: hard
    # edges remain hard; the adjacent fillet normals meet the planar faces smoothly.
    positions=[];normals=[];uv=[];indices=[]
    for face in solid.Faces():
        vs,ts=face.tessellate(.0015,.12)
        base=len(positions)//3
        for v in vs:
            positions.extend([round(v.x,6),round(v.y,6),round(v.z,6)])
            n=face.normalAt(v)
            normals.extend([round(n.x,6),round(n.y,6),round(n.z,6)])
            uv.extend([round(v.x,6),round(v.y,6)])
        for tri in ts:indices.extend(base+i for i in tri)
    name='left' if side<0 else 'right'
    step=OUT/f'sapphire-bank-{name}.step'
    cq.exporters.export(solid.scale(10),str(step))  # STEP coordinates are millimetres
    parts.append({'id':f'continuous-sapphire-block-{name}','position':positions,'normal':normals,'uv':uv,'index':indices})
    check={'side':side,'valid':solid.isValid(),'solids':len(solid.Solids()),'radialBores':len(holes),'beforeVolume':source_volume,'afterVolume':solid.Volume(),'faces':len(solid.Faces()),'triangles':len(indices)//3,'axes':holes,'stepSha256':hashlib.sha256(step.read_bytes()).hexdigest()}
    checks.append(check);print(json.dumps(check),flush=True)
(OUT/'sapphire-banks.json').write_text(json.dumps(parts,separators=(',',':')))
(OUT/'sapphire-banks-audit.json').write_text(json.dumps({'cadquery':cq.__version__,'units':'browser: 10 mm per unit; STEP: millimetres','generatorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'AUTHORED_DISPLAY_GEOMETRY_NOT_FACTORY_CAD','parts':checks},indent=2))
