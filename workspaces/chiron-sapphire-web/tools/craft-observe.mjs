import {chromium} from '@playwright/test';import fs from 'node:fs';
const out=process.env.OBS_OUT||'evidence/R04/current';fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync('dist/build-manifest.json'));const report={buildHash:manifest.buildHash,transport:'LOCAL_DOCUMENT_INJECTION',shots:[],errors:[]};
const browser=await chromium.launch({headless:false,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,reducedMotion:'reduce'});page.setDefaultTimeout(90000);
page.on('pageerror',e=>{report.errors.push(e.message);console.error(e.message)});page.on('console',m=>{if(m.type()==='error')console.error(m.text());});
async function snap(name){const initial=await page.evaluate(()=>window.__chiron.snapshot().totalFrames);await page.waitForFunction(n=>window.__chiron.snapshot().totalFrames>n,initial,{timeout:120000});await page.waitForTimeout(200);const s=await page.evaluate(()=>window.__chiron.snapshot());await page.screenshot({path:`${out}/${name}.png`});report.shots.push({name,...s});fs.writeFileSync(out+'/observations.json',JSON.stringify(report,null,2));console.log('SHOT',name,s.renderer);}
try{
 await page.setContent(fs.readFileSync('dist/Chiron-Sapphire-R02.html','utf8'));await page.waitForFunction(()=>window.__chiron?.snapshot().state.ready,{},{timeout:120000});
 await page.locator('#the-object [data-do=explore]').click();
 await page.locator('#light-toggle').click();
 for(const view of (process.env.VIEWS||'front,back,left,right,engine,tourbillon').split(',')){
  await page.locator(view==='engine'||view==='tourbillon'?`#explorer [data-do=inspect-${view}]`:`[data-view=${view}]`).click();await snap(view+'-neutral');
 }
 await page.locator('[data-view=hero]').click();await page.locator('#light-toggle').click();await snap('hero-studio');
 fs.writeFileSync(out+'/structural.json',JSON.stringify(await page.evaluate(()=>window.__chiron.structural?.()),null,2));
 fs.writeFileSync(out+'/passport.json',JSON.stringify(await page.evaluate(()=>window.__chiron.passport()),null,2));
}finally{await browser.close();}
