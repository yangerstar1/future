/**
 * Visible mechanical architecture, R04. References: the two official bare-JCAM37
 * front/back photographs registered in REFERENCES.md. Contours, bearing dimensions
 * and concealed gear topology below are authored, documented display approximations,
 * not factory CAD. No decorative/random gear scatter is used.
 */
import * as THREE from 'three';
const TAU=Math.PI*2;

export function craftTools(c){
 const {V,mat,mesh,extrude,box,cyl,ring,bar,screw}=c;
 function polygon(points){const s=new THREE.Shape();s.moveTo(...points[0]);for(const p of points.slice(1))s.lineTo(...p);s.closePath();return s;}
 function plate(parent,name,points,z,depth=.085,m=mat.rhodium,holes=[]){
  const s=polygon(points);
  for(const h of holes){const p=new THREE.Path();if(h.length===3&&typeof h[0]==='number')p.absarc(h[0],h[1],h[2],0,TAU,true);else{p.moveTo(...h[0]);for(const v of h.slice(1))p.lineTo(...v);p.closePath();}s.holes.push(p);}
  return extrude(parent,s,depth,z,m,Math.min(.012,depth*.15),name);
 }
 function washer(parent,x,y,z,outer,inner,depth=.035,m=mat.polished,axis='z',name='annular-bearing'){
  if(!(outer>inner&&inner>0&&depth>0))throw new Error('Invalid annular bearing dimensions: '+name);
  const b=Math.min(.003,(outer-inner)*.12,depth*.15),h=depth/2;
  const profile=[[inner,-h+b],[inner+b,-h],[outer-b,-h],[outer,-h+b],[outer,h-b],[outer-b,h],[inner+b,h],[inner,h-b],[inner,-h+b]];
  const segments=outer>.15?64:40,g=new THREE.LatheGeometry(profile.map(([r,v])=>new THREE.Vector2(r,v)),segments);
  const o=mesh(parent,g,m,name,V(x,y,z));if(axis==='z')o.rotation.x=Math.PI/2;if(axis==='x')o.rotation.z=-Math.PI/2;
  let minR=Infinity,maxR=0,minY=Infinity,maxY=-Infinity;const p=g.attributes.position;
  for(let i=0;i<p.count;i++){const r=Math.hypot(p.getX(i),p.getZ(i));minR=Math.min(minR,r);maxR=Math.max(maxR,r);minY=Math.min(minY,p.getY(i));maxY=Math.max(maxY,p.getY(i));}
  c.interfaceMeasurements?.push({id:name,axis,nominal:{bore:inner,outer,depth},actual:{minimumVertexRadius:minR,minimumFacetBore:minR*Math.cos(Math.PI/segments),maximumRadius:maxR,depth:maxY-minY},bevelContained:true});
  return o;
 }
 function turned(parent,name,x,y,z,profile,m=mat.polished,axis='z'){
  const g=new THREE.LatheGeometry(profile.map(([r,v])=>new THREE.Vector2(r,v)),48);const o=mesh(parent,g,m,name,V(x,y,z));if(axis==='z')o.rotation.x=Math.PI/2;if(axis==='x')o.rotation.z=-Math.PI/2;return o;
 }
 function post(parent,name,x,y,z0,z1,r=.07){
  const h=Math.abs(z1-z0)/2,f=Math.min(.036,h*.20),b=Math.min(.008,f*.30);
  return turned(parent,name,x,y,(z0+z1)/2,[[0,-h],[r*1.45-b,-h],[r*1.45,-h+b],[r*1.45,-h+f-b],[r,-h+f],[r,h-f],[r*1.45,h-f+b],[r*1.45,h-b],[r*1.45-b,h],[0,h]],mat.brushed);
 }
 function leaf(parent,name,pts,z,width=.017,m=mat.polished){
  const curve=new THREE.CatmullRomCurve3(pts.map(([x,y])=>V(x,y,z)));return mesh(parent,new THREE.TubeGeometry(curve,48,width,4,false),m,name);
 }
 function bearing(parent,name,x,y,z,r=.07){
  // The ruby sits IN a stepped counterbore, on the shoulder. Separate solids
  // must not overlap just because their animation pivots agree.
  turned(parent,name+'-stepped-chaton',x,y,z,[[r*.70,-.030],[r*1.62,-.030],[r*1.70,-.025],[r*1.70,.030],[r*1.60,.036],[r*1.02,.036],[r*1.02,.014],[r*.70,.014],[r*.70,-.030]],mat.brushed);
  washer(parent,x,y,z+.024,r,r*.28,.020,mat.ruby,'z',name+'-bored-jewel');
  cyl(parent,x,y,z+.011,r*.25,.076,mat.polished,'z',name+'-pivot',24);
 }
 return {polygon,plate,washer,turned,post,leaf,bearing};
}

