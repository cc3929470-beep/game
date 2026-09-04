import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SNIPER: NEXT-GEN WARZONE", layout="wide")
st.title("🔥 OVERPOWERED ULTRA GRAPHICS WARZONE")
st.caption("🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | Shift = 달리기 | Space = 점프 | [1, 2, 3] = 총기 변경 | 마우스 드래그 = 시선 전환 | 좌클릭 = 사격 | 우클릭 = ADS 조준")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Segoe UI', sans-serif; user-select: none; }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 6px; height: 6px;
            transform: translate(-50%, -50%); pointer-events: none; z-index: 10;
            background: #00f5a0; border-radius: 50%; box-shadow: 0 0 15px #00f5a0, 0 0 25px #00f5a0;
        }
        #scope-overlay {
            position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none; z-index: 9; display: none;
            background: radial-gradient(circle, transparent 20%, rgba(0,0,0,0.98) 45%, black 100%);
        }
        #scope-overlay::before, #scope-overlay::after {
            content: ''; position: absolute; background: rgba(0, 245, 160, 0.9);
            box-shadow: 0 0 8px #00f5a0;
        }
        #scope-overlay::before { top: 50%; left: 0; width: 100%; height: 1px; }
        #scope-overlay::after { top: 0; left: 50%; width: 1px; height: 100%; }
        #hud {
            position: absolute; top: 20px; left: 20px; color: #f8fafc; font-size: 18px;
            font-weight: 800; z-index: 10; letter-spacing: 2px;
            background: rgba(15, 23, 42, 0.85); padding: 12px 22px; border-left: 5px solid #ff4655;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8); backdrop-filter: blur(12px);
        }
        #gun-hud {
            position: absolute; bottom: 30px; right: 30px; color: #00f5a0; font-size: 20px;
            font-weight: 900; z-index: 10; background: rgba(15, 23, 42, 0.85);
            padding: 12px 24px; border-radius: 6px; border: 1px solid #00f5a0;
            box-shadow: 0 0 20px rgba(0,245,160,0.4); backdrop-filter: blur(12px);
        }
        #hp-bar {
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            width: 360px; height: 16px; background: rgba(15, 23, 42, 0.85); z-index: 10;
            border: 2px solid #ff4655; border-radius: 4px; box-shadow: 0 0 25px rgba(255, 70, 85, 0.6);
        }
        #hp-fill {
            width: 100%; height: 100%; background: linear-gradient(90deg, #00f5a0, #00d2ff);
            transition: width 0.1s;
        }
        #game-over {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: #ff4655; font-size: 42px; font-weight: 900; text-align: center; display: none; z-index: 20;
            text-shadow: 0 0 35px rgba(255, 70, 85, 0.9); background: rgba(15, 23, 42, 0.95); padding: 40px 60px; border-radius: 8px;
            border: 1px solid #ff4655;
        }
        #hit-feedback {
            position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
            color: #ffcc00; font-size: 30px; font-weight: 900; pointer-events: none; z-index: 11;
            opacity: 0; transition: opacity 0.2s; text-shadow: 0 0 15px rgba(0,0,0,0.9);
        }
    </style>
