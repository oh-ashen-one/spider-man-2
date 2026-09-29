import fs from 'node:fs';
import * as THREE from 'three';
const raw=fs.readFileSync('public/assets/spiderman.glb'),doc=JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)));
const nodes=doc.nodes.map(n=>{const o=new THREE.Object3D();o.name=THREE.PropertyBinding.sanitizeNodeName(n.name||'');if(n.matrix)new THREE.Matrix4().fromArray(n.matrix).decompose(o.position,o.quaternion,o.scale);else{if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);}return o;});
doc.nodes.forEach((n,i)=>n.children?.forEach(j=>nodes[i].add(nodes[j])));
const model=new THREE.Group();doc.scenes[doc.scene||0].nodes.forEach(i=>model.add(nodes[i]));
const byName=Object.fromEntries(doc.nodes.map((n,i)=>[n.name,nodes[i]]));
const mixer=new THREE.AnimationMixer(model);
const clips=JSON.parse(fs.readFileSync('public/assets/animations/hero-acrobatics.json')).clips.map(c=>THREE.AnimationClip.parse(c));
const witness=JSON.parse(fs.readFileSync('.scratch/blender-witness.json'));
let clipName=null,maxMatrixError=0,maxJointPositionError=0,worst=null;
for(const row of witness.rows){
 if(clipName!==row.clip){mixer.stopAllAction();mixer.clipAction(clips.find(c=>c.name===row.clip)).play();clipName=row.clip;}
 mixer.setTime(row.time);model.updateMatrixWorld(true);
 for(const [name,want] of Object.entries(row.world)){
  const got=byName[name].matrixWorld.elements;
  const err=Math.max(...got.map((v,i)=>Math.abs(v-want[i])));
  if(err>maxMatrixError){maxMatrixError=err;worst={clip:row.clip,time:row.time,bone:name};}
  maxJointPositionError=Math.max(maxJointPositionError,Math.hypot(got[12]-want[12],got[13]-want[13],got[14]-want[14]));
 }
}
const contacts={};
for(const row of witness.contacts)for(const [name,p] of Object.entries(row.feet)){
 const key=row.clip+'/'+name;
 if(!contacts[key])contacts[key]={min:[...p],max:[...p]};
 p.forEach((v,i)=>{contacts[key].min[i]=Math.min(contacts[key].min[i],v);contacts[key].max[i]=Math.max(contacts[key].max[i],v);});
}
const report={poses:witness.rows.length,bones:58,sampling:'Nonuniform times including between baked 120 Hz keys',maxMatrixError,maxJointPositionError,worst,tolerance:{matrix:.015,jointPositionMetres:.01},contacts};
report.passed=maxMatrixError<.015&&maxJointPositionError<.01;
fs.writeFileSync('docs/anim/hero/export-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));process.exit(report.passed?0:1);