export function chassis(c,base,power){
 const {V,mat,group,box,cyl,ring,bar,pathTube,screw,jewel,gear,flatLabel,rim,batchGroups}=c;
 const {plate,washer,turned,post,leaf,bearing}=craftTools(c),wheels=[];
 // The outer black frame carries ALL internal bridge feet. A lower tier provides
 // bearing material between the open front skeleton and the finished caseback.
 rim(base,3.52,4.81,3.08,4.33,.17,-.61,mat.dark,.040,'continuous-movement-frame');
 for(const x of [-1.52,1.52]){
  box(base,x,0,-.42,.18,3.92,.22,mat.dark,.034,'chassis-side-wall');
  box(base,x,0,-.27,.058,3.80,.043,mat.brushed,.010,'rail-machined-edge');
 }
 plate(base,'upper-carrier-deck',[[-1.5,1.38],[-1.42,2.18],[-.78,2.28],[.78,2.28],[1.42,2.18],[1.5,1.38],[.89,1.33],[.68,1.62],[-.68,1.62],[-.89,1.33]],-.56,.14,mat.dark,
  [[[-1.25,1.55],[-1.22,2.06],[-.88,2.07],[-.90,1.72]],[[1.25,1.55],[1.22,2.06],[.88,2.07],[.90,1.72]]]);
 plate(base,'lower-keyless-deck',[[-1.48,-2.22],[1.48,-2.22],[1.52,-1.35],[1.13,-1.17],[.72,-1.50],[-.66,-1.50],[-1.11,-1.17],[-1.52,-1.35]],-.55,.13,mat.dark,
  [[[-1.28,-2.05],[-.83,-2.05],[-.83,-1.67],[-1.18,-1.50]],[[1.28,-2.05],[.83,-2.05],[.83,-1.67],[1.18,-1.50]],[0,-1.86,.18]]);
 for(const y of [-2.20,2.16]){box(base,0,y,-.45,2.89,.13,.17,mat.rhodium,.025,'frame-crossmember');for(const x of [-1.35,-.56,.56,1.35]){screw(base,x,y,-.347,.046);screw(base,x,y,-.559,.045,true);}}
 // Barrel axles are held by the shared frame, not merely parented to a rotating wheel.
 for(const x of [-1.035,1.035]){
  plate(power,'barrel-fixed-saddle-'+x,[[x-.30,.34],[x+.30,.34],[x+.34,-.21],[x+.15,-.33],[x-.20,-.33],[x-.34,-.21]],-.53,.105,mat.dark,[[x,.065,.085]]);
  for(const sy of [-.26,.39]){bar(power,V(x,sy,-.48),V(Math.sign(x)*1.51,sy,-.48),.064,mat.brushed,'saddle-to-rail-'+x);screw(power,Math.sign(x)*1.48,sy,-.387,.052);}
  cyl(power,x,.065,-.56,.010,.64,mat.polished,'z','fixed-barrel-arbor');
  bearing(power,'barrel-front-journal',x,.065,-.264,.054);
  const g=gear(power,x,.065,-.63,.705,88,mat.rhodium,14);g.name=x<0?'timekeeping-barrel':'automaton-barrel';
  wheels.push({g,rate:x<0?.012:.018,domain:x<0?'clock':'engine'});
  washer(g,0,0,.298,.673,.598,.033,mat.rhodium,'z','barrel-front-skeleton-rim');
  washer(g,0,0,.292,.095,.012,.066,mat.brushed,'z','barrel-front-bored-hub');
  for(let i=0;i<14;i++){
   const a=i/14*TAU,points=[];
   for(const [r,t] of [[.076,-.08],[.30,-.033],[.625,-.013],[.625,.013],[.30,.033],[.076,.08]])points.push([Math.cos(a+t)*r,Math.sin(a+t)*r]);
   plate(g,'barrel-front-spoke',points,.282,.026,mat.rhodium);
   if(i%2===0)bar(g,V(Math.cos(a)*.629,Math.sin(a)*.629,-.016),V(Math.cos(a)*.629,Math.sin(a)*.629,.290),.018,mat.brushed,'barrel-axial-spacer');
  }

  // Solid turned caseback drum: this is deliberately NOT an open spoke disc on both faces.
  turned(g,'turned-barrel-drum',0,0,-.010,[[.012,-.008],[.56,-.008],[.636,-.018],[.659,-.035],[.659,-.133],[.642,-.150],[.56,-.156],[.012,-.156],[.012,-.008]],mat.brushed);
  washer(g,0,0,-.164,.607,.50,.014,mat.polished,'z','barrel-cover-annulus');
  const ratchet=gear(g,0,0,-.202,.446,46,mat.polished,6);washer(ratchet,0,0,-.033,.367,.012,.045,mat.brushed,'z','ratchet-bored-web');
  washer(ratchet,0,0,-.062,.121,.055,.019,mat.polished);screw(ratchet,0,0,-.090,.052,true);
  for(const [xx,yy] of [[-.125,-.07],[.12,-.07],[0,.17]])screw(ratchet,xx,yy,-.071,.053,true);
  for(const a0 of [1.25,4.40]){
   const pts=[];for(let j=0;j<=18;j++){const a=a0+j/18*.88;pts.push([Math.cos(a)*.58,Math.sin(a)*.58]);}for(let j=18;j>=0;j--){const a=a0+j/18*.88;pts.push([Math.cos(a)*.475,Math.sin(a)*.475]);}
   plate(g,'curved-barrel-retainer',pts,-.186,.022,mat.rhodium);
   screw(g,Math.cos(a0+.16)*.535,Math.sin(a0+.16)*.535,-.217,.035,true);
  }
  for(let i=0;i<4;i++){const a=TAU*i/4+.29;washer(g,Math.cos(a)*.529,Math.sin(a)*.529,-.17,.046,.027,.012,mat.brushed);screw(g,Math.cos(a)*.529,Math.sin(a)*.529,-.182,.032,true);}
  for(const a of [1.15,3.70]){const px=x+Math.cos(a)*.58,py=.065+Math.sin(a)*.58;screw(power,px,py,-.865,.041,true);}
  // A fixed click, its pivot and spring; its free tip terminates on the ratchet ring.
  const sign=Math.sign(x),px=x-sign*.50,py=.50;
  plate(power,'barrel-click-'+x,[[px-.035,py-.09],[px+.052,py-.09],[x+sign*.29,.30],[x+sign*.25,.38],[px+.035,py+.045],[px-.035,py+.045]],-.852,.028,mat.polished);
  screw(power,px,py,-.887,.037,true);
  leaf(power,'barrel-click-leaf-'+x,[[x-sign*.56,-.10],[x-sign*.53,.29],[px,py-.02]],-.824,.010,mat.polished);
 }
 // Two SEPARATE compound trains. The radii/axles are derived, rather than random
 // decorative wheels. Front-visible wheels are silver; small brass pinions below.
 const trains=[
  {domain:'clock',start:[-1.035,.065,.705,88],angles:[1.11,.42,.89],gears:[[.269,32],[.196,23],[.164,19]]},
  {domain:'engine',start:[1.035,.065,.705,88],angles:[-1.35,-2.85,-2.34],gears:[[.230,27],[.198,23],[.178,21]]},
 ];
 const trainPairs=[];
 for(const t of trains){let phi=0;let [px,py,pr,pn]=t.start,rate=t.domain==='clock'?.012:.018;const module=2*pr/(pn+2);
  for(let i=0;i<t.gears.length;i++){
   const n=t.gears[i][1],r=module*(n+2)/2,a=t.angles[i],d=pr*pn/(pn+2)+r*n/(n+2),x=px+Math.cos(a)*d,y=py+Math.sin(a)*d;
   const g=gear(power,x,y,-.628,r,n,mat.rhodium,6);g.name=t.domain+'-train-wheel-'+i;rate*=-pn/n;const nextPhi=a+Math.PI-(Math.PI-pn*(a-phi))/n;wheels.push({g,rate,domain:t.domain,offset:nextPhi});phi=nextPhi;
   washer(g,0,0,.071,Math.max(r*.26,.025),.012,.09,mat.brass,'z','integral-bored-pinion-'+i);washer(power,x,y,-.49,.064,.027,.048,mat.brushed,'z','pinion-counterbore');
   bearing(power,'train-bearing-'+t.domain+'-'+i,x,y,-.399,.036);
   const railX=Math.sign(x||1)*1.51,attachment=V(railX,y,-.48);
   bar(power,attachment,V(x,y,-.48),.042,mat.dark,'train-bridge-web');screw(power,railX,y,-.395,.039);
   cyl(power,x,y,-.67,.0085,.39,mat.polished,'z','train-through-arbor',24);washer(power,x,y,-.868,.060,.025,.036,mat.rhodium);jewel(power,x,y,-.891,.033,true);
   trainPairs.push({domain:t.domain,index:i,centerA:[px,py],centerB:[x,y],pitchA:pr*pn/(pn+2),pitchB:r*n/(n+2),teeth:[pn,n],moduleA:2*pr/(pn+2),moduleB:2*r/(n+2),centerDistance:d});
   px=x;py=y;pr=r;pn=n;
  }
 }
 // Back signature bridge: open triangular windows, bevelled edges and real feet.
 plate(power,'rear-signature-bridge',[[-1.13,2.06],[1.13,2.06],[1.17,1.33],[.43,1.16],[-.43,1.16],[-1.17,1.33]],-.825,.105,mat.dark,
  [[[-.98,1.91],[-.64,1.91],[-.98,1.64]],[[-.52,1.91],[-.52,1.66],[-.22,1.91]],[[.98,1.91],[.64,1.91],[.98,1.64]],[[.52,1.91],[.52,1.66],[.22,1.91]],[[-.99,1.51],[-.99,1.36],[-.61,1.36],[-.72,1.51]],[[.99,1.51],[.99,1.36],[.61,1.36],[.72,1.51]]]);
 for(const sign of [-1,1]){bar(power,V(sign*1.10,1.79,-.77),V(sign*1.51,1.79,-.52),.079,mat.brushed,'signature-bridge-foot');screw(power,sign*1.03,1.41,-.856,.072,true);}
 const brand=flatLabel(power,'JACOB & CO.',0,1.675,-.842,1.12,.22,'#59a3c1','#181d23');brand.rotation.y=Math.PI;
 const swiss=flatLabel(power,'SWISS MADE',0,1.407,-.844,.61,.068,'#6f9fb4','#181d23');swiss.rotation.y=Math.PI;
 plate(power,'rear-centre-bearing-bridge',[[-.25,1.26],[.26,1.26],[.22,.72],[.17,.29],[.28,-.12],[.39,-.44],[.40,-.75],[.19,-.95],[-.22,-.95],[-.40,-.73],[-.28,-.28],[-.16,.34],[-.20,.79]],-.905,.088,mat.dark,
  [[0,.88,.070],[0,-.55,.081]]);
 jewel(power,0,.87,-.933,.045,true);jewel(power,0,-.55,-.939,.051,true);screw(power,.265,-.828,-.943,.061,true);
 // Visible lower keyless works and return spring. Axles reach frame material on
 // both faces; bridges end on the rail/deck instead of in empty space.
 const rearWorks=group(power,'rear-keyless-works',true);rearWorks.scale.x=-1;
 plate(rearWorks,'keyless-triangular-bridge',[[-1.22,-1.20],[-.34,-1.03],[-.17,-1.94],[-1.35,-1.94]],-.83,.115,mat.brushed,
  [[[-1.07,-1.79],[-.71,-1.32],[-.38,-1.79]],[[-1.13,-1.53],[-1.10,-1.34],[-.96,-1.30]]]);
 for(const [x,y] of [[-1.16,-1.81],[-.42,-1.82],[-.47,-1.21]])screw(rearWorks,x,y,-.860,.052,true);
 plate(rearWorks,'right-keyless-bearing-bridge',[[.87,-.88],[1.25,-1.08],[1.22,-2.04],[.88,-2.04]],-.84,.135,mat.rhodium,[[1.05,-1.47,.065]]);
 for(const y of [-1.09,-1.83,-2.00])screw(rearWorks,1.04,y,-.872,.046,true);
 let previousKeyless=null;
 for(const [i,n] of [23,21,27].entries()){
  const module=.017,ang=-.12,pitch=module*n/2;
  const x=previousKeyless?previousKeyless.x+Math.cos(ang)*(previousKeyless.pitch+pitch):-.88;
  const y=previousKeyless?previousKeyless.y+Math.sin(ang)*(previousKeyless.pitch+pitch):-1.57;
  const offset=previousKeyless?ang+Math.PI-(Math.PI-previousKeyless.n*(ang-previousKeyless.offset))/n:0;
  const g=gear(rearWorks,x,y,-.39,module*(n+2)/2,n,mat.rhodium,5);g.name='keyless-transmission-'+i;
  wheels.push({g,rate:0,offset,domain:'winding'});g.rotation.z=offset;
  cyl(rearWorks,x,y,-.57,.0085,.51,mat.polished,'z','keyless-through-arbor',24);jewel(rearWorks,x,y,-.30,.039);
  if(previousKeyless)trainPairs.push({domain:'winding-static-inspection',centerA:[previousKeyless.x,previousKeyless.y],centerB:[x,y],pitchA:previousKeyless.pitch,pitchB:pitch,moduleA:module,moduleB:module,teethA:previousKeyless.n,teethB:n,phaseA:previousKeyless.offset,phaseB:offset});
  previousKeyless={x,y,pitch,n,offset};
 }
 leaf(rearWorks,'long-keyless-return-spring',[[-1.35,-.92],[-1.05,-.95],[-.69,-1.10],[.10,-1.22],[.71,-1.31],[1.04,-1.47]],-.883,.014,mat.polished);
 leaf(rearWorks,'winding-yoke-return-spring',[[-.42,-1.92],[-.10,-1.56],[.30,-1.54],[.57,-1.32]],-.909,.010,mat.polished);
 for(const x of [-1.11,0,1.11]){
  cyl(power,x,-1.94,-.24,.035,.55,mat.polished,'y','keyless-stem-'+x,24);
  box(power,x,-1.98,-.36,.21,.22,.18,mat.brushed,.025,'stem-pillow-block');
  washer(power,x,-2.10,-.24,.079,.037,.064,mat.rhodium,'y','stem-bearing-sleeve');
  screw(power,x-.06,-2.00,-.25,.028);
 }
 // The former three floating washers are replaced by supported motion works.
 // Standard 12:1 motion-works principle, NOT a claimed JCAM37 factory tooth count.
 // One compound minute wheel gives (12/36)*(12/48)=1/12. Both pitch distances .48.
 const aa=.45,dx=.48*Math.cos(aa),dy=.60+.48*Math.sin(aa),motionWorks={};
 post(power,'central-hand-arbor',0,.60,-.48,.61,.046);
 const cannon=gear(power,0,.60,.28,.140,12,mat.polished,5,.049);cannon.name='motion-cannon-12';
 const minuteWheel=gear(power,dx,dy,.28,.380,36,mat.rhodium,7,.012);minuteWheel.name='motion-minute-36';
 const intermediate=gear(minuteWheel,0,0,-.18,.112,12,mat.brass,5,.012);intermediate.name='motion-minute-integral-pinion-12';
 const hourWheel=gear(power,0,.60,.10,.400,48,mat.rhodium,8,.049);hourWheel.name='motion-hour-48';
 washer(power,0,.60,.025,.092,.049,.035,mat.brass,'z','hour-pinion-lower-thrust');
 washer(power,0,.60,.368,.089,.049,.032,mat.polished,'z','cannon-upper-thrust');
 cyl(power,dx,dy,.175,.0085,.62,mat.polished,'z','compound-motion-arbor',24);
 bearing(power,'compound-lower-bearing',dx,dy,-.115,.037);
 plate(power,'under-dial-bearing-bridge',[[-.68,.75],[.70,.92],[.79,.70],[.79,.47],[.30,.35],[-.28,.35],[-.79,.47]],-.18,.10,mat.brushed,[[0,.60,.10],[dx,dy,.043],[-.48,.59,.066]]);
 for(const sx of [-1,1]){
  // Continuous lower webs land directly on the frame. No post ends in air.
  plate(power,'motion-to-frame-web-'+sx,[[sx*.56,.49],[sx*1.57,.49],[sx*1.57,.73],[sx*.66,.74]],-.49,.12,mat.dark);
  post(power,'motion-work-support-'+sx,sx*.62,.59,-.435,-.12,.065);
  screw(power,sx*1.48,.60,-.345,.039);
 }
 // Upper bearing bridge carries the compound wheel and central hand arbor.
 // Its feet share the chassis rather than sitting on a rotating gear's spokes.
 const upper=plate(power,'upper-motion-bearing-bridge',[[-.84,.34],[-.64,.27],[-.16,.40],[.12,.41],[dx+.10,dy-.08],[dx+.17,dy+.04],[dx+.02,dy+.14],[.04,.78],[-.16,.76],[-.68,.48]],.433,.043,mat.brushed,[[0,.60,.082],[dx,dy,.046]]);
 for(const [x,y] of [[-.73,.37],[dx+.11,dy+.04]]){post(power,'upper-motion-bridge-foot',x,y,-.39,.44,.039);screw(power,x,y,.486,.034);}
 plate(power,'upper-motion-right-foot-web',[[dx+.04,dy-.02],[1.57,dy-.02],[1.57,dy+.15],[dx+.18,dy+.15]],-.49,.12,mat.dark);
 plate(power,'upper-motion-left-foot-web',[[-1.57,.25],[-.67,.25],[-.67,.47],[-1.57,.47]],-.49,.12,mat.dark);
 bearing(power,'compound-upper-bearing',dx,dy,.470,.034);
 const phiB=aa+Math.PI-(Math.PI-12*aa)/36,ab=aa+Math.PI,phiH=ab+Math.PI-(Math.PI-12*(ab-phiB))/48;
 motionWorks.update=seconds=>{const t=-TAU*seconds/3600;cannon.rotation.z=t;minuteWheel.rotation.z=phiB-t/3;hourWheel.rotation.z=phiH+t/12;};
 motionWorks.description={status:'ENGINEERING_APPROXIMATION',source:'generic motion-works principle; not JCAM37 tooth counts',ratio:12,centerDistance:.48,pairs:[{teeth:[12,36],pitch:[.12,.36],z:.28},{teeth:[12,48],pitch:[.096,.384],z:.10}],axes:[[0,.60],[dx,dy]],supportedBy:['under-dial-bearing-bridge','upper-motion-bearing-bridge','motion-to-frame-webs']};
 motionWorks.update(0);
 return {wheels,trainPairs,motionWorks};
}

