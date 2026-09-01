import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SNIPER: MORNING MARKET", layout="wide")
st.title("🎯 SNIPER: MORNING MARKET (MAX GRAPHICS)")
st.caption("🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | 마우스 드래그 = 전방위 자유 시선 전환 (하늘/바닥 완전 자유) | 좌클릭 = 사격 | 우클릭 = 스나이퍼 조준(ADS)")

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

    <script>
        window.focus();
        document.addEventListener('contextmenu', event => event.preventDefault());

        let scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0xfff3e0, 0.008);

        // 아침 하늘 스카이돔
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
                    float h = normalize(vWorldPosition + 50.0).y;
                    gl_FragColor = vec4(mix(bottomColor, topColor, max(h, 0.0)), 1.0);
                }
            `,
            uniforms: {
                topColor: { value: new THREE.Color(0x38bdf8) },    // 맑은 아침 하늘색
                bottomColor: { value: new THREE.Color(0xffedd5) } // 아침 노을/햇살 감성
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
        renderer.toneMappingExposure = 1.25;
        document.body.appendChild(renderer.domElement);

        const PLAYER_HEIGHT = 2.0;
        camera.position.set(0, PLAYER_HEIGHT, 0);

        // --- 마우스 드래그 기반 자유 시선 회전 시스템 ---
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

            // 상하 제한을 89도까지 풀어 거의 수직으로 위/아래를 볼 수 있게 보장
            let maxPitch = Math.PI / 2 - 0.01;
            pitch = Math.max(-maxPitch, Math.min(maxPitch, pitch));

            let euler = new THREE.Euler(pitch, yaw, 0, 'YXZ');
            camera.quaternion.setFromEuler(euler);
        });

        // 조명 (밝은 아침 햇살)
        scene.add(new THREE.AmbientLight(0xfff7ed, 0.75));
        let sun = new THREE.DirectionalLight(0xffedd5, 1.8);
        sun.position.set(60, 80, 40);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 200;
        let d = 60;
        sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
        sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
        scene.add(sun);

        // --- 아침 재래시장 맵 제작 ---
        let floorMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.8, metalness: 0.1 });
        let stallWood = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 });
        let awningRed = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.4 });
        let awningBlue = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.4 });
        let crateMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.8 });
        let bldgMat1 = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.6 });
        let bldgMat2 = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.5 });

        let floor = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        // 시장 상점 좌판 생성 함수
        function createMarketStall(x, z, angle, clothMat) {
            let stall = new THREE.Group();
            
            // 기둥 및 카운터
            let counter = new THREE.Mesh(new THREE.BoxGeometry(3.5, 1.1, 1.8), stallWood);
            counter.position.y = 0.55; counter.castShadow = true; counter.receiveShadow = true;
            stall.add(counter);

            // 차양 (천막 어닝)
            let roof = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.1, 2.2), clothMat);
            roof.position.set(0, 2.6, 0); roof.rotation.x = 0.15; roof.castShadow = true;
            stall.add(roof);

            let pole1 = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.6), stallWood);
            pole1.position.set(-1.7, 1.3, -0.8);
            let pole2 = pole1.clone(); pole2.position.set(1.7, 1.3, -0.8);
            stall.add(pole1, pole2);

            // 상점 물건 (박스/야채 더미 연출)
            for (let i = 0; i < 4; i++) {
                let item = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.3, 0.5), crateMat);
                item.position.set(-1 + i * 0.6, 1.25, 0);
                stall.add(item);
            }

            stall.position.set(x, 0, z);
            stall.rotation.y = angle;
            scene.add(stall);
        }

        // 건물 및 상점 배치
        function createBuilding(x, z, w, h, d, mat) {
            let bldg = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
            bldg.position.set(x, h/2, z);
            bldg.castShadow = true; bldg.receiveShadow = true;
            scene.add(bldg);
        }

        // 복잡한 시장 골목 형성
        for (let i = -40; i <= 40; i += 12) {
            createBuilding(-18, i, 12, 10 + (Math.abs(i)%3)*3, 10, bldgMat1);
            createBuilding(18, i, 12, 10 + (Math.abs(i)%2)*4, 10, bldgMat2);

            createMarketStall(-10, i, Math.PI / 2, i % 2 === 0 ? awningRed : awningBlue);
            createMarketStall(10, i, -Math.PI / 2, i % 2 === 0 ? awningBlue : awningRed);
        }

        // 중앙 시장 상자들
        for (let j = 0; j < 12; j++) {
            let crate = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 1.2), crateMat);
            crate.position.set((Math.random()-0.5)*12, 0.6, (Math.random()-0.5)*50);
            crate.rotation.y = Math.random();
            crate.castShadow = true; crate.receiveShadow = true;
            scene.add(crate);
        }

        // --- 실사 스나이퍼 소총 ---
        function createDetailedSniper() {
            let gun = new THREE.Group();
            let metalDark = new THREE.MeshStandardMaterial({ color: 0x111625, roughness: 0.35, metalness: 0.85 });
            let metalSteel = new THREE.MeshStandardMaterial({ color: 0x2e384d, roughness: 0.25, metalness: 0.95 });
            let polymer = new THREE.MeshStandardMaterial({ color: 0x1e2638, roughness: 0.6, metalness: 0.1 });
            let goldAccent = new THREE.MeshStandardMaterial({ color: 0xc59b27, roughness: 0.3, metalness: 0.9 });
            let lensGlass = new THREE.MeshStandardMaterial({ color: 0x00f5a0, emissive: 0x00a86b, emissiveIntensity: 0.6, roughness: 0.1 });

            let mainBarrel = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.032, 2.2, 24), metalSteel);
            mainBarrel.rotateX(Math.PI / 2); mainBarrel.position.set(0, 0, -1.1);

            let muzzleBrake = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.35, 16), metalDark);
            muzzleBrake.rotateX(Math.PI / 2); muzzleBrake.position.set(0, 0, -2.35);

            let handguard = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.14, 1.2), polymer);
            handguard.position.set(0, -0.01, -0.8);

            let receiver = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.2, 0.8), metalDark);
            receiver.position.set(0, -0.01, -0.1);

            let scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.8, 24), metalDark);
            scopeBody.rotateX(Math.PI / 2); scopeBody.position.set(0, 0.19, -0.2);

            let scopeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.01, 24), lensGlass);
            scopeLens.rotateX(Math.PI / 2); scopeLens.position.set(0, 0.19, -0.74);

            let mag = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.38, 0.28), polymer);
            mag.position.set(0, -0.24, -0.25); mag.rotation.x = -0.15;

            let grip = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.3, 0.14), polymer);
            grip.position.set(0, -0.2, 0.1); grip.rotation.x = -0.4;

            let stock = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.18, 0.65), polymer);
            stock.position.set(0, -0.01, 0.48);

            gun.add(mainBarrel, muzzleBrake, handguard, receiver, scopeBody, scopeLens, mag, grip, stock);

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

        // --- 정밀 전술 로봇(Bot) ---
        function createDetailedBot() {
            let bot = new THREE.Group();
            bot.userData = { hp: 100 };

            let armorMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3, metalness: 0.8 });
            let redGlow = new THREE.MeshStandardMaterial({ color: 0xff1e43, emissive: 0xff1e43, emissiveIntensity: 2.0 });

            let headGroup = new THREE.Group();
            let headBase = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.32, 0.38), armorMat);
            headBase.castShadow = true;
            let visor = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.1, 0.05), redGlow);
            visor.position.set(0, 0.04, -0.2);
            headGroup.add(headBase, visor);
            headGroup.position.y = 2.1;
            headGroup.userData = { type: 'head' };

            let bodyGroup = new THREE.Group();
            let chestCore = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.85, 0.45), armorMat);
            chestCore.position.y = 1.35; chestCore.castShadow = true;
            bodyGroup.add(chestCore);
            bodyGroup.userData = { type: 'body' };

            let legGroup = new THREE.Group();
            let legL = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.8, 12), armorMat);
            legL.position.set(-0.22, 0.4, 0); legL.castShadow = true;
            let legR = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.8, 12), armorMat);
            legR.position.set(0.22, 0.4, 0); legR.castShadow = true;
            legGroup.add(legL, legR);
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
            let count = 20;
            let positions = new Float32Array(count * 3);
            let velocities = [];
            for (let i = 0; i < count; i++) {
                positions[i*3] = pos.x; positions[i*3+1] = pos.y; positions[i*3+2] = pos.z;
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
            fb.innerText = text; fb.style.color = color; fb.style.opacity = '1';
            setTimeout(() => { fb.style.opacity = '0'; }, 500);
        }

        let raycaster = new THREE.Raycaster();
        let canShoot = true;

        document.addEventListener('mousedown', (e) => {
            if (e.button === 2) {
                isAiming = true;
                camera.fov = 22; camera.updateProjectionMatrix();
                gun.position.copy(AIM_GUN_POS);
                document.getElementById('scope-overlay').style.display = 'block';
                document.getElementById('crosshair').style.display = 'none';
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 2) {
                isAiming = false;
                camera.fov = 65; camera.updateProjectionMatrix();
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
            gun.position.z += 0.22; gun.rotation.x = 0.25;
            setTimeout(() => { flashMat.opacity = 0; }, 60);
            setTimeout(() => {
                gun.position.copy(isAiming ? AIM_GUN_POS : NORMAL_GUN_POS);
                gun.rotation.x = 0; canShoot = true;
            }, 450);

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
                        dmg = 100; sparkColor = 0xff0055;
                        showHitFeedback("CRITICAL HEADSHOT! -100", "#ff0055");
                    } else if (hitType === 'body') {
                        dmg = 50; sparkColor = 0xffaa00;
                        showHitFeedback("BODY HIT -50", "#ffaa00");
                    } else if (hitType === 'legs') {
                        dmg = 25; sparkColor = 0x00d2ff;
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
            pitch = 0; yaw = 0;
            camera.quaternion.setFromEuler(new THREE.Euler(0, 0, 0));
            for (let i = 0; i < 5; i++) bots.push(createDetailedBot());
        }

        function animate() {
            requestAnimationFrame(animate);
            if (isGameOver) return;

            // 시선 이동 기반 키보드 WASD 움직임
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
