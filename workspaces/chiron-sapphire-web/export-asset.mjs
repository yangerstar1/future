import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

/** Export copies own their materials. The renderer's live maps and shader hooks
 * must never be changed to make an offline asset export succeed. */
export async function exportWatchGLB(watch) {
  const assetRoot = new THREE.Group();
  assetRoot.name = 'Chiron-Clear-R05-METRES';
  assetRoot.scale.setScalar(.01);
  assetRoot.userData = {units:'metres', sourceUnits:'1 source unit = 10 mm',
    asset:'authored non-factory reconstruction', animation:'static pose; editable movement in source',
    optics:'standard glTF material approximation; live nested optics are in the website'};
  assetRoot.add(watch.root.clone(true));
  const instances=[];
  assetRoot.traverse(o=>{if(o.isInstancedMesh)instances.push(o);});
  for(const batch of instances){
    for(let i=0;i<batch.count;i++){
      const id=batch.userData.instanceNodeIds[i],node=assetRoot.getObjectByName(id);
      if(!node)throw new Error('Missing editable instance node '+id);
      const mesh=new THREE.Mesh(batch.geometry,batch.material);
      mesh.name=id+':'+batch.material.name;mesh.userData.logicalPart=id;node.add(mesh);
    }
    batch.removeFromParent();
  }
  const materials=new Map(),textures=new Map();
  function portableTexture(t){
    if(!t?.isDataTexture)return t;
    if(textures.has(t))return textures.get(t);
    if(t.type!==THREE.UnsignedByteType||t.format!==THREE.RGBAFormat)
      throw new Error('Unsupported export data texture: '+t.name);
    const {width,height,data}=t.image,c=document.createElement('canvas');
    c.width=width;c.height=height;
    c.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(data),width,height),0,0);
    const copy=new THREE.CanvasTexture(c);
    // Preserve the exact roughness bytes and UV convention used by the live map.
    for(const key of ['name','colorSpace','flipY','wrapS','wrapT','magFilter','minFilter','channel'])copy[key]=t[key];
    copy.offset.copy(t.offset);copy.repeat.copy(t.repeat);copy.center.copy(t.center);copy.rotation=t.rotation;
    textures.set(t,copy);return copy;
  }
  assetRoot.traverse(o=>{
    if(!o.isMesh)return;
    const source=o.material;
    if(!materials.has(source)){
      const m=source.clone();
      for(const key of ['map','roughnessMap','metalnessMap','normalMap','bumpMap','alphaMap'])if(m[key])m[key]=portableTexture(m[key]);
      if(source.name==='cylinderGlass'){m.transmission=.94;m.opacity=1;m.transparent=false;m.thickness=.012;}
      materials.set(source,m);
    }
    o.material=materials.get(source);
  });
  assetRoot.updateMatrixWorld(true);
  try{return await new GLTFExporter().parseAsync(assetRoot,{binary:true,onlyVisible:false,trs:true});}
  finally{for(const t of textures.values())t.dispose();for(const m of materials.values())m.dispose();}
}
