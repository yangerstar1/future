/**
 * Two-layer real-time sapphire using the pinned Three.js physical shader.
 * Captures this SAME watch, without its outer sapphire, into a linear HDR target.
 * Outer materials retain Three.js Fresnel/refraction and sample that target,
 * so they do not erase the inner transmissive eight-bore cylinder blocks.
 * This remains screen-space refraction, not multi-bounce ray-traced optics.
 */
import * as THREE from 'three';
export class NestedSapphire {
 constructor(renderer,watch){
  this.renderer=renderer;this.watch=watch;this.size=new THREE.Vector2(512,512);this.captures=0;
  this.mapUniform={value:null};this.sizeUniform={value:this.size};this.restoreTarget();
  // Present the already rendered inner watch once, including its depth. The
  // final geometry pass contains only sapphire; it never shades the same opaque
  // mechanism three times. These are live scene buffers, not baked imagery.
  this.copyMaterial=new THREE.ShaderMaterial({
   uniforms:{radiance:this.mapUniform,depthMap:{value:this.target.depthTexture}},
   vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',
   fragmentShader:'uniform sampler2D radiance; uniform sampler2D depthMap; varying vec2 vUv; void main(){gl_FragColor=texture2D(radiance,vUv);gl_FragDepth=texture2D(depthMap,vUv).r;\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}',
   depthTest:true,depthWrite:true,depthFunc:THREE.AlwaysDepth,blending:THREE.NoBlending
  });
  this.copyScene=new THREE.Scene();this.copyCamera=new THREE.Camera();
  const triangle=new THREE.BufferGeometry();
  triangle.setAttribute('position',new THREE.Float32BufferAttribute([-1,-1,0,3,-1,0,-1,3,0],3));
  triangle.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,2,0,0,2],2));
  const quad=new THREE.Mesh(triangle,this.copyMaterial);quad.frustumCulled=false;this.copyScene.add(quad);
  const source=THREE.ShaderChunk.transmission_pars_fragment;
  if(!source.includes('transmissionSamplerMap'))throw new Error('Unsupported Three.js transmission shader');
  const outer=['crystal','crystalEdge','cover'];
  if(Object.entries(watch.mat).some(([name,m])=>m.transmission>0&&!outer.includes(name)))throw new Error('An unregistered transmission material would use the reduced compatibility buffer');
  // These three materials sample our full-resolution live capture. r180 still
  // renders its built-in, unused transmission target; retain a small compatibility
  // buffer instead of shading a second full-screen opaque image and four MSAA samples.
  renderer.transmissionResolutionScale=.125;
  const replacement=source.replaceAll('transmissionSamplerMap','chironInnerScene').replaceAll('transmissionSamplerSize','chironInnerSize').replace('return textureBicubic( chironInnerScene, fragCoord.xy, lod );','return textureLod( chironInnerScene, fragCoord.xy, 0.0 );');
  for(const name of ['crystal','crystalEdge','cover']){
   const m=watch.mat[name];
   m.onBeforeCompile=shader=>{shader.uniforms.chironInnerScene=this.mapUniform;shader.uniforms.chironInnerSize=this.sizeUniform;shader.fragmentShader=shader.fragmentShader.replace('#include <transmission_pars_fragment>',replacement);};
   m.customProgramCacheKey=()=>`chiron-two-layer-transmission-three-${THREE.REVISION}`;m.needsUpdate=true;
  }
 }
 restoreTarget(){this.disposeTarget();this.target=new THREE.WebGLRenderTarget(this.size.x,this.size.y,{type:THREE.HalfFloatType,format:THREE.RGBAFormat,generateMipmaps:false,minFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter,depthBuffer:true,samples:0});this.target.depthTexture=new THREE.DepthTexture(this.size.x,this.size.y,THREE.UnsignedIntType);this.target.texture.name='live-inner-watch-radiance';this.target.texture.colorSpace=THREE.LinearSRGBColorSpace;this.mapUniform.value=this.target.texture;if(this.copyMaterial)this.copyMaterial.uniforms.depthMap.value=this.target.depthTexture;}
 setSize(w,h){const width=Math.max(1,Math.round(w)),height=Math.max(1,Math.round(h));if(this.size.x!==width||this.size.y!==height){this.size.set(width,height);this.target?.setSize(width,height);}}
 capture(scene,camera){
  if(!this.target)return false;const meshes=[];
  this.watch.root.traverse(o=>{if(o.isMesh&&o.visible&&['crystal','crystalEdge','cover'].includes(o.material.name)){let p=o.parent;while(p){if(!p.visible)return;p=p.parent;}meshes.push(o);}});
  if(!meshes.length)return false;
  const r=this.renderer,rt=r.getRenderTarget(),tm=r.toneMapping,clear=r.getClearColor(new THREE.Color()),alpha=r.getClearAlpha();
  for(const o of meshes)o.visible=false;
  try{r.toneMapping=THREE.NoToneMapping;r.setClearColor(0x090c10,1);r.setRenderTarget(this.target);r.clear();r.render(scene,camera);this.captures++;}
  finally{for(const o of meshes)o.visible=true;r.setRenderTarget(rt);r.toneMapping=tm;r.setClearColor(clear,alpha);}
  return true;
 }
 present(scene,camera){
  const r=this.renderer,auto=r.autoClear,hidden=[];
  r.setRenderTarget(null);r.autoClear=true;r.render(this.copyScene,this.copyCamera);
  this.watch.root.traverse(o=>{if(o.isMesh&&o.visible&&!['crystal','crystalEdge','cover'].includes(o.material.name)){hidden.push(o);o.visible=false;}});
  try{r.autoClear=false;r.render(scene,camera);}finally{for(const o of hidden)o.visible=true;r.autoClear=auto;}
 }
 disposeTarget(){this.target?.dispose();this.target=null;if(this.mapUniform)this.mapUniform.value=null;}
 snapshot(){return {mode:'live two-layer screen-space physical transmission',resolution:this.size.toArray(),captures:this.captures,textureLive:!!this.target,limitations:'No multi-bounce caustics or factory anti-reflective coating simulation'};}
}
