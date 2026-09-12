/** Continuous, curved tonneau sapphire surfaces. Authored from the observed Clear
 * outline; this is editable digital geometry, not an original manufacturer's CAD. */
import * as THREE from 'three';
export function makeSapphire(c,crystal){
 const {V,mat,mesh,contour,pathTube}=c;
 const N=144,verts=[],uv=[],ids=[];
 // The Clear source shows a broad rolled shoulder and a convex flank, not a
 // vertical transparent sleeve. These authored sections keep the frozen outer
 // envelope; their thickness distribution is a visible-shape approximation.
 const levels=[[-.99,4.10,5.44,3.79,4.99],[-.955,4.21,5.56,3.81,5.02],[-.865,4.31,5.66,3.85,5.07],[-.65,4.405,5.75,3.90,5.13],[-.32,4.44,5.78,3.94,5.17],[.12,4.42,5.77,3.95,5.19],[.43,4.355,5.70,3.94,5.19],[.66,4.26,5.60,3.92,5.18],[.83,4.145,5.47,3.90,5.17],[.94,4.055,5.35,3.88,5.15],[.979,4.015,5.29,3.88,5.15]];
 const warp=(x,y,z)=>z+.085*(1-(y/2.9)**2)+.018*(x/2.22)**2;
 for(let side=0;side<2;side++)for(let k=0;k<levels.length;k++){
  const l=levels[k],points=contour(l[side?3:1],l[side?4:2]).getSpacedPoints(N).slice(0,N);
  points.forEach((p,i)=>{verts.push(p.x,p.y,warp(p.x,p.y,l[0]));uv.push(i/N,k/(levels.length-1));});
 }
 const K=levels.length,inner=N*K;
 for(let k=0;k<K-1;k++)for(let i=0;i<N;i++){
  const j=(i+1)%N,a=k*N+i,b=k*N+j,d=(k+1)*N+i,e=(k+1)*N+j;
  ids.push(a,d,b,b,d,e);ids.push(inner+a,inner+b,inner+d,inner+b,inner+e,inner+d);
 }
 for(let i=0;i<N;i++){const j=(i+1)%N;
  // Closed top and bottom landings join the outer and inner curved side walls.
  const a=(K-1)*N+i,b=(K-1)*N+j,d=inner+(K-1)*N+i,e=inner+(K-1)*N+j;
  ids.push(d,e,a,e,b,a);ids.push(i,j,inner+i,j,inner+j,inner+i);
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(ids);g.computeVertexNormals();
 mesh(crystal,g,mat.crystal,'continuous-lofted-sapphire-case');
 function lens(w,h,z,depth,name,curved){
  const M=144,R=20,outline=contour(w,h).getSpacedPoints(M).slice(0,M),v=[],t=[],ix=[];
  const capZ=(x,y)=>z+(curved?.125*(1-(y/(h/2))**2)*(1-.17*(x/(w/2))**2):0);
  const add=(x,y,zz)=>{v.push(x,y,zz);t.push(x/w+.5,y/h+.5);};
  for(const face of [0,1]){
   add(0,0,capZ(0,0)-face*depth);
   for(let r=1;r<=R;r++)for(const p of outline){const x=p.x*r/R,y=p.y*r/R;add(x,y,capZ(x,y)-face*depth);}
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
 const front=lens(3.885,5.15,1.01,.061,'front-crystal',true),rear=lens(3.82,5.03,-.965,.045,'rear-crystal',false);
 for(const [w,h,z] of [[4.016,5.291,.978],[4.21,5.56,-.955]]){
  const points=contour(w,h).getSpacedPoints(144).slice(0,144).map(p=>V(p.x,p.y,warp(p.x,p.y,z)));pathTube(crystal,points,.008,mat.crystalEdge,'polished-sapphire-arris',true);
 }
 return {front,rear};
}
