import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SNIPER", layout="wide")
st.title("🎯 SNIPER")
st.caption("🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | 마우스 드래그 = 시점 전환 | 좌클릭 = 사격 | 우클릭 = 스나이퍼 조준(ADS)")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #0f172a; font-family: 'Segoe UI', sans-serif; user-select: none; }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 6px; height: 6px;
            transform: translate(-50%, -50%); pointer-events: none; z-index: 10;
            background: #00f5a0; border-radius: 50%; box-shadow: 0 0 10px #00f5a0;
        }
        #scope-overlay {
            position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none; z-index: 9; display: none;
            background: radial-gradient(circle, transparent 30%, rgba(0,0,0,0.85) 60%, black 100%);
        }
        #scope-overlay::before, #scope-overlay::after {
            content: ''; position: absolute; background: rgba(0, 245, 160, 0.6);
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
        
        // --- 1. 푸른 하늘 및 구름 환경 생성 ---
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
            topColor: { value: new THREE.Color(0x3a82ee) },
            bottomColor: { value: new THREE.Color(0xdbeafe) },
            offset: { value: 330 },
            exponent: { value: 0.6 }
        };
        let skyGeo = new THREE.SphereGeometry(400, 32, 15);
        let skyMat = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms, side: THREE.BackSide });
        let sky = new THREE.Mesh(skyGeo, skyMat);
        scene.add(sky);

        // 동적 구름
        let clouds = [];
        let cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1.0, transparent: true, opacity: 0.85 });
        for (let i = 0; i < 20; i++) {
            let cloudGroup = new THREE.Group();
            let pCount = 3 + Math.floor(Math.random() * 4);
            for (let j = 0; j < pCount; j++) {
                let p = new THREE.Mesh(new THREE.DodecahedronGeometry(6 + Math.random() * 6), cloudMat);
                p.position.set(j * 4 - pCount * 2, Math.random() * 2, Math.random() * 3);
                cloudGroup.add(p);
            }
            cloudGroup.position.set((Math.random() - 0.5) * 160, 35 + Math.random() * 15, (Math.random() - 0.5) * 160);
            scene.add(cloudGroup);
            clouds.push(cloudGroup);
        }

        let camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        document.body.appendChild(renderer.domElement);

        let controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.enableZoom = false;

        const PLAYER_HEIGHT = 2.0;
        camera.position.set(0, PLAYER_HEIGHT, 0.1);
        controls.target.set(0, PLAYER_HEIGHT, -10);

        // 조명
        scene.add(new THREE.AmbientLight(0xffffff, 0.65));
        let sun = new THREE.DirectionalLight(0xfffaed, 1.3);
        sun.position.set(40, 60, 30);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 150;
        let d = 45;
        sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
        sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
        scene.add(sun);

        // --- 2. 마을 지형/건축물 생성 (80x80 좁은 마을) ---
        let wallMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.6 });
        let roofMat = new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.4 });
        let roadMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 });
        let grassMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.9 });
        let woodMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 });

        let floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), grassMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        // 중앙 도로
        let mainRoad = new THREE.Mesh(new THREE.PlaneGeometry(16, 80), roadMat);
        mainRoad.rotation.x = -Math.PI / 2;
        mainRoad.position.y = 0.01;
        mainRoad.receiveShadow = true;
        scene.add(mainRoad);

        let crossRoad = new THREE.Mesh(new THREE.PlaneGeometry(80, 14), roadMat);
        crossRoad.rotation.x = -Math.PI / 2;
        crossRoad.position.y = 0.01;
        crossRoad.receiveShadow = true;
        scene.add(crossRoad);

        // 실제 건물 구조 함수
        function createVillageHouse(x, z, w, h, d, color) {
            let house = new THREE.Group();
            let mat = color ? new THREE.MeshStandardMaterial({ color: color, roughness: 0.6 }) : wallMat;
            
            let bldg = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
            bldg.position.y = h / 2;
            bldg.castShadow = true; bldg.receiveShadow = true;
            house.add(bldg);

            let roof = new THREE.Mesh(new THREE.ConeGeometry(Math.max(w, d) * 0.7, 2.5, 4), roofMat);
            roof.position.y = h + 1.25;
            roof.rotation.y = Math.PI / 4;
            roof.castShadow = true;
            house.add(roof);

            // 창문 및 문 상세 연출
            let door = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.2, 0.1), woodMat);
            door.position.set(0, 1.1, d / 2 + 0.06);
            house.add(door);

            house.position.set(x, 0, z);
            scene.add(house);
        }

        function createCrate(x, z) {
            let crate = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.5, 1.5), woodMat);
            crate.position.set(x, 0.75, z);
            crate.castShadow = true; crate.receiveShadow = true;
            scene.add(crate);
        }

        // 마을 건물 및 장애물 구조 배치
        createVillageHouse(-22, -22, 10, 6, 12, 0x64748b);
        createVillageHouse(22, -22, 12, 8, 10, 0x475569);
        createVillageHouse(-22, 22, 11, 7, 11, 0x334155);
        createVillageHouse(22, 22, 10, 6, 12, 0x64748b);
        
        // 엄폐용 작은 상자들
        createCrate(-6, -10); createCrate(-5, -8); createCrate(7, -12);
        createCrate(6, 10); createCrate(-7, 14); createCrate(8, 15);

        // 외곽 경계 담장
        let wallBound1 = new THREE.Mesh(new THREE.BoxGeometry(80, 3, 1), wallMat);
        wallBound1.position.set(0, 1.5, -40); scene.add(wallBound1);
        let wallBound2 = wallBound1.clone(); wallBound2.position.set(0, 1.5, 40); scene.add(wallBound2);
        let wallBound3 = new THREE.Mesh(new THREE.BoxGeometry(1, 3, 80), wallMat);
        wallBound3.position.set(-40, 1.5, 0); scene.add(wallBound3);
        let wallBound4 = wallBound3.clone(); wallBound4.position.set(40, 1.5, 0); scene.add(wallBound4);

        // --- 3. 총기 시스템 ---
        let gun = new THREE.Group();
        let gunDark = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2, metalness: 0.85 });
        let gunGold = new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.2, metalness: 0.9 });
        let scopeLensMat = new THREE.MeshStandardMaterial({ color: 0x00ffcc, emissive: 0x00bb99, emissiveIntensity: 0.8 });

        let barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.045, 2.8, 16), gunDark);
        barrel.rotateX(Math.PI / 2); barrel.position.set(0, 0, -1.3);

        let muzzle = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.09, 0.25), gunGold);
        muzzle.position.set(0, 0, -2.7);

        let flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
        let muzzleFlash = new THREE.Mesh(new THREE.OctahedronGeometry(0.25), flashMat);
        muzzleFlash.position.set(0, 0, -2.9);
        gun.add(muzzleFlash);

        let scopeTube = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.9, 20), gunDark);
        scopeTube.rotateX(Math.PI / 2); scopeTube.position.set(0, 0.16, -0.6);

        let scopeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.02, 20), scopeLensMat);
        scopeLens.rotateX(Math.PI / 2); scopeLens.position.set(0, 0.16, -1.05);

        let receiver = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.22, 1.1), gunDark);
        receiver.position.set(0, -0.04, -0.3);

        let mag = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.4, 0.25), gunGold);
        mag.position.set(0, -0.28, -0.4); mag.rotation.x = -0.2;

        let stock = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.7), gunDark);
        stock.position.set(0, -0.02, 0.3);

        gun.add(barrel, muzzle, scopeTube, scopeLens, receiver, mag, stock);

        const NORMAL_GUN_POS = new THREE.Vector3(0.38, -0.32, -0.55);
        const AIM_GUN_POS = new THREE.Vector3(0, -0.16, -0.4);
        gun.position.copy(NORMAL_GUN_POS);

        camera.add(gun);
        scene.add(camera);

        // --- 4. 봇 생성 및 부위별 태그(Head/Body/Legs) 설정 ---
        let hp = 100, score = 0, isGameOver = false;
        let keys = { KeyW: false, KeyS: false, KeyA: false, KeyD: false };
        let bots = [], sparks = [];
        let isAiming = false;

        function createBot() {
            if (isGameOver) return;
            let bot = new THREE.Group();
            bot.userData = { hp: 100 }; // 상대 HP 100 고정

            let armorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.2, metalness: 0.8 });
            let energyMat = new THREE.MeshStandardMaterial({ color: 0xff4655, emissive: 0xff1122, emissiveIntensity: 1.5 });
            let jointMat = new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.8, metalness: 0.3 });
            let detailGold = new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.2, metalness: 0.9 });

            // [부위 판정 1] Head - 100 데미지
            let headGroup = new THREE.Group();
            let headMesh = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.36, 0.42), armorMat);
            headMesh.castShadow = true;
            let eyeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.1, 16), energyMat);
            eyeLens.rotateX(Math.PI / 2); eyeLens.position.set(0, 0.03, -0.22);
            headGroup.add(headMesh, eyeLens);
            headGroup.position.y = 2.05;
            headGroup.userData = { type: 'head' }; // 부위 식별

            // [부위 판정 2] Body - 50 데미지
            let bodyGroup = new THREE.Group();
            let chest = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.9, 0.52), armorMat);
            chest.position.y = 1.35; chest.castShadow = true;
            let core = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 16), energyMat);
            core.position.set(0, 1.45, -0.27);
            let shoulderL = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.32, 0.42), detailGold);
            shoulderL.position.set(-0.58, 1.65, 0); shoulderL.castShadow = true;
            let shoulderR = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.32, 0.42), detailGold);
            shoulderR.position.set(0.58, 1.65, 0); shoulderR.castShadow = true;
            let armL = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.08, 0.7), jointMat);
            armL.position.set(-0.58, 1.15, 0);
            let armR = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.08, 0.7), jointMat);
            armR.position.set(0.58, 1.15, 0);
            let waist = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.3), jointMat);
            waist.position.y = 0.85;
            bodyGroup.add(chest, core, shoulderL, shoulderR, armL, armR, waist);
            bodyGroup.userData = { type: 'body' };

            // [부위 판정 3] Legs - 25 데미지
            let legGroup = new THREE.Group();
            let legL = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.75, 0.24), armorMat);
            legL.position.set(-0.24, 0.4, 0); legL.castShadow = true;
            let legR = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.75, 0.24), armorMat);
            legR.position.set(0.24, 0.4, 0); legR.castShadow = true;
            legGroup.add(legL, legR);
            legGroup.userData = { type: 'legs' };

            bot.add(headGroup, bodyGroup, legGroup);

            // 스폰 위치 (좁아진 맵에 맞게 조정)
            let angle = Math.random() * Math.PI * 2;
            let dist = 12 + Math.random() * 15;
            bot.position.set(camera.position.x + Math.cos(angle) * dist, 0, camera.position.z + Math.sin(angle) * dist);

            scene.add(bot);
            bots.push(bot);
        }

        for (let i = 0; i < 5; i++) createBot();
        setInterval(() => { if (bots.length < 6) createBot(); }, 2500);

        document.addEventListener('keydown', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = true; });
        document.addEventListener('keyup', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = false; });

        function createSparks(pos, colorHex) {
            let pGeo = new THREE.BufferGeometry();
            let count = 15;
            let positions = new Float32Array(count * 3);
            let velocities = [];
            for (let i = 0; i < count; i++) {
                positions[i*3] = pos.x;
                positions[i*3+1] = pos.y;
                positions[i*3+2] = pos.z;
                velocities.push(new THREE.Vector3((Math.random()-0.5)*0.3, (Math.random()-0.5)*0.3, (Math.random()-0.5)*0.3));
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            let pMat = new THREE.PointsMaterial({ color: colorHex || 0x00f5a0, size: 0.15, transparent: true, opacity: 1 });
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
                camera.fov = 25;
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

        // --- 사격 및 부위별 데미지 연산 ---
        document.addEventListener('click', (e) => {
            if (e.button !== 0) return;
            if (isGameOver) { resetGame(); return; }
            if (!canShoot) return;
            canShoot = false;

            flashMat.opacity = 1.0;
            gun.position.z += 0.22;
            gun.rotation.x = 0.3;
            setTimeout(() => { flashMat.opacity = 0; }, 60);
            setTimeout(() => {
                gun.position.copy(isAiming ? AIM_GUN_POS : NORMAL_GUN_POS);
                gun.rotation.x = 0;
                canShoot = true;
            }, 500);

            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let allBotMeshes = [];
            bots.forEach(b => {
                b.traverse(child => { if (child.isMesh) allBotMeshes.push(child); });
            });

            let intersects = raycaster.intersectObjects(allBotMeshes);
            if (intersects.length > 0) {
                let hitPoint = intersects[0].point;
                let hitMesh = intersects[0].object;

                // 타격된 부위 찾기
                let partGroup = hitMesh.parent;
                while (partGroup && !['head', 'body', 'legs'].includes(partGroup.userData?.type)) {
                    partGroup = partGroup.parent;
                }

                // 봇 최상위 객체 찾기
                let hitBot = hitMesh.parent;
                while (hitBot && !bots.includes(hitBot)) {
                    hitBot = hitBot.parent;
                }

                if (hitBot && partGroup) {
                    let hitType = partGroup.userData.type;
                    let dmg = 0;
                    let sparkColor = 0x00f5a0;

                    if (hitType === 'head') {
                        dmg = 100; // 헤드샷 - 즉사
                        sparkColor = 0xff0055;
                        showHitFeedback("HEADSHOT! -100", "#ff0055");
                    } else if (hitType === 'body') {
                        dmg = 50;  // 몸통 - 50
                        sparkColor = 0xffaa00;
                        showHitFeedback("BODY HIT -50", "#ffaa00");
                    } else if (hitType === 'legs') {
                        dmg = 25;  // 다리 - 25
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
                        setTimeout(createBot, 400);
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
            camera.position.set(0, PLAYER_HEIGHT, 0.1);
            controls.target.set(0, PLAYER_HEIGHT, -10);
            for (let i = 0; i < 5; i++) createBot();
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver) return;

            // 구름 천천히 이동
            clouds.forEach(c => {
                c.position.x += 0.02;
                if (c.position.x > 80) c.position.x = -80;
            });

            let moveSpeed = 0.08;
            let forward = new THREE.Vector3();
            camera.getWorldDirection(forward);
            forward.y = 0; forward.normalize();

            let right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();
            let move = new THREE.Vector3();

            if (keys.KeyW) move.add(forward);
            if (keys.KeyS) move.sub(forward);
            if (keys.KeyD) move.add(right);
            if (keys.KeyA) move.sub(right);

            if (move.lengthSq() > 0) {
                move.normalize().multiplyScalar(moveSpeed);
                camera.position.add(move);
                controls.target.add(move);
            }

            camera.position.y = PLAYER_HEIGHT;

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

            // --- 봇 이동 (속도를 0.025로 하향 조정) ---
            bots.forEach(bot => {
                let dir = new THREE.Vector3().subVectors(camera.position, bot.position);
                dir.y = 0;
                let dist = dir.length();
                dir.normalize();

                if (dist > 1.8) {
                    bot.position.addScaledVector(dir, 0.025); // 봇 이동 속도 하향 반영
                } else {
                    hp -= 0.25;
                    document.getElementById('hp-fill').style.width = Math.max(0, hp) + '%';
                    if (hp <= 0) {
                        isGameOver = true;
                        document.getElementById('game-over').style.display = 'block';
                    }
                }
                bot.lookAt(camera.position.x, 0, camera.position.z);
            });

            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=720)