export function suspension(c,root,carrier,fixed){
 const {V,mat,group,box,cyl,ring,bar,pathTube,screw,batchGroups}=c,{plate,washer,turned}=craftTools(c);
 const springMounts=group(root,'four-point-suspension'),mountMoving=group(carrier,'suspended-bearing-mounts',true),springs=[],interfaces=[];
 for(const sx of [-1,1])for(const sy of [-1,1]){
  const name=`shock-${sx}-${sy}`,a=V(sx*1.70,sy*1.88,-.55),b=V(sx*1.39,sy*1.47,.51),d=b.clone().sub(a),L=d.length();
  const fg=group(springMounts,name+'-fixed'),cg=group(springMounts,name+'-telescopic');fg.position.copy(a);
  // Fixed lug reaches the case gasket. Independent of the suspended movement.
  bar(fixed,V(sx*1.96,sy*1.99,-.73),a,.100,mat.brushed,name+'-case-lug');
  cyl(fg,0,0,0,.124,.12,mat.polished,'z',name+'-fixed-bearing');screw(fg,0,0,.073,.069);
  const movingPad=plate(mountMoving,name+'-moving-pad',[[sx*1.14,sy*1.24],[sx*1.57,sy*1.39],[sx*1.56,sy*1.72],[sx*1.17,sy*1.64]],.455,.102,mat.rhodium,[[b.x,b.y,.049]]);
  // Load path from the pad to the continuous chassis side rail.
  // A bored side web replaces the thin isolated rod. It lands on the chassis
  // rail below and the existing shock pad above; the window retains inspection.
  const web=group(mountMoving,name+'-side-bearing-web');
  web.position.set(sx*1.49,sy*1.63,0);web.rotation.y=Math.PI/2;
  plate(web,name+'-machined-support',[[.43,-.15],[.43,.15],[-.455,.15],[-.455,-.15]],-.052,.104,mat.brushed,
   [[[.31,-.061],[.31,.061],[-.30,.061],[-.30,-.061]]]);
  box(mountMoving,sx*1.49,sy*1.63,-.404,.23,.38,.083,mat.dark,.018,name+'-rail-saddle');
  for(const yy of [-.12,.12])screw(mountMoving,sx*1.49,sy*1.63+yy,.558,.031);
  // Journal through the .049 pad bore, shoulder beneath the .079 fork bore,
  // and a .050 threaded neck through the .056 retaining washer. No intersections.
  turned(mountMoving,name+'-stepped-top-seat',b.x,b.y,0,[[0,.455],[.046,.455],[.046,.552],[.073,.554],[.077,.558],[.077,.601],[.050,.605],[.050,.672],[0,.672]],mat.polished);
  washer(mountMoving,b.x,b.y,.620,.129,.056,.028,mat.polished,'z',name+'-retaining-washer');
  const hex=[];for(let i=0;i<6;i++){const a=TAU*i/6;hex.push([b.x+.107*Math.cos(a),b.y+.107*Math.sin(a)]);}
  plate(mountMoving,name+'-hexagonal-gland-nut',hex,.635,.041,mat.rhodium,[[b.x,b.y,.056]]);
  washer(mountMoving,b.x,b.y,.674,.069,.052,.013,mat.brushed,'z',name+'-nut-top-counterbore');

  cyl(cg,0,0,L*.32,.056,L*.60,mat.brushed,'z',name+'-shock-body',32);
  cyl(cg,0,0,L*.70,.027,L*.60,mat.polished,'z',name+'-piston-rod',24);
  for(const [z,bore] of [[.08,.058],[L-.07,.029]])washer(cg,0,0,z,.105,bore,.034,mat.polished,'z',name+'-spring-seat');
  const pts=[];for(let i=0;i<=128;i++){const t=i/128,a=t*TAU*8;pts.push(V(Math.cos(a)*.081,Math.sin(a)*.081,.085+t*(L-.17)));}
  pathTube(cg,pts,.014,mat.blue,name+'-eight-turn-coil');batchGroups.push(cg,fg);
  const update=bob=>{const end=b.clone().add(V(0,0,bob)),delta=end.clone().sub(a);cg.position.copy(a);cg.quaternion.setFromUnitVectors(V(0,0,1),delta.clone().normalize());cg.scale.z=delta.length()/L;};update(0);
  springs.push({update,a,b,L,g:cg,report(){root.updateMatrixWorld(true);return {name,fixedResidual:cg.localToWorld(V()).distanceTo(root.localToWorld(a.clone())),movingResidual:cg.localToWorld(V(0,0,L)).distanceTo(carrier.localToWorld(b.clone())),length:cg.localToWorld(V()).distanceTo(cg.localToWorld(V(0,0,L)))};}});interfaces.push({name,fixedPoint:a.toArray(),movingPoint:b.toArray(),fixedConnection:'case-lug',movingConnection:'moving-pad and moving-post to chassis',evidence:'ENGINEERING_APPROXIMATION anchored to observed four-corner placement'});
 }
 return {springs,springMounts,mountMoving,interfaces};
}

