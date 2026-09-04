import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ULTRA MECHA ARENA", layout="wide")
st.title("🔥 ULTRA GRAPHICS MECHA ARENA")
st.caption("WASD 이동 | Shift 달리기 | Space 점프 | 마우스 드래그 시점 | 좌클릭 사격 | 우클릭 ADS")

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
html,body{margin:0;overflow:hidden;background:#020617;font-family:Arial,sans-serif}
canvas{display:block}
#crosshair{position:fixed;left:50%;top:50%;width:10px;height:10px;transform:translate(-50%,-50%);
border:2px solid #7fffd4;border-radius:50%;box-shadow:0 0 12px #00ffaa,0 0 30px #00ffaa;z-index:20}
#crosshair:before,#crosshair:after{content:"";position:absolute;background:#7fffd4;box-shadow:0 0 8px #00ffaa}
#crosshair:before{width:2px;height:22px;left:2px;top:-8px}
#crosshair:after{width:22px;height:2px;left:-8px;top:2px}
#hud{position:fixed;top:20px;left:20px;z-index:20;color:white;padding:15px 22px;
background:linear-gradient(135deg,rgba(8,15,30,.92),rgba(15,30,45,.65));
border:1px solid rgba(0,255,190,.5);border-left:5px solid #00f5a0;
box-shadow:0 0 35px rgba(0,255,180,.15),inset 0 0 20px rgba(255,255,255,.03);backdrop-filter:blur(15px)}
#hud b{color:#00f5a0}
#weapon{position:fixed;right:24px;bottom:24px;z-index:20;color:#d9fff6;text-align:right;
font-size:14px;letter-spacing:2px;text-shadow:0 0 15px #00f5a0}
#weapon span{font-size:25px;font-weight:900;color:#00f5a0}
#hpwrap{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);width:420px;height:18px;
background:#08111d;border:1px solid #ff4655;padding:3px;z-index:20;box-shadow:0 0 25px rgba(255,50,80,.4)}
#hp{height:100%;width:100%;background:linear-gradient(90deg,#00e5ff,#00f5a0,#dfff00);transition:width .15s}
#damage{position:fixed;inset:0;pointer-events:none;opacity:0;z-index:18;
background:radial-gradient(circle,transparent 45%,rgba(255,0,35,.45) 100%);transition:opacity .1s}
#flash{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);font-size:38px;font-weight:900;
color:#fff;opacity:0;z-index:22;text-shadow:0 0 20px #00f5a0;pointer-events:none}
#over{display:none;position:fixed;inset:0;z-index:30;place-items:center;color:white;text-align:center;
background:rgba(0,0,0,.75);font-size:58px;font-weight:900;text-shadow:0 0 40px #ff1744}
#over small{font-size:18px;color:#9ca3af}
</style>
</head>
<body>
<div id="crosshair"></div>
<div id="hud">ELIMINATIONS: <b id="score">0</b><br><span style="font-size:11px;color:#94a3b8">ULTRA RENDER PIPELINE ACTIVE</span></div>
<div id="weapon">SYSTEM WEAPON<br><span>VX-9 PULSE RIFLE</span></div>
<div id="hpwrap"><div id="hp"></div></div>
<div id="damage"></div><div id="flash"></div>
<div id="over">SYSTEM FAILURE<br><small>페이지를 새로고침하여 재시작</small></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js"></script>

<script>
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x020612);
scene.fog=new THREE.FogExp2(0x07111d,.014);

const camera=new THREE.PerspectiveCamera(68,innerWidth/innerHeight,.05,600);
camera.position.set(0,2,8);

const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:"high-performance"});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2.5));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.physicallyCorrectLights=true;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.35;
document.body.appendChild(renderer.domElement);

const composer=new THREE.EffectComposer(renderer);
composer.addPass(new THREE.RenderPass(scene,camera));
const bloom=new THREE.UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),1.15,.65,.18);
composer.addPass(bloom);

function proceduralTexture(size=2048){
 const c=document.createElement("canvas");c.width=c.height=size;const x=c.getContext("2d");
 x.fillStyle="#111827";x.fillRect(0,0,size,size);
 for(let i=0;i<280000;i++){
   const px=Math.random()*size,py=Math.random()*size,v=(Math.random()*50)|0;
   x.fillStyle=`rgb(${15+v},${20+v},${28+v})`;
   x.fillRect(px,py,Math.random()*2+1,Math.random()*2+1);
 }
 for(let i=0;i<7000;i++){
   x.strokeStyle="rgba(120,140,160,.10)";
   x.beginPath();
   x.moveTo(Math.random()*size,Math.random()*size);
   x.lineTo(Math.random()*size,Math.random()*size);
   x.stroke();
 }
 const t=new THREE.CanvasTexture(c);
 t.wrapS=t.wrapT=THREE.RepeatWrapping;
 t.anisotropy=renderer.capabilities.getMaxAnisotropy();
 return t;
}

