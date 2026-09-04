import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tactical Shooting Range", layout="wide")
st.title("TACTICAL SHOOTING RANGE")
st.caption("화면 클릭 → 마우스 잠금 | WASD 이동 | Shift 달리기 | 좌클릭 사격 | R 재시작")

game = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#15120f;font-family:Arial,sans-serif}
canvas{display:block}
#ui{position:fixed;inset:0;pointer-events:none;color:#e8edf0;z-index:10}
#rangeLabel{position:absolute;left:0;top:112px;background:rgba(40,62,61,.9);padding:12px 22px;font-size:15px;font-weight:bold;letter-spacing:1px}
#settings{position:absolute;left:0;top:160px;width:170px;background:rgba(12,16,17,.72);border-right:1px solid rgba(255,255,255,.15);font-size:11px;line-height:25px;padding:7px 10px}
#settings b{float:right;color:#d9dedb}
#scoreBoard{position:absolute;top:28px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:0}
.scoreBox{width:210px;height:62px;background:rgba(24,31,34,.86);border:2px solid #59646a;box-shadow:0 3px 12px rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;color:#d9e6e9}
.scoreMid{width:170px;height:70px;background:rgba(26,33,37,.95);border:2px solid #687278;display:flex;align-items:center;justify-content:space-around;font-size:28px;color:#b9e0eb}
#cross{position:absolute;left:50%;top:50%;width:20px;height:20px;transform:translate(-50%,-50%)}
#cross:before,#cross:after{content:"";position:absolute;background:#d8f1ed;box-shadow:0 0 5px #000}
#cross:before{width:2px;height:18px;left:9px;top:1px}
#cross:after{width:18px;height:2px;left:1px;top:9px}
#bottomPanel{position:absolute;left:50%;bottom:-10px;transform:translateX(-50%);width:350px;height:145px;background:linear-gradient(110deg,rgba(20,31,35,.94),rgba(41,60,67,.94));border:3px solid #11181b;border-top:2px solid #6a9da2;clip-path:polygon(8% 0,92% 0,100% 100%,0 100%);padding:14px 55px;color:#c9d8da}
#bottomPanel h3{text-align:center;font-size:13px;margin:0 0 8px;letter-spacing:1px}
.option{font-size:20px;line-height:35px}.dim{color:#7c898b}
#weaponInfo{position:absolute;right:28px;bottom:22px;text-align:right;font-size:12px;color:#93aaa7}
#weaponInfo strong{display:block;font-size:24px;color:#e4eeed}
#message{position:absolute;top:120px;left:50%;transform:translateX(-50%);font-size:18px;font-weight:bold;color:#ffce73;text-shadow:0 0 12px #000}
#damage{position:absolute;inset:0;background:radial-gradient(circle,transparent 50%,rgba(255,90,30,.35));opacity:0;transition:.08s}
</style>
</head>
<body>
<div id="ui">
 <div id="rangeLabel">SHOOTING RANGE</div>
 <div id="settings">Challenge <b>HARD</b><br>Bot Armor <b>DISABLED</b><br>Infinite Ammo <b>ENABLED</b><br><span style="color:#9ba7a8">Press [F3] change settings</span></div>
 <div id="scoreBoard"><div class="scoreBox" id="kills">00</div><div class="scoreMid"><span id="timer">60</span><span style="font-size:13px;color:#6d8287">●</span><span id="hits">00</span></div><div class="scoreBox" id="best">000</div></div>
 <div id="cross"></div>
 <div id="message">CLICK TO ENTER RANGE</div>
 <div id="bottomPanel"><h3>SKILLS TEST</h3><div class="option">□ EXIT</div><div class="option">□ Practice</div><div class="dim" style="font-size:11px;margin-top:5px">AIM SENSITIVITY&nbsp;&nbsp; 1.35</div></div>
 <div id="weaponInfo">TRAINING WEAPON<strong>VX-9</strong>∞ AMMO</div>
 <div id="damage"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x4b4034);
scene.fog=new THREE.Fog(0x4b4034,32,85);

const camera=new THREE.PerspectiveCamera(73,innerWidth/innerHeight,.05,150);
camera.position.set(0,1.65,10);

const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:"high-performance"});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.25;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffd9aa,0x30343b,2.0));
const key=new THREE.DirectionalLight(0xffe0bd,3.2);key.position.set(-9,16,12);key.castShadow=true;key.shadow.mapSize.set(2048,2048);scene.add(key);
const fill=new THREE.PointLight(0xffb36b,4,32);fill.position.set(0,7,-7);scene.add(fill);

function mat(c,r=.7,m=.05){return new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m});}
const concrete=mat(0x82796d,.88), wallMat=mat(0xa09383,.95), wood=mat(0x5a351e,.7), beamMat=mat(0x3c2920,.55,.15), steel=mat(0x31393b,.4,.7);

