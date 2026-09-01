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
    </style>
</head>
<body>
    <div id="crosshair"></div>
    <div id="scope-overlay"></div>
    <div id="hud">ELIMINATIONS: <span id="score" style="color:#ff4655;">0</span></div>
    <div id="hp-bar"><div id="hp-fill"></div></div>
    <div id="game-over">MISSION FAILED<br><span style="font-size:18px; color:#fff;">클릭하여 다시 시작</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        window.focus();
        document.addEventListener('contextmenu', event => event.preventDefault());

        let scene = new THREE.Scene();
        scene.background = new THREE.Color(0xdce8f0);
        scene.fog = new THREE.FogExp2(0xdce8f0, 0.005);

        let camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;
        document.body.appendChild(renderer.domElement);

        let controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.enableZoom = false;

        const PLAYER_HEIGHT = 2.0;
        camera.position.set(0, PLAYER_HEIGHT, 0.1);
        controls.target.set(0, PLAYER_HEIGHT, -10);

        // 조명 설정
        scene.add(new THREE.AmbientLight(0xfff5ea, 0.7));
        let sun = new THREE.DirectionalLight(0xfffaed, 1.4);
        sun.position.set(50, 80, 40);
        sun.castShadow = true;
        sun.shadow.mapSize.width = 2048;
        sun.shadow.mapSize.height = 2048;
        sun.shadow.camera.near = 0.5;
        sun.shadow.camera.far = 200;
        let d = 50;
        sun.shadow.camera.left = -d; sun.shadow.camera.right = d;
        sun.shadow.camera.top = d; sun.shadow.camera.bottom = -d;
        scene.add(sun);

        // 재질 설정
        let stoneMat = new THREE.MeshStandardMaterial({ color: 0xe2d7c5, roughness: 0.5, metalness: 0.1 });
        let roofMat = new THREE.MeshStandardMaterial({ color: 0xc05634, roughness: 0.4 });
        let groundMat = new THREE.MeshStandardMaterial({ color: 0xbdb099, roughness: 0.8, metalness: 0.1 });

        let floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), groundMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        let grid = new THREE.GridHelper(200, 50, 0x7a6d58, 0x9e917c);
        grid.position.y = 0.01;
        scene.add(grid);

        function createColumn(x, z) {
            let col = new THREE.Group();
            let base = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.4, 1.6), stoneMat);
            base.position.y = 0.2; base.castShadow = true; base.receiveShadow = true;
            let shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.6, 6, 24), stoneMat);
            shaft.position.y = 3.4; shaft.castShadow = true; shaft.receiveShadow = true;
            let capital = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.5, 1.5), stoneMat);
            capital.position.y = 6.65; capital.castShadow = true; capital.receiveShadow = true;
            col.add(base, shaft, capital);
            col.position.set(x, 0, z);
            scene.add(col);
        }

        function createHouse(x, z, w, h, d) {
            let bldg = new THREE.Group();
            let wall = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), stoneMat);
            wall.position.y = h / 2; wall.castShadow = true; wall.receiveShadow = true;
            let roof = new THREE.Mesh(new THREE.ConeGeometry(Math.max(w, d) * 0.75, 3, 4), roofMat);
            roof.position.y = h + 1.5; roof.rotation.y = Math.PI / 4; roof.castShadow = true;
            bldg.add(wall, roof);
            bldg.position.set(x, 0, z);
            scene.add(bldg);
        }

        createHouse(-20, -28, 9, 7, 11);
        createHouse(22, -32, 11, 8, 9);
        createHouse(-25, 12, 10, 7, 10);
        createHouse(25, 15, 9, 6, 9);

        createColumn(-9, -14); createColumn(9, -14);
        createColumn(-9, -24); createColumn(9, -24);
        createColumn(-16, 0); createColumn(16, 0);

        // 총기 및 스코프
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

        // 봇 & 게임 상태
        let hp = 100, score = 0, isGameOver = false;
        let keys = { KeyW: false, KeyS: false, KeyA: false, KeyD: false };
        let bots = [], sparks = [];
        let isAiming = false;

        function createBot() {
            if (isGameOver) return;
            let bot = new THREE.Group();

            let armorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.2, metalness: 0.8 });
            let energyMat = new THREE.MeshStandardMaterial({ color: 0xff4655, emissive: 0xff1122, emissiveIntensity: 1.5 });
            let jointMat = new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.8, metalness: 0.3 });
            let detailGold = new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.2, metalness: 0.9 });

            let head = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.36, 0.42), armorMat);
            head.position.y = 2.05; head.castShadow = true;
            let eyeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.1, 16), energyMat);
            eyeLens.rotateX(Math.PI / 2); eyeLens.position.set(0, 2.08, -0.22);

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

            let legL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.75, 0.24), armorMat);
            legL.position.set(-0.24, 0.4, 0); legL.castShadow = true;
            let legR = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.75, 0.24), armorMat);
            legR.position.set(0.24, 0.4, 0); legR.castShadow = true;

            bot.add(head, eyeLens, chest, core, shoulderL, shoulderR, armL, armR, waist, legL, legR);

            let angle = Math.random() * Math.PI * 2;
            let dist = 18 + Math.random() * 20;
            bot.position.set(camera.position.x + Math.cos(angle) * dist, 0, camera.position.z + Math.sin(angle) * dist);

            scene.add(bot);
            bots.push(bot);
        }

        for (let i = 0; i < 5; i++) createBot();
        setInterval(() => { if (bots.length < 7) createBot(); }, 2000);

        document.addEventListener('keydown', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = true; });
        document.addEventListener('keyup', (e) => { if (keys.hasOwnProperty(e.code)) keys[e.code] = false; });

        function createSparks(pos) {
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
            let pMat = new THREE.PointsMaterial({ color: 0x00f5a0, size: 0.15, transparent: true, opacity: 1 });
            let pSystem = new THREE.Points(pGeo, pMat);
            scene.add(pSystem);
            sparks.push({ system: pSystem, vels: velocities, life: 1.0 });
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
                createSparks(hitPoint);

                let hitMesh = intersects[0].object;
                let hitBot = hitMesh.parent;
                while (hitBot && !bots.includes(hitBot)) {
                    hitBot = hitBot.parent;
                }
                if (hitBot) {
                    scene.remove(hitBot);
                    bots = bots.filter(b => b !== hitBot);
                    score += 1;
                    document.getElementById('score').innerText = score;
                    setTimeout(createBot, 500);
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

            bots.forEach(bot => {
                let dir = new THREE.Vector3().subVectors(camera.position, bot.position);
                dir.y = 0;
                let dist = dir.length();
                dir.normalize();

                if (dist > 1.8) {
                    bot.position.addScaledVector(dir, 0.045);
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

            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=720)
