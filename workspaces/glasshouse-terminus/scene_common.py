"""Native Blender helpers shared by material study and the eventual master scene.
No external modeling framework. Dimensions are metres; Z is up.
"""
import bpy, math, json, time, os, hashlib
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi


def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for data in list(bpy.data.materials):
        bpy.data.materials.remove(data)
    s=bpy.context.scene
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.render.engine='CYCLES';s.cycles.device='CPU'
    s.cycles.samples=32;s.cycles.use_denoising=True
    s.cycles.max_bounces=8;s.cycles.transmission_bounces=6
    s.cycles.transparent_max_bounces=8
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
    s.render.resolution_percentage=100
    s.view_settings.view_transform='AgX'
    s.view_settings.look='AgX - Medium High Contrast'
    s.view_settings.exposure=0;s.view_settings.gamma=1
    s.render.film_transparent=False
    s.render.fps=30;s.frame_start=1;s.frame_end=840
    s.world=bpy.data.worlds.new('Weather_world')
    s.world.use_nodes=True
    world(s,(.12,.16,.22),.5)
    return s


def world(s,color,strength):
    p=s.world.node_tree.nodes.get('Background')
    p.inputs['Color'].default_value=(*color,1)
    p.inputs['Strength'].default_value=strength


def material(name,color,metal=0,rough=.45,transmission=0,coat=0,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission
    p.inputs['IOR'].default_value=1.46
    p.inputs['Coat Weight'].default_value=coat
    p.inputs['Coat Roughness'].default_value=.19
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1)
        p.inputs['Emission Strength'].default_value=emission
    return m


def pbr(name,asset,root,roughness_path=None,normal_strength=.35,coat=0):
    m=material(name,(.5,.5,.5),rough=.4,coat=coat)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    for role,socket in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
        path=Path(root)/(asset+'_'+role+'_2k.jpg')
        if role=='rough' and roughness_path:path=Path(roughness_path)
        image=bpy.data.images.load(str(path.resolve()),check_existing=True)
        if role!='diff':image.colorspace_settings.name='Non-Color'
        tex=n.new('ShaderNodeTexImage');tex.name=role;tex.image=image;tex.interpolation='Linear'
        if role=='nor_gl':
            normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=normal_strength
            l.new(tex.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs[socket])
        else:l.new(tex.outputs['Color'],p.inputs[socket])
    m['source_asset']=asset;m['source_license']='CC0-1.0'
    return m


def mesh(name,verts,faces,mat=None,uv=None,smooth=False):
    data=bpy.data.meshes.new(name+'_mesh');data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
    if mat:data.materials.append(mat)
    if uv:
        layer=data.uv_layers.new(name='UVMap')
        for poly in data.polygons:
            for li in poly.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
    for poly in data.polygons:poly.use_smooth=smooth
    return ob


def cube(name,loc,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    if bevel:
        b=ob.modifiers.new('Machined edge radius','BEVEL');b.width=bevel;b.segments=3
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return ob


def cylinder(name,a,b,radius,mat,vertices=24,radius2=None):
    a=Vector(a);b=Vector(b);d=b-a
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=d.length,location=(a+b)/2)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius2,depth=d.length,location=(a+b)/2)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
    return ob


def curve(name,points,radius,mat,cyclic=False,resolution=2):
    d=bpy.data.curves.new(name+'_curve','CURVE');d.dimensions='3D'
    d.resolution_u=resolution;d.bevel_depth=radius;d.bevel_resolution=2
    spline=d.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    spline.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(ob);d.materials.append(mat)
    return ob


def sweep(name,path,profile,mat,frame='X'):
    """Sweep a real designed cross-section: X=arch, Z=plan curve rail."""
    pts=[Vector(p) for p in path];verts=[];uv=[]
    distance=0
    for i,p in enumerate(pts):
        if i:distance+=(p-pts[i-1]).length
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        if frame=='X':
            u=Vector((1,0,0));v=tangent.cross(u).normalized()
        else:
            v=Vector((0,0,1));u=tangent.cross(v).normalized()
        for j,(a,b) in enumerate(profile):
            verts.append(tuple(p+u*a+v*b));uv.append((j/len(profile),distance))
    k=len(profile);faces=[]
    for i in range(len(pts)-1):
        for j in range(k):faces.append((i*k+j,i*k+(j+1)%k,(i+1)*k+(j+1)%k,(i+1)*k+j))
    faces.extend([tuple(reversed(range(k))),tuple((len(pts)-1)*k+j for j in range(k))])
    return mesh(name,verts,faces,mat,uv)


