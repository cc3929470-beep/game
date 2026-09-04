import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="High-Graphics 3D Cyber FPS", layout="wide")

# Streamlit 페이지 스타일 초기화
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    iframe { border: none; }
    </style>
""", unsafe_allow_html=True)

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>3D Cyber FPS</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: 'Arial', sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; }
        
        /* HUD UI */
        #ui {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            font-weight: bold;
            font-size: 18px;
            pointer-events: none;
            z-index: 10;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 10px;
            height: 10px;
            border: 2px solid #00ffff;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 10;
            box-shadow: 0 0 8px #00ffff;
        }
        #hp-bar {
            width: 200px;
            height: 15px;
            border: 1px solid #00ffff;
            background: rgba(0, 0, 0, 0.5);
            margin-top: 5px;
        }
        #hp-fill {
            width: 100%;
            height: 100%;
            background: #00ffff;
            box-shadow: 0 0 10px #00ffff;
            transition: width 0.1s;
        }
        #blocker {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #fff;
            z-index: 20;
            cursor: pointer;
        }
        #game-over {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #ff0055;
            font-size: 48px;
            font-weight: bold;
            text-shadow: 0 0 20px #ff0055;
            display: none;
            z-index: 30;
        }
    </style>
</head>
<body>
    <div id="ui">
        SCORE: <span id="score">0</span><br>
        HEALTH
        <div id="hp-bar"><div id="hp-fill"></div></div>
    </div>
    <div id="crosshair"></div>
    <div id="game-over">SYSTEM OVERLOAD (GAME OVER)</div>

    <div id="blocker">
        <h1 style="color:#00ffff; text-shadow: 0 0 15px #00ffff; margin-bottom: 10px;">CYBER STRIKE 3D</h1>
        <p>클릭하여 시작 및 조준 (WASD: 이동 / 마우스: 회전 / 좌클릭: 사격)</p>
    </div>

    <div id="canvas-container"></div>

    <!-- Three.js & PointerLockControls 라이브러리 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>

    <script>
    // --- 기본 씬 설정 ---
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050510, 0.03);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('canvas-container').appendChild(renderer.domElement);

    const controls = new THREE.PointerLockControls(camera, document.body);
    const blocker = document.getElementById('blocker');

    blocker.addEventListener('click', () => { controls.lock(); });
    controls.addEventListener('lock', () => { blocker.style.display = 'none'; });
    controls.addEventListener('unlock', () => { if(hp > 0) blocker.style.display = 'flex'; });

    // --- 그래픽 오버헤드를 높이는 조명 설정 ---
    const ambientLight = new THREE.AmbientLight(0x222233, 1.5);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xff007f, 2);
    dirLight.position.set(20, 40, 20);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0x00ffff, 3, 30);
    pointLight.position.set(0, 5, 0);
    scene.add(pointLight);

    // --- 그리드 바닥 및 환경 연출 ---
    const gridHelper = new THREE.GridHelper(200, 100, 0x00ffff, 0x111122);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    const floorGeo = new THREE.PlaneGeometry(200, 200);
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x050510, roughness: 0.1, metalness: 0.8 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // --- 디테일 총기 제작 (Desert Eagle 구조) ---
    const gunGroup = new THREE.Group();
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.3, metalness: 0.9 });
    const darkMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.8, metalness: 0.2 });

    // 총 몸통 & 슬라이드
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.18, 0.7), metalMat);
    body.position.set(0, 0, 0);
    gunGroup.add(body);

    const slide = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.12, 0.68), metalMat);
    slide.position.set(0, 0.05, -0.01);
    gunGroup.add(slide);

    // 총열
    const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.7, 16), metalMat);
    barrel.rotation.x = Math.PI / 2;
    barrel.position.set(0, 0.04, -0.05);
    gunGroup.add(barrel);

    // 손잡이
    const grip = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.4, 0.2), darkMat);
    grip.position.set(0, -0.2, 0.18);
    grip.rotation.x = 0.3;
    gunGroup.add(grip);

    // 총구 화염 (Muzzle Flash)
    const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
    const flash = new THREE.Mesh(new THREE.SphereGeometry(0.15, 8, 8), flashMat);
    flash.position.set(0, 0.05, -0.45);
    gunGroup.add(flash);

    camera.add(gunGroup);
    gunGroup.position.set(0.3, -0.25, -0.5);
    scene.add(camera);

    // --- 정교한 로봇 메쉬 생성 함수 ---
    function createRobot() {
        const robot = new THREE.Group();
        const armorMat = new THREE.MeshStandardMaterial({ color: 0x333344, metalness: 0.8, roughness: 0.2 });
        const jointMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.5, roughness: 0.5 });
        const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff0033 });

        // 머리
        const head = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.35, 0.35), armorMat);
        head.position.y = 1.6;
        head.castShadow = true;
        robot.add(head);

        // 로봇 눈 (센서)
        const eye = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.08, 0.1), eyeMat);
        eye.position.set(0, 1.62, 0.18);
        robot.add(eye);

        // 상체 (Torso)
        const body = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.8, 0.4), armorMat);
        body.position.y = 1.0;
        body.castShadow = true;
        robot.add(body);

        // 관절 및 팔/다리
        [-0.45, 0.45].forEach(x => {
            const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.7), jointMat);
            arm.position.set(x, 1.0, 0);
            arm.castShadow = true;
            robot.add(arm);
        });

        [-0.2, 0.2].forEach(x => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.8), jointMat);
            leg.position.set(x, 0.4, 0);
            leg.castShadow = true;
            robot.add(leg);
        });

        return robot;
    }

    // --- 게임 상태 변수 ---
    let bots = [];
    let sparks = [];
    let score = 0;
    let hp = 100;
    let isGameOver = false;

    function spawnBot() {
        if (isGameOver) return;
        const bot = createRobot();
        const angle = Math.random() * Math.PI * 2;
        const radius = 20 + Math.random() * 15;
        bot.position.set(Math.cos(angle) * radius, 0, Math.sin(angle) * radius);
        scene.add(bot);
        bots.push(bot);
    }

    for(let i=0; i<6; i++) spawnBot();

    // --- 조작 및 컨트롤 ---
    let moveF = false, moveB = false, moveL = false, moveR = false;
    const velocity = new THREE.Vector3();
    const direction = new THREE.Vector3();

    document.addEventListener('keydown', (e) => {
        if(e.code === 'KeyW') moveF = true;
        if(e.code === 'KeyS') moveB = true;
        if(e.code === 'KeyA') moveL = true;
        if(e.code === 'KeyD') moveR = true;
    });

    document.addEventListener('keyup', (e) => {
        if(e.code === 'KeyW') moveF = false;
        if(e.code === 'KeyS') moveB = false;
        if(e.code === 'KeyA') moveL = false;
        if(e.code === 'KeyD') moveR = false;
    });

    // --- 사격 및 충돌 판정 ---
    const raycaster = new THREE.Raycaster();
    let recoilOffset = 0;

    document.addEventListener('mousedown', (e) => {
        if (!controls.isLocked || isGameOver || e.button !== 0) return;

        // 반동 및 화염
        recoilOffset = 0.15;
        flashMat.opacity = 1;
        setTimeout(() => { flashMat.opacity = 0; }, 40);

        raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
        const intersects = raycaster.intersectObjects(bots, true);

        if (intersects.length > 0) {
            let hitObj = intersects[0].object;
            while (hitObj.parent && hitObj.parent !== scene) {
                hitObj = hitObj.parent;
            }

            // 스파크 파티클 생성
            createSparks(intersects[0].point);

            // 로봇 제거 및 재생성
            scene.remove(hitObj);
            bots = bots.filter(b => b !== hitObj);
            score += 100;
            document.getElementById('score').innerText = score;

            setTimeout(spawnBot, 1000);
        }
    });

    function createSparks(pos) {
        const pGeo = new THREE.BufferGeometry();
        const count = 15;
        const positions = new Float32Array(count * 3);
        const vels = [];

        for (let i = 0; i < count; i++) {
            positions[i*3] = pos.x;
            positions[i*3+1] = pos.y;
            positions[i*3+2] = pos.z;
            vels.push(new THREE.Vector3(
                (Math.random() - 0.5) * 0.3,
                (Math.random() - 0.5) * 0.3,
                (Math.random() - 0.5) * 0.3
            ));
        }

        pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const pMat = new THREE.PointsMaterial({ color: 0x00ffff, size: 0.1, transparent: true });
        const pSys = new THREE.Points(pGeo, pMat);
        scene.add(pSys);
        sparks.push({ system: pSys, vels: vels, life: 1.0 });
    }

    // --- 메인 루프 ---
    let prevTime = performance.now();

    function animate() {
        requestAnimationFrame(animate);

        const time = performance.now();
        const delta = (time - prevTime) / 1000;
        prevTime = time;

        if (controls.isLocked && !isGameOver) {
            // 플레이어 이동
            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveF) - Number(moveB);
            direction.x = Number(moveR) - Number(moveL);
            direction.normalize();

            if (moveF || moveB) velocity.z -= direction.z * 120.0 * delta;
            if (moveL || moveR) velocity.x -= direction.x * 120.0 * delta;

            controls.moveRight(-velocity.x * delta);
            controls.moveForward(-velocity.z * delta);
        }

        // 총기 반동 및 복원
        if (recoilOffset > 0) {
            gunGroup.position.z = -0.5 + recoilOffset;
            gunGroup.rotation.x = recoilOffset * 0.5;
            recoilOffset -= delta * 0.8;
        } else {
            gunGroup.position.z = -0.5;
            gunGroup.rotation.x = 0;
        }

        // 스파크 애니메이션
        sparks.forEach((sp, idx) => {
            sp.life -= delta * 3;
            const positions = sp.system.geometry.attributes.position.array;
            for (let i = 0; i < sp.vels.length; i++) {
                positions[i*3] += sp.vels[i].x;
                positions[i*3+1] += sp.vels[i].y;
                positions[i*3+2] += sp.vels[i].z;
            }
            sp.system.geometry.attributes.position.needsUpdate = true;
            sp.system.material.opacity = sp.life;

            if (sp.life <= 0) {
                scene.remove(sp.system);
                sparks.splice(idx, 1);
            }
        });

        // 봇 AI (추격) 및 공격
        bots.forEach(b => {
            let dir = new THREE.Vector3().subVectors(camera.position, b.position);
            dir.y = 0;
            let dist = dir.length();

            if (dist > 1.2) {
                dir.normalize().multiplyScalar(0.05);
                b.position.add(dir);
            }

            b.lookAt(camera.position.x, b.position.y, camera.position.z);

            // 데미지 계산
            if (dist < 1.8 && !isGameOver) {
                hp -= 0.3;
                document.getElementById('hp-fill').style.width = Math.max(0, hp) + '%';

                if (hp <= 0) {
                    isGameOver = true;
                    document.getElementById('game-over').style.display = 'block';
                    controls.unlock();
                }
            }
        });

        renderer.render(scene, camera);
    }

    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    </script>
</body>
</html>
"""

components.html(game_html, height=800, scrolling=False)