const groundTex=proceduralTexture();
groundTex.repeat.set(18,18);

const floor=new THREE.Mesh(
 new THREE.PlaneGeometry(260,260,160,160),
 new THREE.MeshStandardMaterial({map:groundTex,roughness:.72,metalness:.42})
);
floor.rotation.x=-Math.PI/2;
floor.receiveShadow=true;
scene.add(floor);

scene.add(new THREE.HemisphereLight(0x4d7cff,0x05070c,1.7));

const moon=new THREE.DirectionalLight(0xb9d5ff,4.5);
moon.position.set(30,55,25);
moon.castShadow=true;
moon.shadow.mapSize.set(4096,4096);
moon.shadow.camera.left=-70;
moon.shadow.camera.right=70;
moon.shadow.camera.top=70;
moon.shadow.camera.bottom=-70;
scene.add(moon);

const rim=new THREE.PointLight(0x00d9ff,18,55);
rim.position.set(-18,9,-10);
scene.add(rim);

const warm=new THREE.PointLight(0xff6a00,13,45);
warm.position.set(18,7,8);
scene.add(warm);

const metal=new THREE.MeshPhysicalMaterial({
 color:0x17202f,metalness:.95,roughness:.22,
 clearcoat:.5,clearcoatRoughness:.16
});
const dark=new THREE.MeshPhysicalMaterial({
 color:0x070b12,metalness:.88,roughness:.32
});
const plate=new THREE.MeshStandardMaterial({
 color:0x526274,metalness:.9,roughness:.24
});
const joint=new THREE.MeshStandardMaterial({
 color:0x101827,metalness:.95,roughness:.18
});
const glow=new THREE.MeshStandardMaterial({
 color:0x00eaff,emissive:0x00d9ff,
 emissiveIntensity:8,metalness:.5
});
const eye=new THREE.MeshStandardMaterial({
 color:0xff183e,emissive:0xff0022,
 emissiveIntensity:12
});

function mesh(g,m,p=[0,0,0],rot=[0,0,0],shadow=true){
 const o=new THREE.Mesh(g,m);
 o.position.set(...p);
 o.rotation.set(...rot);
 o.castShadow=o.receiveShadow=shadow;
 return o;
}

for(let i=0;i<32;i++){
 const a=Math.random()*Math.PI*2;
 const r=25+Math.random()*65;
 const h=4+Math.random()*20;
 const b=mesh(
   new THREE.BoxGeometry(3+Math.random()*5,h,3+Math.random()*5),
   new THREE.MeshStandardMaterial({
     color:0x111827,metalness:.8,roughness:.4
   }),
   [Math.cos(a)*r,h/2,Math.sin(a)*r]
 );
 scene.add(b);
}

