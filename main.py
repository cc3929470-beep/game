import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SNIPER", layout="wide")
st.title("🎯 SNIPER: HIGH DETAIL")
st.caption("🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | 마우스 드래그 = 시선 전환 (전방위 Y축 포함) | 좌클릭 = 사격 | 우클릭 = 스나이퍼 조준(ADS)")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #050811; font-family: 'Segoe UI', sans-serif; user-select: none; }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 6px; height: 6px;
            transform: translate(-50%, -50%); pointer-events: none; z-index: 10;
            background: #00f5a0; border-radius: 50%; box-shadow: 0 0 10px #00f5a0;
        }
        #scope-overlay {
            position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none; z-index: 9; display: none;
            background: radial-gradient(circle, transparent 28%, rgba(0,0,0,0.92) 55%, black 100%);
        }
        #scope-overlay::before, #scope-overlay::after {
            content: ''; position: absolute; background: rgba(0, 245, 160, 0.7);
        }
        #scope-overlay::before { top: 50%; left: 0; width: 100%; height: 1px; }
        #scope-overlay::after { top: 0; left: 50%; width: 1px; height: 100%; }
        #hud {
            position: absolute; top: 20px; left: 20px; color: #f8fafc; font-size: 20px;
            font-weight: 800; z-index: 10; letter-spacing: 2px;
            background: rgba(15, 23, 42, 0.85); padding: 12px 22px; border-left: 5px solid #ff4655;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5); backdrop-filter: blur(4px);
        }
        #hp-bar {
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            width: 340px; height: 14px; background: rgba(15, 23, 42, 0.8); z-index: 10;
            border: 2px solid #ff4655; border-radius: 4px; box-shadow: 0 0 15px rgba(255, 70, 85, 0.4);
        }
        #hp-fill {
            width: 100%; height: 100%; background: linear-gradient(90deg, #00f5a0, #00d2ff);
            transition: width 0.1s;
        }
        #game-over {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: #ff4655; font-size: 42px; font-weight: 900; text-align: center; display: none; z-index: 20;
            text-shadow: 0 0 25px rgba(255, 70, 85, 0.9); background: rgba(15, 23, 42, 0.9); padding: 40px; border-radius: 8px;
        }
        #hit-feedback {
            position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);
            color: #ffcc00; font-size: 28px; font-weight: 900; pointer-events: none; z-index: 11;
            opacity: 0; transition: opacity 0.2s; text-shadow: 0 0 10px rgba(0,0,0,0.8);
        }
    </style>
