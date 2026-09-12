/** Continuous, curved tonneau sapphire surfaces. Authored from the observed Clear
 * outline; this is editable digital geometry, not an original manufacturer's CAD. */
import * as THREE from 'three';
import mainCase from './generated/sapphire-main-case.json';
export function makeSapphire(c,crystal){
 const {V,mat,mesh,contour,pathTube}=c;
 // The actual single CAD solid includes all three through-bores and both lens
 // seats. Preserve its coordinates and analytic normals at the crown interfaces.
 const g=new THREE.BufferGeometry();
 for(const [name,size] of [['position',3],['normal',3],['uv',2]])g.setAttribute(name,new THREE.Float32BufferAttribute(mainCase[name],size));
 g.setIndex(mainCase.index);mesh(crystal,g,mat.crystal,mainCase.id);
 function lens({width:w,height:h,surfaceZ:z,baseZ,curved},name){
  const M=144,R=20,outline=contour(w,h).getSpacedPoints(M).slice(0,M),v=[],t=[],ix=[];
  const capZ=(x,y)=>z+(curved?.125*(1-(y/(h/2))**2)*(1-.17*(x/(w/2))**2):0);
  const add=(x,y,zz)=>{v.push(x,y,zz);t.push(x/w+.5,y/h+.5);};
  for(const face of [0,1]){
   add(0,0,face?baseZ:capZ(0,0));
   for(let r=1;r<=R;r++)for(const p of outline){const x=p.x*r/R,y=p.y*r/R;add(x,y,face?baseZ:capZ(x,y));}
  }
  const L=1+R*M;
  for(let face=0;face<2;face++){
   const b=face*L,tri=(a,c,d)=>face?ix.push(b+a,b+d,b+c):ix.push(b+a,b+c,b+d);
   for(let i=0;i<M;i++)tri(0,1+(i+1)%M,1+i);
   for(let r=0;r<R-1;r++)for(let i=0;i<M;i++){const j=(i+1)%M,a=1+r*M+i,b=1+r*M+j,d=1+(r+1)*M+i,e=1+(r+1)*M+j;tri(a,b,d);tri(b,e,d);}
  }
  for(let i=0;i<M;i++){const j=(i+1)%M,a=1+(R-1)*M+i,b=1+(R-1)*M+j;ix.push(a,L+a,b,b,L+a,L+b);}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(v,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(t,2));geo.setIndex(ix);geo.computeVertexNormals();return mesh(crystal,geo,mat.cover,name);
 }
 const front=lens(mainCase.lenses.front,'front-crystal'),rear=lens(mainCase.lenses.rear,'rear-crystal');
 for(const [w,h,z] of [[4.015,5.29,.95],[4.10,5.44,-.995]]){
  const points=contour(w,h).getSpacedPoints(144).slice(0,144).map(p=>V(p.x,p.y,z));pathTube(crystal,points,.008,mat.crystalEdge,'polished-sapphire-arris',true);
 }
 return {front,rear};
}