export function engineHousing(c,eng,engStatic,PISTONS){
 const {V,mat,group,box,cyl,ring,bar,pathTube,screw,flatLabel,batchGroups}=c,{plate,washer,turned}=craftTools(c);
 const journals=[],mounts=[];
 // Continuous machined bed with a central crank clearance slot and fixed bearing saddles.
 plate(engStatic,'W16-crankcase-bed',[[-.72,-.96],[.72,-.96],[.76,-.78],[.76,.78],[.62,.92],[-.62,.92],[-.76,.78],[-.76,-.78]],-.272,.094,mat.dark,
  [[[-.135,-.84],[.135,-.84],[.135,.81],[-.135,.81]]]);
 for(const sx of [-1,1]){
  box(engStatic,sx*.735,-.025,-.113,.075,1.73,.27,mat.dark,.025,'W16-integral-side-rail');
  box(engStatic,sx*.737,-.025,.025,.039,1.66,.036,mat.polished,.008,'W16-rail-chamfer');
 }
 // Nine real annular journal bearings are between station pairs, not through rods.
 for(let j=0;j<=8;j++){
  const y=(j-4)*.205;
  washer(engStatic,0,y,0,.071,.044,.033,mat.brushed,'y','fixed-crank-journal-'+j);
  washer(engStatic,0,y,0,.0436,.028,.037,mat.brass,'y','crank-journal-bush-'+j);
  const p=plate(engStatic,'journal-saddle-'+j,[[-.16,-.02],[-.082,.086],[.082,.086],[.16,-.02],[.16,-.216],[-.16,-.216]],-.015,.032,mat.rhodium,[[0,0,.073]]);
  // local 2D plate xy becomes xz; its bore follows the Y shaft.
  p.rotation.x=Math.PI/2;p.position.y=y;p.position.z=0;
  for(const sx of [-1,1])cyl(engStatic,sx*.115,y,-.145,.018,.14,mat.polished,'z','journal-cap-bolt',16);
  journals.push({id:'fixed-crank-journal-'+j,center:[0,y,0],innerRadius:.028,shaftRadius:.026});
 }
 // Cylinder blocks have visible mounting material: four banks -> lugs -> bed,
 // but the entire moving piston and ring remains inside the actual bored volume.
 for(const bank of [0,1,2,3]){
  const d=PISTONS.find(p=>p.bank===bank),u=V(Math.sin(d.angle),0,Math.cos(d.angle)),sx=Math.sign(u.x);
  for(const y of [-.88,.87]){
   const a=V(u.x*.62,y,u.z*.62),b=V(sx*.68,y,-.14);
   bar(engStatic,a,b,.035,mat.polished,'bank-'+bank+'-mount-leg');
   cyl(engStatic,a.x,a.y,a.z,.046,.044,mat.rhodium,'y','bank-'+bank+'-flange-fastener',24);
  }
 }
 // Bed attachment feet to lower movement deck and side rails; complete solid load paths.
 for(const sx of [-1,1])for(const y of [-.83,.78]){
  box(engStatic,sx*.87,y,-.20,.35,.20,.14,mat.rhodium,.025,'W16-chassis-foot');
  bar(engStatic,V(sx*.72,y,-.20),V(sx*1.45,y,-.48),.045,mat.dark,'W16-to-mainframe-web');
  box(engStatic,sx*1.43,y,-.468,.16,.19,.07,mat.brushed,.014,'W16-frame-interface-flange');screw(engStatic,sx*1.43,y,-.412,.038);screw(engStatic,sx*.91,y,-.104,.039);mounts.push({x:sx*.91,y,z:-.20});
 }
 // Turbines now have stationary volutes and bearing shafts. Only the interior
 // vanes rotate, not the ring, retaining screws and support together.
 const turbos=[];
 for(const sx of [-1,1]){
  const housing=group(engStatic,'turbine-fixed-housing-'+sx);housing.position.set(sx*.925,.10,.24);
  turned(housing,'turbine-bearing-hub',0,0,0,[[.0258,-.105],[.060,-.105],[.082,-.061],[.086,-.015],[.073,.046],[.043,.069],[.0258,.069],[.0258,-.105]],mat.brushed);
  washer(housing,0,0,.012,.257,.218,.044,mat.polished,'z','turbine-fixed-rim');washer(housing,0,0,-.047,.251,.209,.031,mat.brushed);
  for(const a of [Math.PI/2,Math.PI*1.17,Math.PI*1.83]){const x=Math.cos(a)*.234,y=Math.sin(a)*.234;
   screw(housing,x,y,.041,.025);bar(housing,V(x,y,-.054),V(x*.22,y*.22,-.076),.013,mat.brushed,'turbine-rear-bearing-spoke');
  }
  cyl(housing,0,0,.018,.024,.20,mat.polished,'z','turbine-fixed-axis',24);
  const rotor=group(eng,'turbine-rotor-'+sx);rotor.position.copy(housing.position).add(V(0,0,.028));
  for(let i=0;i<12;i++){
   const a=i/12*TAU,points=[];
   for(const [r,t] of [[.047,0],[.125,.20],[.211,.37],[.213,.48],[.126,.28],[.045,.09]])points.push([Math.cos(a+t)*r,Math.sin(a+t)*r]);
   plate(rotor,'milled-turbine-vane',points,-.01,.023,mat.rhodium);
  }
  washer(rotor,0,0,.022,.050,.025,.018,mat.polished);turbos.push(rotor);batchGroups.push(rotor,housing);
  bar(engStatic,V(sx*.927,.09,.155),V(sx*.72,.09,-.132),.064,mat.dark,'turbine-housing-pedestal');
  pathTube(engStatic,[V(sx*1.14,.06,.21),V(sx*1.18,-.02,.13),V(sx*1.12,-.38,-.05),V(sx*1.04,-.72,-.09),V(sx*.83,-.86,-.15),V(sx*.70,-.87,-.15)],.040,mat.polished,'turbine-housing-collector');
  box(engStatic,sx*.73,-.87,-.15,.15,.16,.11,mat.brushed,.014,'collector-terminal-flange');screw(engStatic,sx*.74,-.88,-.080,.035);
 }
 // Rear lower gear case: real material behind the cylinder banks, not an empty side view.
 plate(engStatic,'W16-rear-gearcase',[[-.60,-.92],[.60,-.92],[.56,-.67],[.26,-.62],[-.26,-.62],[-.56,-.67]],-.325,.09,mat.dark,
  [[-.37,-.78,.087],[.37,-.78,.087]]);
 return {turbos,journals,mounts};
}

