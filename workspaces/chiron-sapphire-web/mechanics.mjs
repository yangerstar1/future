/** Digital kinematics, NOT JCAM37 manufacturing parameters. Units: 10 mm. */
export const TAU = Math.PI * 2;
export const SPEC = Object.freeze({caseWidth:4.44,caseLength:5.78,caseThickness:2.15,
  engineDuration:15,balanceHz:3,cagePeriod:60,clockReserveHours:60,
  evidence:'ENGINEERING_APPROXIMATION',cagePeriodEvidence:'UNKNOWN; 60 s digital display approximation'});
const phase = [0, Math.PI, Math.PI/2, Math.PI*1.5, Math.PI, 0, Math.PI*1.5, Math.PI/2];
export const PISTONS = Object.freeze(Array.from({length:16},(_,i)=>{
  const station=Math.floor(i/2),side=i%2===0?-1:1;
  const angle=side*(station%2===0?1.00:0.43);
  return Object.freeze({id:`piston-${String(i+1).padStart(2,'0')}`,station,
    sharedPin:`crankpin-${station+1}`,bank:side<0?(station%2===0?0:1):(station%2===0?3:2),
    y:(station-3.5)*.205+side*.028,angle,phase:phase[station],radius:.068,length:.48,
    evidence:'ENGINEERING_APPROXIMATION'});
}));
export const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
export function solvePiston(def, theta){
  const phi=theta+def.phase;
  const c=[def.radius*Math.cos(phi),def.y,def.radius*Math.sin(phi)];
  const u=[Math.sin(def.angle),0,Math.cos(def.angle)];
  const a=u[0]*c[0]+u[2]*c[2];
  const radicand=def.length**2-(c[0]**2+c[2]**2-a*a);
  if(radicand<0)throw new RangeError(`${def.id}: no continuous slider-crank solution`);
  const s=a+Math.sqrt(radicand), p=[u[0]*s,def.y,u[2]*s];
  const residual=Math.abs(Math.hypot(...p.map((v,i)=>v-c[i]))-def.length)/def.length;
  return {id:def.id,c,p,u,s,residual,radicand};
}
export function verifyKinematics(samples=721){
  let maxResidual=0,minRadicand=Infinity,maxJump=0;
  for(const d of PISTONS){let prev=null;for(let j=0;j<samples;j++){
    const a=solvePiston(d,TAU*j/(samples-1));maxResidual=Math.max(maxResidual,a.residual);
    minRadicand=Math.min(minRadicand,a.radicand);if(prev)maxJump=Math.max(maxJump,Math.abs(a.s-prev.s));prev=a;
  }}return {samples,outputs:PISTONS.length,maxResidual,minRadicand,maxJump,pass:maxResidual<=1e-4&&minRadicand>=0};
}
export function createState(){return {ready:false,mode:'story',engine:'idle',engineTime:0,engineTheta:0,
  engineRate:1,engineEnergy:3,clockEnergy:1,clockSeconds:(10*3600+8*60),
  balanceTime:0,balanceRate:1,balancePaused:false,reduced:false,muted:true,
  explode:0,explodeTarget:0,crystalOff:false,selection:'all',suspensionTime:10,
  autoOrbit:false,light:'studio',starts:0};}
export function action(s,type,value){
  switch(type){
    case 'start':
      if(!s.ready)return 'The three-dimensional movement is not ready.';
      if(s.engine==='paused'){s.engine='running';return 'W16 resumed.';}
      if(s.engine==='running')return 'A single W16 cycle is already running.';
      if(s.engineEnergy<1){s.engine='exhausted';return 'Wind the automaton counterclockwise before starting.';}
      s.engineEnergy-=1;s.engineTime=0;s.engine='running';s.starts++;return 'W16 started. One 15-second simulation cycle.';
    case 'pause': if(s.engine==='running')s.engine='paused';else if(s.engine==='paused')s.engine='running';return `W16 ${s.engine}.`;
    case 'windEngine':s.engineEnergy=Math.min(3,s.engineEnergy+1);if(s.engine==='exhausted')s.engine='idle';return 'Automaton wound counterclockwise. One display cycle added.';
    case 'windClock':s.clockEnergy=clamp(s.clockEnergy+.25,0,1);return 'Timekeeping wound clockwise. Independent reserve increased.';
    case 'exhaust':s.engine='idle';s.engineEnergy=0;return 'Operation demonstration: automaton empty. Timekeeping reserve unchanged.';
    case 'phase':if(s.engine==='running')s.engine='paused';s.engineTheta=Math.floor(s.engineTheta/TAU)*TAU+clamp(Number(value)||0,0,360)/360*TAU;return 'Manual crank-phase inspection. Not a factory operating control.';
    case 'setTime': {const m=/^(\d{1,2}):(\d{2})$/.exec(value||'');if(!m||+m[1]>23||+m[2]>59)return 'Enter a valid time.';s.clockSeconds=+m[1]*3600+(+m[2])*60;return `Hands set to ${value}.`;}
    case 'restore':s.explodeTarget=0;s.crystalOff=false;s.selection='all';s.autoOrbit=false;return 'Same watch reassembled. Winding history preserved.';
    case 'isolate':s.selection=value;s.explodeTarget=0;return value==='all'?'Complete watch.':`${value==='engine'?'W16':'Tourbillon'} isolated — digital inspection.`;
    case 'explode':s.explodeTarget=clamp(Number(value)||0,0,1);s.selection='all';return 'Digital disassembly. Functional assemblies remain connected.';
    case 'suspension':s.suspensionTime=0;return 'Four-point suspension: bounded digital displacement demonstration.';
    default:return '';
  }
}
export function tick(s,dt){
  if(!Number.isFinite(dt)||dt<0||dt>.25)dt=0; // No wall-clock catch-up after a background interruption.
  if(s.clockEnergy>0){s.clockSeconds=(s.clockSeconds+dt)%86400;s.clockEnergy=Math.max(0,s.clockEnergy-dt/(SPEC.clockReserveHours*3600));}
  if(!s.balancePaused&&(!s.reduced||s.balanceRequested)&&s.clockEnergy>0)s.balanceTime+=dt*s.balanceRate;
  if(s.engine==='running'){
    const used=Math.min(dt*s.engineRate,SPEC.engineDuration-s.engineTime);
    s.engineTime+=used;s.engineTheta+=used*TAU*1.15;
    if(s.engineTime>=SPEC.engineDuration-1e-9){s.engineTime=SPEC.engineDuration;s.engine=s.engineEnergy>=1?'idle':'exhausted';}
  }
  const k=s.reduced?1:1-Math.exp(-dt*7);s.explode+=(s.explodeTarget-s.explode)*k;
  if(Math.abs(s.explodeTarget-s.explode)<1e-5)s.explode=s.explodeTarget;
  s.suspensionTime+=dt;
}
export function handAngles(seconds){const h=seconds/3600;return {hour:-TAU*(h%12)/12,minute:-TAU*((seconds/60)%60)/60};}
export function suspensionOffset(t){return t>3?0:.052*Math.exp(-t*2.5)*Math.sin(t*21);}
