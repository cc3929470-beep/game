<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Neon Strike 3D - Web FPS</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #000;
            font-family: 'Arial', sans-serif;
            user-select: none;
        }

        /* 크로스헤어 (조준점) */
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 10;
        }
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: #00ffcc;
            box-shadow: 0 0 8px #00ffcc;
        }
        #crosshair::before { top: 5px; left: 0; width: 12px; height: 2px; }
        #crosshair::after { top: 0; left: 5px; width: 2px; height: 12px; }

        /* UI 오버레이 */
        #ui {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #fff;
            font-size: 20px;
            font-weight: bold;
            text-shadow: 0 0 10px #00ffcc;
            z-index: 10;
        }

        /* 게임 시작 안내 스크린 */
        #blocker {
            position: absolute;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 20;
        }
        #instructions {
            text-align: center;
            cursor: pointer;
            border: 3px solid #00ffcc;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 20px #00ffcc;
            background: rgba(0,0,0,0.6);
        }
        h1 { margin: 0 0 10px 0; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }
        p { font-size: 18px; line-height: 1.6; }
    </style>
</head>
<body>

    <div id="crosshair"></div>
    
    <div id="ui">
        🎯 SCORE: <span id="score">0</span>
    </div>

    <div id="blocker">
        <div id="instructions">
            <h1>💥 NEON STRIKE 3D 💥</h1>
            <p>화면을 클릭하여 전투 시작!</p>
            <p>
                🕹️ <b>이동:</b> W, A, S, D<br>
                🔫 <b>사격:</b> 마우스 왼쪽 클릭<br>
                👀 <b>시점 전환:</b> 마우스 이동<br>
                🛑 <b>일시정지:</b> ESC
            </p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>

    <script>
        // -------------------------------------------------------------
        // 1. 기본 씬 설정 및 카메라, 렌더러 생성
        // -------------------------------------------------------------
        let scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050515);
        scene.fog = new THREE.FogExp2(0x050515, 0.015);

        let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        // -------------------------------------------------------------
        // 2. 조작계 (PointerLockControls) 설정
        // -------------------------------------------------------------
        let controls = new THREE.PointerLockControls(camera, document.body);
        let blocker = document.getElementById('blocker');

        blocker.addEventListener('click', () => controls.lock());
        controls.addEventListener('lock', () => blocker.style.display = 'none');
        controls.addEventListener('unlock', () => blocker.style.display = 'flex');

        scene.add(controls.getObject());

        // 이동 관련 변수
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let velocity = new THREE.Vector3();
        let direction = new THREE.Vector3();
        let prevTime = performance.now();

        document.addEventListener('keydown', (e) => {
            switch (e.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyD': moveRight = true; break;
            }
        });

        document.addEventListener('keyup', (e) => {
            switch (e.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyD': moveRight = false; break;
            }
        });

        // -------------------------------------------------------------
        // 3. 조명 및 분위기 연출 (네온/サイバーパンク 분위기)
        // -------------------------------------------------------------
        let ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
        scene.add(ambientLight);

        let dirLight = new THREE.DirectionalLight(0xff00ff, 0.8);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);

        // 바닥 격자 및 장애물 생성
        let gridHelper = new THREE.GridHelper(200, 50, 0x00ffcc, 0xff00ff);
        scene.add(gridHelper);

        let targets = [];
        let score = 0;

        // 벽 및 구조물 배치
        for (let i = 0; i < 30; i++) {
            let wallGeo = new THREE.BoxGeometry(4, Math.random() * 8 + 4, 4);
            let wallMat = new THREE.MeshStandardMaterial({ color: 0x111122, roughness: 0.3 });
            let wall = new THREE.Mesh(wallGeo, wallMat);
            wall.position.set((Math.random() - 0.5) * 120, wallGeo.parameters.height / 2, (Math.random() - 0.5) * 120);
            scene.add(wall);
        }

        // Target (적/타겟 생성 함수)
        function createTarget() {
            let geo = new THREE.SphereGeometry(1.5, 16, 16);
            let mat = new THREE.MeshStandardMaterial({ 
                color: 0xff0055, 
                emissive: 0xff0055, 
                emissiveIntensity: 0.6 
            });
            let target = new THREE.Mesh(geo, mat);
            target.position.set((Math.random() - 0.5) * 80, Math.random() * 3 + 2, (Math.random() - 0.5) * 80);
            scene.add(target);
            targets.push(target);
        }

        for (let i = 0; i < 10; i++) createTarget();

        // -------------------------------------------------------------
        // 4. 총기 및 사격 기능 (Raycaster)
        // -------------------------------------------------------------
        // 총기 3D 모형 (1인칭 손)
        let gunGeo = new THREE.BoxGeometry(0.3, 0.3, 1);
        let gunMat = new THREE.MeshStandardMaterial({ color: 0x333333, metalness: 0.8 });
        let gun = new THREE.Mesh(gunGeo, gunMat);
        gun.position.set(0.4, -0.4, -0.8);
        camera.add(gun);

        let raycaster = new THREE.Raycaster();

        document.addEventListener('mousedown', (e) => {
            if (!controls.isLocked || e.button !== 0) return;

            // 사격 이펙트 (총 반동)
            gun.position.z = -0.6;
            setTimeout(() => gun.position.z = -0.8, 50);

            // 화면 중앙(조준점) 방향으로 레이저 발사
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let intersects = raycaster.intersectObjects(targets);

            if (intersects.length > 0) {
                let hitTarget = intersects[0].object;
                
                // 파괴 피드백 (이펙트)
                scene.remove(hitTarget);
                targets = targets.filter(t => t !== hitTarget);

                score += 100