</head>
<body>
    <div id="crosshair"></div>
    <div id="scope-overlay"></div>
    <div id="hud">ELIMINATIONS: <span id="score" style="color:#ff4655;">0</span></div>
    <div id="hp-bar"><div id="hp-fill"></div></div>
    <div id="hit-feedback"></div>
    <div id="game-over">MISSION FAILED<br><span style="font-size:18px; color:#fff;">클릭하여 다시 시작</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        window.focus();
        document.addEventListener('contextmenu', event => event.preventDefault());

        let scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a0f1d, 0.015);
        
        // 하늘 및 분위기
        let vertexShader = `
            varying vec3 vWorldPosition;
            void main() {
                vec4 worldPosition = modelMatrix * vec4(position, 1.0);
                vWorldPosition = worldPosition.xyz;
                gl_Position = projectionMatrix * viewMatrix * worldPosition;
            }
        `;
        let fragmentShader = `
            uniform vec3 topColor;
            uniform vec3 bottomColor;
            uniform float offset;
            uniform float exponent;
            varying vec3 vWorldPosition;
            void main() {
                float h = normalize(vWorldPosition + offset).y;
                gl_FragColor = vec4(mix(bottomColor, topColor, max(pow(max(h, 0.0), exponent), 0.0)), 1.0);
            }
        `;
        let uniforms = {
            topColor: { value: new THREE.Color(0x0d1527) },
            bottomColor: { value: new THREE.Color(0x1a2638) },
            offset: { value: 100 },
            exponent: { value: 0.8 }
        };
        let skyGeo = new THREE.SphereGeometry(400, 32, 15);
        let skyMat = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms, side: THREE.BackSide });
        let sky = new THREE.Mesh(skyGeo, skyMat);
        scene.add(sky);

        let camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.body.appendChild(renderer.domElement);

        let controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.enableZoom = false;
        // 마우스 Y축 제한 해제 (하늘부터 바로 밑 바닥까지 회전 가능)
        controls.minPolarAngle = 0.01;
        controls.maxPolarAngle = Math.PI - 0.01;

        const PLAYER_HEIGHT = 2.0;
        camera.position.set(0, PLAYER_HEIGHT, 0);
        controls.target.set(0, PLAYER_HEIGHT, -1);

        // 조명
        scene.add(new THREE.AmbientLight(0xffffff, 0.4));
        let sun = new THREE.DirectionalLight(0xe2e8f0, 1.5);
        sun.position.set(50, 70, 30);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 150;
        let d = 50;
        sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
        sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
        scene.add(sun);

        // 지형/건축물
        let wallMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7, metalness: 0.2 });
        let roadMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.9 });
        let grassMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9 });

        let floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), grassMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        let mainRoad = new THREE.Mesh(new THREE.PlaneGeometry(20, 100), roadMat);
        mainRoad.rotation.x = -Math.PI / 2;
        mainRoad.position.y = 0.01;
        mainRoad.receiveShadow = true;
        scene.add(mainRoad);

        // --- 디테일 총기 제작 함수 ---
        function createDetailedSniper() {
            let gun = new THREE.Group();

            let metalDark = new THREE.MeshStandardMaterial({ color: 0x111625, roughness: 0.35, metalness: 0.85 });
            let metalSteel = new THREE.MeshStandardMaterial({ color: 0x2e384d, roughness: 0.25, metalness: 0.95 });
            let polymer = new THREE.MeshStandardMaterial({ color: 0x1e2638, roughness: 0.6, metalness: 0.1 });
            let goldAccent = new THREE.MeshStandardMaterial({ color: 0xc59b27, roughness: 0.3, metalness: 0.9 });
            let lensGlass = new THREE.MeshStandardMaterial({ color: 0x00f5a0, emissive: 0x00a86b, emissiveIntensity: 0.6, roughness: 0.1, metalness: 0.9 });

            // 총열 (Barrel)
            let mainBarrel = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.032, 2.2, 24), metalSteel);
            mainBarrel.rotateX(Math.PI / 2);
            mainBarrel.position.set(0, 0, -1.1);

            // 포구 제동기 (Muzzle Brake)
            let muzzleBrake = new THREE.Group();
            let mbBody = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.35, 16), metalDark);
            mbBody.rotateX(Math.PI / 2);
            let mbHole1 = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.02, 0.1), metalSteel);
            mbHole1.position.set(0, 0, 0);
            muzzleBrake.add(mbBody, mbHole1);
            muzzleBrake.position.set(0, 0, -2.35);

            // 총열 덮개 (Handguard / Rail)
            let handguard = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.14, 1.2), polymer);
            handguard.position.set(0, -0.01, -0.8);

            // 2각대 (Bipod)
            let bipodMount = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.06, 0.15), metalSteel);
            bipodMount.position.set(0, -0.09, -1.3);
            let legL = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.5), metalDark);
            legL.position.set(-0.08, -0.28, -1.3); legL.rotation.z = 0.25;
            let legR = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.5), metalDark);
            legR.position.set(0.08, -0.28, -1.3); legR.rotation.z = -0.25;
            gun.add(bipodMount, legL, legR);

            // 리시버 / 몸통 (Receiver)
            let receiver = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.2, 0.8), metalDark);
            receiver.position.set(0, -0.01, -0.1);

            // 장전 손잡이 (Bolt Handle)
            let boltHandle = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.15), goldAccent);
            boltHandle.rotation.z = Math.PI / 2;
            boltHandle.position.set(0.1, 0.02, -0.15);
            let boltKnob = new THREE.Mesh(new THREE.SphereGeometry(0.025, 12, 12), goldAccent);
            boltKnob.position.set(0.17, 0.02, -0.15);
            gun.add(boltHandle, boltKnob);

            // 스코프 (Scope & Mount)
            let scopeMount = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.4), metalSteel);
            scopeMount.position.set(0, 0.12, -0.2);

            let scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.8, 24), metalDark);
            scopeBody.rotateX(Math.PI / 2);
            scopeBody.position.set(0, 0.19, -0.2);

            let scopeFrontBell = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.065, 0.2, 24), metalDark);
            scopeFrontBell.rotateX(Math.PI / 2);
            scopeFrontBell.position.set(0, 0.19, -0.65);

            let scopeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.01, 24), lensGlass);
            scopeLens.rotateX(Math.PI / 2);
            scopeLens.position.set(0, 0.19, -0.74);

            let scopeDial = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.04, 12), goldAccent);
            scopeDial.position.set(0, 0.26, -0.2);

            gun.add(scopeMount, scopeBody, scopeFrontBell, scopeLens, scopeDial);

            // 탄창 (Magazine)
            let mag = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.38, 0.28), polymer);
            mag.position.set(0, -0.24, -0.25);
            mag.rotation.x = -0.15;

            // 권총 손잡이 (Grip)
            let grip = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.3, 0.14), polymer);
            grip.position.set(0, -0.2, 0.1);
            grip.rotation.x = -0.4;

            // 개머리판 (Stock)
            let stock = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.18, 0.65), polymer);
            stock.position.set(0, -0.01, 0.48);

            let cheekRest = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.06, 0.3), metalSteel);
            cheekRest.position.set(0, 0.09, 0.45);

            gun.add(mainBarrel, muzzleBrake, handguard, receiver, mag, grip, stock, cheekRest);

            // 총구 화염 (Muzzle Flash)
            let flashMat = new THREE.MeshBasicMaterial({ color: 0xffcc44, transparent: true, opacity: 0 });
            let muzzleFlash = new THREE.Mesh(new THREE.OctahedronGeometry(0.3), flashMat);
            muzzleFlash.position.set(0, 0, -2.6);
            gun.add(muzzleFlash);

            return { gunGroup: gun, flashMat: flashMat };
        }

        let gunData = createDetailedSniper();
        let gun = gunData.gunGroup;
        let flashMat = gunData.flashMat;

        const NORMAL_GUN_POS = new THREE.Vector3(0.35, -0.28, -0.5);
        const AIM_GUN_POS = new THREE.Vector3(0, -0.19, -0.32);
        gun.position.copy(NORMAL_GUN_POS);

        camera.add(gun);
        scene.add(camera);

        // --- 디테일 전술 로봇(Bot) 제작 함수 ---
        function createDetailedBot() {
            let bot = new THREE.Group();
            bot.userData = { hp: 100 };

            let armorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3, metalness: 0.8 });
            let darkMetal = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5, metalness: 0.9 });
            let redGlow = new THREE.MeshStandardMaterial({ color: 0xff1e43, emissive: 0xff1e43, emissiveIntensity: 2.0 });
            let cyanGlow = new THREE.MeshStandardMaterial({ color: 0x00f5a0, emissive: 0x00f5a0, emissiveIntensity: 1.5 });

            // 1. 머리 (Head & Optics)
            let headGroup = new THREE.Group();
            let headBase = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.32, 0.38), armorMat);
            headBase.castShadow = true;

            let visor = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.1, 0.05), redGlow);
            visor.position.set(0, 0.04, -0.2);

            let subSensor = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.08, 12), cyanGlow);
            subSensor.rotateX(Math.PI / 2);
            subSensor.position.set(-0.1, -0.08, -0.2);

            headGroup.add(headBase, visor, subSensor);
            headGroup.position.y = 2.1;
            headGroup.userData = { type: 'head' };

            // 2. 상체 (Torso & Armor Plates)
            let bodyGroup = new THREE.Group();
            let chestCore = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.85, 0.45), darkMetal);
            chestCore.position.y = 1.35; chestCore.castShadow = true;

            let plateL = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.5, 0.1), armorMat);
            plateL.position.set(-0.2, 1.45, -0.25); plateL.rotation.y = -0.15;
            let plateR = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.5, 0.1), armorMat);
            plateR.position.set(0.2, 1.45, -0.25); plateR.rotation.y = 0.15;

            let reactor = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.1, 16), redGlow);
            reactor.rotateX(Math.PI / 2);
            reactor.position.set(0, 1.4, -0.24);

            let shoulderL = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), armorMat);
            shoulderL.position.set(-0.52, 1.65, 0);
            let shoulderR = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), armorMat);
            shoulderR.position.set(0.52, 1.65, 0);

            bodyGroup.add(chestCore, plateL, plateR, reactor, shoulderL, shoulderR);
            bodyGroup.userData = { type: 'body' };

            // 3. 하체 및 다리 (Legs & Joints)
            let legGroup = new THREE.Group();
            let hip = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.3), darkMetal);
            hip.position.y = 0.85;

            let legL = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.8, 12), armorMat);
            legL.position.set(-0.22, 0.4, 0); legL.castShadow = true;
            let legR = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.8, 12), armorMat);
            legR.position.set(0.22, 0.4, 0); legR.castShadow = true;

            legGroup.add(hip, legL, legR);
            legGroup.userData = { type: 'legs' };

            bot.add(headGroup, bodyGroup, legGroup);

            let angle = Math.random() * Math.PI * 2;
            let dist = 14 + Math.random() * 16;
            bot.position.set(camera.position.x + Math.cos(angle) * dist, 0, camera.position.z + Math.sin(angle) * dist);

            scene.add(bot);
            return bot;
        }

        let hp = 100, score = 0, isGameOver = false;
        let keys = { KeyW: false, KeyS: false, KeyA: false, KeyD: false };
        let bots = [], sparks = [];
        let isAiming = false;

        for (let i = 0; i < 5; i++) bots.push(createDetailedBot());
        setInterval(() => { if (bots.length < 6 && !isGameOver) bots.push(createDetailedBot()); }, 2500);

        document.addEventListener('keydown', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = true; });
        document.addEventListener('keyup', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = false; });

        function createSparks(pos, colorHex) {
            let pGeo = new THREE.BufferGeometry();
            let count = 18;
            let positions = new Float32Array(count * 3);
            let velocities = [];
            for (let i = 0; i < count; i++) {
                positions[i*3] = pos.x;
                positions[i*3+1] = pos.y;
                positions[i*3+2] = pos.z;
                velocities.push(new THREE.Vector3((Math.random()-0.5)*0.35, (Math.random()-0.5)*0.35, (Math.random()-0.5)*0.35));
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            let pMat = new THREE.PointsMaterial({ color: colorHex || 0x00f5a0, size: 0.18, transparent: true, opacity: 1 });
            let pSystem = new THREE.Points(pGeo, pMat);
            scene.add(pSystem);
            sparks.push({ system: pSystem, vels: velocities, life: 1.0 });
        }

        function showHitFeedback(text, color) {
            let fb = document.getElementById('hit-feedback');
            fb.innerText = text;
            fb.style.color = color;
            fb.style.opacity = '1';
            setTimeout(() => { fb.style.opacity = '0'; }, 500);
        }

        let raycaster = new THREE.Raycaster();
        let canShoot = true;

        document.addEventListener('mousedown', (e) => {
            if (e.button === 2) {
                isAiming = true;
                camera.fov = 22;
                camera.updateProjectionMatrix();
                gun.position.copy(AIM_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'block';
                document.getElementById('crosshair').style.display = 'none';
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 2) {
                isAiming = false;
                camera.fov = 65;
                camera.updateProjectionMatrix();
                gun.position.copy(NORMAL_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'none';
                document.getElementById('crosshair').style.display = 'block';
            }
        });

        document.addEventListener('click', (e) => {
            if (e.button !== 0) return;
            if (isGameOver) { resetGame(); return; }
            if (!canShoot) return;
            canShoot = false;

            flashMat.opacity = 1.0;
            gun.position.z += 0.22;
            gun.rotation.x = 0.25;
            setTimeout(() => { flashMat.opacity = 0; }, 60);
            setTimeout(() => {
                gun.position.copy(isAiming ? AIM_GUN_POS : NORMAL_GUN_POS);
                gun.rotation.x = 0;
                canShoot = true;
            }, 450);

            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let allBotMeshes = [];
            bots.forEach(b => {
                b.traverse(child => { if (child.isMesh) allBotMeshes.push(child); });
            });

            let intersects = raycaster.intersectObjects(allBotMeshes);
            if (intersects.length > 0) {
                let hitPoint = intersects[0].point;
                let hitMesh = intersects[0].object;

                let partGroup = hitMesh.parent;
                while (partGroup && !['head', 'body', 'legs'].includes(partGroup.userData?.type)) {
                    partGroup = partGroup.parent;
                }

                let hitBot = hitMesh.parent;
                while (hitBot && !bots.includes(hitBot)) {
                    hitBot = hitBot.parent;
                }

                if (hitBot && partGroup) {
                    let hitType = partGroup.userData.type;
                    let dmg = 0;
                    let sparkColor = 0x00f5a0;

                    if (hitType === 'head') {
                        dmg = 100;
                        sparkColor = 0xff0055;
                        showHitFeedback("CRITICAL HEADSHOT! -100", "#ff0055");
                    } else if (hitType === 'body') {
                        dmg = 50;
                        sparkColor = 0xffaa00;
                        showHitFeedback("BODY HIT -50", "#ffaa00");
                    } else if (hitType === 'legs') {
                        dmg = 25;
                        sparkColor = 0x00d2ff;
                        showHitFeedback("LEG HIT -25", "#00d2ff");
                    }

                    createSparks(hitPoint, sparkColor);
                    hitBot.userData.hp -= dmg;

                    if (hitBot.userData.hp <= 0) {
                        scene.remove(hitBot);
                        bots = bots.filter(b => b !== hitBot);
                        score += 1;
                        document.getElementById('score').innerText = score;
                    }
                }
            }
        });

        function resetGame() {
            bots.forEach(b => scene.remove(b));
            bots = []; hp = 100; score = 0; isGameOver = false;
            document.getElementById('hp-fill').style.width = '100%';
            document.getElementById('score').innerText = '0';
            document.getElementById('game-over').style.display = 'none';
            camera.position.set(0, PLAYER_HEIGHT, 0);
            controls.target.set(0, PLAYER_HEIGHT, -1);
            for (let i = 0; i < 5; i++) bots.push(createDetailedBot());
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver) return;

            // 시선 방향 계산
            let lookDir = new THREE.Vector3();
            camera.getWorldDirection(lookDir);
            
            let forward = lookDir.clone();
            forward.y = 0;
            forward.normalize();

            let right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();
            let move = new THREE.Vector3();

            if (keys.KeyW) move.add(forward);
            if (keys.KeyS) move.sub(forward);
            if (keys.KeyD) move.add(right);
            if (keys.KeyA) move.sub(right);

            if (move.lengthSq() > 0) {
                let moveSpeed = 0.085;
                move.normalize().multiplyScalar(moveSpeed);
                camera.position.add(move);
                controls.target.add(move);
            }

            camera.position.y = PLAYER_HEIGHT;

            // 마우스 Y축 드래그 시 카메라 위치 고정 처리
            let camPos = camera.position.clone();
            controls.update();
            let lookOffset = new THREE.Vector3().subVectors(controls.target, camera.position);
            camera.position.copy(camPos);
            controls.target.copy(camPos).add(lookOffset);

            sparks.forEach((sp, idx) => {
                sp.life -= 0.05;
                let pos = sp.system.geometry.attributes.position.array;
                for (let i = 0; i < sp.vels.length; i++) {
                    pos[i*3] += sp.vels[i].x;
                    pos[i*3+1] += sp.vels[i].y;
                    pos[i*3+2] += sp.vels[i].z;
                }
                sp.system.geometry.attributes.position.needsUpdate = true;
                sp.system.material.opacity = sp.life;
                if (sp.life <= 0) {
                    scene.remove(sp.system);
                    sparks.splice(idx, 1);
                }
            });

            bots.forEach(bot => {
                let dir = new THREE.Vector3().subVectors(camera.position, bot.position);
                dir.y = 0;
                let dist = dir.length();
                dir.normalize();

                if (dist > 1.8) {
                    bot.position.addScaledVector(dir, 0.03);
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
