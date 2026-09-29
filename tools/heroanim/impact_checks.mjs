import {chromium} from 'playwright-core';import fs from 'node:fs';
const b=await chromium.connectOverCDP('http://127.0.0.1:9334',{noDefaults:true});const p=b.contexts().flatMap(c=>c.pages()).find(p=>p.url().startsWith('http://127.0.0.1:5193/'));
await p.bringToFront();await p.waitForFunction(()=>window.__ctx?.player?.rig?.animator&&window.__sys,null,{timeout:120000,polling:100});
const report={checks:[]};
report.checks.push(await p.evaluate(()=>{
 const c=__ctx,p=c.player;c.manualStep=true;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,65,167),0);p.velocity.set(0,5,0);c.stepFrame(1/60);c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();const before=p.sub;
 p.velocity.set(0,-56,0);let frames=0;while(p.mode==='air'&&frames++<180)c.stepFrame(1/60);
 return {name:'landing-releases-trick',passed:before==='trick'&&p.mode==='ground'&&!p.anim.trick,mode:p.mode,sub:p.sub,frames,clip:p.rig.animator.debug.clip};
}));
report.checks.push(await p.evaluate(()=>{
 const c=__ctx,p=c.player;c.input.releaseAll();c.input.poll();let hit=null;
 for(const y of [40,25,15]){if(hit)break;const o=new c.THREE.Vector3(250,y,167);for(let k=0;k<16;k++){const a=k*Math.PI/8,h=c.world.raycast(o,new c.THREE.Vector3(Math.cos(a),0,Math.sin(a)),120);if(h&&Math.abs(h.normal.y)<.1){const q=h.point.clone().addScaledVector(h.normal,3);if(q.y-c.world.groundHeight(q.x,q.z,q.y)>8){hit=h;break;}}}}
 if(!hit)return {name:'wall-interrupts-trick',passed:false,reason:'No fixture facade found'};
 p.teleport(hit.point.clone().addScaledVector(hit.normal,3),0);p.velocity.copy(hit.normal).multiplyScalar(-20);p.velocity.y=15;c.stepFrame(1/60);c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();const before=p.sub;
 let frames=0;while(p.sub==='trick'&&frames++<25)c.stepFrame(1/60);
 return {name:'wall-interrupts-trick',passed:before==='trick'&&p.sub!=='trick'&&frames<25,mode:p.mode,sub:p.sub,frames,clip:p.rig.animator.debug.clip};
}));
await p.route('**/assets/animations/hero-acrobatics.json',route=>route.fulfill({status:404,body:'Deliberate missing-library test'}));
await p.reload();await p.waitForFunction(()=>window.__ctx?.player?.rig?.animator&&window.__sys,null,{timeout:120000,polling:100});
report.checks.push(await p.evaluate(()=>{
 const c=__ctx,p=c.player;c.manualStep=true;c.input.releaseAll();c.input.poll();p.teleport(new c.THREE.Vector3(250,65,167),0);p.velocity.set(0,5,0);c.stepFrame(1/60);c.input.press('KeyX');c.stepFrame(1/60);c.input.releaseAll();const clip=p.rig.animator.debug.clip;
 __sys.pause.show('suits');for(let i=0;i<90;i++)c.stepFrame(1/60);__sys.pause.close();
 return {name:'missing-library-falls-back',passed:p.rig.allClips.length===79&&clip.startsWith('trick:')&&p.rig.animator.enabled,clip,clips:p.rig.allClips.length};
}));
await p.unroute('**/assets/animations/hero-acrobatics.json');await p.reload();
fs.writeFileSync('docs/anim/hero/impact-fallback-checks.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));process.exit(report.checks.every(c=>c.passed)?0:1);
