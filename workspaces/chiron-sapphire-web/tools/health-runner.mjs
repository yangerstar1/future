/** Remove Playwright's forced-active override before measuring real tab hiding.
 * This changes only the disposable test harness, never the app or Page Visibility.
 * Package, exact replacement and both source hashes are saved; original restored.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const pkgPath=require.resolve('playwright-core/package.json');
const pkg=JSON.parse(fs.readFileSync(pkgPath));
assert.equal(pkg.version,'1.55.1','Reinspect a changed Playwright harness before use');
const file=path.join(path.dirname(pkgPath),'lib/server/chromium/crPage.js');
const original=fs.readFileSync(file,'utf8');
const from='this._client.send("Emulation.setFocusEmulationEnabled", { enabled: true })';
const to='this._client.send("Emulation.setFocusEmulationEnabled", { enabled: false })';
assert.equal(original.split(from).length-1,1,'Expected one known main-frame override');
const patched=original.replace(from,to),sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const out='evidence/R05/health';fs.mkdirSync(out,{recursive:true});
const report={package:'playwright-core',version:pkg.version,file:'lib/server/chromium/crPage.js',from,to,originalSha256:sha(original),measurementSha256:sha(patched),restored:false,
  reason:'The locked Playwright driver forces its own main-frame CDP session active. Earlier new-CDPSession(false) probes did not remove that session override. Disable only that harness override before importing the driver; require actual document.hidden after normal same-window tab activation.',
  protocol:'https://chromedevtools.github.io/devtools-protocol/tot/Emulation/#method-setFocusEmulationEnabled',
  scope:'Ephemeral test dependency only. No application changes, visibility setters, fake events, clock steps or weakened assertions.'};
const save=()=>fs.writeFileSync(out+'/visibility-harness.json',JSON.stringify(report,null,2));
save();fs.writeFileSync(file,patched);
try{await import('./health-check.mjs');}
finally{fs.writeFileSync(file,original);report.restored=sha(fs.readFileSync(file))===report.originalSha256;save();assert(report.restored);}
