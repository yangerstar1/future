import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {build} from 'esbuild';
import {PISTONS} from '../mechanics.mjs';

/** Export through the product API; independently re-import with the normal glTF
 * loader, inspect editable transforms and geometry, then dispose the test copy. */
export async function verifyAsset(page){
 const loader=await build({stdin:{contents:`import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';import {Box3,Vector3} from 'three';
 window.__reviewGLB=async b=>{const gltf=await new GLTFLoader().parseAsync(b,'');gltf.scene.updateMatrixWorld(true);let meshes=0,triangles=0;const logicalParts={},materials=new Set(),textures=new Set();gltf.scene.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;if(o.userData.logicalPart){logicalParts[o.userData.logicalPart]??={meshes:0,triangles:0,matrix:o.matrixWorld.toArray()};logicalParts[o.userData.logicalPart].meshes++;logicalParts[o.userData.logicalPart].triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;}materials.add(o.material);for(const v of Object.values(o.material))if(v?.isTexture)textures.add(v);}});const box=new Box3().setFromObject(gltf.scene);const result={meshes,triangles,logicalParts,boundsMetres:{min:box.min.toArray(),max:box.max.toArray(),size:box.getSize(new Vector3()).toArray()},materials:[...materials].map(m=>({name:m.name,hasRoughnessMap:!!m.roughnessMap,textureWidth:m.roughnessMap?.image?.width||null}))};gltf.scene.traverse(o=>o.geometry?.dispose());for(const m of materials)m.dispose();for(const t of textures)t.dispose();return result;};`,resolveDir:process.cwd(),sourcefile:'asset-roundtrip-browser.mjs'},bundle:true,format:'iife',write:false});
 await page.addScriptTag({content:loader.outputFiles[0].text});
 const before=await page.evaluate(()=>window.__chiron.snapshot());
 const result=await page.evaluate(async()=>{
  const buffer=await window.__chiron.exportGLB(),inspection=await window.__reviewGLB(buffer),b=new Uint8Array(buffer),chunks=[];
  for(let i=0;i<b.length;i+=32768)chunks.push(btoa(String.fromCharCode(...b.subarray(i,i+32768))));
  return {chunks,inspection};
 });
 const glb=Buffer.concat(result.chunks.map(x=>Buffer.from(x,'base64')));
 assert.equal(glb.readUInt32LE(0),0x46546c67);assert.equal(glb.readUInt32LE(4),2);assert.equal(glb.readUInt32LE(8),glb.length);
 for(const p of PISTONS)for(const id of [p.id,'connecting-rod-'+p.id]){assert(result.inspection.logicalParts[id]?.meshes>0,`Missing editable geometry: ${id}`);assert(result.inspection.logicalParts[id].triangles>100);}
 const translations=PISTONS.map(p=>result.inspection.logicalParts[p.id].matrix.slice(12,15).map(n=>n.toFixed(8)).join(','));
 assert.equal(new Set(translations).size,16,'Exported pistons collapse to one transform');
 assert(result.inspection.materials.some(m=>m.hasRoughnessMap&&m.textureWidth>=256),'Authored finish maps missing from exported asset');
 assert(result.inspection.boundsMetres.size.every(v=>Number.isFinite(v)&&v>.02&&v<.25),'Physical export scale is not plausible metres');
 const after=await page.evaluate(()=>window.__chiron.snapshot());
 assert.equal(before.runtime.initializations,after.runtime.initializations);assert.equal(after.runtime.errors.length,0);assert.equal(before.renderer.memory.geometries,after.renderer.memory.geometries);
 fs.mkdirSync('assets',{recursive:true});fs.writeFileSync('assets/chiron-clear-r05.glb',glb);
 const report={status:'PASS_EXPORT_AND_GLTF_REIMPORT',buildHash:JSON.parse(fs.readFileSync('dist/build-manifest.json')).buildHash,bytes:glb.length,sha256:crypto.createHash('sha256').update(glb).digest('hex'),...result.inspection,limitations:'Static editable pose; live animation, solver and layered optics are in the versioned source. No factory CAD equivalence.'};
 fs.writeFileSync('assets/asset-roundtrip.json',JSON.stringify(report,null,2));
 fs.writeFileSync('assets/asset-register.json',JSON.stringify(await page.evaluate(()=>window.__chiron.passport()),null,2));
 console.log('ASSET',report.status,report.bytes,report.sha256);return report;
}