def ibeam_profile(width=.16,depth=.24,flange=.022,web=.014):
    w=width/2;d=depth/2;t=flange;a=web/2
    return [(-w,-d),(w,-d),(w,-d+t),(a,-d+t),(a,d-t),(w,d-t),(w,d),(-w,d),(-w,d-t),(-a,d-t),(-a,-d+t),(-w,-d+t)]


def lathe(name,profile,loc,mat,segments=64):
    verts=[];uv=[]
    for j,(r,z) in enumerate(profile):
        for i in range(segments):
            a=2*pi*i/segments;verts.append((loc[0]+r*cos(a),loc[1]+r*sin(a),loc[2]+z));uv.append((i/segments,j/max(1,len(profile)-1)))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    return mesh(name,verts,faces,mat,uv,True)


def leaf(name,base,direction,length,width,mat,vein_mat=None):
    """Curved, folded 3D blade with a petiole and readable midrib, not a sprite."""
    base=Vector(base);d=Vector(direction).normalized();side=d.cross(Vector((0,0,1))).normalized()
    if side.length<.1:side=Vector((1,0,0))
    up=side.cross(d).normalized();verts=[];uv=[];mid=[];rows=18;cols=6
    for i in range(rows+1):
        t=i/rows;center=base+d*length*t+Vector((0,0,1))*length*.20*sin(pi*t)-Vector((0,0,1))*length*.12*t*t
        mid.append(tuple(center+up*.009))
        w=width*(sin(pi*t)**.72)*(1-.23*t)+.002
        for j in range(cols+1):
            v=2*j/cols-1
            p=center+side*w*v+up*(.055*length*abs(v)*sin(pi*t)+.014*length*sin(5*pi*t)*v*v)
            verts.append(tuple(p));uv.append((j/cols,t))
    faces=[]
    for i in range(rows):
        for j in range(cols):
            a=i*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
    ob=mesh(name,verts,faces,mat,uv,True)
    sol=ob.modifiers.new('Leaf lamina thickness','SOLIDIFY');sol.thickness=.0014
    if vein_mat:
        curve(name+'_midrib',mid,.0035,vein_mat)
        for i in (4,7,10,13):
            for j in (0,cols):
                a=Vector(verts[i*(cols+1)+cols//2]);b=Vector(verts[(i+2)*(cols+1)+j]);
                curve(name+'_lateral_vein', [tuple(a+up*.003),tuple((a+b)/2+up*.008),tuple(b+up*.003)],.0012,vein_mat)
    return ob


def camera(name,position,target,lens=48,ortho=None):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
    ob.location=position;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.06;data.clip_end=1000
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return ob


def area(name,position,target,power,size,color=(1,.82,.65),size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color
    if size_y:d.shape='RECTANGLE';d.size=size;d.size_y=size_y
    else:d.shape='DISK';d.size=size
    ob=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(ob);ob.location=position
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob


def render(s,cam,path,res=(1280,800),samples=32,frame=1):
    s.camera=cam;s.frame_set(frame);s.cycles.samples=samples
    s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(path)
    t=time.monotonic();bpy.ops.render.render(write_still=True)
    return {'view':cam.name,'file':Path(path).name,'frame':frame,'seconds':time.monotonic()-t,
            'resolution':list(res),'samples':samples,'engine':s.render.engine,'exposure':s.view_settings.exposure,
            'lens_mm':cam.data.lens,'position':list(cam.location),'rotation':list(cam.rotation_euler)}


def save(s,path):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(path).resolve()),compress=True)


def export_glb(path,animations=False):
    # Export only existing source meshes/curves, PBR textures and cameras.
    bpy.ops.export_scene.gltf(filepath=str(Path(path).resolve()),export_format='GLB',
        export_apply=True,export_cameras=True,export_lights=True,
        export_animations=animations,export_yup=True)


def manifest(root,extra):
    root=Path(root)
    record=dict(extra)
    record['source_commit']=os.getenv('GITHUB_SHA','LOCAL')
    record['run_id']=os.getenv('GITHUB_RUN_ID','LOCAL')
    record['blender']=bpy.app.version_string;record['render_device']='CPU'
    record['files']={str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in root.rglob('*') if p.is_file() and p.name!='manifest.json'}
    (root/'manifest.json').write_text(json.dumps(record,indent=2))