function addBox(x,y,z,w,h,d,material=concrete){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;scene.add(o);return o;
}

// floor + shooting lanes
addBox(0,-.12,-18,52,.25,70,mat(0x68635d,.9));
for(let x=-12;x<=12;x+=6){
 const line=addBox(x,.02,-15,.055,.025,50,mat(0xd2a35c,.45,.1));
}

// hangar walls
addBox(0,5,-35,52,10,.8,wallMat);
addBox(-25,4,-12,.8,8,48,wallMat);
addBox(25,4,-12,.8,8,48,wallMat);

// ceiling wooden trusses
for(let z=-2;z>=-34;z-=7){
 addBox(0,8.3,z,48,.35,.45,wood);
 addBox(-12,7.1,z,20,.28,.28,beamMat).rotation.z=.38;
 addBox(12,7.1,z,20,.28,.28,beamMat).rotation.z=-.38;
}
for(let x=-21;x<=21;x+=7){
 addBox(x,7.8,-18,.42,2.6,35,beamMat);
}

// right elevated room + stairs
addBox(17,4.5,-15,14,7,9,mat(0x756e64,.85));
addBox(17,7.5,-15,13.4,.1,8.5,steel);
for(let i=0;i<9;i++) addBox(11.5+i*.58,.25+i*.35,-10.3,1.5,.32,3,wood);

// crates and equipment
for(const p of [[-18,.8,-5,2,1.6,2],[-16,.5,-5,1.5,1,1.4],[20,.6,-27,2,1.2,2],[22,.45,-28,1.3,.9,1.4]]){
 addBox(...p,wood);
}

// suspended scoreboard
const boardMat=mat(0x20282b,.35,.45);
const board=addBox(0,6.2,-14,7.8,1.55,.18,boardMat);
const boardLight=new THREE.PointLight(0x9ddcff,2.2,9);boardLight.position.set(0,6.0,-12.8);scene.add(boardLight);
for(const x of [-2.2,2.2]) addBox(x,7.8,-14,.08,2.2,.08,steel);
const scoreTex=document.createElement("canvas");scoreTex.width=512;scoreTex.height=120;
const ctx=scoreTex.getContext("2d");ctx.fillStyle="#243137";ctx.fillRect(0,0,512,120);
ctx.font="bold 62px Arial";ctx.fillStyle="#b9d9e4";ctx.fillText("00       23",55,82);
const scoreMat=new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(scoreTex)});
const scoreFace=new THREE.Mesh(new THREE.PlaneGeometry(6.8,1.2),scoreMat);scoreFace.position.set(0,6.2,-13.88);scene.add(scoreFace);

// wall weapon racks / pipes
for(let x=-15;x<=15;x+=10){
 addBox(x,3.8,-34.4,4,.08,.25,steel);
 addBox(x-1.8,3.8,-34.2,.08,.8,.1,steel);
}

// bot materials
const botBody=mat(0x252d32,.45,.55);
const botArmor=mat(0x83516b,.55,.25);
const botGlow=new THREE.MeshStandardMaterial({color:0xff6b9c,emissive:0xff2b65,emissiveIntensity:2});

const bots=[];
function makeBot(){
 const g=new THREE.Group();
 const torso=new THREE.Mesh(new THREE.CapsuleGeometry(.28,.72,5,10),botArmor);torso.position.y=1.15;torso.castShadow=true;g.add(torso);
 const head=new THREE.Mesh(new THREE.SphereGeometry(.22,16,12),botBody);head.position.y=1.95;g.add(head);
 const visor=new THREE.Mesh(new THREE.BoxGeometry(.28,.08,.08),botGlow);visor.position.set(0,1.95,-.2);g.add(visor);
 [-1,1].forEach(s=>{
   const arm=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,.68,10),botBody);arm.position.set(.38*s,1.28,0);arm.rotation.z=.08*s;g.add(arm);
   const leg=new THREE.Mesh(new THREE.CylinderGeometry(.11,.13,.78,10),botBody);leg.position.set(.16*s,.38,0);g.add(leg);
 });
 g.userData={phase:Math.random()*6.28,alive:true,respawn:0};
 scene.add(g);bots.push(g);return g;
}
function randomizeBot(b){
 b.position.set((Math.random()-.5)*24,0,-8-Math.random()*26);
 b.rotation.y=Math.random()*Math.PI;
 b.visible=true;b.userData.alive=true;
}
for(let i=0;i<7;i++){const b=makeBot();randomizeBot(b);}

