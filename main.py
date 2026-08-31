import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🚀 Streamlit Web FPS",
    page_icon="💥",
    layout="wide"
)

st.title("💥 Neon Strike 3D (Streamlit Web FPS)")
st.caption("버튼 클릭 후 화면이 반응하지 않으면, 화면 내부 아무 곳이나 1회 클릭 후 다시 시도해보세요.")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #000;
            font-family: 'Arial', sans-serif;
            user-select: none;
        }

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

        #blocker {
            position: absolute;
            width: 100%;
            height: 100%;
            background-color: rgba(5, 5, 20, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 20;
        }
        
        #instructions {
            text-align: center;
            border: 2px solid #00ffcc;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 0 30px rgba(0, 255, 204, 0.3);
            background: rgba(10, 10, 30, 0.85);
            max-width: 450px;
        }

        #start-btn {
            display: inline-block;
            margin-top: 25px;
            padding: 15px 35px;
            font-size: 22px;
            font-weight: bold;
            color: #000;
            background: linear-gradient(45deg, #00ffcc, #00bfff);
            border: none;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 0 15px #00ffcc;
        }

        h1 { margin: 0 0 15px 0; color: #00ffcc; text-shadow: 0 0 10px #00ffcc; font-size: 28px; }
        p { font-size: 16px; line-height: 1.7; color: #d0d0d0; }
        #err-msg { color: #ff3366; font-size: 14px; margin-top: 10px; display: none; }
    </style>
</head>
<body>

    <div id="crosshair"></div>
    <div id="ui">🎯 SCORE: <span id="score">0</span></div>

    <div id="blocker">
        <div id="instructions">
            <h1>💥 NEON STRIKE 3D 💥</h1>
            <p>
                🕹️ <b>이동:</b> W, A, S, D<br>
                🔫 <b>사격:</b> 마우스 왼쪽 클릭<br>
                👀 <b>시점 전환:</b> 마우스 이동<br>
                🛑 <b>일시정지:</b> ESC
            </p>
            <button id="start-btn">🎮 게임 시작</button>
            <div id="err-msg">⚠️ 마우스 고정에 실패했습니다. 박스 내부를 클릭한 뒤 다시 눌러주세요.</div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>

    <script>
        let scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050515);
        scene.fog = new THREE.FogExp2(0x050515, 0.015);

        let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        let controls = new THREE.PointerLockControls(camera, document.body);
        let blocker = document.getElementById('blocker');
        let startBtn = document.getElementById('start-btn');
        let errMsg = document.getElementById('err-msg');

        startBtn.addEventListener('click', () => {
            try {
                controls.lock();
            } catch (e) {
                errMsg.style.display = 'block';
            }
        });

        controls.addEventListener('lock', () => {
            blocker.style.display = 'none';
            errMsg.style.display = 'none';
        });

        controls.addEventListener('unlock', () => {
            blocker.style.display = 'flex';
        });

        // 예외 처리
        controls.addEventListener('error', () => {
            errMsg.style.display = 'block';
        });

        scene.add(controls.getObject());

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

        let ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        scene.add(ambientLight);

        let dirLight = new THREE.DirectionalLight(0xff00ff, 0.8);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);

        let gridHelper = new THREE.GridHelper(200, 50, 0x00ffcc, 0xff00ff);
        scene.add(gridHelper);

        let targets = [];
        let score = 0;

        for (let i = 0; i < 25; i++) {
            let wallGeo = new THREE.BoxGeometry(4, Math.random() * 8 + 4, 4);
            let wallMat = new THREE.MeshStandardMaterial({ color: 0x111122 });
            let wall = new THREE.Mesh(wallGeo, wallMat);
            wall.position.set((Math.random() - 0.5) * 120, wallGeo.parameters.height / 2, (Math.random() - 0.5) * 120);
            scene.add(wall);
        }

        function createTarget() {
            let geo = new THREE.SphereGeometry(1.5, 16, 16);
            let mat = new THREE.MeshStandardMaterial({ color: 0xff0055, emissive: 0xff0055, emissiveIntensity: 0.6 });
            let target = new THREE.Mesh(geo, mat);
            target.position.set((Math.random() - 0.5) * 80, Math.random() * 3 + 2, (Math.random() - 0.5) * 80);
            scene.add(target);
            targets.push(target);
        }

        for (let i = 0; i < 10; i++) createTarget();

        let gunGeo = new THREE.BoxGeometry(0.3, 0.3, 1);
        let gunMat = new THREE.MeshStandardMaterial({ color: 0x333333 });
        let gun = new THREE.Mesh(gunGeo, gunMat);
        gun.position.set(0.4, -0.4, -0.8);
        camera.add(gun);

        let raycaster = new THREE.Raycaster();

        document.addEventListener('mousedown', (e) => {
            if (!controls.isLocked || e.button !== 0) return;

            gun.position.z = -0.6;
            setTimeout(() => gun.position.z = -0.8, 50);

            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            let intersects = raycaster.intersectObjects(targets);

            if (intersects.length > 0) {
                let hitTarget = intersects[0].object;
                scene.remove(hitTarget);
                targets = targets.filter(t => t !== hitTarget);
                score += 100;
                document.getElementById('score').innerText = score;
                setTimeout(createTarget, 1000);
            }
        });

        controls.getObject().position.y = 2;

        function animate() {
            requestAnimationFrame(animate);
            let time = performance.now();
            let delta = (time - prevTime) / 1000;

            if (controls.isLocked) {
                velocity.x -= velocity.x * 10.0 * delta;
                velocity.z -= velocity.z * 10.0 * delta;

                direction.z = Number(moveForward) - Number(moveBackward);
                direction.x = Number(moveRight) - Number(moveLeft);
                direction.normalize();

                if (moveForward || moveBackward) velocity.z -= direction.z * 40.0 * delta;
                if (moveLeft || moveRight) velocity.x -= direction.x * 40.0 * delta;

                controls.moveRight(-velocity.x * delta);
                controls.moveForward(-velocity.z * delta);
            }

            targets.forEach((target, index) => {
                target.position.y += Math.sin(time * 0.003 + index) * 0.01;
            });

            prevTime = time;
            renderer.render(scene, camera);
        }

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    </script>
</body>
</html>
"""

# scrolling=True 또는 allow_scripts 기본 탑재
components.html(game_html, height=720, scrolling=False)
