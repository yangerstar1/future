import {chromium} from '@playwright/test';
import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {observeFrame} from './observed-frame.mjs';
import {verifyAsset} from './verify-asset.mjs';
const out=process.env.OBS_OUT||'evidence/R05/visual';fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync('dist/build-manifest.json'));
const report={buildHash:manifest.buildHash,transport:'HTTP',viewportAssurance:'emulated viewport; real Chromium software rendering, not physical device',shots:[],errors:[]};
const save=()=>fs.writeFileSync(out+'/observations.json',JSON.stringify(report,null,2));
const server=spawn(process.execPath,['tools/serve.mjs'],{stdio:'inherit'});
const opts={headless:false,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']};
if(process.env.CHROMIUM_PATH)opts.executablePath=process.env.CHROMIUM_PATH;
const browser=await chromium.launch(opts),page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});
page.setDefaultTimeout(90000);
page.on('pageerror',e=>{report.errors.push(e.message);save();});
page.on('console',m=>{if(m.type()==='error'){report.errors.push(m.text());save();}});
async function snap(name){const s=await observeFrame(page);await page.screenshot({path:`${out}/${name}.png`});report.shots.push({name,...s});save();console.log('SHOT',name,JSON.stringify(s.renderer));}
try{
 await page.goto('http://127.0.0.1:4173');await page.waitForFunction(()=>window.__chiron?.snapshot().state.ready,{},{timeout:120000});
 await snap('hero-desktop');
 await page.locator('#the-object [data-do=explore]').click();
 report.asset=await verifyAsset(page);save();
 await page.locator('#light-toggle').click();
 for(const view of ['front','back','left','right','engine','tourbillon']){
  await page.locator(view==='engine'||view==='tourbillon'?`#dock [data-do=inspect-${view}]`:`[data-view=${view}]`).click();await snap(view+'-neutral');
 }
 await page.locator('#explorer .explore-top [data-do=restore]').click();
 await snap('oblique-neutral');await page.locator('#crystal-control').click();await snap('oblique-crystal-off');await page.locator('#crystal-control').click();
 await page.locator('#anatomy-toggle').click();await page.locator('#explode').focus();await page.keyboard.press('End');await snap('exploded-100');await page.locator('#anatomy-panel [data-do=restore]').click();await page.locator('#anatomy-toggle').click();
 await page.locator('#light-toggle').click();await page.locator('#explorer [data-do=exit]').click();
 for(const viewport of [{width:390,height:844},{width:844,height:390},{width:360,height:800}]){
  await page.setViewportSize(viewport);await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await snap(`hero-${viewport.width}x${viewport.height}`);
  await page.locator('#the-object [data-do=explore]').click();await snap(`explore-${viewport.width}x${viewport.height}`);await page.locator('#explorer [data-do=exit]').click();
 }
 report.structural=await page.evaluate(()=>window.__chiron.structural());
 report.passport=await page.evaluate(()=>window.__chiron.passport());
}catch(e){report.errors.push(e.stack);console.error(e);process.exitCode=1;}
finally{report.finished=new Date().toISOString();save();await browser.close();server.kill();}
if(report.errors.length)process.exitCode=1;
