/** Numerical resource/configuration tests; these do NOT certify rendered pixels. */
import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {NestedSapphire} from '../nested-sapphire.mjs';
function renderer(colour=[4,2],depth=[4,2]){
 const gl={RENDERBUFFER:1,RGBA16F:2,DEPTH_COMPONENT24:3,SAMPLES:4,
  getInternalformatParameter(target,format,parameter){assert.equal(target,1);assert.equal(parameter,4);return new Int32Array(format===2?colour:depth);}};
 return {getContext:()=>gl};
}
test('Live HDR capture chooses at most four samples supported by colour AND depth',()=>{
 const choose=(a,b)=>NestedSapphire.prototype.supportedSamples.call({renderer:renderer(a,b)});
 assert.equal(choose([8,4,2],[8,4,2]),4);
 assert.equal(choose([4,2],[2]),2);
 assert.equal(choose([4],[2]),0);
 assert.equal(choose([],[]),0);
});
test('Context restoration replaces disposed targets and rebinds live colour/depth uniforms',()=>{
 const watch={root:new THREE.Group(),mat:{}};
 for(const key of ['crystal','crystalEdge','cover'])watch.mat[key]=new THREE.MeshPhysicalMaterial({transmission:1});
 const optics=new NestedSapphire(renderer(),watch),old=optics.target;
 let disposed=0;old.addEventListener('dispose',()=>disposed++);
 assert.equal(old.samples,4);assert.equal(old.resolveDepthBuffer,true);
 optics.setSize(390,844);assert.deepEqual(optics.size.toArray(),[390,844]);
 // resize disposes the old GPU allocation; restoration must dispose it again,
 // construct a fresh descriptor and update both references, not stale textures.
 const beforeRestore=disposed;optics.restoreTarget();assert.equal(disposed,beforeRestore+1);
 assert.notEqual(optics.target,old);assert.equal(optics.target.width,390);assert.equal(optics.target.height,844);
 assert.equal(optics.mapUniform.value,optics.target.texture);
 assert.equal(optics.copyMaterial.uniforms.depthMap.value,optics.target.depthTexture);
 assert.equal(optics.target.texture.colorSpace,THREE.LinearSRGBColorSpace);
 optics.disposeTarget();assert.equal(optics.mapUniform.value,null);
 optics.copyMaterial.dispose();optics.copyScene.children[0].geometry.dispose();
 for(const material of Object.values(watch.mat))material.dispose();
});
