import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { PISTONS, SPEC, TAU, solvePiston, handAngles, suspensionOffset } from './mechanics.mjs';
const V=(x=0,y=0,z=0)=>new THREE.Vector3(x,y,z);
const Y=V(0,1,0),Z=V(0,0,1);let serial=0;
/** Original, editable procedural production asset. Hidden architecture is a labelled digital approximation. */
export function makeWatch(){
  const root=new THREE.Group();root.name='Chiron-Sapphire-Clear';
  const registry=[], critical=[];
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
    return mesh(parent,cached(k,()=>new RoundedBoxGeometry(w,h,d,2,Math.min(r,w*.22,h*.22,d*.22))),m,name,V(x,y,z));
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
    cyl(g,0,0,-.017,r*.76,.065,mat.dark);cyl(g,0,0,0,r,.024,mat.polished);
    ring(g,0,0,.013,r*.88,.006,mat.brushed);box(g,0,0,.014,r*1.38,r*.20,.009,mat.black,.002);
    g.rotation.z=(serial%7)*.38;return g;
  }
  function jewel(parent,x,y,z,r=.06,reverse=false){cyl(parent,x,y,z,r*1.46,.035,mat.polished);cyl(parent,x,y,z+(reverse?-.026:.026),r,.025,mat.ruby);cyl(parent,x,y,z+(reverse?-.041:.041),r*.26,.032,mat.dark);}
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
    const g=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:bevel>0,bevelSegments:2,steps:1,bevelSize:bevel,bevelThickness:bevel,curveSegments:32});g.translate(0,0,z);
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
  function gear(parent,x,y,z,r,teeth=60,m=mat.rhodium,spokes=7){
    const g=group(parent,`gear-${teeth}-${++serial}`);g.position.set(x,y,z);
    const s=new THREE.Shape(),rootR=r*.935;
    for(let i=0;i<teeth*4;i++){const a=i/(teeth*4)*TAU;const rr=(i%4===1||i%4===2)?r:rootR;const xx=Math.cos(a)*rr,yy=Math.sin(a)*rr;if(i===0)s.moveTo(xx,yy);else s.lineTo(xx,yy);}s.closePath();
    const hole=new THREE.Path();hole.absarc(0,0,r*.73,0,TAU,true);s.holes.push(hole);
    extrude(g,s,.055,-.0275,m,.004,'toothed-rim');ring(g,0,0,.033,r*.83,.007,mat.polished);
    cyl(g,0,0,0,r*.15,.105,m);cyl(g,0,0,.065,r*.055,.045,mat.polished);
    for(let i=0;i<spokes;i++){const a=i/spokes*TAU,b=box(g,Math.cos(a)*r*.44,Math.sin(a)*r*.44,0,r*.64,r*.049,.045,m,.008);b.rotation.z=a;}
    batchGroups.push(g);return g;
  }
  const rearCrystal=group(root,'sapphire-back-cover',true);
  const crystal=group(root,'sapphire-shell',true),fixed=group(root,'case-and-crown-carrier',true),straps=group(root,'translucent-rubber-straps',true);
  const carrier=group(root,'suspended-movement');critical.push(carrier);
  const base=group(carrier,'bottom-support',true),power=group(carrier,'winding-and-wheel-train',true),dial=group(carrier,'skeleton-dial',true),eng=group(carrier,'W16-assembly'),tour=group(carrier,'tourbillon-assembly');
  const engStatic=group(eng,'W16-static-cylinders',true),tourStatic=group(tour,'tourbillon-support',true);
  const layers=[{g:rearCrystal,v:V(0,0,-2.3)},{g:crystal,v:V(0,0,3.65)},{g:dial,v:V(0,.15,2.25)},{g:tour,v:V(0,.4,1.55)},{g:eng,v:V(0,-.1,.8)},{g:power,v:V(0,0,-.65)},{g:base,v:V(0,0,-1.6)}];
  // Clear tonneau: actual continuous volume with an open internal cavity, front and rear crystals.
  rim(crystal,4.31,5.65,3.95,5.15,1.80,-.925,mat.crystal,.065,'sapphire-case-body');
  rim(crystal,4.35,5.69,3.92,5.13,.095,.9,mat.crystalEdge,.045,'upper-sapphire-bevel');
  extrude(crystal,contour(3.97,5.18),.085,.985,mat.cover,.022,'front-crystal');
  const rearCover=extrude(crystal,contour(3.95,5.14),.045,-1.055,mat.cover,.018,'rear-crystal');
  for(const z of [.915,-.95]){const pts=contour(4.29,5.65).getPoints(84).map(p=>V(p.x,p.y,z));pathTube(crystal,pts,.016,mat.crystalEdge,`crystal-polished-edge-${z}`,true);}
  crystal.updateMatrixWorld(true);const cb=new THREE.Box3().setFromObject(crystal),sz=cb.getSize(V());
  crystal.scale.set(SPEC.caseWidth/sz.x,SPEC.caseLength/sz.y,SPEC.caseThickness/sz.z);
  crystal.position.sub(cb.getCenter(V()).multiply(crystal.scale));
  root.updateMatrixWorld(true);rearCrystal.attach(rearCover);registry.find(x=>x.id==='rear-crystal').parent=rearCrystal.name;
  rim(fixed,4.02,5.24,3.83,5.03,.11,-.925,mat.rhodium,.022,'titanium-caseback-gasket');
  // Precise visible attachment locations, not a random screw field.
  for(const x of [-1.79,1.79])for(const y of [-2.16,2.14]){screw(fixed,x,y,.934,.065);screw(fixed,x,y,-.988,.056,true);}
  for(const y of [-2.77,2.77])for(const x of [-.94,.94]){
    box(fixed,x,y,-.15,.28,.58,.45,mat.polished,.045,'lug-hinge');cyl(fixed,x,y,.092,.07,.027,mat.brushed);
    cyl(fixed,x,y,-.25,.065,.44,mat.rhodium,'x');
  }
  for(const y of [-2.46,2.5]){bar(fixed,V(-1.08,y,-.6),V(1.08,y,-.6),.085,mat.polished,'strap-cross-pin');}
  // Crown collars are attached to the fixed case. Three separate functional targets.
  const crowns=[];
  for(let i=0;i<3;i++){
    const x=(i-1)*1.11,cy=i===1?-3.18:-3.065;
    const cg=group(root,['crown-set-time','crown-wind-two-directions','crown-start-W16'][i]);cg.position.set(x,cy,-.03);crowns.push(cg);critical.push(cg);
    cyl(cg,0,.20,0,.305,.14,mat.polished,'y','crown-collar');cyl(cg,0,-.01,0,.25,.36,mat.rhodium,'y','crown-grip');
    for(let j=0;j<28;j++){const a=j/28*TAU;const rib=box(cg,Math.cos(a)*.246,-.035,Math.sin(a)*.246,.035,.29,.045,mat.polished,.011,'crown-flute');rib.rotation.y=-a;}
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
  for(const x of [-.52,.52])box(buckle,x,.65,-.16,.085,1.25,.065,mat.brushed,.02);
  bar(buckle,V(-.89,.28,0),V(.89,.28,0),.043,mat.polished,'clasp-hinge');box(buckle,0,.08,.08,.095,.41,.055,mat.rhodium,.02,'buckle-tongue');
  // Main skeleton chassis, open on both sides, with load-bearing rails and machined bridges.
  rim(base,3.43,4.78,3.05,4.33,.15,-.62,mat.dark,.055,'skeleton-main-plate');
  for(const x of [-1.45,1.45])box(base,x,0,-.53,.145,4.2,.21,mat.dark,.035,'longitudinal-load-rail');
  for(const y of [-2.12,2.09])box(base,0,y,-.49,3.0,.16,.17,mat.rhodium,.028,'transverse-bridge');
  for(const x of [-1.36,1.36])for(const y of [-1.6,1.72]){box(base,x,y,-.4,.38,.40,.15,mat.rhodium,.035);screw(base,x,y,-.307,.089);}
  for(let k=0;k<5;k++)box(base,0,1.82-k*.08,-.72,2.08,.018,.026,mat.brushed,.004,'back-geneva-stripe');
  box(base,0,1.85,-.7,2.12,.53,.085,mat.dark,.04,'rear-signature-bridge');
  const backLabel=flatLabel(base,'JACOB & CO.',0,1.89,-.756,1.21,.18,'#74a9c5','#151a21');backLabel.rotation.y=Math.PI;
  for(const x of [-.95,.95])screw(base,x,1.86,-.775,.075,true);
  // Two independent reserve barrels. Wheel centers/tooth counts are a visible approximation, not factory geometry.
  const wheels=[];
  for(const x of [-.84,.84]){
    const gg=gear(power,x*1.25,.08,-.64,.72,86,mat.rhodium,16);wheels.push({g:gg,rate:.012,domain:x<0?'clock':'engine'});
    cyl(gg,0,0,-.082,.594,.09,mat.dark);ring(gg,0,0,-.137,.533,.015,mat.polished);ring(gg,0,0,-.142,.36,.008,mat.polished);
    cyl(gg,0,0,-.157,.21,.042,mat.rhodium);screw(gg,0,0,-.187,.065,true);
    for(let i=0;i<5;i++){const a=TAU*i/5; screw(gg,Math.cos(a)*.44,Math.sin(a)*.44,-.148,.041,true);}
    jewel(power,x*1.25,.08,-.44,.054);
  }
  const train=[[-.41,1.0,.263,30],[.11,.94,.272,31],[.52,1.35,.301,34],[.94,1.68,.254,29],[0,-.85,.25,28]];
  for(const [i,[x,y,r,n]] of train.entries()){const g=gear(power,x,y,-.40,r,n,mat.brass,5);wheels.push({g,rate:.14*30/n*(i%2?-1:1),domain:i===4?'engine':'clock'});jewel(power,x,y,-.30,.045);}
  // Reverse-side cutout bridges and retainers remain present when the watch is turned over.
  const bridgeShape=new THREE.Shape();bridgeShape.moveTo(-.19,1.37);bridgeShape.lineTo(.19,1.37);bridgeShape.lineTo(.27,-.40);bridgeShape.lineTo(.12,-.91);bridgeShape.lineTo(-.12,-.91);bridgeShape.lineTo(-.27,-.40);bridgeShape.closePath();
  extrude(power,bridgeShape,.105,-.89,mat.dark,.025,'rear-central-bridge');
  for(const y of [.96,.5,-.53])jewel(power,0,y,-.915,.055,true);
  for(const x of [-1.19,1.19]){bar(power,V(x,-1.40,-.69),V(x*.65,-.85,-.69),.055,mat.rhodium,'reverse-fork');screw(power,x,-1.4,-.755,.057,true);}
  box(power,0,-1.6,-.59,1.43,.17,.1,mat.rhodium,.027,'engine-rear-bridge');for(const x of [-.62,.62])screw(power,x,-1.6,-.663,.053,true);
  // Four springs connect the fixed case to a common suspended carrier. Recomputed endpoints, no floating decoration.
  const springs=[],springMounts=group(root,'four-point-suspension'),mountMoving=group(carrier,'suspended-bearing-mounts',true);
  for(const x of [-1.40,1.40])for(const y of [-1.67,1.68]){
    const fg=group(springMounts,`suspension-${x}-${y}`);fg.position.set(x,y,-.56);
    cyl(fg,0,0,0,.112,.105,mat.brushed);cyl(fg,0,0,.51,.041,1.04,mat.polished);ring(fg,0,0,.015,.105,.018,mat.dark);
    const pts=[];for(let j=0;j<=112;j++){const a=j/112*TAU*7;pts.push(V(Math.cos(a)*.087,Math.sin(a)*.087,.055+j/112*1.045));}
    const coil=pathTube(fg,pts,.015,mat.blue,'blue-suspension-coil');springs.push(coil);
    cyl(mountMoving,x,y,.54,.112,.123,mat.polished);box(mountMoving,x,y,.58,.35,.24,.10,mat.polished,.027,'suspension-top-bearing');screw(mountMoving,x,y,.65,.074);
  }
  // W16: four explicit banks × four cylinders, eight shared crankpins, sixteen independently constrained rods.
  eng.position.set(0,-1.15,.02);const crank=group(eng,'crankshaft');const pistons=[],rods=[];
  for(let station=0;station<8;station++){
    const d={...PISTONS[station*2],y:(station-3.5)*.205},px=d.radius*Math.cos(d.phase),pz=d.radius*Math.sin(d.phase);
    cyl(crank,px,d.y,pz,.046,.123,mat.polished,'y',d.sharedPin,32);
    for(const off of [-.079,.079]){
      bar(crank,V(0,d.y+off,0),V(px,d.y+off,pz),.056,mat.brushed,'crank-web');
      cyl(crank,0,d.y+off,0,.064,.028,mat.brushed,'y','main-journal',32);
    }
    if(station<7)cyl(crank,0,d.y+.1025,0,.026,.034,mat.polished,'y','shaft-segment',24);
  }
  batchGroups.push(crank);critical.push(crank);
  for(const b of [0,1,2,3]){
    const ds=PISTONS.filter(d=>d.bank===b),s=new THREE.Shape();s.moveTo(-.118,-.83);s.lineTo(.118,-.83);s.lineTo(.118,.83);s.lineTo(-.118,.83);s.closePath();
    for(const d of ds){const h=new THREE.Path();h.absarc(0,d.y,.084,0,TAU,true);s.holes.push(h);}
    const bank=extrude(engStatic,s,.268,.326,mat.cylinderGlass,.008,`sapphire-cylinder-bank-${b+1}`);bank.rotation.y=ds[0].angle;
    for(const d of ds){const u=V(Math.sin(d.angle),0,Math.cos(d.angle));
      const rim1=ring(engStatic,u.x*.594,d.y,u.z*.594,.087,.008,mat.crystalEdge,`cylinder-rim-${d.id}`);rim1.rotation.y=d.angle;
      const rim2=ring(engStatic,u.x*.331,d.y,u.z*.331,.087,.006,mat.crystalEdge);rim2.rotation.y=d.angle;
    }
  }
  for(const d of PISTONS){
    const pg=group(eng,d.id),rg=group(eng,`connecting-rod-${d.id}`);
    cyl(pg,0,0,0,.071,.105,mat.rhodium,'y','piston-skirt',32);cyl(pg,0,.055,0,.071,.016,mat.polished,'y','piston-head',32);
    ring(pg,0,.026,0,.071,.0045,mat.dark,'piston-groove','y');ring(pg,0,.041,0,.071,.004,mat.polished,'piston-ring','y');
    cyl(pg,0,0,0,.021,.16,mat.polished,'z','wrist-pin',20);
    pg.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V(Math.cos(d.angle),0,-Math.sin(d.angle)),V(Math.sin(d.angle),0,Math.cos(d.angle)),V(0,-1,0)));
    box(rg,0,0,d.length*.5,.045,.038,d.length,mat.rhodium,.014,'connecting-rod-web');
    for(const z of [0,d.length]){ring(rg,0,0,z,.033,.011,mat.polished,'rod-eye','y');cyl(rg,0,0,z,.021,.049,mat.brass,'y','rod-bearing',24);}
    pistons.push({g:pg,d});rods.push({g:rg,d});batchGroups.push(pg,rg);critical.push(pg,rg);
  }
  for(const x of [-.75,.75]){
    box(engStatic,x,0,-.015,.10,1.92,.14,mat.dark,.025,'engine-longitudinal-support');
    for(const y of [-.87,.87]){bar(engStatic,V(x,y,-.05),V(0,y,-.04),.048,mat.rhodium,'crankshaft-bearing-crossmember');screw(engStatic,x,y,.061,.046);}
    // Two rotating turbine-like components, mechanically associated with the automaton.
  }
  const turbos=[];for(const x of [-.96,.96]){
    const g=group(eng,'turbo-rotor');g.position.set(x,.23,.13);ring(g,0,0,0,.27,.027,mat.polished);ring(g,0,0,0,.22,.008,mat.brushed);
    for(let i=0;i<13;i++){const a=i/13*TAU;const pts=[V(Math.cos(a)*.06,Math.sin(a)*.06,.008),V(Math.cos(a+.25)*.15,Math.sin(a+.25)*.15,.035),V(Math.cos(a+.45)*.246,Math.sin(a+.45)*.246,0)];pathTube(g,pts,.009,mat.rhodium,'turbine-vane');}
    cyl(g,0,0,.02,.071,.058,mat.polished);turbos.push(g);batchGroups.push(g);
  }
  for(const x of [-1.08,1.08])pathTube(engStatic,[V(x,.51,-.12),V(x,.14,-.19),V(x,-.53,-.10),V(x*.9,-.93,.025)],.043,mat.polished,'engine-exhaust-form');
  box(engStatic,0,-.976,.194,.73,.18,.064,mat.rhodium,.016,'engine-maker-plate');flatLabel(engStatic,'JACOB & CO.',0,-.976,.230,.68,.118);flatLabel(engStatic,'GENÈVE',0,-1.035,.232,.28,.032);
  // Skeleton dial and forked hands at the observed upper-center position.
  const dialY=.60;
  const arc=[];for(let i=0;i<=128;i++){const a=.12+i/128*(TAU-.24);arc.push(V(Math.sin(a)*1.14,dialY+Math.cos(a)*1.14,.64));}
  pathTube(dial,arc,.023,mat.polished,'open-dial-minute-ring');
  for(let i=1;i<=11;i++){
    const a=i/12*TAU,x=Math.sin(a),y=Math.cos(a);
    const idx=box(dial,x*1.094,dialY+y*1.094,.697,.078,.286,.045,mat.rhodium,.012,`index-${i}`);idx.rotation.z=-a;
    const blue=box(dial,x*1.099,dialY+y*1.099,.724,.039,.227,.015,mat.blue,.005,`blue-index-${i}`);blue.rotation.z=-a;
  }
  for(const a of [Math.PI*.33,Math.PI*.70,Math.PI*1.29,Math.PI*1.66]){
    const x=Math.sin(a)*1.13,y=dialY+Math.cos(a)*1.13;
    const len=Math.hypot(x,y-dialY),bridge=box(dial,x*.49,dialY+(y-dialY)*.49,.63,.112,len*.96,.054,mat.rhodium,.014,'skeleton-dial-bridge');bridge.rotation.z=-Math.atan2(x,y-dialY);
  }
  ring(dial,0,dialY,.53,.49,.044,mat.rhodium,'central-open-bearing-bridge');ring(dial,0,dialY,.553,.38,.012,mat.dark);
  cyl(dial,0,dialY,.704,.175,.053,mat.polished);ring(dial,0,dialY,.738,.128,.008,mat.dark);
  box(dial,0,-.306,.696,.36,.26,.055,mat.rhodium,.038,'EB-medallion');flatLabel(dial,'EB',0,-.307,.728,.279,.176,'#0085c6','#d7dee2');
  function hand(length,name){const g=group(carrier,name);g.position.set(0,dialY,name==='minute-hand'?.819:.777);
    const s=new THREE.Shape();s.moveTo(-.063,-.16);s.lineTo(-.063,.21);s.lineTo(-.055,length*.70);s.lineTo(0,length);s.lineTo(.055,length*.70);s.lineTo(.063,.21);s.lineTo(.063,-.16);s.closePath();
    const hole=new THREE.Path();hole.moveTo(-.021,.20);hole.lineTo(0,length*.73);hole.lineTo(.021,.2);hole.closePath();s.holes.push(hole);
    extrude(g,s,.021,0,mat.polished,.008,name+'-skeleton');box(g,0,length*.81,.034,.039,length*.25,.012,mat.blue,.005,'hand-luminous-tip');batchGroups.push(g);critical.push(g);return g;
  }
  const hour=hand(.85,'hour-hand'),minute=hand(1.12,'minute-hand');cyl(dial,0,dialY,.874,.072,.062,mat.rhodium);cyl(dial,0,dialY,.908,.034,.012,mat.polished);
  // Small fuel-gauge-shaped timekeeping reserve at nine o'clock.
  const gauge=group(dial,'power-reserve-gauge');gauge.position.set(-1.20,-.28,.49);cyl(gauge,0,0,0,.25,.055,mat.dark);ring(gauge,0,0,.038,.235,.016,mat.polished);
  for(let i=0;i<11;i++){const a=(-.72+i/10*1.5)*Math.PI,xx=Math.cos(a)*.184,yy=Math.sin(a)*.184;const t=box(gauge,xx,yy,.038,.032,.07,.01,i<3?mat.ruby:mat.lume,.005);t.rotation.z=a-Math.PI/2;}
  const reserveHand=group(gauge,'reserve-pointer');batchGroups.push(reserveHand);box(reserveHand,0,.083,.057,.018,.17,.016,mat.polished,.004);cyl(gauge,0,0,.061,.027,.02,mat.polished);
  // Inclined flying tourbillon: stationary protective frame, rotating cage, independent oscillating balance.
  tour.position.set(0,1.82,.33);tour.rotation.x=Math.PI/6;
  ring(tourStatic,0,0,-.105,.386,.025,mat.dark,'tourbillon-bearing-seat');cyl(tourStatic,0,0,-.17,.068,.20,mat.polished);
  const cage=group(tour,'flying-tourbillon-cage');
  const crownWheel=gear(cage,0,0,-.079,.337,62,mat.brass,5);ring(cage,0,0,.162,.343,.020,mat.polished,'cage-front-ring');ring(cage,0,0,-.05,.355,.018,mat.rhodium);
  for(let i=0;i<3;i++){const a=i/3*TAU;bar(cage,V(Math.cos(a)*.338,Math.sin(a)*.338,-.065),V(Math.cos(a)*.338,Math.sin(a)*.338,.167),.021,mat.polished,'cage-pillar');bar(cage,V(0,0,.169),V(Math.cos(a)*.338,Math.sin(a)*.338,.169),.016,mat.polished,'cage-spoke');screw(cage,Math.cos(a)*.323,Math.sin(a)*.323,.19,.025);}
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

  const escape=gear(cage,.16,-.133,-.009,.104,15,mat.rhodium,4);jewel(cage,0,0,.187,.033);
  pathTube(tourStatic,[V(-.39,-.30,-.11),V(-.49,.08,.04),V(-.36,.39,.04),V(0,.5,.04),V(.36,.39,.04),V(.49,.08,.04),V(.39,-.30,-.11)],.027,mat.polished,'tourbillon-protective-arch');
  batchGroups.push(cage,balance);critical.push(cage,balance);
  // Telescoping display connection maintains fixed crown to moving mechanism attachment.
  const coupling=bar(root,V(0,-2.66,-.17),V(0,-2.13,-.17),.038,mat.polished,'winding-display-coupling');
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
    for(const item of lists.values()){const geo=mergeGeometries(item.geos,false);if(!geo)throw new Error('Static geometry batching failed');const m=new THREE.Mesh(geo,item.mat);m.name=`${g.name}:${item.mat.name}`;m.renderOrder=item.order;g.add(m);for(const x of item.geos)x.dispose();}
  }
  root.updateMatrixWorld(true);
  // Children first; excluded dynamic subgroups keep their node identity and pivots.
  for(const g of [...batchGroups].reverse())batch(g);
  root.traverse(o=>{if(o.isMesh&&!o.material.transparent){o.castShadow=true;o.receiveShadow=true;}});
  root.updateMatrixWorld(true);
  const rest=layers.map(({g,v})=>({g,v,p:g.position.clone(),q:g.quaternion.clone()}));
  const handRest=[hour.position.clone(),minute.position.clone()];
  const assembledCaseBox=new THREE.Box3().setFromObject(crystal).expandByObject(rearCrystal),caseSize=assembledCaseBox.getSize(V());
  const passport={units:'1 scene unit = 10 mm',caseMeasuredMm:caseSize.toArray().map(x=>x*10),caseSpecificationMm:[44.4,57.8,21.5],measurementBoundary:'sapphire shell incl. front and back; excludes crowns, strap and lugs',parts:registry,
    pistons:PISTONS,approximation:'Original visible digital reconstruction. No factory CAD or 578-part manufacturing equivalence. Layered physical transmission and transparent cylinder approximation for nested sapphire; hidden gearing, rod geometry, phases and coupling are digital approximations.'};
  root.userData={identity:'BU210.80.AA.AA.B — Clear visual baseline',units:'10 mm',source:'Original procedural geometry; see REFERENCES.md',approximation:passport.approximation};
  function update(state){
    const bob=suspensionOffset(state.suspensionTime);carrier.position.z=bob;
    for(const r of rest){r.g.position.copy(r.p).addScaledVector(r.v,state.explode);r.g.quaternion.copy(r.q);}
    hour.position.copy(handRest[0]).addScaledVector(V(0,.15,2.25),state.explode);minute.position.copy(handRest[1]).addScaledVector(V(0,.15,2.25),state.explode);
    rearCrystal.visible=crystal.visible=!state.crystalOff&&state.selection==='all';fixed.visible=straps.visible=state.selection==='all';springMounts.visible=state.selection==='all';for(const c of crowns)c.visible=state.selection==='all';
    for(const g of [base,power,dial,hour,minute,mountMoving])g.visible=state.selection==='all';
    eng.visible=state.selection==='all'||state.selection==='engine';tour.visible=state.selection==='all'||state.selection==='tourbillon';coupling.visible=state.selection==='all'&&state.explode<.03;
    crank.rotation.y=-state.engineTheta;
    for(const {g,d} of pistons){const p=solvePiston(d,state.engineTheta);g.position.fromArray(p.p);}
    for(const {g,d} of rods){const p=solvePiston(d,state.engineTheta);g.position.fromArray(p.c);g.quaternion.setFromUnitVectors(Z,V(...p.p).sub(V(...p.c)).normalize());}
    for(const g of turbos)g.rotation.z=state.engineTheta*2.2;
    const a=handAngles(state.clockSeconds);hour.rotation.z=a.hour;minute.rotation.z=a.minute;reserveHand.rotation.z=(.72-state.clockEnergy*1.5)*Math.PI;
    cage.rotation.z=state.balanceTime/SPEC.cagePeriod*TAU;balance.rotation.z=Math.sin(state.balanceTime*TAU*SPEC.balanceHz)*2.4;updateHair(balance.rotation.z);pallet.rotation.z=.08*Math.tanh(Math.sin(state.balanceTime*TAU*SPEC.balanceHz)*7);escape.rotation.z=Math.floor(state.balanceTime*6)/15*TAU;
    for(const {g,rate,domain} of wheels)g.rotation.z=(domain==='engine'?state.engineTheta:state.balanceTime)*rate;
    for(const s of springs)s.scale.z=1+bob/1.10;
    const ca=V(0,-2.66,-.17),cb=V(0,-2.13,-.17+bob),delta=cb.clone().sub(ca);coupling.position.copy(ca).add(cb).multiplyScalar(.5);coupling.quaternion.setFromUnitVectors(Y,delta.normalize());coupling.scale.y=ca.distanceTo(cb)/.53;
  }
  function connectionReport(){root.updateMatrixWorld(true);return pistons.map(({g,d},i)=>{const rod=rods[i].g,start=rod.localToWorld(V()),end=rod.localToWorld(V(0,0,d.length)),pin=g.getWorldPosition(V()),crankpin=crank.localToWorld(V(d.radius*Math.cos(d.phase),d.y,d.radius*Math.sin(d.phase)));return {id:d.id,smallEndResidual:end.distanceTo(pin)/d.length,bigEndResidual:start.distanceTo(crankpin)/d.length,worldRodLength:start.distanceTo(end)};});}
  function assemblyError(){let pos=0,rot=0;for(const r of rest){pos=Math.max(pos,r.g.position.distanceTo(r.p));rot=Math.max(rot,r.g.quaternion.angleTo(r.q));}return {position:pos,rotationDegrees:rot*180/Math.PI};}
  function dispose(){const gs=new Set(),ms=new Set(),ts=new Set();root.traverse(o=>{if(o.geometry)gs.add(o.geometry);if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])ms.add(m);}});for(const g of gs)g.dispose();for(const m of ms){for(const v of Object.values(m))if(v?.isTexture)ts.add(v);m.dispose();}for(const t of ts)t.dispose();}
  return {root,update,passport,mat,locations,crowns,critical,connectionReport,assemblyError,dispose};
}