function createUltraBot(pos){
 const bot=new THREE.Group();
 bot.userData={hp:300,phase:Math.random()*6.28,dead:false};

 bot.add(mesh(new THREE.BoxGeometry(.95,.45,.55),plate,[0,1.05,0]));

 const torso=mesh(
   new THREE.BoxGeometry(1.25,1.25,.72),
   dark,[0,1.75,0]
 );
 bot.add(torso);

 const chest=mesh(
   new THREE.BoxGeometry(1.05,.72,.14),
   metal,[0,1.95,-.43]
 );
 bot.add(chest);

 for(let x of [-.38,0,.38]){
   bot.add(mesh(
     new THREE.BoxGeometry(.22,.65,.08),
     plate,[x,1.95,-.52],[0,0,x*.15]
   ));
 }

 const core=mesh(
   new THREE.SphereGeometry(.20,24,16),
   glow,[0,1.78,-.52]
 );
 bot.add(core);

 const ring=mesh(
   new THREE.TorusGeometry(.28,.035,10,28),
   plate,[0,1.78,-.55]
 );
 bot.add(ring);

 bot.add(mesh(
   new THREE.CylinderGeometry(.16,.18,.32,16),
   joint,[0,2.48,0]
 ));

 const head=mesh(
   new THREE.BoxGeometry(.72,.48,.62),
   metal,[0,2.78,0]
 );
 bot.add(head);

 bot.add(mesh(
   new THREE.BoxGeometry(.60,.13,.08),
   eye,[0,2.78,-.34]
 ));

 for(let x of [-.22,.22]){
   bot.add(mesh(
     new THREE.CylinderGeometry(.045,.045,.15,12),
     glow,[x,3.05,-.05],[Math.PI/2,0,0]
   ));
 }

 [-1,1].forEach(side=>{
   const x=side*.82;

   bot.add(mesh(
     new THREE.SphereGeometry(.28,18,14),
     plate,[x,2.18,0]
   ));

   bot.add(mesh(
     new THREE.CylinderGeometry(.17,.20,.72,16),
     metal,[x,1.72,0],[0,0,side*.13]
   ));

   bot.add(mesh(
     new THREE.CylinderGeometry(.11,.11,.48,12),
     joint,[x+side*.10,1.28,0],[0,0,side*.10]
   ));

   bot.add(mesh(
     new THREE.BoxGeometry(.32,.58,.38),
     plate,[x,1.05,0]
   ));

   bot.add(mesh(
     new THREE.SphereGeometry(.18,14,12),
     dark,[x,.68,-.02]
   ));
 });

 [-1,1].forEach(side=>{
   const x=side*.36;

   bot.add(mesh(
     new THREE.SphereGeometry(.18,14,12),
     joint,[x,.82,0]
   ));

   bot.add(mesh(
     new THREE.BoxGeometry(.34,.72,.42),
     metal,[x,.42,0]
   ));

   bot.add(mesh(
     new THREE.SphereGeometry(.19,14,12),
     joint,[x,.02,0]
   ));

   bot.add(mesh(
     new THREE.BoxGeometry(.28,.62,.36),
     plate,[x,-.34,.02]
   ));

   bot.add(mesh(
     new THREE.BoxGeometry(.48,.20,.82),
     dark,[x,-.72,-.14]
   ));

   bot.add(mesh(
     new THREE.CylinderGeometry(.045,.045,.72,10),
     joint,[x+side*.20,.30,-.23],[.2,0,0]
   ));
 });

 for(let x of [-.35,.35]){
   bot.add(mesh(
     new THREE.CylinderGeometry(.10,.14,.58,14),
     joint,[x,2.0,.48],[Math.PI/2,0,0]
   ));

   const e=mesh(
     new THREE.SphereGeometry(.10,14,10),
     glow,[x,2.0,.78]
   );
   bot.add(e);
 }

 bot.position.copy(pos);
 scene.add(bot);
 return bot;
}

function createWeapon(){
 const g=new THREE.Group();

 g.add(mesh(new THREE.BoxGeometry(.20,.20,.85),dark,[0,0,0]));
 g.add(mesh(new THREE.BoxGeometry(.24,.13,.60),metal,[0,.02,-.58]));
 g.add(mesh(
   new THREE.CylinderGeometry(.055,.07,.95,18),
   joint,[0,.02,-1.18],[Math.PI/2,0,0]
 ));
 g.add(mesh(
   new THREE.BoxGeometry(.13,.32,.22),
   metal,[0,-.22,-.10],[0,0,.18]
 ));
 g.add(mesh(
   new THREE.BoxGeometry(.16,.08,.34),
   glow,[0,.13,-.20]
 ));
 g.add(mesh(
   new THREE.CylinderGeometry(.11,.11,.32,18),
   dark,[0,.18,-.45],[Math.PI/2,0,0]
 ));

 return g;
}

const weapon=createWeapon();
weapon.position.set(.48,-.38,-.85);
weapon.rotation.set(-.06,-.12,0);
camera.add(weapon);
scene.add(camera);

let bots=[];

const spawn=[
 [-18,0,-18],
 [18,0,-18],
 [-18,0,18],
 [18,0,18],
 [-28,0,0],
 [28,0,0]
];

for(let i=0;i<6;i++){
 bots.push(createUltraBot(new THREE.Vector3(...spawn[i])));
}

let yaw=0;
let pitch=0;
let drag=false;
let prev={x:0,y:0};
let aim=false;
let shootReady=true;
let hp=100;
let score=0;
let gameOver=false;

const keys={};

addEventListener("keydown",e=>keys[e.code]=true);
addEventListener("keyup",e=>keys[e.code]=false);

addEventListener("mousedown",e=>{
 if(e.button===0){
   drag=true;
   prev={x:e.clientX,y:e.clientY};
   shoot();
 }

 if(e.button===2){
   aim=true;
   camera.fov=38;
   camera.updateProjectionMatrix();
   weapon.position.set(.05,-.28,-.65);
 }
});

addEventListener("mouseup",e=>{
 if(e.button===0) drag=false;

 if(e.button===2){
   aim=false;
   camera.fov=68;
   camera.updateProjectionMatrix();
   weapon.position.set(.48,-.38,-.85);
 }
});

