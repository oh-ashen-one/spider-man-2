import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { loadHeroClips } from '/src/player/anim/hero-clips.js';
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(1);renderer.setSize(1280,720);renderer.setScissorTest(true);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;document.body.append(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color(0x253047);scene.add(new THREE.HemisphereLight(0xcde6ff,0x373442,2));
for(const [x,y,z,power,color] of [[3,5,4,4,0xffe6d4],[-4,3,1,2,0xbed7ff],[1,4,-4,4,0xc5deff]]){
 const l=new THREE.DirectionalLight(color,power);l.position.set(x,y,z);l.castShadow=x===3;l.shadow.mapSize.set(1024,1024);Object.assign(l.shadow.camera,{left:-5,right:5,top:5,bottom:-5});l.shadow.bias=-.0004;scene.add(l);
}
const floor=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x303d55,roughness:.8}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);
const {scene:model}=await new GLTFLoader().loadAsync('/assets/spiderman.glb');model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;}});scene.add(model);
const clips=await loadHeroClips(model);if(clips.length!==8)throw Error('Authored library unavailable');
const mixer=new THREE.AnimationMixer(model),cameras=[new THREE.OrthographicCamera(),new THREE.OrthographicCamera()];
const select=document.querySelector('#clips');select.innerHTML=clips.map(c=>'<option>'+c.name+'</option>').join('');
let current=null,time=0,playing=true,manual=false;
function sample(name,t){
 const clip=clips.find(c=>c.name===name);if(clip!==current){mixer.stopAllAction();mixer.clipAction(clip).play();current=clip;select.value=name;}
 mixer.setTime(Math.min(t,clip.duration-.00001));model.updateMatrixWorld(true);
 const menu=name==='heroSuitEnter',height=menu?4.5:2.8,center=new THREE.Vector3(menu?.7:0,menu?1.4:1,0);
 cameras.forEach((cam,i)=>{cam.left=-height*640/720/2;cam.right=-cam.left;cam.top=height/2;cam.bottom=-height/2;cam.near=.1;cam.far=100;cam.position.copy(center).add(new THREE.Vector3(...(i?[6,0,0]:[3,1,6])));cam.lookAt(center);cam.updateProjectionMatrix();renderer.setViewport(i*640,0,640,720);renderer.setScissor(i*640,0,640,720);renderer.render(scene,cam);});
 document.querySelector('#time').textContent=t.toFixed(2)+' / '+clip.duration.toFixed(2)+' s';
}
select.onchange=()=>{time=0;sample(select.value,0);};document.querySelector('#play').onclick=()=>{playing=!playing;document.querySelector('#play').textContent=playing?'Pause':'Play';};
let previous=performance.now();function animate(now){const dt=Math.min(.05,(now-previous)/1000);previous=now;if(!manual){if(playing)time=(time+dt)%(current.duration+.5);sample(select.value,Math.min(time,current.duration));}requestAnimationFrame(animate);}
sample(clips[0].name,0);requestAnimationFrame(animate);
window.__review={clips:clips.map(c=>({name:c.name,duration:c.duration})),sample:(name,t)=>{manual=true;sample(name,t);},play:()=>{manual=false;playing=true;}};