// first-person rifle
const gun=new THREE.Group();
const gunDark=mat(0x14191c,.28,.8), gunMetal=mat(0x384246,.25,.85), gunAccent=mat(0x685a2c,.45,.4);
const body=new THREE.Mesh(new THREE.BoxGeometry(.42,.30,1.35),gunDark);body.position.set(.35,-.35,-.9);gun.add(body);
const receiver=new THREE.Mesh(new THREE.BoxGeometry(.35,.20,.8),gunMetal);receiver.position.set(.34,-.20,-1.35);gun.add(receiver);
const barrel=new THREE.Mesh(new THREE.CylinderGeometry(.07,.08,.85,12),gunDark);barrel.rotation.x=Math.PI/2;barrel.position.set(.34,-.27,-2.05);gun.add(barrel);
const grip=new THREE.Mesh(new THREE.BoxGeometry(.18,.5,.24),gunMetal);grip.rotation.z=.25;grip.position.set(.25,-.65,-.75);gun.add(grip);
const sight=new THREE.Mesh(new THREE.BoxGeometry(.12,.16,.18),gunAccent);sight.position.set(.35,-.08,-1.3);gun.add(sight);
camera.add(gun);scene.add(camera);

let locked=false,yaw=0,pitch=0,kills=0,hits=0,time=60,shots=0,running=false;
const keys={};
const message=document.getElementById("message");
renderer.domElement.addEventListener("click",()=>renderer.domElement.requestPointerLock());
document.addEventListener("pointerlockchange",()=>{
 locked=document.pointerLockElement===renderer.domElement;
 running=locked;
 message.textContent=locked?"":"CLICK TO ENTER RANGE";
});
document.addEventListener("mousemove",e=>{
 if(!locked)return;
 yaw-=e.movementX*.0022;
 pitch=Math.max(-1.35,Math.min(1.35,pitch-e.movementY*.0022));
 camera.rotation.set(pitch,yaw,0,"YXZ");
});
addEventListener("keydown",e=>{
 keys[e.code]=true;
 if(e.code==="KeyR") resetGame();
});
addEventListener("keyup",e=>keys[e.code]=false);
addEventListener("mousedown",e=>{if(e.button===0&&locked)shoot();});
addEventListener("contextmenu",e=>e.preventDefault());

const ray=new THREE.Raycaster();
function shoot(){
 if(!running||time<=0)return;
 shots++;
 gun.position.z=.09;gun.rotation.x=-.08;
 setTimeout(()=>{gun.position.z=0;gun.rotation.x=0},55);
 ray.setFromCamera(new THREE.Vector2(),camera);
 const meshes=[];
 bots.forEach(b=>{if(b.visible)b.traverse(o=>{if(o.isMesh)meshes.push(o)})});
 const result=ray.intersectObjects(meshes,false);
 if(result.length){
   let hit=result[0].object;
   while(hit.parent&&!bots.includes(hit))hit=hit.parent;
   if(hit&&hit.userData.alive){
     hit.userData.alive=false;hit.visible=false;kills++;hits++;
     setTimeout(()=>randomizeBot(hit),650);
   }
 }
}

function resetGame(){
 kills=0;hits=0;shots=0;time=60;
 bots.forEach(randomizeBot);
}
const clock=new THREE.Clock();
function animate(){
 requestAnimationFrame(animate);
 const dt=Math.min(clock.getDelta(),.05);
 if(running){
   time=Math.max(0,time-dt);
   if(time===0){running=false;document.exitPointerLock?.();message.textContent="TIME OVER · PRESS R";message.style.display="block";}
   const f=new THREE.Vector3(0,0,-1).applyQuaternion(camera.quaternion);f.y=0;f.normalize();
   const r=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion);r.y=0;r.normalize();
   const mv=new THREE.Vector3();
   if(keys.KeyW)mv.add(f);if(keys.KeyS)mv.sub(f);if(keys.KeyD)mv.add(r);if(keys.KeyA)mv.sub(r);
   if(mv.lengthSq())camera.position.addScaledVector(mv.normalize(),dt*(keys.ShiftLeft?7:3.7));
   camera.position.x=Math.max(-22,Math.min(22,camera.position.x));
   camera.position.z=Math.max(-2,Math.min(18,camera.position.z));
   bots.forEach(b=>{
     if(b.visible){
       const t=performance.now()*.001+b.userData.phase;
       b.position.y=Math.sin(t*2)*.035;
       b.rotation.y+=Math.sin(t*.7)*.002;
     }
   });
 }
 document.getElementById("kills").textContent=String(kills).padStart(2,"0");
 document.getElementById("hits").textContent=String(hits).padStart(2,"0");
 document.getElementById("best").textContent=String(kills*100).padStart(3,"0");
 document.getElementById("timer").textContent=Math.ceil(time);
 renderer.render(scene,camera);
}
animate();
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
</script>
</body></html>
"""

components.html(game, height=850, scrolling=False)
