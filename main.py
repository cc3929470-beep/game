import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Web FPS", layout="wide")
st.title("💥 Neon Strike 3D (Streamlit 호환 버전)")
st.caption("🎮 조작법: 마우스 좌클릭 드래그 = 시점 전환 | 마우스 우클릭 = 총 쏘기 | WASD = 이동")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; user-select: none; }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 12px; height: 12px;
            transform: translate(-50%, -50%); pointer-events: none; z-index: 10;
        }
        #crosshair::before, #crosshair::after { content: ''; position: absolute; background: #00ffcc; }
        #crosshair::before { top: 5px; left: 0; width: 12px; height: 2px; }
        #crosshair::after { top: 0; left: 5px; width: 2px; height: 12px; }
        #ui { position: absolute; top: 20px; left: 20px; color: #fff; font-size: 20px; font-weight: bold; z-index: 10; }
    </style>
</head>
<body>
    <div id="crosshair"></div>
    <div id="ui">🎯 SCORE: <span id="score">0</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        let scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050515);
        scene.fog = new THREE.FogExp2(0x050515, 0.015);

        let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        let renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // 드래그 기반 OrbitControls 적용
        let controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.enableZoom = false;
        camera.position.set(0, 2, 0.1);
        controls.target.set(0, 2, -10);

        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;

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

        scene.add(new THREE.AmbientLight(0xffffff, 0.3));
        let dirLight = new THREE.DirectionalLight(0xff00ff, 0.8);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);
        scene.add(new THREE.GridHelper(200, 50, 0x00ffcc, 0xff00ff));

        let targets = [];
        let score = 0;

        for (let i = 0; i < 25; i++) {
            let wallGeo = new THREE.BoxGeometry(4, Math.random() * 8 + 4, 4);
            let wall = new THREE.Mesh(wallGeo, new THREE.MeshStandardMaterial({ color: 0x111122 }));
            wall.position.set((Math.random() - 0.5) * 120, wallGeo.parameters.height / 2, (Math.random() - 0.5) * 120);
            scene.add(wall);
        }

        function createTarget() {
            let target = new THREE.Mesh(
                new THREE.SphereGeometry(1.5, 16, 16),
                new THREE.MeshStandardMaterial({ color: 0xff0055, emissive: 0xff0055, emissiveIntensity: 0.6 })
            );
            target.position.set((Math.random() - 0.5) * 80, Math.random() * 3 + 2, (Math.random() - 0.5) * 80);
            scene.add(target);
            targets.push(target);
        }

        for (let i = 0; i < 10; i++) createTarget();

        let gun = new THREE.Mesh(
            new THREE.BoxGeometry(0.3, 0.3, 1),
            new THREE.MeshStandardMaterial({ color: 0x333333 })
        );
        gun.position.set(0.4, -0.4, -0.8);
        camera.add(gun);
        scene.add(camera);

        let raycaster = new THREE.Raycaster();

        // 우클릭 방지 및 우클릭/우측 버튼 사격 처리
        window.addEventListener('contextmenu', e => e.preventDefault());
        document.addEventListener('mousedown', (e) => {
            // 우클릭(button 2) 또는 드래그가 아닌 단순 사격 처리
            if (e.button === 2 || e.button === 0) {
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
            }
        });

        function animate() {
            requestAnimationFrame(animate);

            let moveSpeed = 0.2;
            let dir = new THREE.Vector3();
            camera.getWorldDirection(dir);
            dir.y = 0;
            dir.normalize();

            let sideDir = new THREE.Vector3(-dir.z, 0, dir.x);

            if (moveForward) { camera.position.addScaledVector(dir, moveSpeed); controls.target.addScaledVector(dir, moveSpeed); }
            if (moveBackward) { camera.position.addScaledVector(dir, -moveSpeed); controls.target.addScaledVector(dir, -moveSpeed); }
            if (moveLeft) { camera.position.addScaledVector(sideDir, -moveSpeed); controls.target.addScaledVector(sideDir, -moveSpeed); }
            if (moveRight) { camera.position.addScaledVector(sideDir, moveSpeed); controls.target.addScaledVector(sideDir, moveSpeed); }

            controls.update();
            renderer.render(scene, camera);
        }

        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=720)
