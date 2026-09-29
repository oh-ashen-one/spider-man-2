import { chromium } from 'playwright-core';
import fs from 'node:fs';
const browser=await chromium.connectOverCDP('http://127.0.0.1:9334', { noDefaults: true });
const page=browser.contexts().flatMap(c=>c.pages()).find(p=>p.url().startsWith('http://127.0.0.1:5193/'));
const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(['error','warning'].includes(m.type()))errors.push(m.type()+': '+m.text());});
await page.bringToFront();await page.reload();await page.waitForFunction(()=>window.__sys&&window.__ctx?.player?.rig?.animator,null,{timeout:120000,polling:100});
await page.bringToFront();
const cdp=await page.context().newCDPSession(page);await cdp.send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
const report={started:new Date().toISOString(),checks:[]};
report.loaded=await page.evaluate(()=>{
 const c=window.__ctx;c.manualStep=true;c.world.life.debugCam=null;
 return {clips:c.player.rig.allClips.map(c=>c.name).filter(n=>n.startsWith('hero')),rig:c.player.rig.source};
});
if(report.loaded.clips.length!==8)throw Error('Eight authored clips did not load');
await page.evaluate(()=>{
 const c=window.__ctx,p=c.player;
 window.__heroBefore={bones:[],pos:p.position.toArray(),vel:p.velocity.toArray(),mode:p.mode,sub:p.sub};
 p.rig.model.traverse(b=>{if(b.isBone)window.__heroBefore.bones.push([b.name,...b.position.toArray(),...b.quaternion.toArray(),...b.scale.toArray()]);});
 window.__sys.pause.show('suits');
});
let frame=0;
for(const t of [0,.4,.8,1.08,1.5,2.5]){
 const want=Math.round(t*60);
 await page.evaluate(n=>{for(let i=0;i<n;i++)window.__ctx.stepFrame(1/60);},want-frame);frame=want;
 await page.screenshot({path:`docs/anim/hero/game-suit-${t.toFixed(2)}.png`});
}
report.checks.push(await page.evaluate(()=>{
 const c=window.__ctx,p=c.player;window.__sys.pause.close();
 const bones=[];p.rig.model.traverse(b=>{if(b.isBone)bones.push([b.name,...b.position.toArray(),...b.quaternion.toArray(),...b.scale.toArray()]);});
 const old=window.__heroBefore;
 return {name:'menu-restores-gameplay',passed:JSON.stringify(bones)===JSON.stringify(old.bones)&&JSON.stringify(p.position.toArray())===JSON.stringify(old.pos)&&JSON.stringify(p.velocity.toArray())===JSON.stringify(old.vel)&&p.mode===old.mode&&p.sub===old.sub};
}));
await page.waitForTimeout(350);
for(const [name,key] of [['front','KeyW'],['back','KeyS'],['left','KeyA'],['right','KeyD'],['neutral',null]]){
 const result=await page.evaluate(({key})=>{
  const c=window.__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,65,167),0);p.velocity.set(0,5,0);
  c.stepFrame(1/60);
  if(key)c.input.press(key);c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();
  const start={mode:p.mode,sub:p.sub,trick:p.anim.trick,side:p.anim.trickSide,clip:p.rig.animator.debug.clip};
  const samples=[];
  for(let i=0;i<20;i++){c.world.life.debugCam=[p.position.x+3,p.position.y+1,p.position.z+4,p.position.x,p.position.y,p.position.z];c.stepFrame(1/60);samples.push(p.rig.animator.debug.clip);}
  return {start,clips:[...new Set(samples)],velocity:p.velocity.toArray()};
 },{key});
 report.checks.push({name:'manual-'+name,...result,passed:result.start.sub==='trick'&&result.start.clip.startsWith('hero')});
 await page.screenshot({path:`docs/anim/hero/game-trick-${name}.png`});
}
// Actual web acquisition followed by release exercises automatic traversal, not just clip playback.
report.checks.push(await page.evaluate(()=>{
 const c=window.__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,45,167),0);p.velocity.set(0,0,18);c.world.life.debugCam=null;
 c.input.press('MouseRight');let attached=false;
 for(let i=0;i<150;i++){c.stepFrame(1/60);if(p.mode==='swing'){attached=true;break;}}
 if(!attached){c.input.releaseAll();return {name:'automatic-release',passed:false,reason:'No web attached at fixture position',mode:p.mode};}
 for(let i=0;i<12;i++)c.stepFrame(1/60);
 c.input.release('MouseRight');c.stepFrame(1/60);
 return {name:'automatic-release',passed:p.sub==='trick'&&p.rig.animator.debug.clip.startsWith('hero'),sub:p.sub,trick:p.anim.trick,clip:p.rig.animator.debug.clip};
}));
report.errors=[...new Set(errors)];
fs.writeFileSync('docs/anim/hero/runtime-checks.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
process.exit(report.checks.every(c=>c.passed)?0:1);
