/** Wait for a newly presented frame matching the real UI/camera/viewport.
 * Read-only observation: never advances a clock or sets application state. */
export async function observeFrame(page) {
 const initial=await page.evaluate(()=>window.__chiron.snapshot().totalFrames);
 await page.waitForFunction(min=>{
  const s=window.__chiron.snapshot(),d=s.runtime.presentedDraw||(!s.runtime.gpuPending&&s.runtime.lastDraw);
  if(!d||d.frame<=min||d.mode!==s.state.mode||d.selection!==s.state.selection||d.crystalOff!==s.state.crystalOff||d.light!==s.state.light)return false;
  if(Math.abs(d.explode-s.state.explodeTarget)>.002||d.width!==s.viewport.canvas.width||d.height!==s.viewport.canvas.height)return false;
  if(d.camera.some((x,i)=>Math.abs(x-s.camera.position[i])>.002))return false;
  if(s.camera.view?.enabled&&(s.camera.view.fullWidth!==d.width||s.camera.view.fullHeight!==d.height))return false;
  return true;
 },initial,{timeout:120000,polling:100});
 return page.evaluate(()=>window.__chiron.snapshot());
}
