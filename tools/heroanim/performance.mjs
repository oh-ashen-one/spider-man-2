import { chromium } from 'playwright-core';
import fs from 'node:fs';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9334', { noDefaults: true });
const url=process.argv[3]||'http://127.0.0.1:5193/?skipintro';
const page = browser.contexts().flatMap(c=>c.pages()).find(p=>p.url()===url)||await browser.contexts()[0].newPage();
await page.goto(url);
await page.bringToFront();
await page.waitForFunction(()=>window.__ctx?.player?.rig?.animator&&window.__sys,null,{timeout:120000,polling:100});
const cdp=await page.context().newCDPSession(page);
await cdp.send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
const original=await cdp.send('Browser.getWindowForTarget');
if(!fs.existsSync('.scratch/original-window.json'))fs.writeFileSync('.scratch/original-window.json',JSON.stringify(original));
if(!process.env.SM2_KEEP_WINDOW) await cdp.send('Browser.setWindowBounds',{windowId:original.windowId,bounds:{left:-1070,top:30,width:1040,height:1100,windowState:'normal'}});
await page.bringToFront();
const stage=process.argv[2]||'final';
const report={stage,started:new Date().toISOString(),resolution:[1920,1080],headless:false,display:process.env.SM2_KEEP_WINDOW?'Original desktop window; 50 Hz main display':'Requested 27E40 120 Hz bounds; inspect per-view actual window bounds',url,views:[]};
for(const view of ['street','park','traversal']){
 if(!process.env.SM2_KEEP_WINDOW) await cdp.send('Browser.setWindowBounds',{windowId:original.windowId,bounds:{left:-1070,top:30,width:1040,height:1100,windowState:'normal'}});
 await cdp.send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
 await page.waitForTimeout(500);
 await page.evaluate(()=>{dispatchEvent(new Event('resize'));});
 await page.evaluate(view=>{
  const c=window.__ctx;c.manualStep=false;c.flow.setMode('play');
  if(view==='street') c.world.life.debugCam=[262,5.5,180,245,1.5,145];
  else if(view==='park') {const s=c.world.life.critters.sites.find(s=>s.kind==='squirrel');if(!s)throw Error('Park site missing');c.world.life.debugCam=[s.x+16,7,s.z+16,s.x,1.5,s.z];}
  else {c.world.life.debugCam=null;c.input.releaseAll();c.input.poll();c.player.teleport(new c.THREE.Vector3(250,65,167),0);c.player.velocity.set(0,2,18);c.input.press('MouseRight');}
 },view);
 await page.waitForTimeout(3500);
 const r=await page.evaluate(async(view)=>{
   const c=window.__ctx;
   if(document.visibilityState!=='visible')throw Error('Desktop tab not visible');
   const frames=[],animationMs=[],clips=new Set();let prev=performance.now();
   await new Promise(resolve=>{function step(t){frames.push(t-prev);prev=t;animationMs.push(c.player.rig.animator.debug.ms||0);clips.add(c.player.rig.animator.debug.clip);
     if(view==='traversal'){const n=frames.length;if([1,220,520].includes(n))c.input.release('MouseRight');if([100,400].includes(n))c.input.press('MouseRight');if([320,600].includes(n))c.input.press('KeyX');if([323,603].includes(n))c.input.release('KeyX');}
     if(frames.length<720)requestAnimationFrame(step);else resolve();}requestAnimationFrame(step);});
   frames.shift();const sorted=[...frames].sort((a,b)=>a-b);
   const mean=frames.reduce((a,b)=>a+b)/frames.length,slow=sorted.slice(-Math.ceil(sorted.length*.01)),slowMean=slow.reduce((a,b)=>a+b)/slow.length;
   const gl=c.renderer.getContext();if(gl.drawingBufferWidth!==1920||gl.drawingBufferHeight!==1080)throw Error('Resolution changed during measurement: '+gl.drawingBufferWidth+'x'+gl.drawingBufferHeight);const ext=gl.getExtension('WEBGL_debug_renderer_info');
   return {clips:[...clips],meanAnimationMs:animationMs.reduce((a,b)=>a+b)/animationMs.length,meanFrameMs:mean,averageFPS:1000/mean,onePercentLowFPS:1000/slowMean,p99FrameMs:sorted[Math.floor(sorted.length*.99)],maxFrameMs:sorted.at(-1),hitchesOver33ms:frames.filter(x=>x>33.34).length,hitchesOver50ms:frames.filter(x=>x>50).length,frames,settings:window.__sys.save.state.settings,buffer:[gl.drawingBufferWidth,gl.drawingBufferHeight],renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),draw:c.renderer.info.render,life:c.world.life.stats(),visibility:document.visibilityState};
 },view);
 report.views.push({view,...r});
 const capture=await cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(`docs/anim/hero/${stage}-${view}.png`,Buffer.from(capture.data,'base64'));
 report.views.at(-1).window=await cdp.send('Browser.getWindowForTarget');
 console.log(view,JSON.stringify({...r,frames:undefined}));
}
fs.writeFileSync(`docs/anim/hero/${stage}-performance.json`,JSON.stringify(report,null,2));
process.exit(0);
