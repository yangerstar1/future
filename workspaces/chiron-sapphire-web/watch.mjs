import * as THREE from 'three';
import sapphireBanks from './generated/sapphire-banks.json';
import {makeSapphire} from './sapphire.mjs';
import {chassis,suspension,engineHousing,dialSupports,tourbillonSupport,materialFinish,craftTools} from './craft.mjs';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries, mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { PISTONS, SPEC, TAU, solvePiston, handAngles, suspensionOffset } from './mechanics.mjs';
const V=(x=0,y=0,z=0)=>new THREE.Vector3(x,y,z);
const Y=V(0,1,0),Z=V(0,0,1);let serial=0;
/** Original, editable procedural production asset. Hidden architecture is a labelled digital approximation. */
export function makeWatch(){
  const root=new THREE.Group();root.name='Chiron-Sapphire-Clear';
  const registry=[], critical=[],interfaceMeasurements=[];
  const mat={
    rhodium:new THREE.MeshPhysicalMaterial({color:0xc7cbd0,metalness:1,roughness:.225,envMapIntensity:1.15}),
    polished:new THREE.MeshPhysicalMaterial({color:0xe6e9ec,metalness:1,roughness:.105,envMapIntensity:1.1}),
    brushed:new THREE.MeshStandardMaterial({color:0xa3adb6,metalness:1,roughness:.39,envMapIntensity:1.25}),
    dark:new THREE.MeshStandardMaterial({color:0x181c21,metalness:.84,roughness:.31,envMapIntensity:1.1}),
    black:new THREE.MeshStandardMaterial({color:0x080a0e,metalness:.25,roughness:.52}),
    blue:new THREE.MeshPhysicalMaterial({color:0x007ebd,metalness:.48,roughness:.2,clearcoat:.7}),
    lume:new THREE.MeshStandardMaterial({color:0x9ed9f4,metalness:.15,roughness:.3}),
    brass:new THREE.MeshStandardMaterial({color:0xc0a164,metalness:1,roughness:.29}),
    ruby:new THREE.MeshPhysicalMaterial({color:0x931955,metalness:.15,roughness:.12,clearcoat:1}),
    rubber:new THREE.MeshPhysicalMaterial({color:0xc2cdd3,metalness:0,roughness:.4,transparent:true,opacity:.78,depthWrite:false,side:THREE.DoubleSide}),
    rubberDetail:new THREE.MeshStandardMaterial({color:0xa2adb3,metalness:0,roughness:.52}),
    crystal:new THREE.MeshPhysicalMaterial({color:0xe3f1f8,metalness:0,roughness:.025,ior:1.76,transmission:1,thickness:.16,transparent:true,opacity:1,depthWrite:false,side:THREE.FrontSide,envMapIntensity:1.25,clearcoat:1}),
    crystalEdge:new THREE.MeshPhysicalMaterial({color:0xe5f0fa,metalness:0,roughness:.035,transmission:1,thickness:.28,ior:1.76,transparent:true,opacity:1,depthWrite:false,envMapIntensity:1.0}),
    cylinderGlass:new THREE.MeshPhysicalMaterial({color:0xe0f0f4,metalness:0,roughness:.13,transparent:true,opacity:.045,depthWrite:false,side:THREE.DoubleSide,envMapIntensity:.75}),
  };
  // Intentional real-time alpha optical approximation: nested transparent cylinders remain visible.
  // Avoid screen-space transmission hiding one transparent object behind another.
  mat.cover=mat.crystal.clone();mat.cover.transmission=0;mat.cover.opacity=.022;mat.cover.roughness=.055;
  materialFinish(mat);
  for(const [name,m] of Object.entries(mat))m.name=name;
  const batchGroups=[];
  function group(parent,name,batch=false){const g=new THREE.Group();g.name=name;parent.add(g);if(batch)batchGroups.push(g);return g;}
  function mesh(parent,geo,m,name,p=V()){
    const o=new THREE.Mesh(geo,m);o.name=name||`detail-${++serial}`;o.position.copy(p);parent.add(o);
    if(m.transparent)o.renderOrder=m===mat.crystal||m===mat.crystalEdge?30:m===mat.cover?45:m===mat.cylinderGlass?40:5;
    registry.push({id:o.name,parent:parent.name,material:m.name,geometry:geo.type});return o;
  }
  const geoCache=new Map();function cached(key,fn){if(!geoCache.has(key))geoCache.set(key,fn());return geoCache.get(key);}
  function box(parent,x,y,z,w,h,d,m=mat.rhodium,r=.03,name){
    const k=`b:${w}:${h}:${d}:${r}`;
    return mesh(parent,cached(k,()=>new RoundedBoxGeometry(w,h,d,1,Math.min(r,w*.22,h*.22,d*.22))),m,name,V(x,y,z));
  }
  function cyl(parent,x,y,z,r,h,m=mat.rhodium,axis='z',name,segments=48){
    const k=`c:${r}:${h}:${segments}`;const o=mesh(parent,cached(k,()=>new THREE.CylinderGeometry(r,r,h,segments,1)),m,name,V(x,y,z));
    if(axis==='z')o.rotation.x=Math.PI/2;else if(axis==='x')o.rotation.z=Math.PI/2;return o;
  }
  function ring(parent,x,y,z,r,t,m=mat.polished,name,axis='z'){
    const k=`r:${r}:${t}`;const o=mesh(parent,cached(k,()=>new THREE.TorusGeometry(r,t,6,48)),m,name,V(x,y,z));
    if(axis==='y')o.rotation.x=Math.PI/2;else if(axis==='x')o.rotation.y=Math.PI/2;return o;
  }
  function bar(parent,a,b,r,m=mat.polished,name){
    const vec=b.clone().sub(a),o=cyl(parent,0,0,0,r,vec.length(),m,'y',name,16);
    o.position.copy(a).add(b).multiplyScalar(.5);o.quaternion.setFromUnitVectors(Y,vec.normalize());return o;
  }
  function pathTube(parent,pts,r,m=mat.polished,name,closed=false){
    const curve=new THREE.CatmullRomCurve3(pts,closed,'centripetal');
    return mesh(parent,new THREE.TubeGeometry(curve,Math.min(300,Math.max(40,pts.length*3)),r,6,closed),m,name);
  }
  function screw(parent,x,y,z,r=.052,reverse=false){
    const g=group(parent,`screw-${++serial}`);g.position.set(x,y,z);if(reverse)g.rotation.y=Math.PI;
    cyl(g,0,0,-.021,r*.71,.058,mat.brushed,'z','threaded-screw-stem',24);
    cyl(g,0,0,-.007,r*.87,.007,mat.dark,'z','recessed-slot-floor',24);
    const geo=cached(`slotted:${r}`,()=>{
      const s=new THREE.Shape();s.absarc(0,0,r,0,TAU,false);
      const h=new THREE.Path();h.moveTo(-r*.76,-r*.115);h.lineTo(r*.76,-r*.115);h.lineTo(r*.76,r*.115);h.lineTo(-r*.76,r*.115);h.closePath();s.holes.push(h);
      return new THREE.ExtrudeGeometry(s,{depth:.018,bevelEnabled:true,bevelSize:Math.min(.003,r*.07),bevelThickness:.0025,bevelSegments:2,steps:1,curveSegments:16});
    });
    mesh(g,geo,mat.polished,'machined-slotted-screw-head');ring(g,0,0,.003,r*.97,.003,mat.brushed);
    g.rotation.z=(serial%7)*.38;return g;
  }
  function jewel(parent,x,y,z,r=.06,reverse=false){const g=group(parent,'bored-jewel-'+(++serial));g.position.set(x,y,z);if(reverse)g.rotation.y=Math.PI;craftTools(ctx0()).bearing(g,'jewel-chaton-'+serial,0,0,0,r);}
  function contour(w,h){
    const s=new THREE.Shape(),a=w/2,b=h/2;
    s.moveTo(0,b);s.bezierCurveTo(a*.44,b,a*.78,b*.97,a*.88,b*.87);
    s.bezierCurveTo(a*1.01,b*.69,a,b*.28,a,0);
    s.bezierCurveTo(a,-b*.32,a*.99,-b*.74,a*.84,-b*.88);
    s.bezierCurveTo(a*.73,-b*.995,a*.3,-b,0,-b);
    s.bezierCurveTo(-a*.3,-b,-a*.73,-b*.995,-a*.84,-b*.88);
    s.bezierCurveTo(-a*.99,-b*.74,-a,-b*.32,-a,0);
    s.bezierCurveTo(-a,b*.28,-a*1.01,b*.69,-a*.88,b*.87);
    s.bezierCurveTo(-a*.78,b*.97,-a*.44,b,0,b);return s;
  }
  function extrude(parent,shape,depth,z,m,bevel=.025,name){
    const b=Math.min(bevel,depth*.22);const g=new THREE.ExtrudeGeometry(shape,{depth:depth-2*b,bevelEnabled:b>0,bevelSegments:2,steps:1,bevelSize:b,bevelThickness:b,bevelOffset:-b,curveSegments:24});g.translate(0,0,z+b);
    return mesh(parent,g,m,name);
  }
  function rim(parent,w,h,innerW,innerH,d,z,m,bevel=.025,name){const s=contour(w,h);s.holes.push(new THREE.Path(contour(innerW,innerH).getPoints(64).reverse()));return extrude(parent,s,d,z,m,bevel,name);}
  function flatLabel(parent,text,x,y,z,w,h,ink='#151b20',background='#cad1d5'){
    const c=document.createElement('canvas');c.width=768;c.height=192;const ct=c.getContext('2d');ct.fillStyle=background;ct.fillRect(0,0,c.width,c.height);
    ct.fillStyle=ink;ct.textAlign='center';ct.textBaseline='middle';ct.font=`${text==='EB'?'bold ':text==='Chiron'?'italic ':''}${text.length>14?56:88}px ${text==='JACOB & CO.'||text==='Chiron'?'Georgia':'Arial'}`;if(text==='JACOB & CO.'){ct.fillText(text,384,77,730);ct.font='30px Arial';ct.fillText('GENÈVE',384,151);}else ct.fillText(text,384,102,730);
    const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=4;
    const m=new THREE.MeshStandardMaterial({map:tex,metalness:.5,roughness:.3});m.name=`marking:${text}`;
    const o=mesh(parent,new THREE.PlaneGeometry(w,h),m,`inscription-${text}`,V(x,y,z));return o;
  }
  function gear(parent,x,y,z,r,teeth=60,m=mat.rhodium,spokes=7,bore=r>.13?.012:.0075){
    const g=group(parent,`gear-${teeth}-${++serial}`);g.position.set(x,y,z);
    const s=new THREE.Shape(),pitch=r*teeth/(teeth+2),mod=2*pitch/teeth,rootR=pitch-1.25*mod,baseR=pitch*Math.cos(Math.PI/9),invPitch=Math.tan(Math.PI/9)-Math.PI/9;
    const width=rr=>{const aa=Math.acos(Math.min(1,baseR/Math.max(baseR,rr)));return Math.PI/(2*teeth)+invPitch-(Math.tan(aa)-aa);};
    let first=true;const point=(rr,a)=>{const x=Math.cos(a)*rr,y=Math.sin(a)*rr;if(first){s.moveTo(x,y);first=false;}else s.lineTo(x,y);};
    for(let i=0;i<teeth;i++){
      const a=i/teeth*TAU,lo=Math.max(rootR,baseR),step=TAU/teeth;
      point(rootR,a-step*.5);point(rootR,a-width(lo));
      for(let k=0;k<=4;k++){const rr=lo+(r-lo)*k/4;point(rr,a-width(rr));}
      point(r,a);point(r,a+width(r));
      for(let k=3;k>=0;k--){const rr=lo+(r-lo)*k/4;point(rr,a+width(rr));}
      point(rootR,a+width(lo));point(rootR,a+step*.5);
    }s.closePath();
    const hole=new THREE.Path();hole.absarc(0,0,teeth<20?bore:Math.min(r*.73,rootR*.82),0,TAU,true);s.holes.push(hole);
    extrude(g,s,.055,-.0275,m,.004,'toothed-rim');ring(g,0,0,.033,r*.83,.007,mat.polished);
    const hubR=Math.max(r*.15,bore*1.65),tool=craftTools(ctx0());
    tool.washer(g,0,0,0,hubR,bore,.105,m,'z','through-bored-wheel-hub');
    tool.washer(g,0,0,.065,Math.max(r*.072,bore*1.38),bore,.025,mat.polished,'z','wheel-hub-shoulder');
    for(let i=0;i<(teeth<20?0:spokes);i++){const a=i/spokes*TAU,b=box(g,Math.cos(a)*r*.44,Math.sin(a)*r*.44,0,r*.64,r*.049,.045,m,.008);b.rotation.z=a;}
    batchGroups.push(g);return g;
  }
  function ctx0(){return {V,mat,group,mesh,box,cyl,ring,bar,pathTube,screw,jewel,contour,extrude,rim,flatLabel,gear,batchGroups,interfaceMeasurements};}
  const rearCrystal=group(root,'sapphire-back-cover',true);
  const crystalLayer=group(root,'sapphire-case-assembly',true),crystal=group(crystalLayer,'sapphire-shell',true),fixed=group(root,'case-and-crown-carrier',true),straps=group(root,'translucent-rubber-straps',true);
  const carrier=group(root,'suspended-movement');critical.push(carrier);
  const base=group(carrier,'bottom-support',true),power=group(carrier,'winding-and-wheel-train',true),dial=group(carrier,'skeleton-dial',true),eng=group(carrier,'W16-assembly'),tour=group(carrier,'tourbillon-assembly');
  const engStatic=group(eng,'W16-static-cylinders',true),tourStatic=group(tour,'tourbillon-support',true);
  const layers=[{g:rearCrystal,v:V(0,0,-2.3)},{g:crystalLayer,v:V(0,0,3.65)},{g:dial,v:V(0,.15,2.25)},{g:tour,v:V(0,.4,1.55)},{g:eng,v:V(0,-.1,.8)},{g:power,v:V(0,0,-.65)},{g:base,v:V(0,0,-1.6)}];
  const {rear:rearCover}=makeSapphire(ctx0(),crystal);
  crystal.updateMatrixWorld(true);const cb=new THREE.Box3().setFromObject(crystal),sz=cb.getSize(V());
  crystal.scale.set(SPEC.caseWidth/sz.x,SPEC.caseLength/sz.y,SPEC.caseThickness/sz.z);
  crystal.position.sub(cb.getCenter(V()).multiply(crystal.scale));
  root.updateMatrixWorld(true);rearCrystal.attach(rearCover);registry.find(x=>x.id==='rear-crystal').parent=rearCrystal.name;
  rim(fixed,4.02,5.24,3.83,5.03,.11,-.925,mat.rhodium,.022,'titanium-caseback-gasket');
  // Precise visible attachment locations, not a random screw field.
  for(const x of [-1.79,1.79])for(const y of [-2.16,2.14]){screw(crystalLayer,x,y,.934,.065);screw(rearCrystal,x,y,-.988,.056,true);}
  // Continuous curved sapphire strap horns, not protruding metal L brackets.
  // The hidden pin crosses both cheeks AND the rubber end at its true origin.
  for(const sy of [-1,1]){
    const pinY=sy*2.76,pinZ=-.55;
    for(const sx of [-1,1]){
      const h=group(fixed,`sapphire-strap-horn-${sx}-${sy}`);
      h.position.set(sx*1.18,pinY,pinZ);h.rotation.y=Math.PI/2;
      const points=[[-.21,-sy*.30],[-.19,sy*.07],[-.13,sy*.17],[.08,sy*.15],[.15,-sy*.07],[.17,-sy*.30]];
      craftTools(ctx0()).plate(h,'bored-curved-sapphire-horn',points,-.105,.21,mat.crystal,[[0,0,.036]]);
      craftTools(ctx0()).washer(h,0,0,sx*.113,.083,.026,.023,mat.polished,'z','strap-pin-end-bearing');
    }
    cyl(fixed,0,pinY,pinZ,.023,2.64,mat.polished,'x','continuous-strap-springbar',32);
  }
  // Crown collars are attached to the fixed case. Three separate functional targets.
  const crowns=[];
  for(let i=0;i<3;i++){
    const x=(i-1)*1.11,cy=i===1?-3.18:-3.065;
    const cg=group(root,['crown-set-time','crown-wind-two-directions','crown-start-W16'][i]);cg.position.set(x,cy,-.03);crowns.push(cg);critical.push(cg);
    cyl(cg,0,.20,0,.305,.14,mat.polished,'y','crown-collar');craftTools(ctx0()).turned(cg,'sculpted-crown-grip',0,0,0,[[0,-.205],[.18,-.205],[.232,-.17],[.266,-.075],[.27,.015],[.249,.11],[.21,.166],[0,.166]],mat.rhodium,'y');
    for(let j=0;j<24;j++){const a=j/24*TAU;pathTube(cg,[V(Math.cos(a)*.222,-.175,Math.sin(a)*.222),V(Math.cos(a)*.265,-.07,Math.sin(a)*.265),V(Math.cos(a)*.27,.01,Math.sin(a)*.27),V(Math.cos(a)*.227,.15,Math.sin(a)*.227)],.008,mat.polished,'curved-crown-flute');}
    cyl(cg,0,-.215,0,.198,.046,mat.blue,'y','blue-crown-tip');ring(cg,0,-.239,0,.173,.018,mat.polished,'crown-ring','y');
    const mark=flatLabel(cg,'EB',0,-.264,0,.205,.148,'#edf4f7','#0879b1');mark.rotation.x=Math.PI/2;batchGroups.push(cg);
  }
  const frontRibs=group(fixed,'front-case-ribs');for(let k=0;k<7;k++)box(frontRibs,0,-2.705,-.63+k*.135,3.02,.047,.026,mat.rhodium,.008);
  box(fixed,0,-2.805,.37,.85,.07,.21,mat.blue,.035);
  const chiron=flatLabel(fixed,'Chiron',0,-2.847,.38,.73,.15,'#d9e4e9','#0879b1');chiron.rotation.x=Math.PI/2;
  // Original swept strap geometry. Closed cross-section with thickness and softened corners.
  function strap(sign){
    const curve=new THREE.CubicBezierCurve3(V(0,sign*2.76,-.55),V(0,sign*4.45,-.85),V(0,sign*4.12,-2.35),V(0,sign*3.03,-3.18));
    const verts=[],uv=[],idx=[],N=48,M=16;
    for(let i=0;i<=N;i++){const t=i/N,p=curve.getPoint(t),tangent=curve.getTangent(t).normalize(),side=V(1,0,0),up=new THREE.Vector3().crossVectors(side,tangent).normalize();
      const width=1.18-t*.22;
      for(let j=0;j<M;j++){const a=j/M*TAU,c=Math.cos(a),s=Math.sin(a),xx=Math.sign(c)*Math.pow(Math.abs(c),.32)*width,zz=Math.sign(s)*Math.pow(Math.abs(s),.4)*.085;
        const q=p.clone().addScaledVector(side,xx).addScaledVector(up,zz);verts.push(q.x,q.y,q.z);uv.push(j/M,t*4);}
    }
    for(let i=0;i<N;i++)for(let j=0;j<M;j++){const a=i*M+j,b=i*M+(j+1)%M,c=(i+1)*M+j,d=(i+1)*M+(j+1)%M;idx.push(a,b,c,b,d,c);}
    for(let j=1;j<M-1;j++){idx.push(0,j+1,j);idx.push(N*M,N*M+j,N*M+j+1);}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();mesh(straps,geo,mat.rubber,`rubber-strap-${sign}`);
    for(let i=2;i<=14;i++){const t=i/17,p=curve.getPoint(t),tan=curve.getTangent(t),up=new THREE.Vector3().crossVectors(V(1,0,0),tan).normalize();p.addScaledVector(up,.087);bar(straps,p.clone().add(V(-.88+t*.12,0,0)),p.clone().add(V(.88-t*.12,0,0)),.012,mat.rubberDetail,'moulded-strap-channel');}
    return curve;
  }
  strap(1);strap(-1);
  const buckle=group(straps,'titanium-deployant-clasp');buckle.position.set(0,-3.03,-3.18);buckle.rotation.x=-.56;
  for(const x of [-.91,.91])box(buckle,x,0,0,.13,.68,.14,mat.polished,.045);
  for(const y of [-.29,.29])box(buckle,0,y,0,1.93,.13,.14,mat.polished,.035);
  for(const x of [-.52,.52]){
    const ear=group(buckle,'deployant-proximal-hinge-ear');ear.position.x=x;ear.rotation.y=Math.PI/2;
    craftTools(ctx0()).plate(ear,'bored-folding-blade-ear',[[-.076,.19],[-.076,.37],[.204,.37],[.204,.19]],-.065,.13,mat.brushed,[[0,.28,.060]]);
    const shape=new THREE.Shape();shape.moveTo(x-.064,.25);shape.lineTo(x+.064,.25);shape.lineTo(x+.067,.90);shape.quadraticCurveTo(x+.061,1.12,x+.045,1.20);shape.lineTo(x-.045,1.20);shape.quadraticCurveTo(x-.06,1.12,x-.067,.90);shape.closePath();
    extrude(buckle,shape,.073,-.198,mat.brushed,.014,'deployant-folding-blade');
    cyl(buckle,x,1.17,-.148,.063,.12,mat.polished,'x','deployant-distal-hinge');
  }
  bar(buckle,V(-.58,1.17,-.148),V(.58,1.17,-.148),.036,mat.polished,'deployant-continuous-hinge-pin');
  box(buckle,0,1.15,-.163,1.22,.20,.115,mat.brushed,.027,'deployant-return-crossmember');
  for(const x of [-.67,.67]){
    box(buckle,x,.02,.071,.21,.42,.09,mat.brushed,.028,'deployant-release-shoulder');
    screw(buckle,x,.18,.128,.040);
  }
  bar(buckle,V(-.89,.28,0),V(.89,.28,0),.043,mat.polished,'clasp-hinge');box(buckle,0,.08,.08,.095,.41,.055,mat.rhodium,.02,'buckle-tongue');
  const ctx=ctx0();
  const tooling=craftTools(ctx);
  const {wheels,trainPairs,motionWorks}=chassis(ctx,base,power);
  const {springs,springMounts,mountMoving,interfaces}=suspension(ctx,root,carrier,fixed);
  // W16: four explicit banks × four cylinders, eight shared crankpins, sixteen independently constrained rods.
  eng.position.set(0,-1.15,.02);const crank=group(eng,'crankshaft');const pistons=[],rods=[];
  for(let station=0;station<8;station++){
    const d={...PISTONS[station*2],y:(station-3.5)*.205},px=d.radius*Math.cos(d.phase),pz=d.radius*Math.sin(d.phase);
    cyl(crank,px,d.y,pz,.0195,.130,mat.polished,'y',d.sharedPin,32);
    for(const off of [-.0705,.0705]){
      const a=Math.atan2(pz,px),pts=[];
      for(let j=0;j<=12;j++){const t=a-Math.PI/2+j/12*Math.PI;pts.push([px+Math.cos(t)*.030,pz+Math.sin(t)*.030]);}
      for(let j=0;j<=12;j++){const t=a+Math.PI/2+j/12*Math.PI;pts.push([Math.cos(t)*.041,Math.sin(t)*.041]);}
      const web=tooling.plate(crank,'machined-flat-crank-web',pts,-.009,.018,mat.brushed);web.rotation.x=Math.PI/2;web.position.y=d.y+off;
      cyl(crank,0,d.y+off,0,.026,.030,mat.polished,'y','main-journal',32);
    }
    if(station<7)cyl(crank,0,d.y+.1025,0,.026,.034,mat.polished,'y','shaft-segment',24);
  }
  for(const s of [-1,1])cyl(crank,0,s*.859,0,.026,.148,mat.polished,'y','crank-end-journal-'+s,32);
  batchGroups.push(crank);critical.push(crank);
  for(const data of sapphireBanks){
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(data.position,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(data.normal,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(data.uv,2));g.setIndex(data.index);
    mesh(engStatic,g,mat.cylinderGlass,data.id);
  }
  for(const d of PISTONS){
    const pg=group(eng,d.id),rg=group(eng,`connecting-rod-${d.id}`);
    cyl(pg,0,0,0,.078,.105,mat.rhodium,'y','piston-skirt',32);cyl(pg,0,.055,0,.078,.016,mat.polished,'y','piston-head',32);
    ring(pg,0,.026,0,.077,.0035,mat.dark,'piston-groove','y');ring(pg,0,.041,0,.079,.003,mat.polished,'piston-ring','y');
    cyl(pg,0,0,0,.021,.16,mat.polished,'z','wrist-pin',20);
    pg.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V(Math.cos(d.angle),0,-Math.sin(d.angle)),V(Math.sin(d.angle),0,Math.cos(d.angle)),V(0,-1,0)));
    box(rg,0,0,d.length*.5,.038,.018,d.length-.030,mat.rhodium,.005,'connecting-rod-web');
    for(const x of [-.019,.019])box(rg,x,0,d.length*.5,.009,.035,d.length-.055,mat.polished,.003,'connecting-rod-forged-flange');
    for(const z of [0,d.length]){
      tooling.washer(rg,0,0,z,z===0?.043:.036,.024,.036,mat.polished,'y','bored-rod-eye');
      tooling.washer(rg,0,0,z,.0238,.0218,.031,mat.brass,'y','rod-bearing-bush');
    }
    for(const x of [-.032,.032])cyl(rg,x,0,-.018,.007,.047,mat.polished,'y','big-end-cap-bolt',12);
    pistons.push({g:pg,d});rods.push({g:rg,d});batchGroups.push(pg,rg);critical.push(pg,rg);
  }
  const {turbos,journals,mounts}=engineHousing(ctx,eng,engStatic,PISTONS);
  box(engStatic,0,-.976,.194,.73,.18,.064,mat.rhodium,.016,'engine-maker-plate');flatLabel(engStatic,'JACOB & CO.',0,-.976,.230,.68,.118);flatLabel(engStatic,'GENÈVE',0,-1.035,.232,.28,.032);
  // Skeleton dial and forked hands at the observed upper-center position.
  const dialY=.60;
  const arc=[];for(let i=0;i<=128;i++){const a=.12+i/128*(TAU-.24);arc.push(V(Math.sin(a)*1.14,dialY+Math.cos(a)*1.14,.64));}
  pathTube(dial,arc,.023,mat.polished,'open-dial-minute-ring');
  for(let i=1;i<=11;i++){
    const a=i/12*TAU,x=Math.sin(a),y=Math.cos(a);
    const idx=box(dial,x*1.094,dialY+y*1.094,.697,.078,.286,.045,mat.rhodium,.012,`index-${i}`);idx.rotation.z=-a;
    const blue=box(dial,x*1.099,dialY+y*1.099,.724,.054,.227,.015,mat.blue,.005,`blue-index-${i}`);blue.rotation.z=-a;
  }
  for(const a of [Math.PI*.33,Math.PI*.70,Math.PI*1.29,Math.PI*1.66]){
    const u=V(Math.sin(a),Math.cos(a),0),n=V(u.y,-u.x,0),pts=[];
    for(const [r,t] of [[.42,-.108],[.98,-.092],[1.165,-.052],[1.165,.052],[.98,.092],[.42,.108]])pts.push([u.x*r+n.x*t,dialY+u.y*r+n.y*t]);
    tooling.plate(dial,'milled-dial-bridge-arm',pts,.608,.052,mat.rhodium);
    bar(dial,V(u.x*.13,dialY+u.y*.13,.633),V(u.x*.48,dialY+u.y*.48,.633),.023,mat.rhodium,'hub-to-annular-bridge-spoke');
  }
  tooling.washer(dial,0,dialY,.634,.532,.438,.052,mat.rhodium,'z','central-open-bearing-bridge');
  cyl(dial,0,dialY,.704,.175,.053,mat.polished);ring(dial,0,dialY,.738,.128,.008,mat.dark);
  box(dial,0,-.306,.696,.36,.26,.055,mat.rhodium,.038,'EB-medallion');flatLabel(dial,'EB',0,-.307,.728,.279,.176,'#0085c6','#d7dee2');
  dialSupports(ctx,dial,power);
  function hand(length,name){const g=group(carrier,name);g.position.set(0,dialY,name==='minute-hand'?.819:.777);
    const s=new THREE.Shape();s.moveTo(-.063,-.16);s.lineTo(-.063,.21);s.lineTo(-.055,length*.70);s.lineTo(0,length);s.lineTo(.055,length*.70);s.lineTo(.063,.21);s.lineTo(.063,-.16);s.closePath();
    const hole=new THREE.Path();hole.moveTo(-.021,.20);hole.lineTo(0,length*.73);hole.lineTo(.021,.2);hole.closePath();s.holes.push(hole);
    extrude(g,s,.021,0,mat.polished,.008,name+'-skeleton');box(g,0,length*.81,.034,.039,length*.25,.012,mat.blue,.005,'hand-luminous-tip');batchGroups.push(g);critical.push(g);return g;
  }
  const hour=hand(.85,'hour-hand'),minute=hand(1.12,'minute-hand');cyl(dial,0,dialY,.874,.072,.062,mat.rhodium);cyl(dial,0,dialY,.908,.034,.012,mat.polished);
  // Small fuel-gauge-shaped timekeeping reserve at nine o'clock.
  const gauge=group(dial,'power-reserve-gauge');gauge.position.set(-1.20,-.28,.49);cyl(gauge,0,0,0,.25,.055,mat.dark);ring(gauge,0,0,.038,.235,.016,mat.polished);
  for(let i=0;i<11;i++){const a=(-.72+i/10*1.5)*Math.PI,xx=Math.cos(a)*.184,yy=Math.sin(a)*.184;const t=box(gauge,xx,yy,.038,.032,.07,.01,i<3?mat.ruby:mat.lume,.005);t.rotation.z=a-Math.PI/2;}
  cyl(dial,-1.20,-.28,.426,.034,.22,mat.polished,'z','reserve-gauge-arbor');bar(dial,V(-1.20,-.28,.388),V(-1.33,-.28,.538),.036,mat.dark,'reserve-gauge-bearing-foot');
  const reserveHand=group(gauge,'reserve-pointer');batchGroups.push(reserveHand);box(reserveHand,0,.083,.057,.018,.17,.016,mat.polished,.004);cyl(gauge,0,0,.061,.027,.02,mat.polished);
  // Inclined flying tourbillon: stationary protective frame, rotating cage, independent oscillating balance.
  tour.position.set(0,1.78,.33);tour.rotation.x=Math.PI/6;tour.scale.setScalar(1.38);
  ring(tourStatic,0,0,-.105,.386,.014,mat.dark,'tourbillon-bearing-seat');
  tourbillonSupport(ctx,tourStatic);
  const cage=group(tour,'flying-tourbillon-cage');
  const crownWheel=gear(cage,0,0,-.079,.337,62,mat.brass,5,.074);
  tooling.turned(cage,'hollow-revolving-cage-journal',0,0,0,[[.0534,-.212],[.070,-.212],[.072,-.207],[.072,-.032],[.102,-.026],[.104,-.022],[.102,-.018],[.013,-.018],[.013,-.126],[.0534,-.127],[.0534,-.212]],mat.polished);

  // Machined, skeletonized rotating cage: seven slender angular arms and a
  // chamfered perimeter. There is no stationary upper bridge on this flying cage.
  tooling.washer(cage,0,0,.152,.353,.331,.026,mat.rhodium,'z','machined-cage-perimeter');
  tooling.washer(cage,0,0,-.056,.359,.337,.025,mat.brushed,'z','lower-cage-perimeter');
  for(let i=0;i<7;i++){
    const a=i/7*TAU,points=[],inset=[];
    for(const [r,t] of [[.078,-.125],[.170,-.095],[.190,-.235],[.337,-.12],[.337,-.055],[.212,-.16],[.184,.050],[.078,.135]])points.push([Math.cos(a+t)*r,Math.sin(a+t)*r]);
    tooling.plate(cage,'machined-cage-radial-arm',points,.140,.027,mat.rhodium);
    for(const [r,t] of [[.176,-.01],[.20,-.201],[.332,-.096],[.332,-.074],[.208,-.18],[.182,.012]])inset.push([Math.cos(a+t)*r,Math.sin(a+t)*r]);
    tooling.plate(cage,'blue-cage-arm-inlay',inset,.168,.004,mat.blue);
    const x=Math.cos(a-.087)*.340,y=Math.sin(a-.087)*.340;
    tooling.post(cage,'cage-through-pillar',x,y,-.058,.150,.014);screw(cage,x,y,.174,.020);
  }
  tooling.turned(cage,'cage-central-journal-cap',0,0,.173,[[.013,-.032],[.070,-.032],[.087,-.012],[.091,.004],[.084,.027],[.065,.037],[.0575,.037],[.0575,.008],[.013,.008],[.013,-.032]],mat.polished);
  tooling.washer(cage,0,0,.137,.082,.059,.015,mat.blue,'z','blue-journal-cap-seat');
  const balance=group(cage,'3Hz-balance-wheel');ring(balance,0,0,.048,.255,.016,mat.brass);ring(balance,0,0,.048,.226,.008,mat.brass);
  for(let i=0;i<4;i++){const a=i/4*TAU;bar(balance,V(0,0,.048),V(Math.cos(a)*.252,Math.sin(a)*.252,.048),.010,mat.rhodium,'balance-spoke');cyl(balance,Math.cos(a)*.252,Math.sin(a)*.252,.065,.02,.017,mat.polished);}
  // Bounded elastic-display approximation: inner spring end follows the balance; outer end stays pinned to the cage.
  const hairN=192,hairM=6,hairGeo=new THREE.BufferGeometry(),hairPos=new Float32Array((hairN+1)*(hairM+1)*3),hairNormal=new Float32Array(hairPos.length),hairUV=new Float32Array((hairN+1)*(hairM+1)*2),hairIdx=[];
  for(let i=0;i<=hairN;i++)for(let j=0;j<=hairM;j++){const k=i*(hairM+1)+j;hairUV[k*2]=i/hairN;hairUV[k*2+1]=j/hairM;if(i<hairN&&j<hairM){const n=k+hairM+1;hairIdx.push(k,k+1,n,k+1,n+1,n);}}
  hairGeo.setAttribute('position',new THREE.BufferAttribute(hairPos,3).setUsage(THREE.DynamicDrawUsage));hairGeo.setAttribute('normal',new THREE.BufferAttribute(hairNormal,3).setUsage(THREE.DynamicDrawUsage));hairGeo.setAttribute('uv',new THREE.BufferAttribute(hairUV,2));hairGeo.setIndex(hairIdx);
  const hair=mesh(cage,hairGeo,mat.blue,'live-balance-hairspring');hair.userData.keepDynamicGeometry=true;hair.frustumCulled=false;let lastHairAngle=Infinity;
  function updateHair(theta){if(theta===lastHairAngle)return;lastHairAngle=theta;for(let i=0;i<=hairN;i++){const t=i/hairN,r=.025+t*.178,a=t*TAU*4.5+theta*(1-t)**2,da=TAU*4.5-2*theta*(1-t),co=Math.cos(a),si=Math.sin(a),dx=.178*co-r*si*da,dy=.178*si+r*co*da,norm=Math.hypot(dx,dy),nx=-dy/norm,ny=dx/norm;for(let j=0;j<=hairM;j++){const q=j/hairM*TAU,cs=Math.cos(q),sn=Math.sin(q),k=(i*(hairM+1)+j)*3;hairPos[k]=r*co+.0037*nx*cs;hairPos[k+1]=r*si+.0037*ny*cs;hairPos[k+2]=.103+.0037*sn;hairNormal[k]=nx*cs;hairNormal[k+1]=ny*cs;hairNormal[k+2]=sn;}}hairGeo.attributes.position.needsUpdate=true;hairGeo.attributes.normal.needsUpdate=true;}
  updateHair(0);cyl(cage,-.203,0,.103,.010,.030,mat.polished,'z','hairspring-outer-stud',16);
  const pallet=group(cage,'pallet-fork');pallet.position.set(.075,-.065,.014);box(pallet,0,-.02,0,.02,.095,.015,mat.polished,.004);bar(pallet,V(0,-.05,0),V(.043,-.073,0),.008,mat.polished,'pallet-arm');bar(pallet,V(0,-.05,0),V(-.021,-.08,0),.008,mat.polished,'pallet-arm');box(pallet,.043,-.073,.014,.014,.028,.014,mat.ruby,.003);box(pallet,-.021,-.08,.014,.014,.026,.014,mat.ruby,.003);cyl(cage,.075,-.065,.040,.019,.04,mat.polished,'z','pallet-pivot',16);batchGroups.push(pallet);

  tooling.plate(cage,'escapement-bearing-bridge',[[-.019,-.307],[.288,-.208],[.319,-.120],[.184,-.034],[.048,-.024],[-.023,-.104]],-.086,.031,mat.brushed,[[.16,-.133,.018],[.075,-.065,.011]]);
  for(const [x,y] of [[.16,-.133],[.075,-.065]]){cyl(cage,x,y,-.01,.006,.15,mat.polished,'z','escapement-through-pivot',16);tooling.washer(cage,x,y,-.094,.025,.012,.02,mat.ruby);}
  cyl(cage,0,0,.10,.011,.31,mat.polished,'z','balance-journal-arbor',16);cyl(balance,0,0,.048,.025,.10,mat.rhodium,'z','balance-collet',24);cyl(balance,.025,0,.103,.006,.018,mat.polished,'z','hairspring-inner-stud',12);
  const escape=gear(cage,.16,-.133,-.009,.104,15,mat.rhodium,4);tooling.washer(cage,0,0,.200,.056,.014,.033,mat.polished,'z','cage-central-bearing-setting');cyl(cage,0,0,.221,.018,.035,mat.polished,'z','faceted-balance-end-cap',12);
  pathTube(tourStatic,[V(-.39,-.30,-.11),V(-.49,.08,.04),V(-.36,.39,.04),V(0,.5,.04),V(.36,.39,.04),V(.49,.08,.04),V(.39,-.30,-.11)],.018,mat.polished,'tourbillon-protective-arch');
  batchGroups.push(cage,balance);critical.push(cage,balance);
  // Telescoping display connection maintains fixed crown to moving mechanism attachment.
  const couplings=[];
  for(let i=0;i<3;i++){
    const x=(i-1)*1.11,cy=i===1?-3.18:-3.065;
    cyl(fixed,x,(cy+.2-2.59)/2,-.03,.072,-2.59-(cy+.2),mat.brushed,'y','case-crown-tube-'+i,32);
    tooling.washer(fixed,x,-2.60,-.03,.120,.070,.068,mat.polished,'y','crown-tube-flange-'+i);
    const a=V(x,-2.59,-.03),b=V(x,-2.09,-.24),o=bar(root,a,b,.034,mat.polished,'crown-articulated-display-stem-'+i);
    couplings.push({o,a,b,length:a.distanceTo(b)});
  }
  const locations={engine:eng,tourbillon:tour};
  // Bake only static meshes within each explicitly registered logical group. Never cross moving parents.
  const batchSet=new Set(batchGroups);
  function batch(g){
    const lists=new Map();
    const visit=(o)=>{for(const c of [...o.children]){
      if((c!==g&&batchSet.has(c))||c.userData.keepDynamicGeometry)continue;
      if(c.isMesh){c.updateWorldMatrix(true,false);g.updateWorldMatrix(true,false);
        const matrix=new THREE.Matrix4().copy(g.matrixWorld).invert().multiply(c.matrixWorld);
        let geo=c.geometry.clone();geo.applyMatrix4(matrix);if(geo.index)geo=geo.toNonIndexed();
        // Compatible attribute set; generated geometries all have position/normal/uv.
        for(const n of Object.keys(geo.attributes))if(!['position','normal','uv'].includes(n))geo.deleteAttribute(n);
        if(!geo.attributes.uv)geo.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(geo.attributes.position.count*2),2));
        const key=c.material.uuid;if(!lists.has(key))lists.set(key,{mat:c.material,geos:[],order:c.renderOrder});lists.get(key).geos.push(geo);o.remove(c);
      }else visit(c);
    }};visit(g);
    for(const item of lists.values()){const joined=mergeGeometries(item.geos,false);if(!joined)throw new Error('Static geometry batching failed');const geo=mergeVertices(joined,1e-6);joined.dispose();const m=new THREE.Mesh(geo,item.mat);m.name=`${g.name}:${item.mat.name}`;m.renderOrder=item.order;g.add(m);for(const x of item.geos)x.dispose();}
  }
  root.updateMatrixWorld(true);
  // Children first; excluded dynamic subgroups keep their node identity and pivots.
  for(const g of [...batchGroups].reverse())batch(g);
  // Identical machined pistons/rods share GPU geometry, but their sixteen
  // independently solved node transforms and IDs are retained and audited.
  const instanceSets=[],instanceAudit=[];
  function instanceFamily(family,items){
    const groups=items.map(x=>x.g),first=groups[0],plan=[];
    for(const template of first.children.filter(o=>o.isMesh)){
      const matches=groups.map(g=>g.children.find(o=>o.isMesh&&o.material===template.material));
      let delta=0,compatible=true;
      for(const o of matches){
        if(!o||o.geometry.index?.count!==template.geometry.index?.count){compatible=false;break;}
        for(const name of ['position','normal','uv']){
          const a=o.geometry.attributes[name]?.array,b=template.geometry.attributes[name]?.array;
          if(a?.length!==b?.length){compatible=false;break;}
          for(let i=0;i<a.length;i++)delta=Math.max(delta,Math.abs(a[i]-b[i]));
        }
        const ia=o.geometry.index?.array,ib=template.geometry.index?.array;
        if(ia&&ib)for(let i=0;i<ia.length;i++)if(ia[i]!==ib[i]){compatible=false;break;}
      }
      if(!compatible||delta>1e-5){instanceAudit.push({family,status:'RETAIN_INDIVIDUAL_GEOMETRY',delta});return;}
      plan.push({template,matches,delta});
    }
    for(const {template,matches,delta} of plan){
      const mesh=new THREE.InstancedMesh(template.geometry,template.material,groups.length);mesh.name=family+':'+template.material.name;
      mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;
      mesh.userData.instanceNodeIds=groups.map(g=>g.name);mesh.userData.family=family;mesh.renderOrder=template.renderOrder;
      eng.add(mesh);for(const old of matches){old.parent.remove(old);if(old.geometry!==template.geometry)old.geometry.dispose();}
      instanceSets.push({mesh,groups});instanceAudit.push({family,material:template.material.name,count:groups.length,delta,status:'IDENTICAL_GEOMETRY_REUSED'});
    }
  }
  instanceFamily('sixteen-pistons',pistons);instanceFamily('sixteen-rods',rods);
  root.traverse(o=>{if(o.isMesh){const optical=o.material.transparent||o.material.transmission>0;o.castShadow=!optical;o.receiveShadow=!optical;}});
  root.updateMatrixWorld(true);
  const rest=layers.map(({g,v})=>({g,v,p:g.position.clone(),q:g.quaternion.clone()}));
  const handRest=[hour.position.clone(),minute.position.clone()];
  const assembledCaseBox=new THREE.Box3().setFromObject(crystal).expandByObject(rearCrystal),caseSize=assembledCaseBox.getSize(V());
  const passport={units:'1 scene unit = 10 mm',caseMeasuredMm:caseSize.toArray().map(x=>x*10),caseSpecificationMm:[44.4,57.8,21.5],measurementBoundary:'sapphire shell incl. front and back; excludes crowns, strap and lugs',parts:registry,
    pistons:PISTONS,instanceAudit,trainPairs,motionWorks:motionWorks.description,interfaceMeasurements,suspensionInterfaces:interfaces,crankJournalStations:journals,engineMounts:mounts,revision:'R05',approximation:'Original visible digital reconstruction. No factory CAD or 578-part manufacturing equivalence. Layered physical transmission and transparent cylinder approximation for nested sapphire; hidden gearing, rod geometry, phases and coupling are digital approximations.'};
  root.userData={identity:'BU210.80.AA.AA.B — Clear visual baseline',units:'10 mm',source:'Original procedural geometry; see REFERENCES.md',approximation:passport.approximation};
  function update(state){
    const bob=suspensionOffset(state.suspensionTime);carrier.position.z=bob;
    for(const r of rest){r.g.position.copy(r.p).addScaledVector(r.v,state.explode);r.g.quaternion.copy(r.q);}
    hour.position.copy(handRest[0]).addScaledVector(V(0,.15,2.25),state.explode);minute.position.copy(handRest[1]).addScaledVector(V(0,.15,2.25),state.explode);
    rearCrystal.visible=crystalLayer.visible=!state.crystalOff&&state.selection==='all';fixed.visible=straps.visible=state.selection==='all';springMounts.visible=state.selection==='all';for(const c of crowns)c.visible=state.selection==='all';
    for(const g of [base,power,dial,hour,minute,mountMoving])g.visible=state.selection==='all';
    eng.visible=state.selection==='all'||state.selection==='engine';tour.visible=state.selection==='all'||state.selection==='tourbillon';for(const {o} of couplings)o.visible=state.selection==='all'&&state.explode<.03;
    crank.rotation.y=-state.engineTheta;
    for(const {g,d} of pistons){const p=solvePiston(d,state.engineTheta);g.position.fromArray(p.p);}
    for(const {g,d} of rods){const p=solvePiston(d,state.engineTheta);g.position.fromArray(p.c);g.quaternion.setFromUnitVectors(Z,V(...p.p).sub(V(...p.c)).normalize());}
    for(const {mesh,groups} of instanceSets){groups.forEach((g,i)=>{g.updateMatrix();mesh.setMatrixAt(i,g.matrix);});mesh.instanceMatrix.needsUpdate=true;}
    for(const g of turbos)g.rotation.z=state.engineTheta*2.2;
    const a=handAngles(state.clockSeconds);hour.rotation.z=a.hour;minute.rotation.z=a.minute;reserveHand.rotation.z=(.72-state.clockEnergy*1.5)*Math.PI;
    cage.rotation.z=state.balanceTime/SPEC.cagePeriod*TAU;balance.rotation.z=Math.sin(state.balanceTime*TAU*SPEC.balanceHz)*2.4;updateHair(balance.rotation.z);pallet.rotation.z=.08*Math.tanh(Math.sin(state.balanceTime*TAU*SPEC.balanceHz)*7);escape.rotation.z=Math.floor(state.balanceTime*6)/15*TAU;
    motionWorks.update(state.clockSeconds);
    for(const {g,rate,domain,offset=0} of wheels)g.rotation.z=offset+(domain==='engine'?state.engineTheta:state.balanceTime)*rate;
    for(const s of springs)s.update(bob);
    for(const {o,a,b,length} of couplings){const cb=b.clone().add(V(0,0,bob)),delta=cb.clone().sub(a);o.position.copy(a).add(cb).multiplyScalar(.5);o.quaternion.setFromUnitVectors(Y,delta.normalize());o.scale.y=a.distanceTo(cb)/length;}
  }
  function connectionReport(){root.updateMatrixWorld(true);return pistons.map(({g,d},i)=>{const rod=rods[i].g,start=rod.localToWorld(V()),end=rod.localToWorld(V(0,0,d.length)),pin=g.getWorldPosition(V()),crankpin=crank.localToWorld(V(d.radius*Math.cos(d.phase),d.y,d.radius*Math.sin(d.phase)));return {id:d.id,smallEndResidual:end.distanceTo(pin)/d.length,bigEndResidual:start.distanceTo(crankpin)/d.length,worldRodLength:start.distanceTo(end)};});}
  function instanceReport(){return instanceSets.map(({mesh,groups})=>{const m=new THREE.Matrix4();let maxDelta=0;groups.forEach((g,i)=>{mesh.getMatrixAt(i,m);g.updateMatrix();for(let j=0;j<16;j++)maxDelta=Math.max(maxDelta,Math.abs(m.elements[j]-g.matrix.elements[j]));});return {family:mesh.userData.family,material:mesh.material.name,ids:mesh.userData.instanceNodeIds,count:mesh.count,maxTransformResidual:maxDelta};});}
  function structuralReport(){return {revision:'R05',instanceBindings:instanceReport(),motionWorks:motionWorks.description,interfaceMeasurements,trainPairs:trainPairs.map(p=>({...p,residual:Math.abs(Math.hypot(p.centerB[0]-p.centerA[0],p.centerB[1]-p.centerA[1])-p.pitchA-p.pitchB)})),crankpinRadius:.0195,rodBushBoreRadius:.0218,rodEyeBoreRadius:.024,rodBushOuterRadius:.0238,crankWebAxialHalfExtent:.009,crankWebAxialOffset:.0705,pistonRadius:.082,boreRadius:.089,boreRange:[.312,.652],suspension:springs.map(s=>s.report?.()??{registered:true}),warning:'Local geometry/kinematic checks do not certify absence of every collision or factory topology.'};}
  function assemblyError(){let pos=0,rot=0;for(const r of rest){pos=Math.max(pos,r.g.position.distanceTo(r.p));rot=Math.max(rot,r.g.quaternion.angleTo(r.q));}return {position:pos,rotationDegrees:rot*180/Math.PI};}
  function dispose(){const gs=new Set(),ms=new Set(),ts=new Set();root.traverse(o=>{if(o.geometry)gs.add(o.geometry);if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])ms.add(m);}});for(const g of gs)g.dispose();for(const m of ms){for(const v of Object.values(m))if(v?.isTexture)ts.add(v);m.dispose();}for(const t of ts)t.dispose();}
  return {root,update,passport,mat,locations,crowns,critical,connectionReport,structuralReport,assemblyError,dispose};
}
