import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="VALORANT Web Edition", page_icon="🎯", layout="wide")

st.title("🎯 VALORANT 3D Web Edition")

# 클릭 안내 화면 제거 & 즉시 실행 버전
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; overflow: hidden; font-family: 'Arial', sans-serif; background: #111; color: white; }
        #canvas-container { width: 100vw; height: 85vh; position: relative; }
        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 8px; height: 8px; background: #00ffcc;
            transform: translate(-50%, -50%); border-radius: 50%;
            pointer-events: none; z-index: 10;
        }
        #hud {
            position: absolute; bottom: 20px; left: 20px;
            font-size: 20px; font-weight: bold; background: rgba(0,0,0,0.6);
            padding: 15px; border-radius: 8px; border: 1px solid #333;
            pointer-events: none; z-index: 10;
        }
        #guide {
            position: absolute; top: 15px; right: 20px;
            background: rgba(0,0,0,0.7); padding: 10px 15px; border-radius: 6px;
            font-size: 14px; pointer-events: none; z-index: 10; border: 1px solid #444;
        }
    </style>
</head>
<body>
    <div id="canvas-container">
        <div id="crosshair"></div>
        <div id="guide">
            <b>조작법:</b> W,A,S,D 이동 | 마우스 에임 | 좌클릭 사격 | E 대시 | C 연막
        </div>
        <div id="hud">
            <div>HP: <span id="hp" style="color:#00ffcc;">100</span> | SHIELD: <span id="shield" style="color:#00aaff;">50</span></div>
            <div>AMMO: <span id="ammo" style="color:#ffcc00;">25 / 75</span></div>
            <div style="font-size: 16px; margin-top: 5px; color: #ff4655;">남은 적: <span id="enemies">3</span></div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let camera, scene, renderer;
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
        let prevTime = performance.now();
        const velocity = new THREE.Vector3();
        const direction = new THREE.Vector3();
        
        let hp = 100, ammo = 25, totalAmmo = 75;
        let enemies = [];
        let eCooldown = false;

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            scene.fog = new THREE.Fog(0x1a1a2e, 0, 75);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / (window.innerHeight * 0.85), 0.1, 1000);
            camera.position.y = 1.6;

            // 조명
            const light = new THREE.HemisphereLight(0xeeeeff, 0x777788, 0.75);
            light.position.set(0.5, 1, 0.75);
            scene.add(light);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);

            // 바닥
            const floorGeo = new THREE.PlaneGeometry(100, 100);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x333344 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            scene.add(floor);

            // 엄폐물
            const boxGeo = new THREE.BoxGeometry(3, 3, 3);
            const boxMat = new THREE.MeshStandardMaterial({ color: 0x8b5a2b });
            [[5, 1.5, -10], [-5, 1.5, -15], [10, 1.5, -20], [-10, 1.5, -5]].forEach(pos => {
                const box = new THREE.Mesh(boxGeo, boxMat);
                box.position.set(...pos);
                scene.add(box);
            });

            // 적 생성
            createEnemy(0, 1.5, -15);
            createEnemy(8, 1.5, -25);
            createEnemy(-8, 1.5, -20);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight * 0.85);
            const container = document.getElementById('canvas-container');
            container.appendChild(renderer.domElement);

            // 이벤트 리스너 (시작 클릭 화면 없이 바로 반응)
            container.addEventListener('mousemove', onMouseMove);
            window.addEventListener('keydown', onKeyDown);
            window.addEventListener('keyup', onKeyUp);
            container.addEventListener('mousedown', onMouseDown);

            animate();
        }

        function createEnemy(x, y, z) {
            const group = new THREE.Group();
            
            const bodyGeo = new THREE.CylinderGeometry(0.5, 0.5, 2, 16);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0xff4655 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            group.add(body);

            const headGeo = new THREE.SphereGeometry(0.35, 16, 16);
            const headMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 1.3;
            group.add(head);

            group.position.set(x, y, z);
            group.userData = { hp: 100, head: head };
            scene.add(group);
            enemies.push(group);
        }

        let pitch = 0, yaw = 0;
        function onMouseMove(event) {
            // 화면 위에서 마우스를 움직이면 즉시 에임 회전
            if (event.buttons === 1 || event.buttons === 0) {
                yaw -= event.movementX * 0.003;
                pitch -= event.movementY * 0.003;
                pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, pitch));
                
                camera.rotation.identity();
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;
                camera.rotation.order = "YXZ";
            }
        }

        function onKeyDown(e) {
            switch (e.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyD': moveRight = true; break;
                case 'KeyR': reload(); break;
                case 'KeyE': useDash(); break;
                case 'KeyC': useSmoke(); break;
            }
        }

        function onKeyUp(e) {
            switch (e.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyD': moveRight = false; break;
            }
        }

        function onMouseDown(e) {
            if (ammo <= 0) return;
            ammo--;
            document.getElementById('ammo').innerText = `${ammo} / ${totalAmmo}`;

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

            const intersects = raycaster.intersectObjects(scene.children, true);
            if (intersects.length > 0) {
                let hitObj = intersects[0].object;
                let parentGroup = hitObj.parent;

                if (enemies.includes(parentGroup)) {
                    let isHead = (hitObj === parentGroup.userData.head);
                    let dmg = isHead ? 150 : 40;
                    parentGroup.userData.hp -= dmg;

                    if (parentGroup.userData.hp <= 0) {
                        scene.remove(parentGroup);
                        enemies = enemies.filter(e => e !== parentGroup);
                        document.getElementById('enemies').innerText = enemies.length;
                    }
                }
            }
        }

        function useDash() {
            if (eCooldown) return;
            eCooldown = true;
            const dashDir = new THREE.Vector3();
            camera.getWorldDirection(dashDir);
            camera.position.addScaledVector(dashDir, 8);
            setTimeout(() => { eCooldown = false; }, 3000);
        }

        function useSmoke() {
            const smokeGeo = new THREE.SphereGeometry(3, 16, 16);
            const smokeMat = new THREE.MeshBasicMaterial({ color: 0xcccccc, transparent: true, opacity: 0.6 });
            const smoke = new THREE.Mesh(smokeGeo, smokeMat);
            
            const dir = new THREE.Vector3();
            camera.getWorldDirection(dir);
            smoke.position.copy(camera.position).addScaledVector(dir, 6);
            scene.add(smoke);

            setTimeout(() => { scene.remove(smoke); }, 5000);
        }

        function reload() {
            setTimeout(() => {
                ammo = 25;
                document.getElementById('ammo').innerText = `${ammo} / ${totalAmmo}`;
            }, 1000);
        }

        function animate() {
            requestAnimationFrame(animate);
            const time = performance.now();
            const delta = (time - prevTime) / 1000;

            velocity.x -= velocity.x * 10.0 * delta;
            velocity.z -= velocity.z * 10.0 * delta;

            direction.z = Number(moveForward) - Number(moveBackward);
            direction.x = Number(moveRight) - Number(moveLeft);
            direction.normalize();

            if (moveForward || moveBackward) velocity.z -= direction.z * 150.0 * delta;
            if (moveLeft || moveRight) velocity.x -= direction.x * 150.0 * delta;

            const camDir = new THREE.Vector3();
            camera.getWorldDirection(camDir);
            camDir.y = 0;
            camDir.normalize();

            const sideDir = new THREE.Vector3().crossVectors(camera.up, camDir).normalize();

            camera.position.addScaledVector(camDir, -velocity.z * delta * 0.1);
            camera.position.addScaledVector(sideDir, velocity.x * delta * 0.1);

            prevTime = time;
            renderer.render(scene, camera);
        }

        init();
    </script>
</body>
</html>
"""

components.html(game_html, height=720)