</head>
<body>
    <div id="crosshair"></div>
    <div id="scope-overlay"></div>
    <div id="hud">ELIMINATIONS: <span id="score" style="color:#ff4655;">0</span></div>
    <div id="gun-hud">WEAPON: <span id="gun-name">M4A1 TACTICAL</span></div>
    <div id="hp-bar"><div id="hp-fill"></div></div>
    <div id="hit-feedback"></div>
    <div id="game-over">SYSTEM OVERLOAD<br><span style="font-size:18px; color:#fff;">클릭하여 리부트</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
        window.focus();
        document.addEventListener('contextmenu', event => event.preventDefault());

        // 텍스처 및 절차적 Normal Map/Metalness 연산기
        function generateHighResTexture(type) {
            let canvas = document.createElement('canvas');
            canvas.width = 1024; canvas.height = 1024;
            let ctx = canvas.getContext('2d');

            if (type === 'metal_armor') {
                ctx.fillStyle = '#1e293b'; ctx.fillRect(0, 0, 1024, 1024);
                ctx.strokeStyle = '#334155'; ctx.lineWidth = 4;
                for(let i=0; i<1024; i+=128) {
                    ctx.strokeRect(i, 0, 128, 1024);
                    ctx.strokeRect(0, i, 1024, 128);
                }
                for (let i = 0; i < 80000; i++) {
                    let x = Math.random() * 1024, y = Math.random() * 1024;
                    let v = Math.random() * 80;
                    ctx.fillStyle = `rgba(${v},${v+10},${v+20},0.2)`;
                    ctx.fillRect(x, y, 2, 2);
                }
            } else if (type === 'asphalt_ultra') {
                ctx.fillStyle = '#0f172a'; ctx.fillRect(0, 0, 1024, 1024);
                for (let i = 0; i < 120000; i++) {
                    let x = Math.random() * 1024, y = Math.random() * 1024;
                    let c = Math.floor(Math.random() * 90 + 20);
                    ctx.fillStyle = `rgb(${c},${c+5},${c+10})`;
                    ctx.fillRect(x, y, 1, 1);
                }
            }
            let texture = new THREE.CanvasTexture(canvas);
            texture.wrapS = THREE.RepeatWrapping; texture.wrapT = THREE.RepeatWrapping;
            return texture;
        }

        let armorTex = generateHighResTexture('metal_armor'); armorTex.repeat.set(2, 2);
        let asphaltTex = generateHighResTexture('asphalt_ultra'); asphaltTex.repeat.set(12, 12);

        let scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0f172a, 0.018);

        // 안개 및 고해상도 렌더러 설정
        let camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.4;
        document.body.appendChild(renderer.domElement);

        const PLAYER_HEIGHT = 2.0;
        const PLAYER_RADIUS = 0.8;
        camera.position.set(0, PLAYER_HEIGHT, 0);

        let yVelocity = 0, isGrounded = true;
        const JUMP_FORCE = 0.15, GRAVITY = 0.009;

        let pitch = 0, yaw = 0, isMouseDown = false;
        let prevMousePos = { x: 0, y: 0 };

        document.addEventListener('mousedown', (e) => {
            if (e.button === 0 || e.button === 2) {
                isMouseDown = true; prevMousePos = { x: e.clientX, y: e.clientY };
            }
        });
        document.addEventListener('mouseup', () => { isMouseDown = false; });
        document.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;
            let deltaX = e.clientX - prevMousePos.x, deltaY = e.clientY - prevMousePos.y;
            prevMousePos = { x: e.clientX, y: e.clientY };

            let sensitivity = 0.0028;
            yaw -= deltaX * sensitivity; pitch -= deltaY * sensitivity;
            let maxPitch = Math.PI / 2 - 0.01;
            pitch = Math.max(-maxPitch, Math.min(maxPitch, pitch));

            camera.quaternion.setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ'));
        });

        // 조명 시스템 (고해상도 실시간 그림자)
        scene.add(new THREE.AmbientLight(0x334155, 0.8));
        let mainLight = new THREE.DirectionalLight(0xffa500, 2.5);
        mainLight.position.set(50, 80, 30);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 4096; mainLight.shadow.mapSize.height = 4096;
        mainLight.shadow.camera.near = 0.5; mainLight.shadow.camera.far = 250;
        let d = 50;
        mainLight.shadow.camera.left = -d; mainLight.shadow.camera.right = d;
        mainLight.shadow.camera.top = d; mainLight.shadow.camera.bottom = -d;
        scene.add(mainLight);

        // 재질 정의
        let gunBodyMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.3, metalness: 0.85 });
        let gunSteelMat = new THREE.MeshStandardMaterial({ color: 0x374151, roughness: 0.2, metalness: 0.95 });
        let brassMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.2, metalness: 0.9 });
        let mechDarkMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4, metalness: 0.8, map: armorTex });
        let mechPlateMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.2, metalness: 0.9 });
        let redEyeMat = new THREE.MeshStandardMaterial({ color: 0xff0033, emissive: 0xff0033, emissiveIntensity: 6.0 });
        let glassLantern = new THREE.MeshStandardMaterial({ color: 0xffaa00, roughness: 0.1, metalness: 0.9, transparent: true, opacity: 0.7 });
        let lanternGlow = new THREE.MeshStandardMaterial({ color: 0xffaa00, emissive: 0xff8800, emissiveIntensity: 8.0 });

        let floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), new THREE.MeshStandardMaterial({ map: asphaltTex, roughness: 0.85, metalness: 0.2 }));
        floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
        scene.add(floor);

        let colliders = [];
        function addBoxCollider(x, z, w, d) {
            colliders.push({ minX: x - w/2 - PLAYER_RADIUS, maxX: x + w/2 + PLAYER_RADIUS, minZ: z - d/2 - PLAYER_RADIUS, maxZ: z + d/2 + PLAYER_RADIUS });
        }

        // 가로등 (랜턴 모듈 - 끼임 완전 제거)
        function createLanternPost(x, z) {
            let group = new THREE.Group();
            let pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 5.0, 12), gunSteelMat);
            pole.position.set(x, 2.5, z); pole.castShadow = true;
            group.add(pole);

            let cap = new THREE.Mesh(new THREE.ConeGeometry(0.5, 0.35, 6), gunBodyMat);
            cap.position.set(x, 5.2, z);
            group.add(cap);

            let bulb = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 12), lanternGlow);
            bulb.position.set(x, 4.8, z);
            group.add(bulb);

            let light = new THREE.PointLight(0xff9900, 3.5, 18);
            light.position.set(x, 4.8, z); light.castShadow = true;
            group.add(light);

            scene.add(group);
            addBoxCollider(x, z, 0.2, 0.2);
        }

        // 배치
        for(let x = -30; x <= 30; x += 20) {
            for(let z = -30; z <= 30; z += 20) {
                if(x !== 0 || z !== 0) createLanternPost(x, z);
            }
        }

        // [진짜 로봇 (Mecha Bot) 메쉬 연산 구조]
        function createRealisticBot(spawnPos) {
            let bot = new THREE.Group();
            bot.userData = { hp: 150 };

            // 1. 머리 및 광학 카메라 센서
            let headGroup = new THREE.Group();
            let mainHead = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.35, 0.45), mechPlateMat);
            let sensorEye = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.3, 16), redEyeMat);
            sensorEye.rotateZ(Math.PI / 2); sensorEye.position.set(0, 0.02, -0.23);
            let neckPiston = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.4, 12), gunSteelMat);
            neckPiston.position.set(0, -0.25, 0); // 몸통과 깊게 겹침

            headGroup.add(mainHead, sensorEye, neckPiston);
            headGroup.position.y = 2.1;
            headGroup.userData = { type: 'head' };

            // 2. 흉부 및 반응로 코어
            let bodyGroup = new THREE.Group();
            let chestPlate = new THREE.Mesh(new THREE.BoxGeometry(0.95, 1.1, 0.6), mechDarkMat);
            chestPlate.position.y = 1.35; chestPlate.castShadow = true;

            let reactor = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.1, 16), redEyeMat);
            reactor.rotateX(Math.PI / 2); reactor.position.set(0, 1.45, -0.31);

            let pelvis = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.4, 0.5), mechPlateMat);
            pelvis.position.y = 0.8; // 다리와 일체화

            bodyGroup.add(chestPlate, reactor, pelvis);
            bodyGroup.userData = { type: 'body' };

            // 3. 다리 유압 조인트
            let legGroup = new THREE.Group();
            let thighL = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.12, 1.1, 12), gunSteelMat);
            thighL.position.set(-0.28, 0.45, 0); thighL.castShadow = true;
            let thighR = thighL.clone(); thighR.position.set(0.28, 0.45, 0);

            legGroup.add(thighL, thighR);
            legGroup.userData = { type: 'legs' };

            bot.add(headGroup, bodyGroup, legGroup);
            bot.position.copy(spawnPos);
            scene.add(bot);
            return bot;
        }

        // [진짜 총기 - M4A1 / 조준경 / 탄창 / 노리쇠]
        function createRealGuns() {
            let guns = [];

            // M4A1 SOPMOD
            let m4 = new THREE.Group();
            let receiver = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.18, 0.7), gunBodyMat);
            let barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.2, 16), gunSteelMat);
            barrel.rotateX(Math.PI / 2); barrel.position.set(0, 0.02, -0.8);
            let handguard = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.12, 0.6), gunSteelMat);
            handguard.position.set(0, 0.02, -0.5);
            let mag = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.35, 0.18), brassMat);
            mag.position.set(0, -0.2, -0.1); mag.rotation.x = 0.2;
            let scope = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.5, 16), gunBodyMat);
            scope.rotateX(Math.PI / 2); scope.position.set(0, 0.14, -0.1);

            m4.add(receiver, barrel, handguard, mag, scope);

            guns.push(m4);
            return guns;
        }

        let gunList = createRealGuns();
        let gunContainer = new THREE.Group();
        gunList.forEach(g => gunContainer.add(g));

        const NORMAL_GUN_POS = new THREE.Vector3(0.32, -0.25, -0.5);
        const AIM_GUN_POS = new THREE.Vector3(0, -0.17, -0.3);
        gunContainer.position.copy(NORMAL_GUN_POS);
        camera.add(gunContainer);
        scene.add(camera);

        let hp = 100, score = 0, isGameOver = false;
        let keys = { KeyW: false, KeyS: false, KeyA: false, KeyD: false, ShiftLeft: false, Space: false };
        let bots = [], sparks = [], shellCasings = [];
        let isAiming = false, canShoot = true;

        let spawnPoints = [new THREE.Vector3(-15, 0, -15), new THREE.Vector3(15, 0, -15), new THREE.Vector3(-15, 0, 15), new THREE.Vector3(15, 0, 15)];
        for (let i = 0; i < 4; i++) bots.push(createRealisticBot(spawnPoints[i]));

        document.addEventListener('keydown', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = true; });
        document.addEventListener('keyup', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = false; });

        function createEjectedShell() {
            let shell = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.08, 8), brassMat);
            let worldPos = new THREE.Vector3();
            gunContainer.getWorldPosition(worldPos);
            shell.position.copy(worldPos);
            shell.velocity = new THREE.Vector3(0.08 + Math.random()*0.04, 0.08 + Math.random()*0.04, (Math.random()-0.5)*0.04);
            scene.add(shell);
            shellCasings.push({ mesh: shell, life: 1.0 });
        }

        let raycaster = new THREE.Raycaster();

        document.addEventListener('mousedown', (e) => {
            if (e.button === 2) {
                isAiming = true; camera.fov = 22; camera.updateProjectionMatrix();
                gunContainer.position.copy(AIM_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'block';
                document.getElementById('crosshair').style.display = 'none';
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 2) {
                isAiming = false; camera.fov = 65; camera.updateProjectionMatrix();
                gunContainer.position.copy(NORMAL_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'none';
                document.getElementById('crosshair').style.display = 'block';
            }
        });

        document.addEventListener('click', (e) => {
            if (e.button !== 0 || isGameOver || !canShoot) return;
            canShoot = false;

            createEjectedShell();
            gunContainer.position.z += 0.18; // 반동
            setTimeout(() => {
                gunContainer.position.copy(isAiming ? AIM_GUN_POS : NORMAL_GUN_POS);
                canShoot = true;
            }, 120);

            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let meshes = [];
            bots.forEach(b => b.traverse(c => { if (c.isMesh) meshes.push(c); }));

            let hits = raycaster.intersectObjects(meshes);
            if (hits.length > 0) {
                let hitBot = hits[0].object;
                while (hitBot && !bots.includes(hitBot)) hitBot = hitBot.parent;

                if (hitBot) {
                    hitBot.userData.hp -= 50;
                    if (hitBot.userData.hp <= 0) {
                        scene.remove(hitBot);
                        bots = bots.filter(b => b !== hitBot);
                        score++;
                        document.getElementById('score').innerText = score;
                        setTimeout(() => bots.push(createRealisticBot(spawnPoints[Math.floor(Math.random()*4)])), 1000);
                    }
                }
            }
        });

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver) return;

            // 탄피 연산
            shellCasings.forEach((s, idx) => {
                s.mesh.position.add(s.velocity);
                s.life -= 0.03;
                if (s.life <= 0) { scene.remove(s.mesh); shellCasings.splice(idx, 1); }
            });

            // 플레이어 이동
            let forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion); forward.y = 0; forward.normalize();
            let right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion); right.y = 0; right.normalize();

            let move = new THREE.Vector3();
            if (keys.KeyW) move.add(forward); if (keys.KeyS) move.sub(forward);
            if (keys.KeyD) move.add(right); if (keys.KeyA) move.sub(right);

            if (move.lengthSq() > 0) {
                let speed = keys.ShiftLeft ? 0.14 : 0.09;
                camera.position.add(move.normalize().multiplyScalar(speed));
            }

            // 봇 추적 AI 및 공격
            bots.forEach(bot => {
                let dir = new THREE.Vector3().subVectors(camera.position, bot.position); dir.y = 0;
                let dist = dir.length(); dir.normalize();

                if (dist > 1.8) {
                    bot.position.add(dir.multiplyScalar(0.045));
                } else {
                    hp -= 0.3;
                    document.getElementById('hp-fill').style.width = Math.max(0, hp) + '%';
                    if (hp <= 0) {
                        isGameOver = true;
                        document.getElementById('game-over').style.display = 'block';
                    }
                }
                bot.lookAt(camera.position.x, 0, camera.position.z);
            });

            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=720)
