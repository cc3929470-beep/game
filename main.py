import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SNIPER: URBAN WARZONE", layout="wide")
st.title("🎯 SNIPER: URBAN WARZONE")
st.caption("🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | [1, 2, 3] = 총기 변경 | 마우스 드래그 = 시선 전환 | 좌클릭 = 사격 | 우클릭 = ADS 조준")

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
            position: absolute; top: 20px; left: 20px; color: #f8fafc; font-size: 18px;
            font-weight: 800; z-index: 10; letter-spacing: 2px;
            background: rgba(15, 23, 42, 0.85); padding: 12px 22px; border-left: 5px solid #ff4655;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5); backdrop-filter: blur(4px);
        }
        #gun-hud {
            position: absolute; bottom: 30px; right: 30px; color: #00f5a0; font-size: 22px;
            font-weight: 900; z-index: 10; background: rgba(15, 23, 42, 0.85);
            padding: 10px 20px; border-radius: 6px; border: 1px solid #00f5a0;
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
    <div id="gun-hud">WEAPON: <span id="gun-name">M200 HEAVY</span></div>
    <div id="hp-bar"><div id="hp-fill"></div></div>
    <div id="hit-feedback"></div>
    <div id="game-over">MISSION FAILED<br><span style="font-size:18px; color:#fff;">클릭하여 다시 시작</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
        window.focus();
        document.addEventListener('contextmenu', event => event.preventDefault());

        let scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x334155, 0.012); // 전투 느낌의 자욱한 연기 안개

        // 스카이돔 (어두운 전쟁터 느낌의 하늘)
        let skyGeo = new THREE.SphereGeometry(350, 32, 16);
        let skyMat = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vWorldPosition;
                void main() {
                    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
                    vWorldPosition = worldPosition.xyz;
                    gl_Position = projectionMatrix * viewMatrix * worldPosition;
                }
            `,
            fragmentShader: `
                uniform vec3 topColor;
                uniform vec3 bottomColor;
                varying vec3 vWorldPosition;
                void main() {
                    float h = normalize(vWorldPosition + 20.0).y;
                    gl_FragColor = vec4(mix(bottomColor, topColor, max(h, 0.0)), 1.0);
                }
            `,
            uniforms: {
                topColor: { value: new THREE.Color(0x0f172a) },
                bottomColor: { value: new THREE.Color(0x475569) }
            },
            side: THREE.BackSide
        });
        scene.add(new THREE.Mesh(skyGeo, skyMat));

        let camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;
        document.body.appendChild(renderer.domElement);

        const PLAYER_HEIGHT = 2.0;
        camera.position.set(0, PLAYER_HEIGHT, 0);

        // 시선 전환
        let pitch = 0, yaw = 0;
        let isMouseDown = false;
        let prevMousePos = { x: 0, y: 0 };

        document.addEventListener('mousedown', (e) => {
            if (e.button === 0 || e.button === 2) {
                isMouseDown = true;
                prevMousePos = { x: e.clientX, y: e.clientY };
            }
        });
        document.addEventListener('mouseup', () => { isMouseDown = false; });
        document.addEventListener('mousemove', (e) => {
            if (!isMouseDown) return;
            let deltaX = e.clientX - prevMousePos.x;
            let deltaY = e.clientY - prevMousePos.y;
            prevMousePos = { x: e.clientX, y: e.clientY };

            let sensitivity = 0.003;
            yaw -= deltaX * sensitivity;
            pitch -= deltaY * sensitivity;

            let maxPitch = Math.PI / 2 - 0.01;
            pitch = Math.max(-maxPitch, Math.min(maxPitch, pitch));

            let euler = new THREE.Euler(pitch, yaw, 0, 'YXZ');
            camera.quaternion.setFromEuler(euler);
        });

        // 조명 (드라마틱한 태양빛)
        scene.add(new THREE.AmbientLight(0x94a3b8, 0.6));
        let sun = new THREE.DirectionalLight(0xfba518, 1.8);
        sun.position.set(50, 60, 30);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 200;
        let d = 50;
        sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
        sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
        scene.add(sun);

        // 기본 금속 및 건축 재질
        let heavySteel = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.25, metalness: 0.95 });
        let chromeMetal = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.15, metalness: 0.98 });
        let darkIron = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.9 });
        let brassGold = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.3, metalness: 0.85 });
        let concreteMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.9, metalness: 0.05 });
        let burntMetal = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.8, metalness: 0.7 });
        let rustMetal = new THREE.MeshStandardMaterial({ color: 0x7c2d12, roughness: 0.7, metalness: 0.4 });

        // --- 맵 설계: 제한된 구역 (Boundary Boundary) 및 시가전 거리 ---
        const MAP_LIMIT = 38; // 플레이어 이동제한 영역

        let floorMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.85, metalness: 0.1 });
        let floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        // 外 Map Boundary Walls (4방향 방벽)
        function createBoundaryWalls() {
            let wallMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.9 });
            let h = 12, t = 2;
            let wallN = new THREE.Mesh(new THREE.BoxGeometry(80, h, t), wallMat); wallN.position.set(0, h/2, -MAP_LIMIT);
            let wallS = new THREE.Mesh(new THREE.BoxGeometry(80, h, t), wallMat); wallS.position.set(0, h/2, MAP_LIMIT);
            let wallE = new THREE.Mesh(new THREE.BoxGeometry(t, h, 80), wallMat); wallE.position.set(MAP_LIMIT, h/2, 0);
            let wallW = new THREE.Mesh(new THREE.BoxGeometry(t, h, 80), wallMat); wallW.position.set(-MAP_LIMIT, h/2, 0);

            [wallN, wallS, wallE, wallW].forEach(w => { w.castShadow = true; w.receiveShadow = true; scene.add(w); });
        }
        createBoundaryWalls();

        // 건물 및 골목길 배치 (골목 생성)
        let bldgMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 });
        let glassMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.1, metalness: 0.9, transparent: true, opacity: 0.5 });

        function createBuildingBlock(x, z, w, h, d) {
            let bldg = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), bldgMat);
            bldg.position.set(x, h/2, z);
            bldg.castShadow = true; bldg.receiveShadow = true;

            for (let y = 3; y < h - 2; y += 3) {
                for (let wx = -w/2 + 2; wx < w/2 - 1; wx += 3) {
                    let win = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.8, 0.1), glassMat);
                    win.position.set(x + wx, y, z + (x > 0 ? -d/2 - 0.05 : d/2 + 0.05));
                    scene.add(win);
                }
            }
            scene.add(bldg);
        }

        // 건물을 일정 간격 배치하여 그 사이를 "골목(Alleyway)"으로 연출
        // 좌측 건물군
        createBuildingBlock(-24, -22, 18, 16, 18);
        createBuildingBlock(-24, 0, 18, 18, 16);    // 골목 1 (-24, -11)
        createBuildingBlock(-24, 22, 18, 14, 18);   // 골목 2 (-24, 11)

        // 우측 건물군
        createBuildingBlock(24, -22, 18, 15, 18);
        createBuildingBlock(24, 0, 18, 20, 16);     // 골목 3 (24, -11)
        createBuildingBlock(24, 22, 18, 16, 18);    // 골목 4 (24, 11)

        // 골목길 스폰 포인트 정의
        const ALLEY_SPAWNS = [
            new THREE.Vector3(-26, 0, -11),
            new THREE.Vector3(-26, 0, 11),
            new THREE.Vector3(26, 0, -11),
            new THREE.Vector3(26, 0, 11)
        ];

        // --- 장애물 & 엄폐물 (파괴된 트럭 / 바리케이드) ---
        function createDestroyedTruck(x, z, angle) {
            let truck = new THREE.Group();

            // 차체
            let body = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.4, 5.5), burntMetal);
            body.position.y = 1.0; body.castShadow = true; body.receiveShadow = true;
            truck.add(body);

            // 운전석
            let cab = new THREE.Mesh(new THREE.BoxGeometry(2.5, 1.3, 2.0), rustMetal);
            cab.position.set(0, 1.8, -1.6); cab.castShadow = true;
            truck.add(cab);

            // 바퀴 (소실/파괴된 바퀴 포함)
            for (let bx of [-1.3, 1.3]) {
                for (let bz of [-1.8, 1.8]) {
                    let wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.4, 12), darkIron);
                    wheel.rotateZ(Math.PI / 2); wheel.position.set(bx, 0.5, bz);
                    truck.add(wheel);
                }
            }

            truck.position.set(x, 0, z);
            truck.rotation.y = angle;
            truck.rotation.z = 0.22; // 옆으로 살짝 넘어져 비스듬하게 파괴된 느낌
            scene.add(truck);
        }

        function createBarricade(x, z, angle) {
            let bar = new THREE.Group();
            let conc1 = new THREE.Mesh(new THREE.BoxGeometry(3.5, 1.2, 0.6), concreteMat);
            conc1.position.y = 0.6; conc1.castShadow = true; conc1.receiveShadow = true;

            let conc2 = conc1.clone();
            conc2.position.set(0.8, 0.5, 0.4); conc2.rotation.y = 0.3;

            bar.add(conc1, conc2);
            bar.position.set(x, 0, z);
            bar.rotation.y = angle;
            scene.add(bar);
        }

        // 장애물 배치
        createDestroyedTruck(-4, 6, 0.4);
        createDestroyedTruck(6, -10, -0.6);
        createBarricade(-2, -18, 0.2);
        createBarricade(3, 16, -0.4);
        createBarricade(-12, 0, 1.57);
        createBarricade(12, 0, 1.57);

        // --- 쇠 느낌 극대화 헤비 봇 (Heavy Metal Bot) ---
        function createHeavyBot(spawnPos) {
            let bot = new THREE.Group();
            bot.userData = { hp: 120 };

            let redEye = new THREE.MeshStandardMaterial({ color: 0xff0033, emissive: 0xff0033, emissiveIntensity: 3.0 });
            let reactorGlow = new THREE.MeshStandardMaterial({ color: 0x00f5a0, emissive: 0x00f5a0, emissiveIntensity: 2.0 });

            // 머리
            let headGroup = new THREE.Group();
            let headMesh = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.35, 0.42), heavySteel);
            headMesh.castShadow = true;
            let visor = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.36, 16), redEye);
            visor.rotateZ(Math.PI / 2); visor.position.set(0, 0.05, -0.21);
            headGroup.add(headMesh, visor);
            headGroup.position.y = 2.2;
            headGroup.userData = { type: 'head' };

            // 몸통
            let bodyGroup = new THREE.Group();
            let torso = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.9, 0.5), darkIron);
            torso.position.y = 1.4; torso.castShadow = true;
            let plateL = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.6, 0.12), chromeMetal);
            plateL.position.set(-0.24, 1.48, -0.28);
            let plateR = plateL.clone(); plateR.position.set(0.24, 1.48, -0.28);

            let core = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.1, 16), reactorGlow);
            core.rotateX(Math.PI / 2); core.position.set(0, 1.4, -0.26);

            let shoulderL = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 16), heavySteel);
            shoulderL.position.set(-0.58, 1.7, 0);
            let shoulderR = shoulderL.clone(); shoulderR.position.set(0.58, 1.7, 0);

            bodyGroup.add(torso, plateL, plateR, core, shoulderL, shoulderR);
            bodyGroup.userData = { type: 'body' };

            // 다리
            let legGroup = new THREE.Group();
            let legL = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.09, 0.85, 12), chromeMetal);
            legL.position.set(-0.25, 0.42, 0); legL.castShadow = true;
            let legR = legL.clone(); legR.position.set(0.25, 0.42, 0);
            legGroup.add(legL, legR);
            legGroup.userData = { type: 'legs' };

            bot.add(headGroup, bodyGroup, legGroup);

            // 지정된 골목 사이 스폰 위치 지정
            let p = spawnPos || ALLEY_SPAWNS[Math.floor(Math.random() * ALLEY_SPAWNS.length)];
            bot.position.copy(p);

            scene.add(bot);
            return bot;
        }

        // --- 3종 스나이퍼 소총 ---
        function createGuns() {
            let guns = [];

            // [1] M200 Heavy Bolt-Action
            let g1 = new THREE.Group();
            let b1 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.035, 2.4, 24), chromeMetal);
            b1.rotateX(Math.PI / 2); b1.position.set(0, 0, -1.2);
            let r1 = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.22, 0.9), heavySteel);
            r1.position.set(0, 0, -0.1);
            let sc1 = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.85, 24), darkIron);
            sc1.rotateX(Math.PI / 2); sc1.position.set(0, 0.2, -0.2);
            let st1 = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.7), darkIron);
            st1.position.set(0, -0.02, 0.5);
            g1.add(b1, r1, sc1, st1);

            // [2] EBR Tactical DMR
            let g2 = new THREE.Group();
            let b2 = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.03, 1.8, 24), heavySteel);
            b2.rotateX(Math.PI / 2); b2.position.set(0, 0, -0.9);
            let rail = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.16, 1.1), chromeMetal);
            rail.position.set(0, 0, -0.6);
            let r2 = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.18, 0.7), darkIron);
            r2.position.set(0, 0, -0.05);
            let sc2 = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.65, 24), brassGold);
            sc2.rotateX(Math.PI / 2); sc2.position.set(0, 0.18, -0.15);
            g2.add(b2, rail, r2, sc2);

            // [3] Cyberpunk Laser Sniper
            let g3 = new THREE.Group();
            let b3 = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.0, 24), darkIron);
            b3.rotateX(Math.PI / 2); b3.position.set(0, 0, -1.0);
            let neonTube = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.6, 16), new THREE.MeshStandardMaterial({ color: 0x00f5a0, emissive: 0x00f5a0, emissiveIntensity: 3.0 }));
            neonTube.rotateX(Math.PI / 2); neonTube.position.set(0, 0.06, -1.0);
            let r3 = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.24, 0.8), chromeMetal);
            r3.position.set(0, 0, -0.1);
            let sc3 = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.12, 0.7), heavySteel);
            sc3.position.set(0, 0.21, -0.2);
            g3.add(b3, neonTube, r3, sc3);

            return { gunList: [g1, g2, g3], names: ["M200 HEAVY", "EBR TACTICAL", "CYBER LASER"] };
        }

        let gunData = createGuns();
        let guns = gunData.gunList;
        let gunNames = gunData.names;
        let currentGunIdx = 0;

        let gunContainer = new THREE.Group();
        guns.forEach((g, i) => {
            g.visible = (i === 0);
            gunContainer.add(g);
        });

        const NORMAL_GUN_POS = new THREE.Vector3(0.35, -0.28, -0.5);
        const AIM_GUN_POS = new THREE.Vector3(0, -0.19, -0.32);
        gunContainer.position.copy(NORMAL_GUN_POS);

        camera.add(gunContainer);
        scene.add(camera);

        // 무기 교체 이벤트
        document.addEventListener('keydown', (e) => {
            if (['Digit1', 'Digit2', 'Digit3'].includes(e.code)) {
                let idx = parseInt(e.code.replace('Digit', '')) - 1;
                guns[currentGunIdx].visible = false;
                currentGunIdx = idx;
                guns[currentGunIdx].visible = true;
                document.getElementById('gun-name').innerText = gunNames[currentGunIdx];
            }
        });

        let hp = 100, score = 0, isGameOver = false;
        let keys = { KeyW: false, KeyS: false, KeyA: false, KeyD: false };
        let bots = [], sparks = [];
        let isAiming = false;

        // 초기 봇 생성 (골목 위치)
        for (let i = 0; i < 4; i++) bots.push(createHeavyBot(ALLEY_SPAWNS[i]));
        setInterval(() => { if (bots.length < 6 && !isGameOver) bots.push(createHeavyBot()); }, 2000);

        document.addEventListener('keydown', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = true; });
        document.addEventListener('keyup', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = false; });

        function createSparks(pos, colorHex) {
            let pGeo = new THREE.BufferGeometry();
            let count = 25;
            let positions = new Float32Array(count * 3);
            let velocities = [];
            for (let i = 0; i < count; i++) {
                positions[i*3] = pos.x; positions[i*3+1] = pos.y; positions[i*3+2] = pos.z;
                velocities.push(new THREE.Vector3((Math.random()-0.5)*0.4, (Math.random()-0.5)*0.4, (Math.random()-0.5)*0.4));
            }
            pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            let pMat = new THREE.PointsMaterial({ color: colorHex || 0x00f5a0, size: 0.22, transparent: true, opacity: 1 });
            let pSystem = new THREE.Points(pGeo, pMat);
            scene.add(pSystem);
            sparks.push({ system: pSystem, vels: velocities, life: 1.0 });
        }

        function showHitFeedback(text, color) {
            let fb = document.getElementById('hit-feedback');
            fb.innerText = text; fb.style.color = color; fb.style.opacity = '1';
            setTimeout(() => { fb.style.opacity = '0'; }, 500);
        }

        let raycaster = new THREE.Raycaster();
        let canShoot = true;

        document.addEventListener('mousedown', (e) => {
            if (e.button === 2) {
                isAiming = true;
                camera.fov = 22; camera.updateProjectionMatrix();
                gunContainer.position.copy(AIM_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'block';
                document.getElementById('crosshair').style.display = 'none';
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 2) {
                isAiming = false;
                camera.fov = 65; camera.updateProjectionMatrix();
                gunContainer.position.copy(NORMAL_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'none';
                document.getElementById('crosshair').style.display = 'block';
            }
        });

        document.addEventListener('click', (e) => {
            if (e.button !== 0) return;
            if (isGameOver) { resetGame(); return; }
            if (!canShoot) return;
            canShoot = false;

            gunContainer.position.z += 0.25; gunContainer.rotation.x = 0.3;
            setTimeout(() => {
                gunContainer.position.copy(isAiming ? AIM_GUN_POS : NORMAL_GUN_POS);
                gunContainer.rotation.x = 0; canShoot = true;
            }, 380);

            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let allBotMeshes = [];
            bots.forEach(b => { b.traverse(child => { if (child.isMesh) allBotMeshes.push(child); }); });

            let intersects = raycaster.intersectObjects(allBotMeshes);
            if (intersects.length > 0) {
                let hitPoint = intersects[0].point;
                let hitMesh = intersects[0].object;

                let partGroup = hitMesh.parent;
                while (partGroup && !['head', 'body', 'legs'].includes(partGroup.userData?.type)) {
                    partGroup = partGroup.parent;
                }

                let hitBot = hitMesh.parent;
                while (hitBot && !bots.includes(hitBot)) { hitBot = hitBot.parent; }

                if (hitBot && partGroup) {
                    let hitType = partGroup.userData.type;
                    let dmg = 0, sparkColor = 0x00f5a0;

                    if (hitType === 'head') {
                        dmg = 120; sparkColor = 0xff0055;
                        showHitFeedback("HEAVY HEADSHOT! -120", "#ff0055");
                    } else if (hitType === 'body') {
                        dmg = 60; sparkColor = 0xffaa00;
                        showHitFeedback("ARMOR HIT -60", "#ffaa00");
                    } else if (hitType === 'legs') {
                        dmg = 30; sparkColor = 0x00d2ff;
                        showHitFeedback("LEG HIT -30", "#00d2ff");
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
            pitch = 0; yaw = 0;
            camera.quaternion.setFromEuler(new THREE.Euler(0, 0, 0));
            for (let i = 0; i < 4; i++) bots.push(createHeavyBot(ALLEY_SPAWNS[i]));
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver) return;

            let forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
            forward.y = 0; forward.normalize();

            let right = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
            right.y = 0; right.normalize();

            let move = new THREE.Vector3();
            if (keys.KeyW) move.add(forward);
            if (keys.KeyS) move.sub(forward);
            if (keys.KeyD) move.add(right);
            if (keys.KeyA) move.sub(right);

            if (move.lengthSq() > 0) {
                move.normalize().multiplyScalar(0.09);
                camera.position.add(move);
            }

            // 플레이어가 맵 외곽 콘크리트 방벽을 통과하지 못하게 제한
            let boundLimit = MAP_LIMIT - 2.5;
            camera.position.x = Math.max(-boundLimit, Math.min(boundLimit, camera.position.x));
            camera.position.z = Math.max(-boundLimit, Math.min(boundLimit, camera.position.z));
            camera.position.y = PLAYER_HEIGHT;

            sparks.forEach((sp, idx) => {
                sp.life -= 0.05;
                let pos = sp.system.geometry.attributes.position.array;
                for (let i = 0; i < sp.vels.length; i++) {
                    pos[i*3] += sp.vels[i].x; pos[i*3+1] += sp.vels[i].y; pos[i*3+2] += sp.vels[i].z;
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
                    bot.position.addScaledVector(dir, 0.035);
                } else {
                    hp -= 0.35;
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
