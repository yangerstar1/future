import {chromium} from '@playwright/test';import fs from 'node:fs';
const browser=await chromium.launch({headless:false,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1100,height:800},deviceScaleFactor:1});
page.on('pageerror',e=>console.error('PAGEERROR',e));page.on('console',m=>{if(m.type()==='error')console.error('CONSOLE',m.text());});
await page.setContent(fs.readFileSync('dist/Chiron-Sapphire-R02.html','utf8'),{waitUntil:'load'});await page.waitForFunction(()=>window.__chiron?.snapshot().state.ready,{},{timeout:25000}).catch(e=>console.error(e.message));await page.waitForTimeout(2500);
fs.writeFileSync('evidence/R02/preview-state.json',JSON.stringify(await page.evaluate(()=>window.__chiron.snapshot()),null,2));
await page.screenshot({path:'evidence/R02/hero-quarter.png'});
await browser.close();
