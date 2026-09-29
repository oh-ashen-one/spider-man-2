import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import { createInput } from '../src/player/input.js';
import { manualTrick, hasTrickRoom, TRICK_DURATION } from '../src/player/traversal/tricks.js';
import { createHeroPreview } from '../src/ui/menus/hero-preview.js';

const library=JSON.parse(fs.readFileSync(new URL('../public/assets/animations/hero-acrobatics.json',import.meta.url)));
function rigFixture() {
 const raw=fs.readFileSync(new URL('../public/assets/spiderman.glb',import.meta.url));
 const doc=JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString());
 const jointIds=new Set(doc.skins[0].joints);
 const nodes=doc.nodes.map((n,i)=>{
  const o=jointIds.has(i)?new THREE.Bone():new THREE.Group();o.name=THREE.PropertyBinding.sanitizeNodeName(n.name||'node'+i);
  if(n.matrix) new THREE.Matrix4().fromArray(n.matrix).decompose(o.position,o.quaternion,o.scale);
  else {if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);}
  return o;
 });
 doc.nodes.forEach((n,i)=>n.children?.forEach(j=>nodes[i].add(nodes[j])));
 const model=new THREE.Group();doc.scenes[doc.scene||0].nodes.forEach(i=>model.add(nodes[i]));
 const object=new THREE.Group();object.add(model);
 const parent=new THREE.Group();parent.rotation.set(.4,.7,-.2);parent.position.set(12,25,-9);parent.add(object);parent.updateMatrixWorld(true);
 return {object,model,allClips:library.clips.map(c => THREE.AnimationClip.parse(c)),nodes};
}

test('manual intent is directional; low clearance rejects a trick before impact',()=>{
 assert.deepEqual(manualTrick({x:1,y:0}),{name:'corkscrew',side:1});
 assert.deepEqual(manualTrick({x:-1,y:0}),{name:'corkscrew',side:-1});
 assert.deepEqual(manualTrick({x:0,y:-1}),{name:'layout',side:-1});
 assert.equal(manualTrick({x:0,y:1}).name,'tuckFlip');
 assert.equal(manualTrick({x:0,y:0},1).name,'scissor');
 assert.equal(hasTrickRoom(2,15,1.3),false);
 assert.equal(hasTrickRoom(10,-20,1.3),false);
 assert.equal(hasTrickRoom(50,0,1.3),true);
 assert.equal(hasTrickRoom(NaN,0,1),false);
});

test('keyboard trick and L3 are independent press edges, not held-key repeat or jump',()=>{
 const listeners=new Map();globalThis.addEventListener=(n,fn)=>listeners.set(n,fn);
 globalThis.document={pointerLockElement:null};
 let pads=[];Object.defineProperty(globalThis,'navigator',{value:{getGamepads:()=>pads},configurable:true});
 const input=createInput({addEventListener(){}});
 input.press('KeyX');let s=input.poll();assert.equal(s.trickPressed,true);assert.equal(s.jump,false);
 assert.equal(input.poll().trickPressed,false);
 input.release('KeyX');assert.equal(input.poll().trickReleased,true);
 const buttons=Array.from({length:17},()=>({pressed:false,value:0}));buttons[10]={pressed:true,value:1};
 pads=[{mapping:'standard',axes:[0,0,0,0],buttons}];
 s=input.poll();assert.equal(s.trickPressed,true);assert.equal(s.usingPad,true);assert.equal(s.quick,false);
 buttons[10].pressed=false;input.poll();buttons[10].pressed=true;assert.equal(input.poll().trickPressed,true);
});

test('baked clips bind to the original hero node names and contain real full-body inversions',()=>{
 const rig=rigFixture();const mixer=new THREE.AnimationMixer(rig.model);
 assert.equal(new Set(rig.allClips.map(c=>c.uuid)).size,8);
 assert.ok(rig.allClips.every(c=>c.uuid));
 const mapping={layout:'heroLayoutFront',corkscrew:'heroCorkscrew',tuckFlip:'heroTuckFlip',scissor:'heroScissor'};
 for(const [key,name] of Object.entries(mapping)) assert.ok(Math.abs(rig.allClips.find(c=>c.name===name).duration-TRICK_DURATION[key])<1e-5);
 for(const clip of rig.allClips){
  for(const track of clip.tracks){assert.ok(track.validate());assert.ok(rig.model.getObjectByName(THREE.PropertyBinding.parseTrackName(track.name).nodeName));}
  const action=mixer.clipAction(clip);assert.equal(action.getClip(),clip);action.play();mixer.setTime(0);
  const hips=rig.model.getObjectByName('hips');const start=hips.quaternion.clone();
  let maxRotation=0;
  for(let i=0;i<=60;i++){
   mixer.setTime(clip.duration*i/60);rig.object.updateMatrixWorld(true);
   maxRotation=Math.max(maxRotation,start.angleTo(hips.quaternion));
   for(const n of rig.nodes)assert.ok(n.matrixWorld.elements.every(Number.isFinite));
  }
  if(/Layout|Corkscrew|TuckFlip|Scissor|SuitEnter/.test(clip.name))assert.ok(maxRotation>2.5,clip.name+' must actually turn through inversion');
  mixer.stopAllAction();
 }
});

test('suit entrance anchors correctly under an airborne parent and restores every transform',()=>{
 const rig=rigFixture();
 rig.object.position.set(1,2,3);rig.object.rotation.set(.3,.4,.5);
 const snapshot=rig.nodes.map(b=>[b.position.toArray(),b.quaternion.toArray(),b.scale.toArray()]);
 const root=[rig.object.position.toArray(),rig.object.quaternion.toArray(),rig.object.scale.toArray()];
 const feet=new THREE.Vector3(100,80,120);
 const preview=createHeroPreview(rig,feet,.8);
 preview.update(.55);
 assert.ok(rig.object.getWorldPosition(new THREE.Vector3()).distanceTo(feet)<1e-9);
 const early=rig.model.getObjectByName('hips').position.clone();
 preview.update(3);
 assert.ok(rig.model.getObjectByName('hips').position.distanceTo(early)>.1);
 assert.ok(Math.abs(rig.model.getObjectByName('hips').position.x)<.03, 'idle must replace entrance instead of sharing its mixer cache entry');
 preview.restart();assert.equal(preview.time,0);
 preview.dispose();preview.dispose();
 assert.deepEqual(rig.nodes.map(b=>[b.position.toArray(),b.quaternion.toArray(),b.scale.toArray()]),snapshot);
 assert.deepEqual([rig.object.position.toArray(),rig.object.quaternion.toArray(),rig.object.scale.toArray()],root);
});