export function dialSupports(c,dial,power){
 const {V,mat,box,cyl,ring,bar,screw}=c,{plate,washer,post}=craftTools(c);
 // The index bridge shares the four existing suspension mounts. It does not
 // introduce a second, visually disconnected set of oversized corner cleats.
 for(const sx of [-1,1]){
  plate(dial,'upper-index-to-shock-fork-'+sx,[[sx*.92,1.16],[sx*1.42,1.36],[sx*1.50,1.52],[sx*1.23,1.58],[sx*.91,1.28]],.554,.049,mat.rhodium,[[sx*1.39,1.47,.079]]);
  const path=[V(sx*1.04,.10,.601),V(sx*1.285,-.12,.579),V(sx*1.34,-.83,.555),V(sx*1.39,-1.42,.558)];
  c.pathTube(dial,path,.028,mat.polished,'lower-index-to-shock-rail-'+sx);
  washer(dial,sx*1.39,-1.47,.570,.139,.085,.029,mat.rhodium,'z','shared-lower-mount-collar');
 }
 // Central hub has an actual back bearing and the medallion has a neck rather
 // than an isolated rectangular label in space.
 washer(dial,0,.60,.626,.194,.064,.071,mat.polished,'z','central-dial-hub');
 plate(dial,'EB-integral-neck',[[-.105,.23],[.105,.23],[.158,-.293],[-.158,-.293]],.606,.055,mat.rhodium);
 for(const sx of [-1,1])bar(dial,V(sx*.34,.15,.63),V(sx*.132,-.251,.63),.023,mat.polished,'medallion-fork');
 for(let i=0;i<60;i++){if(i%5===0)continue;const a=i/60*TAU,x=Math.sin(a),y=Math.cos(a);const o=box(dial,x*1.129,.60+y*1.129,.671,.007,.038,.012,mat.brushed,.002,'minute-engraved-graduation');o.rotation.z=-a;}
}

