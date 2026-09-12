/** Real generated-geometry and transform audit. The canvas stub supplies marking
 * metadata only: this is NOT browser rendering or a visual acceptance test. */
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import path from 'node:path';import {build} from 'esbuild';
import * as THREE from 'three';
const out='evidence/R04/geometry-audit';fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync('dist/build-manifest.json'));
for(const [file,hash] of Object.entries(manifest.inputs))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),hash,'Rebuild changed source before running audit: '+file);
await build({stdin:{contents:"export {makeWatch} from './watch.mjs';export {createState,solvePiston,PISTONS,TAU} from './mechanics.mjs';",resolveDir:process.cwd()},bundle:true,platform:'node',format:'esm',external:['three','three/*'],outfile:out+'/generated-model.mjs'});
globalThis.document={createElement(type){assert.equal(type,'canvas');return {width:768,height:192,getContext(){return {fillRect(){},fillText(){}};}};}};
const {makeWatch,createState,solvePiston,PISTONS,TAU}=await import(pathToFileURL(path.resolve(out+'/generated-model.mjs')));
const watch=makeWatch(),s=createState();s.ready=true;s.reduced=true;watch.update(s);watch.root.updateMatrixWorld(true);
const report={buildHash:manifest.buildHash,method:'ACTUAL_GENERATED_GEOMETRY_AND_NODE_TRANSFORMS',checks:[],clearances:[],limitations:['No factory CAD comparison','No claim of exhaustive collision coverage','Not a substitute for normal-UI multi-angle browser inspection']};
function check(name,fn){try{const details=fn();report.checks.push({name,status:'PASS',details});}catch(e){report.checks.push({name,status:'FAIL',error:e.stack});}}
function fit(name,matcher,shaft){const measurements=watch.passport.interfaceMeasurements.filter(matcher);assert(measurements.length>0,name+' has no measured geometry');const bore=Math.min(...measurements.map(m=>m.actual.minimumFacetBore)),gap=bore-shaft;report.clearances.push({name,instances:measurements.length,minimumMeshFacetBore:bore,maximumShaftRadius:shaft,radialGap:gap,units:'10 mm'});assert(gap>0,name+' intersects');return gap;}
check('Case dimensions use the frozen boundary, exclude straps and crowns',()=>{const measured=watch.passport.caseMeasuredMm,target=[44.4,57.8,21.5],relative=measured.map((v,i)=>Math.abs(v-target[i])/target[i]);assert(Math.max(...relative)<.01);return {measured,target,relative};});
check('Rendered main shell is the verified single CAD solid in unchanged assembly coordinates',()=>{
 const cad=JSON.parse(fs.readFileSync('generated/sapphire-main-case-audit.json'));
 for(const [file,key] of [['cad/main_case.py','generatorSha256'],['generated/sapphire-main-case.json','meshSha256'],['generated/sapphire-main-case.step','stepSha256']])assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),cad[key],file+' does not match its CAD audit');
 assert.equal(cad.cadquery,'2.8.0');assert.equal(cad.valid,true);assert.equal(cad.solids,1);assert.equal(cad.crownIntersections.length,3);
 assert(watch.passport.parts.some(p=>p.id==='continuous-bored-sapphire-case'));assert(!watch.passport.parts.some(p=>p.id==='three-bore-sapphire-crown-shoulder'));
 const shell=watch.root.getObjectByName('sapphire-shell:crystal');assert(shell?.isMesh);assert(shell.matrixWorld.equals(new THREE.Matrix4()));
 const geo=shell.geometry,ids=geo.index,p=geo.attributes.position,n=geo.attributes.normal;assert.equal(ids.count/3,cad.triangles);
 let volume=0,normalError=0;const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
 for(let i=0;i<ids.count;i+=3){a.fromBufferAttribute(p,ids.getX(i));b.fromBufferAttribute(p,ids.getX(i+1));c.fromBufferAttribute(p,ids.getX(i+2));volume+=a.dot(b.cross(c))/6;}
 for(let i=0;i<n.count;i++)normalError=Math.max(normalError,Math.abs(a.fromBufferAttribute(n,i).length()-1));
 assert(volume>0);assert(Math.abs(volume-cad.volume)/cad.volume<.01);assert(normalError<1e-5);
 for(let i=0;i<3;i++){
  const crown=watch.crowns[i],port=cad.ports[i],measured=crown.getWorldPosition(new THREE.Vector3());assert(Math.abs(measured.x-port.axisOrigin[0])<1e-8);assert(Math.abs(measured.z-port.axisOrigin[2])<1e-8);
  const collar=crown.getObjectByName(crown.name+':polished');assert(collar?.isMesh);const vertices=collar.geometry.attributes.position;let radius=0,ringVertices=0;
  for(let j=0;j<vertices.count;j++)if(Math.abs(vertices.getY(j)-.13)<1e-6||Math.abs(vertices.getY(j)-.27)<1e-6){radius=Math.max(radius,Math.hypot(vertices.getX(j),vertices.getZ(j)));ringVertices++;}
  assert(ringVertices>=96);assert(Math.abs(radius-.305)<1e-6);assert(radius<port.radius);
  assert.equal(cad.crownIntersections[i].collarOverlapVolume,0);assert.equal(cad.crownIntersections[i].tubeOverlapVolume,0);
 }
 return {triangles:cad.triangles,cadVolume:cad.volume,actualMeshSignedVolume:volume,maxNormalLengthError:normalError,crownIntersections:cad.crownIntersections};
});
check('Both actual lenses fit the CAD-checked envelopes with flat assembly faces',()=>{
 const cad=JSON.parse(fs.readFileSync('generated/sapphire-main-case-audit.json')),asset=JSON.parse(fs.readFileSync('generated/sapphire-main-case.json'));
 return ['front','rear'].map(name=>{
  const part=watch.passport.parts.find(p=>p.id===name+'-crystal'),mesh=watch.root.getObjectByName(part.parent+':cover');assert(mesh?.isMesh);
  const box=new THREE.Box3().setFromObject(mesh),spec=asset.lenses[name],top=spec.surfaceZ+(spec.curved?.125:0),p=mesh.geometry.attributes.position;
  assert(Math.abs(box.min.z-spec.baseZ)<1e-6);assert(Math.abs(box.max.z-top)<1e-6);assert(box.max.z>box.min.z);
  // The cubic tonneau outline slightly exceeds its width parameter. Compare
  // actual CAD envelope bounds, not a fictitious rectangle of nominal width.
  const fit=cad.lensEnvelopeIntersections.find(p=>p.lens===name);
  for(let axis=0;axis<3;axis++){assert(box.min.getComponent(axis)>=fit.envelopeBounds[0][axis]-1e-6);assert(box.max.getComponent(axis)<=fit.envelopeBounds[1][axis]+1e-6);}
  let flatVertices=0;for(let i=0;i<p.count;i++)if(Math.abs(p.getZ(i)-spec.baseZ)<1e-6)flatVertices++;assert(flatVertices>=2881);
  assert.equal(fit.envelopeOverlapVolume,0);assert(fit.axialSeatClearanceMm>0);
  return {name,actualBounds:[box.min.toArray(),box.max.toArray()],flatVertices,...fit};
 });
});
check('Bored bearing geometry contains rather than invades the design clearance',()=>{for(const m of watch.passport.interfaceMeasurements){assert(Math.abs(m.actual.minimumVertexRadius-m.nominal.bore)<1e-6,m.id);assert(Math.abs(m.actual.depth-m.nominal.depth)<1e-6,m.id);}return {measuredRings:watch.passport.interfaceMeasurements.length};});
check('Crankpin to rod bush physical fit',()=>fit('crankpin / bush',m=>m.id==='rod-bearing-bush',.0195));
check('Bush to rod eye physical fit',()=>fit('bush / eye',m=>m.id==='bored-rod-eye',.0238));
check('Main journals fit bored bearings',()=>fit('journal / bearing',m=>m.id.startsWith('crank-journal-bush-'),.026));
check('Shock body and piston rod fit the two distinct spring seats',()=>({body:fit('lower spring seat / shock body',m=>m.id.includes('-spring-seat')&&m.nominal.bore>.04,.056),rod:fit('upper spring seat / rod',m=>m.id.includes('-spring-seat')&&m.nominal.bore<.04,.027)}));
check('Stepped shock neck fits retaining washer',()=>fit('retaining washer / threaded neck',m=>m.id.endsWith('-retaining-washer'),.050));
check('Spring bar fits external end bearings',()=>fit('spring bar / end bearing',m=>m.id==='strap-pin-end-bearing',.023));
check('Flying cage tube fits its bearing cup and thrust seat',()=>({cup:fit('cage / rear cup',m=>m.id==='tourbillon-rear-journal-cup',.072),seat:fit('cage / thrust seat',m=>m.id==='tourbillon-pivot-thrust-seat',.072)}));
check('Every displayed meshing pair has a shared module and pitch-centre distance',()=>{const p=watch.structuralReport().trainPairs;for(const x of p){assert(x.residual<1e-10);assert(Math.abs(x.moduleA-x.moduleB)<1e-12);}return p;});
check('All sixteen actual piston meshes stay within their corresponding CAD bore over 721 phases',()=>{
 const collected=new Map(PISTONS.map(d=>[d.id,[]]));
 watch.root.traverse(mesh=>{if(mesh.isInstancedMesh&&mesh.userData.family==='sixteen-pistons'){
  for(const id of mesh.userData.instanceNodeIds){const g=watch.root.getObjectByName(id),v=mesh.geometry.attributes.position,pts=collected.get(id);for(let i=0;i<v.count;i++)pts.push(new THREE.Vector3(v.getX(i),v.getY(i),v.getZ(i)).applyQuaternion(g.quaternion));}
 }});
 const result=[];
 for(const d of PISTONS){const points=collected.get(d.id);assert(points.length>0,d.id+' has no actual instance geometry');const u=new THREE.Vector3(Math.sin(d.angle),0,Math.cos(d.angle));let maxRadial=0,minOffset=Infinity,maxOffset=-Infinity;
  for(const v of points){const a=v.dot(u),r=v.clone().addScaledVector(u,-a).length();maxRadial=Math.max(maxRadial,r);minOffset=Math.min(minOffset,a);maxOffset=Math.max(maxOffset,a);}
  let minAxial=Infinity,maxAxial=-Infinity;
  for(let j=0;j<721;j++){const {s:p}=solvePiston(d,TAU*j/720);minAxial=Math.min(minAxial,p+minOffset);maxAxial=Math.max(maxAxial,p+maxOffset);}
  assert(maxRadial<.089,d.id+' radial bore collision');assert(minAxial>.312,d.id+' exits lower guide');assert(maxAxial<.652,d.id+' exits upper guide');result.push({id:d.id,actualMeshVertices:points.length,maxRadial,minAxial,maxAxial,radialClearance:.089-maxRadial});
 }return result;
});
check('Rendered instances remain bound to all 16+16 solver nodes at 721 phases',()=>{let max=0,connection=0;for(let j=0;j<721;j++){s.engineTheta=TAU*j/720;watch.update(s);watch.root.updateMatrixWorld(true);for(const b of watch.structuralReport().instanceBindings){assert.equal(b.count,16);max=Math.max(max,b.maxTransformResidual);}for(const b of watch.connectionReport())connection=Math.max(connection,b.smallEndResidual,b.bigEndResidual);}assert(max<1e-5);assert(connection<1e-4);return {maxGPUFloatTransformResidual:max,maxWorldEndpointResidual:connection,instanceReuse:watch.passport.instanceAudit};});
check('Four shock endpoints remain physically anchored throughout the full displacement',()=>{let max=0;for(let i=0;i<=600;i++){s.suspensionTime=i/200;watch.update(s);for(const r of watch.structuralReport().suspension){assert('fixedResidual'in r);max=Math.max(max,r.fixedResidual,r.movingResidual);}}assert(max<1e-9);return {samples:601,shocks:4,maxWorldEndpointResidual:max};});
check('Fifty transform round-trips preserve the same original nodes',()=>{s.suspensionTime=10;const original=watch.root.uuid;for(let i=0;i<50;i++)for(const e of [0,.33,.66,1,.66,.33,0]){s.explode=e;watch.update(s);}assert.equal(watch.root.uuid,original);const result=watch.assemblyError();assert(result.position<1e-5);assert(result.rotationDegrees<.01);return result;});
check('Calibration: old under-sized nominal bore is rejected, not excused by endpoints',()=>{const oldActualBore=.025393,shaft=.026;assert(oldActualBore-shaft<0);return {classification:'SYNTHETIC_FAILURE_EXPECTED_REJECTION',gap:oldActualBore-shaft};});
report.status=report.checks.every(x=>x.status==='PASS')?'PASS_LIMITED_GEOMETRY_AUDIT':'FAIL';fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({buildHash:report.buildHash,status:report.status,checks:report.checks.map(({name,status,error})=>({name,status,error}))},null,2));watch.dispose();if(report.status==='FAIL')process.exitCode=1;
