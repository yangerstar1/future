/** O32 final-build continuous route: ordinary controls, read-only telemetry. */
import {chromium} from '@playwright/test';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {observeFrame} from './observed-frame.mjs';
const out='evidence/R05/route';fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync('dist/build-manifest.json'));
const report={buildHash:manifest.buildHash,transport:'HTTP cold browser context',started:new Date().toISOString(),assurance:'Actual Chromium inputs and video on SwiftShader; no physical GPU/device or smooth-performance claim',steps:[],errors:[]};
const save=()=>fs.writeFileSync(out+'/route-report.json',JSON.stringify(report,null,2));
const server=spawn(process.execPath,['tools/serve.mjs'],{stdio:'inherit'});
const browser=await chromium.launch({headless:false,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1100,height:800},deviceScaleFactor:1,reducedMotion:'reduce',recordVideo:{dir:out+'/video',size:{width:1100,height:800}}});
const page=await context.newPage();page.setDefaultTimeout(90000);
page.on('pageerror',e=>{report.errors.push(e.message);save();});
page.on('console',m=>{if(m.type()==='error'){report.errors.push(m.text());save();}});
const click=q=>page.locator(q).click();
const snap=()=>page.evaluate(()=>window.__chiron.snapshot());
async function checkpoint(id,input){const s=await observeFrame(page);await page.screenshot({path:`${out}/${id}.png`});report.steps.push({id,input,snapshot:s});save();console.log('ROUTE',id);return s;}
try{
 await page.goto('http://127.0.0.1:4173');await page.waitForFunction(()=>window.__chiron?.snapshot().state.ready,{},{timeout:120000});
 assert.equal(await page.locator('.chapter').count(),7);
 const initial=await checkpoint('01-complete-watch','Cold entry');assert(initial.state.muted&&initial.state.reduced);
 await click('#the-object [data-do=start]');assert.equal((await snap()).state.engine,'running');
 await click('#the-object [data-do=explore]');assert.equal((await snap()).state.mode,'explore');
 await click('#dock [data-do=inspect-engine]');const playback=await checkpoint('02-w16-playback','Start W16 → Explore in 3D → W16');
 assert(playback.state.engineTime>0);assert.equal(playback.state.starts,initial.state.starts+1);
 // On the software runner, observing two presented frames took 27 seconds in
 // 3e4656e: the normal 15-second cycle had naturally finished (idle / 15).
 // Preserve that real outcome; never turn a completed cycle into a fake pause.
 const pauseBefore=await snap();
 if(pauseBefore.state.engine==='running')await click('#pause-control');
 const pauseAfter=await snap();report.normalCyclePauseAttempt={before:pauseBefore,after:pauseAfter};save();
 assert.equal(pauseAfter.state.starts,pauseBefore.state.starts);
 assert.equal(pauseAfter.state.engineEnergy,pauseBefore.state.engineEnergy);
 // Read and click are separate browser tasks: natural completion can happen
 // between them. Require the exact 15-second endpoint, not any idle state.
 if(pauseAfter.state.engine==='idle'){assert.equal(pauseAfter.state.engineTime,15);report.naturalCycleCompletion=pauseAfter;}
 else{assert.equal(pauseAfter.state.engine,'paused');assert(pauseAfter.state.engineTime>=pauseBefore.state.engineTime);assert(pauseAfter.state.engineTime<15);}
 const links=await page.evaluate(()=>window.__chiron.connections());assert.equal(links.length,16);assert(links.every(x=>Math.max(x.bigEndResidual,x.smallEndResidual)<1e-4));report.connections=links;
 await click('#crown-toggle');const reserveBefore=await snap(),emptyAt=Date.now();await click('#crown-panel [data-do=exhaust]');const reserveAfter=await snap(),emptyElapsedMs=Date.now()-emptyAt;
 assert.equal(reserveAfter.state.engineEnergy,0);assert(reserveAfter.state.clockEnergy<=reserveBefore.state.clockEnergy);assert(Math.abs((reserveBefore.state.clockEnergy-reserveAfter.state.clockEnergy)-(reserveAfter.state.clockSeconds-reserveBefore.state.clockSeconds)/(60*3600))<1e-9);assert((await page.locator('#reserve-status').textContent()).includes('W16: 0 display cycles'));
 report.independentEmpty={before:reserveBefore,after:reserveAfter,elapsedMs:emptyElapsedMs,ui:await page.locator('#reserve-status').textContent()};save();await click('#crown-panel [data-do=windEngine]');await click('#crown-toggle');
 await click('#explorer .explore-top [data-do=restore]');
 await page.locator('#watch-canvas').focus();const before=await snap();await page.keyboard.press('ArrowRight');await page.keyboard.press('+');const after=await snap();assert.notDeepEqual(before.camera.position,after.camera.position);
 await click('[data-view=back]');await checkpoint('03-back','Restore watch → keyboard rotation/zoom → Back');
 await click('#crystal-control');assert((await snap()).state.crystalOff);await checkpoint('04-case-removed','Crystal off from the rear');
 await click('#anatomy-toggle');await page.locator('#explode').focus();await page.keyboard.press('End');await checkpoint('05-exploded','Anatomy → keyboard End on disassembly');assert.equal((await snap()).state.explode,1);
 await click('#anatomy-toggle');await click('#dock [data-do=inspect-engine]');await click('#crown-toggle');await page.locator('#engine-rate').selectOption('0.1');
 if((await snap()).state.engine==='paused')await click('#pause-control');else await click('#dock [data-do=start]');assert.equal((await snap()).state.engine,'running');const slowBefore=await snap();await checkpoint('06-isolated-slow','W16 isolation → 1/10× → Resume');const slowAfter=await snap();assert(slowAfter.state.engineTime>slowBefore.state.engineTime);assert.equal(slowAfter.state.engineRate,.1);report.slow={before:slowBefore,after:slowAfter};
 await click('#pause-control');const pausedSlow=await snap();assert.equal(pausedSlow.state.engine,'paused');
 await page.waitForTimeout(400);const stillPaused=await snap();assert.equal(stillPaused.state.engineTime,pausedSlow.state.engineTime);assert.equal(stillPaused.state.engineEnergy,pausedSlow.state.engineEnergy);report.slowPause={before:pausedSlow,after:stillPaused};save();
 await click('#crown-toggle');await click('#dock [data-do=inspect-tourbillon]');await checkpoint('07-regulator','Pause W16 → Tourbillon');
 await click('#explorer .explore-top [data-do=restore]');const assembled=await checkpoint('08-reassembled','Restore watch');assert.equal(assembled.state.selection,'all');assert.equal(assembled.state.explode,0);assert.equal(assembled.state.crystalOff,false);assert(assembled.assemblyError.position<5.78e-5);assert(assembled.assemblyError.rotationDegrees<.01);
 await click('#explorer [data-do=exit]');assert.equal((await snap()).state.mode,'story');
 for(const id of ['mechanical-pulse','suspended-precision','sapphire-revealed','anatomy','explore-chapter','the-record']){await page.locator('#'+id).scrollIntoViewIfNeeded();const s=await checkpoint('09-story-'+id,'Back to story → scroll to '+id);if(id==='mechanical-pulse')assert(s.runtime.storyFit.gap>=24,'The projected case must clear the actual story copy');}
 assert.equal(await page.locator('.specifications dd').count(),8);assert(await page.locator('#the-record a.primary').getAttribute('href'));
 await click('#the-record [data-do=explore]');await page.locator('#watch-canvas').focus();await page.keyboard.press('Escape');assert.equal((await snap()).state.mode,'story');
 report.final=await snap();assert.equal(report.final.runtime.initializations,1);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));report.pass=report.errors.length===0;
}catch(e){report.errors.push(e.stack);console.error(e);report.pass=false;process.exitCode=1;}
finally{report.finished=new Date().toISOString();save();await context.close();await browser.close();server.kill();}
if(report.pass){
 await import('./standalone-check.mjs');
 const standalone=JSON.parse(fs.readFileSync(out+'/standalone-report.json'));
 report.standalone={pass:standalone.pass,buildHash:standalone.buildHash};
 report.pass=standalone.pass&&standalone.buildHash===report.buildHash;
 report.finished=new Date().toISOString();save();
}
if(!report.pass)process.exitCode=1;