export function tourbillonSupport(c,tourStatic){
 const {V,mat,box,cyl,ring,bar,screw}=c,{plate,washer,post}=craftTools(c);
 // Single rear journal/cantilever (flying architecture). No added top bridge.
 washer(tourStatic,0,0,-.184,.173,.075,.085,mat.dark,'z','tourbillon-rear-journal-cup');
 washer(tourStatic,0,0,-.231,.140,.056,.025,mat.ruby,'z','tourbillon-rear-jewel');
 cyl(tourStatic,0,0,-.242,.052,.22,mat.polished,'z','tourbillon-rear-pivot');
 washer(tourStatic,0,0,-.135,.084,.075,.044,mat.brushed,'z','tourbillon-pivot-thrust-seat');
 plate(tourStatic,'tourbillon-cantilever',[[-.29,-.22],[.29,-.22],[.34,.09],[.18,.18],[-.18,.18],[-.34,.09]],-.332,.102,mat.brushed,[[0,0,.076]]);
 // Local tilted pedestal lands on upper-carrier-deck after tour.rotation.x=30deg.
 for(const sx of [-1,1]){
  bar(tourStatic,V(sx*.275,-.10,-.28),V(sx*.48,-.09,-.616),.061,mat.dark,'tourbillon-cantilever-leg');
  box(tourStatic,sx*.48,-.09,-.615,.19,.26,.14,mat.brushed,.022,'tourbillon-carrier-foot');
  screw(tourStatic,sx*.48,-.09,-.525,.042);
  bar(tourStatic,V(sx*.39,-.30,-.11),V(sx*.28,-.18,-.31),.022,mat.polished,'protective-arch-foot');
 }
}