addEventListener("mousemove",e=>{
 if(!drag) return;

 const dx=e.clientX-prev.x;
 const dy=e.clientY-prev.y;

 prev={x:e.clientX,y:e.clientY};

 yaw-=dx*.0025;
 pitch=Math.max(
   -1.45,
   Math.min(1.45,pitch-dy*.0025)
 );

 camera.rotation.set(pitch,yaw,0,"YXZ");
});

addEventListener("contextmenu",e=>e.preventDefault());

const ray=new THREE.Raycaster();

function muzzleFlash(){
 const l=new THREE.PointLight(0x8fffe8,20,8);
 l.position.set(.45,-.1,-1.8);
 weapon.add(l);

 setTimeout(()=>weapon.remove(l),45);
}

function shoot(){
 if(gameOver||!shootReady) return;

 shootReady=false;
 muzzleFlash();

 weapon.position.z+=.12;
 weapon.rotation.x-=.08;

 setTimeout(()=>{
   weapon.position.z=aim?-.65:-.85;
   weapon.rotation.x=-.06;
   shootReady=true;
 },90);

 ray.setFromCamera(new THREE.Vector2(),camera);

 const targets=[];

 bots.forEach(b=>{
   b.traverse(x=>{
     if(x.isMesh) targets.push(x);
   });
 });

 const hits=ray.intersectObjects(targets,false);

 if(hits.length){
   let o=hits[0].object;

   while(o && !bots.includes(o)){
     o=o.parent;
   }

   if(o){
     o.userData.hp-=100;

     document.getElementById("flash").textContent="HIT";
     document.getElementById("flash").style.opacity=1;

     setTimeout(()=>{
       document.getElementById("flash").style.opacity=0;
     },80);

     if(o.userData.hp<=0){
       scene.remove(o);

       bots=bots.filter(b=>b!==o);

       score++;
       document.getElementById("score").textContent=score;

       setTimeout(()=>{
         bots.push(
           createUltraBot(
             new THREE.Vector3(
               ...spawn[(Math.random()*spawn.length)|0]
             )
           )
         );
       },700);
     }
   }
 }
}

const clock=new THREE.Clock();

function animate(){
 requestAnimationFrame(animate);

 const dt=Math.min(clock.getDelta(),.05);
 const t=performance.now()*.001;

 if(!gameOver){

   const f=new THREE.Vector3(0,0,-1)
     .applyQuaternion(camera.quaternion);

   f.y=0;
   f.normalize();

   const r=new THREE.Vector3(1,0,0)
     .applyQuaternion(camera.quaternion);

   r.y=0;
   r.normalize();

   const mv=new THREE.Vector3();

   if(keys.KeyW) mv.add(f);
   if(keys.KeyS) mv.sub(f);
   if(keys.KeyD) mv.add(r);
   if(keys.KeyA) mv.sub(r);

   if(mv.lengthSq()){
     camera.position.add(
       mv.normalize().multiplyScalar(
         (keys.ShiftLeft?.18:.095)*dt*60
       )
     );
   }

   if(keys.Space && camera.position.y<2.03){
     camera.position.y+=.12;
   }

   camera.position.y+=(2-camera.position.y)*.12;

   bots.forEach(b=>{
     const d=new THREE.Vector3()
       .subVectors(camera.position,b.position);

     d.y=0;

     const dist=d.length();
     d.normalize();

     if(dist>2.1){
       b.position.addScaledVector(d,dt*1.7);
     }else{
       hp-=dt*9;

       document.getElementById("damage").style.opacity=
         Math.min(.75,(100-hp)/120);

       document.getElementById("hp").style.width=
         Math.max(0,hp)+"%";

       if(hp<=0){
         gameOver=true;
         document.getElementById("over").style.display="grid";
       }
     }

     b.lookAt(
       camera.position.x,
       b.position.y,
       camera.position.z
     );

     b.position.y=Math.sin(
       t*3+b.userData.phase
     )*.025;

     b.rotation.z=Math.sin(
       t*4+b.userData.phase
     )*.018;
   });

   weapon.rotation.y=Math.sin(t*1.7)*.018;
 }

 composer.render();
}

animate();

addEventListener("resize",()=>{
 camera.aspect=innerWidth/innerHeight;
 camera.updateProjectionMatrix();

 renderer.setSize(innerWidth,innerHeight);
 composer.setSize(innerWidth,innerHeight);
});
</script>
</body>
</html>
"""

components.html(game_html, height=800, scrolling=False)
