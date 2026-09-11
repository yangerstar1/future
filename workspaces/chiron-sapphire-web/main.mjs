import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { makeWatch } from './watch.mjs';
import { createState, action, tick, clamp, verifyKinematics } from './mechanics.mjs';
const $=id=>document.getElementById(id),all=q=>[...document.querySelectorAll(q)];
const state=createState(),canvas=$('watch-canvas'),scene=new THREE.Scene();
let renderer,watch,controls,pmrem,env,lights,ao,lossExtension,raf=0,last=0,frames=[],totalFrames=0,contextLost=false,initializing=false;
let camera=new THREE.PerspectiveCamera(32,1,.035,100),cameraTween=null,savedScroll=0,savedFocus=null,lastUi=0,resizeTimer;
const target=new THREE.Vector3(),raycaster=new THREE.Raycaster();
const runtime={revision:'R02',backend:null,errors:[],contextLosses:0,contextRestores:0,initializations:0,hiddenEvents:0,network:[],uiEvents:[],resourceState:'loading',rafOutstanding:0};
const media=matchMedia('(prefers-reduced-motion: reduce)');state.reduced=media.matches;
const presets={hero:{p:[5.8,-8.4,12.2],t:[0,0,-.35]},front:{p:[0,0,17.5],t:[0,0,-.1]},back:{p:[0,0,-17.5],t:[0,0,-.1]},left:{p:[-17,0,0],t:[0,0,-.1]},right:{p:[17,0,0],t:[0,0,-.1]},engine:{p:[2.2,-3.25,3.25],t:[0,-1.15,.25]},tourbillon:{p:[1.05,2.25,2.72],t:[0,1.82,.38]}};
const chapters=all('.chapter'),nav=all('#chapter-nav a');
let storyBounds=[],activeChapter=0,needsRender=true,lastRender=0,renderIntervals=[];
const storyShots=[presets.hero,{p:[3.5,-3.7,7.7],t:[0,-.75,.1]},{p:[3.8,3.65,9.4],t:[0,1.05,.05]},{p:[7.4,-2.8,12.3],t:[0,0,0]},{p:[8,-3.8,15.8],t:[0,0,1.3]},{p:[-4.1,2.7,16.1],t:[0,0,-.2]},presets.hero];
function track(type,value){needsRender=true;runtime.uiEvents.push({time:performance.now(),type,value});if(runtime.uiEvents.length>1600)runtime.uiEvents.shift();}
function toast(text){$('toast').textContent=text;$('toast').classList.add('visible');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').classList.remove('visible'),4200);}
let ac;function sound(){if(state.muted)return;try{ac??=new AudioContext();ac.resume();const o=ac.createOscillator(),g=ac.createGain();o.type='triangle';o.frequency.value=420;g.gain.setValueAtTime(.018,ac.currentTime);g.gain.exponentialRampToValueAtTime(.0001,ac.currentTime+.055);o.connect(g).connect(ac.destination);o.start();o.stop(ac.currentTime+.06);}catch(e){runtime.errors.push('Audio unavailable: '+e.message);}}
function perform(type,value){track(type,value);sound();const msg=action(state,type,value);if(msg)toast(msg);ui();}
function disposeStudio(){
  if(lights){lights.traverse(l=>{l.shadow?.dispose();if(l.shadow){l.shadow.map=null;l.shadow.mapPass=null;}});scene.remove(lights);lights=null;}
  scene.environment=null;env?.dispose();env=null;
}
function createAO(){ao=new GTAOPass(scene,camera,512,512,undefined,{radius:.25,thickness:.08,distanceFallOff:.5,scale:1,samples:12},{radius:4,rings:2,samples:8});ao.output=GTAOPass.OUTPUT.Off;}
function physicalLights(){
  disposeStudio();
  lights=new THREE.Group();scene.add(lights);
  const hemi=new THREE.HemisphereLight(0xbad4e7,0x1b2025,1.0);lights.add(hemi);
  for(const [pos,color,intensity] of [[[4,8,10],0xf0f4ff,4], [[-6,1,5],0xd9ebff,2.2], [[3,-5,-7],0xffffff,4]]){const l=new THREE.DirectionalLight(color,intensity);l.position.set(...pos);if(!lights.children.some(c=>c.castShadow)){l.castShadow=true;l.shadow.mapSize.set(1536,1536);Object.assign(l.shadow.camera,{left:-5,right:5,top:6,bottom:-6,near:.5,far:35});l.shadow.normalBias=.009;l.shadow.bias=-.00003;}lights.add(l);}
  // Locally authored studio panels, no hidden third-party HDRI or network dependency.
  const room=new THREE.Scene();room.background=new THREE.Color(0x080b0f);
  const panel=(w,h,pos,intensity)=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color().setScalar(intensity),side:THREE.DoubleSide}));m.position.set(...pos);m.lookAt(0,0,0);room.add(m);};
  panel(3,10,[-8,3,5],4.8);panel(1.3,10,[8,-1,4],2.8);panel(8,2,[0,9,4],4);panel(2,9,[1,-3,-9],2.5);panel(10,1.5,[0,-8,0],.25);panel(11,7,[0,1,11],1.05);
  pmrem=new THREE.PMREMGenerator(renderer);env=pmrem.fromScene(room,.07,.1,40);scene.environment=env.texture;room.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});pmrem.dispose();
}
// Three.js 0.180.0 GTAO: only solid mechanical geometry contributes to the depth pass.
// Blend onto the antialiased scene, rather than making sapphire behave like opaque AO geometry.
function drawScene(){renderer.info.reset();renderer.shadowMap.needsUpdate=true;renderer.setRenderTarget(null);renderer.render(scene,camera);if(ao){const hidden=[];watch.root.traverse(o=>{if(o.isMesh&&o.visible&&o.material.transparent){hidden.push(o);o.visible=false;}});try{ao.render(renderer,null,null);}finally{for(const o of hidden)o.visible=true;}ao.blendMaterial.uniforms.intensity.value=state.light==='neutral'?.32:.72;ao.blendMaterial.uniforms.tDiffuse.value=ao.pdRenderTarget.texture;ao._renderPass(renderer,ao.blendMaterial,null);}renderer.setRenderTarget(null);}
function refreshLight(){if(!renderer)return;renderer.toneMappingExposure=state.light==='neutral'?1.14:.94;lights.children[0].intensity=state.light==='neutral'?2.8:1;for(let i=1;i<lights.children.length;i++)lights.children[i].intensity=(state.light==='neutral'?[3.0,2.6,2.6]:[4,2.2,4])[i-1];ui();}
function updateBounds(){storyBounds=chapters.map(el=>({top:el.offsetTop,height:el.offsetHeight}));}
function resize(){
  if(!renderer)return;const dockHeight=$('dock').offsetHeight;document.documentElement.style.setProperty('--dock-height',dockHeight+'px');const rect=$('stage').getBoundingClientRect(),w=rect.width,h=rect.height;renderer.setPixelRatio(Math.min(devicePixelRatio,1.35));renderer.setSize(w,h,false);ao?.setSize(Math.max(1,Math.round(w*.6)),Math.max(1,Math.round(h*.6)));camera.aspect=w/h;
  camera.clearViewOffset();if(state.mode==='story'){if(innerWidth<650)camera.setViewOffset(w,h,0,-h*.18,w,h);else camera.setViewOffset(w,h,-w*.19,0,w,h);}
  camera.updateProjectionMatrix();updateBounds();if(state.mode==='story')storyCamera(true);needsRender=true;
}
function adjusted(shot){const p=new THREE.Vector3(...shot.p),t=new THREE.Vector3(...shot.t);if(innerWidth<650&&state.mode==='story'){const f=state.selection!=='all'?1.1:1.72;p.sub(t).multiplyScalar(f).add(t);}if(innerHeight<500&&innerWidth>650&&state.mode==='story')p.sub(t).multiplyScalar(1.23).add(t);return{p,t};}
function goView(key,instant=false){const shot=adjusted(presets[key]||presets.hero);if(instant||state.reduced){camera.position.copy(shot.p);target.copy(shot.t);controls?.target.copy(target);camera.lookAt(target);cameraTween=null;}else cameraTween={from:camera.position.clone(),to:shot.p,tf:target.clone(),tt:shot.t,start:performance.now(),duration:850};
  controls.minDistance=state.selection==='all'?4.7:.85;controls.maxDistance=state.selection==='all'?34:13;
  controls.update();$('view-label').textContent=key==='engine'?'W16 / DIGITAL KINEMATIC STUDY':key==='tourbillon'?'TOURBILLON / REGULATOR STUDY':`${key==='hero'?'The complete object':key+' inspection'} · Clear sapphire`;
  all('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===key)));track('view',key);
}
function storyCamera(instant=false){if(state.mode!=='story'||!state.ready)return;
  const y=scrollY+innerHeight*.28;let idx=0;for(let i=0;i<storyBounds.length;i++)if(y>=storyBounds[i].top)idx=i;
  const b=storyBounds[idx],u=clamp((y-b.top)/b.height,0,1),blend=state.reduced?0:clamp((u-.7)/.3,0,1),v=blend*blend*(3-2*blend);
  const a=adjusted(storyShots[idx]),n=adjusted(storyShots[Math.min(idx+1,6)]);a.p.lerp(n.p,v);a.t.lerp(n.t,v);
  if(instant||state.reduced){camera.position.copy(a.p);target.copy(a.t);}else{camera.position.lerp(a.p,.095);target.lerp(a.t,.095);}camera.lookAt(target);controls.target.copy(target);
  if(idx!==activeChapter){activeChapter=idx;nav.forEach((a,i)=>a.classList.toggle('active',i===idx));}
}
function enter(selection='all'){
  if(!state.ready){toast('The 3D movement is not ready. Product information remains available.');return;}
  if(state.mode==='story'){for(const [id,btn] of [['anatomy-panel','anatomy-toggle'],['crown-panel','crown-toggle']]){$(id).hidden=true;$(btn).setAttribute('aria-expanded','false');}savedScroll=scrollY;savedFocus=document.activeElement;state.mode='explore';document.body.classList.add('exploring');$('explorer').hidden=false;$('story').inert=true;$('site-header').inert=true;$('chapter-nav').inert=true;}
  perform('isolate',selection);controls.enabled=true;resize();goView(selection==='all'?'hero':selection);$('watch-canvas').focus({preventScroll:true});
}
function exit(){if(state.mode!=='explore')return;perform('restore');state.mode='story';controls.enabled=false;cameraTween=null;document.body.classList.remove('exploring');$('explorer').hidden=true;$('story').inert=false;$('site-header').inert=false;$('chapter-nav').inert=false;scrollTo({top:savedScroll,behavior:'instant'});resize();savedFocus?.focus({preventScroll:true});}
function togglePanel(id,btn){const el=$(id),isOpen=el.hidden;if(isOpen)for(const [other,otherBtn] of [['anatomy-panel','anatomy-toggle'],['crown-panel','crown-toggle']])if(other!==id){$(other).hidden=true;$(otherBtn).setAttribute('aria-expanded','false');}el.hidden=!isOpen;$(btn).setAttribute('aria-expanded',String(isOpen));track('panel',id+':'+isOpen);resize();}
function ui(){
  all('[data-do]').forEach(b=>{b.disabled=b.dataset.do!=='exit'&&(!state.ready||contextLost);});
  $('crank-phase-value').textContent=((state.engineTheta%(Math.PI*2))*180/Math.PI).toFixed(1)+'°';
  for(const id of ['crank-phase','phase-degrees'])if(document.activeElement!==$(id))$(id).value=((state.engineTheta%(Math.PI*2))*180/Math.PI).toFixed(1);
  for(const id of ['explode','story-explode'])if(document.activeElement!==$(id))$(id).value=Math.round(state.explodeTarget*100);
  for(const id of ['explode-value','story-explode-value'])$(id).textContent=Math.round(state.explode*100)+'%';
  $('reserve-status').textContent=`W16: ${state.engineEnergy} display cycle${state.engineEnergy===1?'':'s'} · Timekeeping: ${(state.clockEnergy*100).toFixed(0)}% · ${state.engine} ${state.engineTime.toFixed(1)} / 15 s`;
  $('pause-control').textContent=state.engine==='paused'?'Resume W16 ▷':'Pause W16 Ⅱ';$('pause-control').setAttribute('aria-pressed',String(state.engine==='paused'));
  $('crystal-control').textContent=state.crystalOff?'Crystal on':'Crystal off';$('crystal-control').setAttribute('aria-pressed',String(state.crystalOff));
  $('motion-toggle').textContent=state.reduced?'Motion: reduced':'Motion: full';$('motion-toggle').setAttribute('aria-pressed',String(state.reduced));document.body.classList.toggle('reduced',state.reduced);
  $('sound-toggle').textContent=state.muted?'Sound: off':'Sound: digital';$('sound-toggle').setAttribute('aria-pressed',String(!state.muted));
  $('light-toggle').textContent='Light: '+state.light;$('light-toggle').setAttribute('aria-pressed',String(state.light==='neutral'));
  all('[data-do="start"]').forEach(b=>b.setAttribute('aria-pressed',String(state.engine==='running')));
}
all('[data-do]').forEach(b=>b.addEventListener('click',()=>{
  switch(b.dataset.do){
    case 'explore':enter();break;case 'exit':exit();break;
    case 'inspect-engine':enter('engine');break;case 'inspect-tourbillon':enter('tourbillon');break;
    case 'crystal':state.crystalOff=!state.crystalOff;track('crystal',state.crystalOff);toast(state.crystalOff?'Sapphire digitally removed.':'Sapphire restored.');break;
    case 'disassemble':perform('explode',1);break;
    case 'restore':perform('restore');if(state.mode==='explore')goView('hero');break;
    default:perform(b.dataset.do);
  }ui();
}));
all('[data-view]').forEach(b=>b.addEventListener('click',()=>{perform('isolate','all');goView(b.dataset.view);}));
for(const id of ['explode','story-explode'])$(id).addEventListener('input',e=>{perform('explode',+e.target.value/100);});
$('anatomy-toggle').addEventListener('click',()=>togglePanel('anatomy-panel','anatomy-toggle'));
$('crown-toggle').addEventListener('click',()=>togglePanel('crown-panel','crown-toggle'));
$('set-time-apply').addEventListener('click',()=>perform('setTime',$('set-time').value));
for(const id of ['crank-phase','phase-degrees'])$(id).addEventListener('input',e=>perform('phase',e.target.value));
$('engine-rate').addEventListener('change',e=>{state.engineRate=+e.target.value;track('engine-rate',state.engineRate);toast(`W16 observation at ${state.engineRate}×. A cycle still contains 15 simulated seconds.`);});
$('balance-rate').addEventListener('change',e=>{state.balanceRate=+e.target.value;state.balancePaused=state.balanceRate===0;state.balanceRequested=true;track('balance-rate',state.balanceRate);toast('Regulator observation changed. Displayed clock time is unaffected.');});
$('motion-toggle').addEventListener('click',()=>{state.reduced=!state.reduced;state.balanceRequested=false;track('reduced',state.reduced);ui();});
$('sound-toggle').addEventListener('click',()=>{state.muted=!state.muted;track('muted',state.muted);sound();ui();});
$('light-toggle').addEventListener('click',()=>{state.light=state.light==='studio'?'neutral':'studio';refreshLight();track('light',state.light);});
media.addEventListener('change',e=>{state.reduced=e.matches;state.balanceRequested=false;ui();});
canvas.addEventListener('keydown',e=>{
  if(state.mode!=='explore')return;if(e.key==='Escape'){e.preventDefault();exit();return;}
  if(e.key.toLowerCase()==='r'){e.preventDefault();perform('restore');goView('hero');return;}
  if(['f','b'].includes(e.key.toLowerCase())){perform('isolate','all');goView(e.key.toLowerCase()==='f'?'front':'back');return;}
  if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(e.key)){
    e.preventDefault();cameraTween=null;const v=camera.position.clone().sub(controls.target),sp=new THREE.Spherical().setFromVector3(v);
    if(e.key==='ArrowLeft')sp.theta-=.11;if(e.key==='ArrowRight')sp.theta+=.11;if(e.key==='ArrowUp')sp.phi-=.09;if(e.key==='ArrowDown')sp.phi+=.09;if(e.key==='+'||e.key==='=')sp.radius*=.88;if(e.key==='-')sp.radius*=1.12;sp.phi=clamp(sp.phi,.015,Math.PI-.015);sp.radius=clamp(sp.radius,controls.minDistance,controls.maxDistance);camera.position.setFromSpherical(sp).add(controls.target);controls.update();target.copy(controls.target);track('keyboard',e.key);
  }
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&state.mode==='explore'&&e.target!==canvas)exit();});
let down=null;canvas.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY};cameraTween=null;});
canvas.addEventListener('pointerup',e=>{if(state.mode!=='explore'||!down||Math.hypot(e.clientX-down.x,e.clientY-down.y)>6||state.selection!=='all')return;
  const rect=canvas.getBoundingClientRect(),p=new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(p,camera);const hits=raycaster.intersectObjects(watch.crowns,true);if(!hits.length)return;let o=hits[0].object;while(o&&!watch.crowns.includes(o))o=o.parent;const i=watch.crowns.indexOf(o);if(i===2)perform('start');else if(i>=0){$('crown-panel').hidden=false;$('crown-toggle').setAttribute('aria-expanded','true');if(i===0)$('set-time').focus();else toast('Centre crown: clockwise winds timekeeping; counterclockwise winds W16.');}track('crown-hit',i);
});
function fail(e){state.ready=false;runtime.resourceState='failed';runtime.errors.push(String(e?.message||e));$('load-state').hidden=true;$('fallback').hidden=false;$('failure-reason').textContent=e?.message||String(e);if(state.mode==='explore')exit();ui();}
function frame(now){raf=0;runtime.rafOutstanding=0;if(document.hidden||contextLost||!state.ready)return;
  const dt=last?(now-last)/1000:0;last=now;if(dt>0){frames.push(dt*1000);if(frames.length>6000)frames.shift();}
  for(let left=Math.min(dt,10);left>1e-7;left-=.05)tick(state,Math.min(left,.05));watch.update(state);controls.minDistance=state.selection==='all'?4.7+state.explode*3.2:.85;const beforeCamera=camera.position.clone();
  if(state.mode==='story')storyCamera();else if(cameraTween){const v=clamp((now-cameraTween.start)/cameraTween.duration,0,1),t=v*v*(3-2*v);camera.position.lerpVectors(cameraTween.from,cameraTween.to,t);target.lerpVectors(cameraTween.tf,cameraTween.tt,t);controls.target.copy(target);camera.lookAt(target);if(v===1)cameraTween=null;}else{controls.update();target.copy(controls.target);}
  const animating=state.engine==='running'||Math.abs(state.explode-state.explodeTarget)>.00001||state.suspensionTime<3||(!state.balancePaused&&(!state.reduced||state.balanceRequested)&&state.clockEnergy>0);
  if(needsRender||animating||cameraTween||beforeCamera.distanceToSquared(camera.position)>1e-9||now-lastRender>1000){drawScene();if(lastRender){renderIntervals.push(now-lastRender);if(renderIntervals.length>6000)renderIntervals.shift();}lastRender=now;totalFrames++;needsRender=false;}if(now-lastUi>140){ui();updateHotspots();lastUi=now;}schedule();
}
function schedule(){if(!raf&&state.ready&&!document.hidden&&!contextLost){raf=requestAnimationFrame(frame);runtime.rafOutstanding=1;}}
document.addEventListener('visibilitychange',()=>{if(document.hidden){runtime.hiddenEvents++;cancelAnimationFrame(raf);raf=0;runtime.rafOutstanding=0;}else{last=0;schedule();}});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;runtime.resourceState='context-lost';runtime.contextLosses++;disposeStudio();ao?.dispose();ao=null;cancelAnimationFrame(raf);raf=0;runtime.rafOutstanding=0;$('fallback').hidden=false;$('failure-reason').textContent='Graphics context lost. Your watch state is preserved. Restore graphics or retry the view.';ui();});
canvas.addEventListener('webglcontextrestored',()=>{setTimeout(()=>{try{physicalLights();createAO();resize();refreshLight();lossExtension=renderer.getContext().getExtension('WEBGL_lose_context');contextLost=false;runtime.resourceState='ready';runtime.contextRestores++;$('fallback').hidden=true;last=0;needsRender=true;ui();schedule();}catch(e){fail(e);}},0);});
window.addEventListener('scroll',()=>{needsRender=true;},{passive:true});
window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(resize,75);});
new ResizeObserver(()=>{if(state.mode==='explore')resize();}).observe($('dock'));
$('retry').addEventListener('click',()=>{if(contextLost){if(lossExtension)lossExtension.restoreContext();else{$('failure-reason').textContent='The graphics driver cannot restore this context. Reloading starts a fresh digital demonstration.';location.reload();}return;}init();});
async function init(){if(initializing||state.ready)return;initializing=true;$('fallback').hidden=true;$('load-state').hidden=false;runtime.resourceState='loading';
  try{
    $('load-text').textContent='Loading the documented movement parameters…';let config=window.__INLINE_MECHANISM__;
    if(!config){const r=await fetch('./mechanism.json',{cache:'no-store'});runtime.network.push({url:r.url,status:r.status});if(!r.ok)throw new Error(`Movement parameters could not be loaded (HTTP ${r.status}). Product information is available below; retry to restore 3D.`);config=await r.json();}
    if(config.pistons?.length!==16)throw new Error('Movement parameters are incomplete. The 16-piston mechanism was not substituted.');
    if(!renderer){renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'high-performance'});renderer.info.autoReset=false;renderer.shadowMap.enabled=true;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.transmissionResolutionScale=.75;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.setClearColor(0x090c10,0);physicalLights();createAO();controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.08;controls.enablePan=true;controls.screenSpacePanning=true;controls.enableZoom=true;controls.enabled=false;controls.addEventListener('start',()=>{cameraTween=null;});controls.addEventListener('change',()=>{needsRender=true;});
      const gl=renderer.getContext(),dbg=gl.getExtension('WEBGL_debug_renderer_info');lossExtension=gl.getExtension('WEBGL_lose_context');runtime.backend={vendor:dbg?gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL):gl.getParameter(gl.VENDOR),renderer:dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),version:gl.getParameter(gl.VERSION)};
    }
    $('load-text').textContent='Constructing editable geometry and linked mechanical assemblies…';await new Promise(r=>setTimeout(r,20));
    if(!watch){watch=makeWatch();scene.add(watch.root);}state.ready=true;runtime.initializations++;runtime.resourceState='ready';watch.update(state);resize();refreshLight();drawScene();$('load-state').hidden=true;last=0;schedule();
  }catch(e){fail(e);}finally{initializing=false;}
}
function updateHotspots(){const layer=$('hotspot-layer');layer.hidden=state.mode!=='explore'||state.selection!=='all'||!state.ready||state.explode>.05;if(layer.hidden||!watch)return;for(const key of ['engine','tourbillon']){const obj=watch.locations[key],point=obj.localToWorld(new THREE.Vector3(0,0,key==='engine'?.66:.26)),screen=point.clone().project(camera),b=$('hotspot-'+key),dir=point.clone().sub(camera.position),length=dir.length();raycaster.set(camera.position,dir.normalize());raycaster.far=length-.04;const hits=raycaster.intersectObject(watch.root,true);const obstructed=hits.some(h=>{if(h.object.material.transparent||!h.object.visible)return false;let p=h.object;while(p){if(p===obj)return false;if(!p.visible)return false;p=p.parent;}return true;});const rect=canvas.getBoundingClientRect(),x=rect.left+(screen.x*.5+.5)*rect.width,y=rect.top+(-screen.y*.5+.5)*rect.height;b.hidden=obstructed||screen.z>1||x<32||x>innerWidth-32||y<90||y>rect.bottom-22;b.style.transform=`translate(${x-22}px,${y-22}px)`;}raycaster.far=Infinity;}
window.__chiron={
  snapshot(){return {revision:runtime.revision,state:{...state},runtime:{...runtime,uiEvents:[...runtime.uiEvents]},camera:{position:camera.position.toArray(),target:controls?.target.toArray(),near:camera.near,far:camera.far,fov:camera.fov,view:camera.view},viewport:{width:innerWidth,height:innerHeight,canvas:{x:canvas.getBoundingClientRect().x,y:canvas.getBoundingClientRect().y,width:canvas.clientWidth,height:canvas.clientHeight},dpr:renderer?.getPixelRatio()},renderer:renderer?{calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,memory:{...renderer.info.memory}}:null,assemblyError:watch?.assemblyError(),totalFrames,frameIntervals:[...frames],renderIntervals:[...renderIntervals]};},
  passport(){return watch?.passport;},
  constraints:verifyKinematics,
  connections(){return watch?.connectionReport();},
  async exportGLB(){if(!watch)throw new Error('No asset');return await new GLTFExporter().parseAsync(watch.root,{binary:true,onlyVisible:false,trs:true});}
};
window.addEventListener('error',e=>runtime.errors.push(e.message));window.addEventListener('unhandledrejection',e=>runtime.errors.push(String(e.reason)));
ui();init();
