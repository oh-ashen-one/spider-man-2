import {chromium} from 'playwright-core';
import fs from 'node:fs';
const browser=await chromium.connectOverCDP('http://127.0.0.1:9334',{noDefaults:true});
const page=browser.contexts().flatMap(c=>c.pages()).find(p=>p.url().startsWith('http://127.0.0.1:5193/')&&!p.url().includes('tools/'));
await page.bringToFront();await page.reload();await page.waitForFunction(()=>window.__sys&&window.__ctx?.player?.rig?.animator,null,{timeout:120000,polling:100});
const cdp=await page.context().newCDPSession(page);await cdp.send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
await page.bringToFront();
await page.evaluate(()=>{__ctx.manualStep=true;__ctx.input.releaseAll();__ctx.input.poll();__ctx.world.life.debugCam=null;});
const report={started:new Date().toISOString(),checks:[]};
async function check(name,fn,arg){const result=await page.evaluate(fn,arg);report.checks.push({name,...result});console.log(name,JSON.stringify(result));}
for(const id of ['claude','codex','gemini','kimi','qwen']){
 await page.evaluate(()=>__sys.pause.show('suits'));
 await page.locator('.sys-suit[data-id="'+id+'"]').click();
 await page.waitForFunction(id=>__sys.suits.skins.worn==='/assets/skins/'+id+'.glb',id,{timeout:120000,polling:100});
 await page.keyboard.press('r');
 await page.evaluate(()=>{for(let i=0;i<27;i++)__ctx.stepFrame(1/60);});
 await page.screenshot({path:'docs/anim/hero/skin-'+id+'-flip.png'});
 await check('skin-'+id,()=>{
  const c=__ctx;let body,skin;c.player.object.traverse(o=>{if(o.name==='SpiderMan')body=o;if(o.userData.isSuitSkin)skin=o;});
  skin.skeleton.update();skin.computeBoundingBox();const size=skin.boundingBox.getSize(new c.THREE.Vector3());
  return {passed:skin.skeleton===body.skeleton&&!body.visible&&size.toArray().every(v=>Number.isFinite(v)&&v>0&&v<5),bounds:size.toArray(),bones:skin.skeleton.bones.length};
 });
 await page.evaluate(()=>{for(let i=0;i<129;i++)__ctx.stepFrame(1/60);});
 await page.screenshot({path:'docs/anim/hero/skin-'+id+'-idle.png'});
 await check('skin-'+id+'-idle',()=>({passed:Math.abs(__ctx.player.rig.model.getObjectByName('hips').position.x)<.03,x:__ctx.player.rig.model.getObjectByName('hips').position.x}));
 await page.evaluate(()=>__sys.pause.close());await page.waitForTimeout(350);
}
// Real card clicks while pending cached loads; the last request must win.
await page.evaluate(()=>__sys.pause.show('suits'));
await page.evaluate(()=>{for(const id of ['qwen','claude','gemini','codex','kimi','qwen','codex'])document.querySelector('.sys-suit[data-id="'+id+'"]').click();});
await page.waitForFunction(()=>__sys.suits.skins.worn==='/assets/skins/codex.glb');
await check('rapid-card-switch',()=>({passed:__sys.suits.current==='codex'&&__sys.suits.skins.worn==='/assets/skins/codex.glb',current:__sys.suits.current,worn:__sys.suits.skins.worn}));
await page.evaluate(()=>__sys.pause.close());await page.waitForTimeout(350);
await check('low-clearance-rejects-manual',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();const y=c.world.groundHeight(250,167,100)+3;
 p.teleport(new c.THREE.Vector3(250,y,167),0);p.velocity.set(0,-15,0);c.stepFrame(1/60);c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();
 return {passed:p.sub!=='trick',mode:p.mode,sub:p.sub};
});
await check('drop-interrupts-trick',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,65,167),0);p.velocity.set(0,5,0);c.stepFrame(1/60);
 c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();for(let i=0;i<14;i++)c.stepFrame(1/60);
 const before=p.sub;c.input.press('KeyC');for(let i=0;i<5;i++)c.stepFrame(1/60);c.input.releaseAll();
 return {passed:before==='trick'&&p.sub!=='trick'&&!p.rig.animator.debug.clip.startsWith('hero'),before,sub:p.sub,clip:p.rig.animator.debug.clip};
});
await check('fresh-web-press-interrupts-trick',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,45,167),0);p.velocity.set(0,5,18);c.stepFrame(1/60);
 c.input.press('KeyX');c.stepFrame(1/60);const before=p.sub;c.input.releaseAll();c.stepFrame(1/60);c.input.press('MouseRight');
 let frames=0;while(p.mode!=='swing'&&frames++<60)c.stepFrame(1/60);c.input.releaseAll();
 return {passed:before==='trick'&&p.mode==='swing'&&frames<30,before,mode:p.mode,frames,clip:p.rig.animator.debug.clip};
});
await check('held-key-does-not-retrigger',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,180,167),0);p.velocity.set(0,10,0);c.stepFrame(1/60);
 c.input.press('KeyX');let entries=0,last=false;
 for(let i=0;i<180;i++){c.stepFrame(1/60);const trick=p.sub==='trick';if(trick&&!last)entries++;last=trick;}c.input.releaseAll();
 return {passed:entries===1,entries,mode:p.mode,sub:p.sub};
});
await check('airborne-menu-restores-state',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,100,167),1);p.velocity.set(5,5,4);c.stepFrame(1/60);
 c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();for(let i=0;i<20;i++)c.stepFrame(1/60);
 const snap=()=>{const bones=[];p.rig.model.traverse(b=>{if(b.isBone)bones.push([...b.position,...b.quaternion,...b.scale]);});return JSON.stringify({pos:p.position.toArray(),vel:p.velocity.toArray(),mode:p.mode,sub:p.sub,bones});};
 const before=snap();__sys.pause.show('suits');for(let i=0;i<163;i++)c.stepFrame(1/60);__sys.pause.close();
 return {passed:before===snap(),mode:p.mode,sub:p.sub};
});
await page.waitForTimeout(350);
await check('ground-jump-uses-authored-launch',()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();const floor=c.world.groundHeight(250,167,100);
 p.teleport(new c.THREE.Vector3(250,floor+1,167),0);for(let i=0;i<40;i++)c.stepFrame(1/60);
 c.input.press('Space');for(let i=0;i<8;i++)c.stepFrame(1/60);c.input.release('Space');
 const clips=[];for(let i=0;i<45;i++){c.stepFrame(1/60);clips.push(p.rig.animator.debug.clip);}
 return {passed:clips.includes('heroJumpLaunch'),clips:[...new Set(clips)],mode:p.mode,sub:p.sub};
});
fs.writeFileSync('docs/anim/hero/extended-runtime.json',JSON.stringify(report,null,2));
process.exit(report.checks.every(c=>c.passed)?0:1);
