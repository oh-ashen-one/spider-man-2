import {chromium} from 'playwright-core';import fs from 'node:fs';import {spawn} from 'node:child_process';import {once} from 'node:events';
const b=await chromium.connectOverCDP('http://127.0.0.1:9334',{noDefaults:true});
const ctx=b.contexts()[0],url='http://127.0.0.1:5193/tools/heroanim/review.html';
const p=ctx.pages().find(p=>p.url()===url)||await ctx.newPage();await p.goto(url);await p.bringToFront();
const cdp=await ctx.newCDPSession(p);await cdp.send('Emulation.setDeviceMetricsOverride',{width:1280,height:720,deviceScaleFactor:1,mobile:false});
await p.waitForFunction(()=>window.__review,null,{timeout:120000,polling:100});
const clips=await p.evaluate(()=>__review.clips),out='docs/anim/hero/motion';fs.mkdirSync(out,{recursive:true});
for(const clip of clips){
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',out+'/'+clip.name+'.mp4'],{stdio:['pipe','ignore','inherit']});
 const done=once(ff,'close');
 for(let i=0;i<Math.ceil((clip.duration+.4)*30);i++){
  const t=Math.min(clip.duration-.00001,i/30);await p.evaluate(({name,t})=>__review.sample(name,t),{name:clip.name,t});
  const image=await p.screenshot({type:'jpeg',quality:90});if(!ff.stdin.write(image))await once(ff.stdin,'drain');
 }
 ff.stdin.end();const [code]=await done;if(code!==0)throw Error('ffmpeg '+code);console.log('CAPTURED',clip.name);
}
fs.writeFileSync('docs/anim/hero/motion/README.md','# Hero motion reviews\n\nThirty FPS deterministic Three.js playback of the exported Blender Actions, shown at normal speed from simultaneous three-quarter and side views. These are animation reviews, not performance measurements. Source: tools/heroanim/review.html.\n');
process.exit(0);
