import {chromium} from 'playwright-core';import {spawn} from 'node:child_process';import {once} from 'node:events';
const b=await chromium.connectOverCDP('http://127.0.0.1:9334',{noDefaults:true}),p=b.contexts().flatMap(c=>c.pages()).find(p=>p.url().startsWith('http://127.0.0.1:5193/'));
await p.bringToFront();await p.waitForFunction(()=>window.__ctx?.player?.rig?.animator&&window.__sys,null,{timeout:120000,polling:100});
const cdp=await p.context().newCDPSession(p);await cdp.send('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
await p.evaluate(()=>{const c=__ctx;c.manualStep=true;c.input.releaseAll();c.input.poll();c.world.life.debugCam=null;__sys.suits.apply('advanced');__sys.pause.show('suits');});
await p.waitForTimeout(400);
const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','docs/anim/hero/motion/game-suit-entrance.mp4'],{stdio:['pipe','ignore','inherit']});const done=once(ff,'close');
for(let i=0;i<105;i++){await p.evaluate(()=>{__ctx.stepFrame(1/60);__ctx.stepFrame(1/60);});const frame=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:90,captureBeyondViewport:true});if(!ff.stdin.write(Buffer.from(frame.data,'base64')))await once(ff.stdin,'drain');}
ff.stdin.end();const [code]=await done;if(code!==0)throw Error('ffmpeg '+code);
await p.evaluate(()=>{__sys.pause.close();__ctx.manualStep=false;__ctx.input.releaseAll();});
console.log('CAPTURED game-suit-entrance.mp4');process.exit(0);