export function materialFinish(mat){
 // Subtle authored machining roughness. No photographic watch surfaces, baked
 // highlights, random scratches or time-varying noise.
 const n=256,data=new Uint8Array(n*n*4);
 for(let y=0;y<n;y++)for(let x=0;x<n;x++){
  const i=(y*n+x)*4,v=Math.round(218+3*Math.sin(y*2.61)+1.4*Math.sin(y*.719)+.8*Math.sin(x*.073+y*.513));
  data[i]=data[i+1]=data[i+2]=v;data[i+3]=255;
 }
 const tex=new THREE.DataTexture(data,n,n);tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(2,2);tex.minFilter=THREE.LinearMipmapLinearFilter;tex.magFilter=THREE.LinearFilter;tex.generateMipmaps=true;tex.anisotropy=4;tex.needsUpdate=true;tex.name='authored-machining-roughness';
 for(const key of ['brushed','rhodium']){mat[key].roughnessMap=tex;mat[key].needsUpdate=true;}
 mat.rhodium.color.set(0xb5bcc1);mat.rhodium.roughness=.30;
 mat.polished.color.set(0xe0e3e6);mat.polished.roughness=.105;
 mat.brushed.color.set(0x8c979f);mat.brushed.roughness=.43;
 mat.dark.color.set(0x343c43);mat.dark.metalness=.65;mat.dark.roughness=.43;
 mat.rubber.color.set(0xc8cdd0);mat.rubber.opacity=.88;mat.rubber.roughness=.48;
 mat.rubber.side=THREE.FrontSide;
 // Inner bore geometry remains closed and present. A Fresnel-weighted clear
 // surface avoids a second refractive image of each tiny linkage. This is a
 // declared real-time optical approximation, not sapphire ray tracing.
 const inner=mat.cylinderGlass;
 inner.transmission=0;inner.opacity=.32;inner.transparent=true;inner.depthWrite=false;
 inner.side=THREE.FrontSide;inner.roughness=.045;inner.color.set(0xffffff);
 inner.envMapIntensity=1.15;inner.clearcoat=1;inner.clearcoatRoughness=.035;
 inner.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',
  'diffuseColor.a *= 0.18 + 0.82 * pow(1.0 - abs(dot(normal, normalize(vViewPosition))), 2.0);\n#include <opaque_fragment>');};
 inner.customProgramCacheKey=()=> 'chiron-inner-sapphire-fresnel-v1';
 for(const key of ['crystal','crystalEdge','cover']){
  mat[key].color.set(0xffffff);mat[key].clearcoat=0;mat[key].transmission=1;
  mat[key].opacity=1;mat[key].transparent=false;mat[key].depthWrite=true;
 }
 mat.cover.thickness=.045;mat.cover.roughness=.025;mat.cover.specularIntensity=.65;
 mat.crystal.roughness=.033;mat.crystal.thickness=.19;mat.crystal.envMapIntensity=1.55;
 mat.crystalEdge.envMapIntensity=1.65;
}
