const {chromium}=require(process.env.PW_ROOT+'/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const root=process.env.PROBE_ROOT;
 if(!root)throw new Error('PROBE_ROOT required');
 const logs=[],failedRequests=[];
 const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',timeout:20000,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 let page,problem;
 try{
  page=await browser.newPage({viewport:{width:1280,height:800}});
  page.on('console',m=>logs.push({type:m.type(),text:m.text()}));
  page.on('pageerror',e=>logs.push({type:'pageerror',text:String(e)}));
  page.on('requestfailed',r=>failedRequests.push({url:r.url(),failure:r.failure()}));
  await page.goto('http://127.0.0.1:8765/browser/',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__G1_READY||window.__G1_ERROR,{},{timeout:100000});
  const error=await page.evaluate(()=>window.__G1_ERROR);if(error)throw new Error(error);
  const report=await page.evaluate(()=>window.__G1_REPORT);
  report.browser=browser.version();report.renderer='SwiftShader software; not desktop GPU performance';
  fs.writeFileSync(root+'/browser-report.json',JSON.stringify(report,null,2));
  if(!report.renderedFrames)throw new Error('No true rendered frames');
  if(logs.some(l=>l.type==='pageerror'))throw new Error('Browser page error');
 }catch(e){problem=e;fs.writeFileSync(root+'/browser-failure.json',JSON.stringify({error:String(e),stack:e.stack},null,2));}
 finally{
  fs.writeFileSync(root+'/browser-console.json',JSON.stringify(logs,null,2));
  fs.writeFileSync(root+'/browser-failed-requests.json',JSON.stringify(failedRequests,null,2));
  if(page)await page.screenshot({path:root+'/browser-materials.png',timeout:10000}).catch(e=>fs.writeFileSync(root+'/screenshot-error.txt',String(e)));
  await browser.close();
 }
 if(problem)throw problem;
})().catch(e=>{console.error(e);process.exit(1)});
