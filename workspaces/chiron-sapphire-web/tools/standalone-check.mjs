/** The delivered standalone file, not a substitute HTTP fixture. Run in the
 * authorized CI browser environment; never a local-policy bypass. */
import {chromium} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {observeFrame} from './observed-frame.mjs';
const out='evidence/R05/route';fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync('dist/build-manifest.json'));
const report={buildHash:manifest.buildHash,revision:manifest.revision,transport:'file:// exact distributed standalone HTML',requests:[],errors:[],pass:false,assurance:'Actual Chromium/SwiftShader in CI, not a physical consumer device'};
const browser=await chromium.launch({headless:false,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1100,height:800},deviceScaleFactor:1,reducedMotion:'reduce'});
const page=await context.newPage();page.setDefaultTimeout(90000);
page.on('request',r=>report.requests.push(r.url()));
page.on('pageerror',e=>report.errors.push(e.message));
page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});
const snap=()=>page.evaluate(()=>window.__chiron.snapshot());
try{
 const file=path.resolve(`dist/Chiron-Sapphire-${manifest.revision}.html`);
 assert(fs.existsSync(file));await page.goto(pathToFileURL(file).href);
 await page.waitForFunction(()=>window.__chiron?.snapshot().state.ready,{},{timeout:120000});
 report.initial=await observeFrame(page);assert.equal(report.initial.revision,manifest.revision);
 assert.equal(report.initial.runtime.initializations,1);assert.equal(await page.locator('.chapter').count(),7);
 assert.equal(await page.evaluate(()=>window.__INLINE_MECHANISM__.pistons.length),16);
 await page.locator('#the-object [data-do=explore]').click();
 await page.locator('#crown-toggle').click();await page.locator('#engine-rate').selectOption('0.1');
 await page.locator('#crown-toggle').click();await page.locator('#dock [data-do=start]').click();
 report.running=await observeFrame(page);assert(report.running.state.engineTime>0);assert.equal(report.running.state.engine,'running');
 await page.locator('#pause-control').click();const paused=await snap();assert.equal(paused.state.engine,'paused');
 await page.waitForTimeout(400);report.paused=await snap();assert.equal(report.paused.state.engineTime,paused.state.engineTime);
 await page.locator('[data-view=back]').click();await page.locator('#crystal-control').click();assert((await snap()).state.crystalOff);
 await page.locator('#explorer .explore-top [data-do=restore]').click();report.final=await observeFrame(page);
 assert.equal(report.final.state.selection,'all');assert.equal(report.final.state.explode,0);assert.equal(report.final.state.crystalOff,false);
 assert.equal(report.final.runtime.initializations,1);assert.equal(report.final.runtime.network.length,0);
 assert.equal(report.requests.filter(url=>/^https?:/i.test(url)).length,0);
 await page.screenshot({path:out+'/standalone-file.png'});report.pass=report.errors.length===0;
}catch(e){report.errors.push(e.stack);console.error(e);}
finally{report.finished=new Date().toISOString();fs.writeFileSync(out+'/standalone-report.json',JSON.stringify(report,null,2));await context.close();await browser.close();}
console.log('STANDALONE',report.pass?'PASS':'FAIL',report.buildHash);if(!report.pass)process.exitCode=1;
