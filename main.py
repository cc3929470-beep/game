import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Web FPS", layout="wide")
st.title("💥 Neon Strike 3D (y축 높이 고정 버전)")
st.caption("🎮 조작법: 마우스 드래그 = 시점 전환 | 클릭 = 사격 | WASD = 평면 이동 ($y$축 높이 고정)")

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

        let controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enablePan = false;
        controls.enableZoom = false;
        
        // 고정시킬 눈높이 (y축 고정값)
        const PLAYER_HEIGHT = 2.0;

        camera.position.set(0, PLAYER_HEIGHT, 0.1);
        controls.target.set(0, PLAYER_HEIGHT, -10);

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
        scene.add(new THREE.GridHelper(200
