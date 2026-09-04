import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SNIPER: ULTRA URBAN WARZONE",
    layout="wide"
)

st.title("🎯 SNIPER: ULTRA URBAN WARZONE")
st.caption(
    "🎮 조작법: [화면 클릭] 포커스 | WASD = 이동 | Shift = 달리기 | "
    "Space = 점프 | [1, 2, 3] = 총기 변경 | 마우스 드래그 = 시선 전환 | "
    "좌클릭 = 사격 | 우클릭 = ADS 조준"
)

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">

    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #02060b;
            font-family: 'Segoe UI', sans-serif;
            user-select: none;
        }

        body {
            position: relative;
        }

        canvas {
            display: block;
        }

        /* =========================
           CROSSHAIR
        ========================= */

        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 6px;
            height: 6px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 20;
            background: #00f5a0;
            border-radius: 50%;
            box-shadow:
                0 0 8px #00f5a0,
                0 0 18px rgba(0,245,160,0.8);
        }

        /* =========================
           SCOPE
        ========================= */

        #scope-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 19;
            display: none;

            background:
                radial-gradient(
                    circle,
                    transparent 24%,
                    rgba(0,0,0,0.45) 36%,
                    rgba(0,0,0,0.92) 54%,
                    #000 100%
                );
        }

        #scope-overlay::before,
        #scope-overlay::after {
            content: '';
            position: absolute;
            background: rgba(0,245,160,0.85);
            box-shadow: 0 0 5px rgba(0,245,160,0.6);
        }

        #scope-overlay::before {
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
        }

        #scope-overlay::after {
            top: 0;
            left: 50%;
            width: 1px;
            height: 100%;
        }

        /* =========================
           RAIN VIGNETTE
        ========================= */

        #rain-vignette {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 8;

            background:
                radial-gradient(
                    ellipse at center,
                    transparent 30%,
                    rgba(10,20,35,0.10) 58%,
                    rgba(0,0,0,0.42) 100%
                );
        }

        /* =========================
           HUD
        ========================= */

        #hud {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #f8fafc;
            font-size: 18px;
            font-weight: 800;
            z-index: 25;
            letter-spacing: 2px;

            background: rgba(8,15,27,0.84);
            padding: 12px 22px;

            border-left: 5px solid #ff4655;

            box-shadow:
                0 8px 32px rgba(0,0,0,0.75),
                0 0 20px rgba(255,70,85,0.08);

            backdrop-filter: blur(10px);
        }

        #gun-hud {
            position: absolute;
            bottom: 30px;
            right: 30px;

            color: #00f5a0;
            font-size: 22px;
            font-weight: 900;

            z-index: 25;

            background: rgba(8,15,27,0.86);
            padding: 10px 20px;

            border-radius: 6px;
            border: 1px solid #00f5a0;

            box-shadow:
                0 0 15px rgba(0,245,160,0.3),
                inset 0 0 20px rgba(0,245,160,0.04);

            backdrop-filter: blur(10px);
        }

        /* =========================
           HP BAR
        ========================= */

        #hp-bar {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);

            width: 340px;
            height: 14px;

            background: rgba(8,15,27,0.85);

            z-index: 25;

            border: 2px solid #ff4655;
            border-radius: 4px;

            box-shadow:
                0 0 20px rgba(255,70,85,0.5);
        }

        #hp-fill {
            width: 100%;
            height: 100%;

            background:
                linear-gradient(
                    90deg,
                    #00f5a0,
                    #00d2ff
                );

            box-shadow:
                0 0 12px rgba(0,245,160,0.55);

            transition: width 0.1s;
        }

        /* =========================
           HIT FEEDBACK
        ========================= */

        #hit-feedback {
            position: absolute;
            top: 40%;
            left: 50%;

            transform: translate(-50%, -50%);

            color: #ffcc00;
            font-size: 28px;
            font-weight: 900;

            pointer-events: none;
            z-index: 30;

            opacity: 0;

            transition: opacity 0.2s;

            text-shadow:
                0 0 10px rgba(0,0,0,0.9),
                0 0 25px currentColor;
        }

        /* =========================
           GAME OVER
        ========================= */

        #game-over {
            position: absolute;
            top: 50%;
            left: 50%;

            transform: translate(-50%, -50%);

            color: #ff4655;
            font-size: 42px;
            font-weight: 900;

            text-align: center;

            display: none;
            z-index: 50;

            text-shadow:
                0 0 25px rgba(255,70,85,0.9);

            background: rgba(8,15,27,0.95);

            padding: 40px;

            border-radius: 8px;
            border: 1px solid #ff4655;

            box-shadow:
                0 0 50px rgba(0,0,0,0.9),
                inset 0 0 30px rgba(255,70,85,0.05);

            backdrop-filter: blur(12px);
        }
    </style>
</head>

<body>

    <div id="crosshair"></div>

    <div id="scope-overlay"></div>

    <div id="rain-vignette"></div>

    <div id="hud">
        ELIMINATIONS:
        <span id="score" style="color:#ff4655;">0</span>
    </div>

    <div id="gun-hud">
        WEAPON:
        <span id="gun-name">M200 HEAVY</span>
    </div>

    <div id="hp-bar">
        <div id="hp-fill"></div>
    </div>

    <div id="hit-feedback"></div>

    <div id="game-over">
        MISSION FAILED
        <br>
        <span style="font-size:18px; color:#fff;">
            클릭하여 다시 시작
        </span>
    </div>


    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>

        /* ============================================================
           BASIC SETTINGS
        ============================================================ */

        window.focus();

        document.addEventListener(
            'contextmenu',
            event => event.preventDefault()
        );


        /* ============================================================
           PROCEDURAL TEXTURES
        ============================================================ */

        function generateProceduralTexture(type) {

            let canvas = document.createElement('canvas');

            canvas.width = 1024;
            canvas.height = 1024;

            let ctx = canvas.getContext('2d');

            if (type === 'concrete') {

                ctx.fillStyle = '#3a4454';
                ctx.fillRect(0, 0, 1024, 1024);

                for (let i = 0; i < 85000; i++) {

                    let x = Math.random() * 1024;
                    let y = Math.random() * 1024;

                    let v = Math.random() * 60;

                    ctx.fillStyle =
                        `rgba(${v},${v},${v},0.14)`;

                    ctx.fillRect(x, y, 2, 2);
                }

                ctx.strokeStyle =
                    'rgba(15,15,20,0.55)';

                ctx.lineWidth = 2;

                for (let i = 0; i < 16; i++) {

                    ctx.beginPath();

                    ctx.moveTo(
                        Math.random() * 1024,
                        Math.random() * 1024
                    );

                    ctx.lineTo(
                        Math.random() * 1024,
                        Math.random() * 1024
                    );

                    ctx.stroke();
                }

            } else if (type === 'asphalt') {

                ctx.fillStyle = '#151c27';
                ctx.fillRect(0, 0, 1024, 1024);

                for (let i = 0; i < 140000; i++) {

                    let x = Math.random() * 1024;
                    let y = Math.random() * 1024;

                    let c =
                        Math.floor(
                            Math.random() * 75 + 25
                        );

                    ctx.fillStyle =
                        `rgb(${c},${c},${c})`;

                    ctx.fillRect(x, y, 1, 1);
                }

                /* 젖은 아스팔트의 미세한 얼룩 */

                for (let i = 0; i < 1200; i++) {

                    let x = Math.random() * 1024;
                    let y = Math.random() * 1024;

                    let w =
                        5 + Math.random() * 35;

                    let h =
                        2 + Math.random() * 12;

                    ctx.fillStyle =
                        'rgba(130,150,170,0.10)';

                    ctx.fillRect(
                        x,
                        y,
                        w,
                        h
                    );
                }

            } else if (type === 'rust') {

                ctx.fillStyle = '#27272a';
                ctx.fillRect(0, 0, 1024, 1024);

                for (let i = 0; i < 50000; i++) {

                    let x = Math.random() * 1024;
                    let y = Math.random() * 1024;

                    ctx.fillStyle =
                        `rgba(
                            ${120 + Math.random() * 80},
                            ${30 + Math.random() * 40},
                            10,
                            0.25
                        )`;

                    ctx.fillRect(
                        x,
                        y,
                        3,
                        3
                    );
                }
            }

            let texture =
                new THREE.CanvasTexture(canvas);

            texture.wrapS =
                THREE.RepeatWrapping;

            texture.wrapT =
                THREE.RepeatWrapping;

            texture.anisotropy = 8;

            return texture;
        }


        let concreteTex =
            generateProceduralTexture('concrete');

        concreteTex.repeat.set(2, 4);


        let asphaltTex =
            generateProceduralTexture('asphalt');

        asphaltTex.repeat.set(8, 8);


        let rustTex =
            generateProceduralTexture('rust');


        /* ============================================================
           SCENE
        ============================================================ */

        let scene = new THREE.Scene();

        /* 비 오는 날의 차가운 안개 */

        scene.fog =
            new THREE.FogExp2(
                0x263342,
                0.022
            );


        /* ============================================================
           SKY
        ============================================================ */

        let skyGeo =
            new THREE.SphereGeometry(
                400,
                48,
                24
            );


        let skyMat =
            new THREE.ShaderMaterial({

                vertexShader: `
                    varying vec3 vWorldPosition;

                    void main() {

                        vec4 worldPosition =
                            modelMatrix *
                            vec4(position, 1.0);

                        vWorldPosition =
                            worldPosition.xyz;

                        gl_Position =
                            projectionMatrix *
                            viewMatrix *
                            worldPosition;
                    }
                `,

                fragmentShader: `
                    uniform vec3 topColor;
                    uniform vec3 bottomColor;

                    varying vec3 vWorldPosition;

                    void main() {

                        float h =
                            normalize(
                                vWorldPosition + 10.0
                            ).y;

                        gl_FragColor =
                            vec4(
                                mix(
                                    bottomColor,
                                    topColor,
                                    max(h, 0.0)
                                ),
                                1.0
                            );
                    }
                `,

                uniforms: {

                    topColor: {
                        value:
                            new THREE.Color(
                                0x05080d
                            )
                    },

                    bottomColor: {
                        value:
                            new THREE.Color(
                                0x475569
                            )
                    }
                },

                side:
                    THREE.BackSide
            });

        scene.add(
            new THREE.Mesh(
                skyGeo,
                skyMat
            )
        );


        /* ============================================================
           CAMERA
        ============================================================ */

        let camera =
            new THREE.PerspectiveCamera(
                65,
                window.innerWidth /
                window.innerHeight,
                0.1,
                1000
            );


        /* ============================================================
           HIGH QUALITY RENDERER
        ============================================================ */

        let renderer =
            new THREE.WebGLRenderer({

                antialias: true,

                powerPreference:
                    'high-performance',

                logarithmicDepthBuffer:
                    true
            });


        renderer.setSize(
            window.innerWidth,
            window.innerHeight
        );


        renderer.setPixelRatio(
            Math.min(
                window.devicePixelRatio,
                2.5
            )
        );


        renderer.shadowMap.enabled = true;

        renderer.shadowMap.type =
            THREE.PCFSoftShadowMap;


        renderer.toneMapping =
            THREE.ACESFilmicToneMapping;


        renderer.toneMappingExposure =
            1.35;


        renderer.outputEncoding =
            THREE.sRGBEncoding;


        document.body.appendChild(
            renderer.domElement
        );


        /* ============================================================
           PLAYER
        ============================================================ */

        const PLAYER_HEIGHT = 2.0;

        const PLAYER_RADIUS = 0.8;

        camera.position.set(
            0,
            PLAYER_HEIGHT,
            0
        );


        let yVelocity = 0;

        let isGrounded = true;

        const JUMP_FORCE = 0.14;

        const GRAVITY = 0.009;


        let pitch = 0;

        let yaw = 0;

        let isMouseDown = false;

        let prevMousePos = {
            x: 0,
            y: 0
        };


        /* ============================================================
           MOUSE LOOK
        ============================================================ */

        document.addEventListener(
            'mousedown',
            (e) => {

                if (
                    e.button === 0 ||
                    e.button === 2
                ) {

                    isMouseDown = true;

                    prevMousePos = {
                        x: e.clientX,
                        y: e.clientY
                    };
                }
            }
        );


        document.addEventListener(
            'mouseup',
            () => {

                isMouseDown = false;
            }
        );


        document.addEventListener(
            'mousemove',
            (e) => {

                if (!isMouseDown)
                    return;

                let deltaX =
                    e.clientX -
                    prevMousePos.x;

                let deltaY =
                    e.clientY -
                    prevMousePos.y;


                prevMousePos = {
                    x: e.clientX,
                    y: e.clientY
                };


                let sensitivity =
                    0.003;


                yaw -=
                    deltaX *
                    sensitivity;


                pitch -=
                    deltaY *
                    sensitivity;


                let maxPitch =
                    Math.PI / 2 -
                    0.01;


                pitch =
                    Math.max(
                        -maxPitch,
                        Math.min(
                            maxPitch,
                            pitch
                        )
                    );


                let euler =
                    new THREE.Euler(
                        pitch,
                        yaw,
                        0,
                        'YXZ'
                    );


                camera.quaternion.setFromEuler(
                    euler
                );
            }
        );


        /* ============================================================
           LIGHTING
        ============================================================ */

        scene.add(
            new THREE.AmbientLight(
                0x64748b,
                0.7
            )
        );


        let sun =
            new THREE.DirectionalLight(
                0x9bb7d3,
                1.6
            );


        sun.position.set(
            60,
            80,
            40
        );


        sun.castShadow = true;


        sun.shadow.mapSize.width =
            4096;

        sun.shadow.mapSize.height =
            4096;


        sun.shadow.camera.near =
            0.5;

        sun.shadow.camera.far =
            250;


        let d = 60;

        sun.shadow.camera.left =
            -d;

        sun.shadow.camera.right =
            d;

        sun.shadow.camera.top =
            d;

        sun.shadow.camera.bottom =
            -d;


        scene.add(sun);


        /* ============================================================
           RAINY CITY LIGHT
        ============================================================ */

        let rainyFill =
            new THREE.HemisphereLight(
                0x9db8d3,
                0x101722,
                1.15
            );

        scene.add(
            rainyFill
        );


        let blueCityLight =
            new THREE.PointLight(
                0x4aa3ff,
                2.2,
                35
            );

        blueCityLight.position.set(
            0,
            7,
            0
        );

        scene.add(
            blueCityLight
        );


        let redCityLight =
            new THREE.PointLight(
                0xff1744,
                1.7,
                30
            );

        redCityLight.position.set(
            -18,
            5,
            0
        );

        scene.add(
            redCityLight
        );


        /* ============================================================
           MATERIALS
        ============================================================ */

        let bldgMat =
            new THREE.MeshStandardMaterial({

                map: concreteTex,

                roughness: 0.62,

                metalness: 0.18,

                envMapIntensity: 1.25
            });


        let heavySteel =
            new THREE.MeshStandardMaterial({

                color: 0x1e293b,

                roughness: 0.2,

                metalness: 0.9
            });


        let chromeMetal =
            new THREE.MeshStandardMaterial({

                color: 0x475569,

                roughness: 0.1,

                metalness: 0.95
            });


        let darkIron =
            new THREE.MeshStandardMaterial({

                color: 0x0f172a,

                roughness: 0.4,

                metalness: 0.85
            });


        let brassGold =
            new THREE.MeshStandardMaterial({

                color: 0xd97706,

                roughness: 0.3,

                metalness: 0.8
            });


        let glassMat =
            new THREE.MeshStandardMaterial({

                color: 0x0284c7,

                roughness: 0.05,

                metalness: 0.95,

                transparent: true,

                opacity: 0.6
            });


        let burntMetal =
            new THREE.MeshStandardMaterial({

                map: rustTex,

                roughness: 0.7,

                metalness: 0.6
            });


        let signNeon =
            new THREE.MeshStandardMaterial({

                color: 0xff0055,

                emissive: 0xff0055,

                emissiveIntensity: 4.0
            });


        let fireEmissive =
            new THREE.MeshStandardMaterial({

                color: 0xff4500,

                emissive: 0xff4500,

                emissiveIntensity: 3.5
            });


        let lanternGlowMat =
            new THREE.MeshStandardMaterial({

                color: 0xffaa33,

                emissive: 0xff8800,

                emissiveIntensity: 5.0
            });


        /* ============================================================
           FLOOR - WET ASPHALT
        ============================================================ */

        const MAP_LIMIT = 38;


        let floorMat =
            new THREE.MeshStandardMaterial({

                map: asphaltTex,

                roughness: 0.22,

                metalness: 0.45,

                envMapIntensity: 1.8
            });


        let floor =
            new THREE.Mesh(
                new THREE.PlaneGeometry(
                    80,
                    80,
                    1,
                    1
                ),
                floorMat
            );


        floor.rotation.x =
            -Math.PI / 2;


        floor.receiveShadow = true;

        scene.add(floor);


        /* ============================================================
           RAIN SYSTEM
        ============================================================ */

        let rainGroup =
            new THREE.Group();

        scene.add(
            rainGroup
        );


        const RAIN_COUNT = 5500;

        const RAIN_AREA = 90;

        const RAIN_HEIGHT = 45;


        let rainPositions =
            new Float32Array(
                RAIN_COUNT * 3
            );


        let rainVelocities =
            new Float32Array(
                RAIN_COUNT
            );


        for (
            let i = 0;
            i < RAIN_COUNT;
            i++
        ) {

            rainPositions[i * 3] =
                (Math.random() - 0.5) *
                RAIN_AREA;


            rainPositions[i * 3 + 1] =
                Math.random() *
                RAIN_HEIGHT;


            rainPositions[i * 3 + 2] =
                (Math.random() - 0.5) *
                RAIN_AREA;


            rainVelocities[i] =
                0.55 +
                Math.random() * 0.35;
        }


        let rainGeometry =
            new THREE.BufferGeometry();


        rainGeometry.setAttribute(
            'position',
            new THREE.BufferAttribute(
                rainPositions,
                3
            )
        );


        let rainMaterial =
            new THREE.PointsMaterial({

                color: 0xb9d7ff,

                size: 0.075,

                transparent: true,

                opacity: 0.62,

                depthWrite: false,

                blending:
                    THREE.AdditiveBlending
            });


        let rain =
            new THREE.Points(
                rainGeometry,
                rainMaterial
            );


        rainGroup.add(
            rain
        );


        /* ============================================================
           NEAR RAIN
        ============================================================ */

        const NEAR_RAIN_COUNT = 1000;


        let nearRainPositions =
            new Float32Array(
                NEAR_RAIN_COUNT * 3
            );


        let nearRainVelocity =
            new Float32Array(
                NEAR_RAIN_COUNT
            );


        for (
            let i = 0;
            i < NEAR_RAIN_COUNT;
            i++
        ) {

            nearRainPositions[i * 3] =
                (Math.random() - 0.5) *
                25;


            nearRainPositions[i * 3 + 1] =
                Math.random() * 20;


            nearRainPositions[i * 3 + 2] =
                (Math.random() - 0.5) *
                25;


            nearRainVelocity[i] =
                0.7 +
                Math.random() * 0.4;
        }


        let nearRainGeometry =
            new THREE.BufferGeometry();


        nearRainGeometry.setAttribute(
            'position',
            new THREE.BufferAttribute(
                nearRainPositions,
                3
            )
        );


        let nearRainMaterial =
            new THREE.PointsMaterial({

                color: 0xdbeafe,

                size: 0.12,

                transparent: true,

                opacity: 0.42,

                depthWrite: false,

                blending:
                    THREE.AdditiveBlending
            });


        let nearRain =
            new THREE.Points(
                nearRainGeometry,
                nearRainMaterial
            );


        rainGroup.add(
            nearRain
        );


        /* ============================================================
           RAIN UPDATE
        ============================================================ */

        function updateRain() {

            let positions =
                rainGeometry
                    .attributes
                    .position
                    .array;


            for (
                let i = 0;
                i < RAIN_COUNT;
                i++
            ) {

                positions[i * 3 + 1] -=
                    rainVelocities[i];


                /* 바람 때문에 살짝 기울어진 비 */

                positions[i * 3] +=
                    0.035;


                if (
                    positions[i * 3 + 1] < 0
                ) {

                    positions[i * 3] =
                        camera.position.x +
                        (Math.random() - 0.5) *
                        RAIN_AREA;


                    positions[i * 3 + 1] =
                        RAIN_HEIGHT +
                        Math.random() * 10;


                    positions[i * 3 + 2] =
                        camera.position.z +
                        (Math.random() - 0.5) *
                        RAIN_AREA;
                }
            }


            rainGeometry
                .attributes
                .position
                .needsUpdate = true;


            let nearPositions =
                nearRainGeometry
                    .attributes
                    .position
                    .array;


            for (
                let i = 0;
                i < NEAR_RAIN_COUNT;
                i++
            ) {

                nearPositions[i * 3 + 1] -=
                    nearRainVelocity[i];


                nearPositions[i * 3] +=
                    0.055;


                if (
                    nearPositions[i * 3 + 1] < 0
                ) {

                    nearPositions[i * 3] =
                        camera.position.x +
                        (Math.random() - 0.5) *
                        25;


                    nearPositions[i * 3 + 1] =
                        20 +
                        Math.random() * 5;


                    nearPositions[i * 3 + 2] =
                        camera.position.z +
                        (Math.random() - 0.5) *
                        25;
                }
            }


            nearRainGeometry
                .attributes
                .position
                .needsUpdate = true;


            /* 비가 플레이어 주변에서 내리도록 이동 */

            rainGroup.position.x =
                camera.position.x;

            rainGroup.position.z =
                camera.position.z;
        }


        /* ============================================================
           COLLIDERS
        ============================================================ */

        let colliders = [];


        function addBoxCollider(
            x,
            z,
            w,
            d
        ) {

            colliders.push({

                minX:
                    x -
                    w / 2 -
                    PLAYER_RADIUS,

                maxX:
                    x +
                    w / 2 +
                    PLAYER_RADIUS,

                minZ:
                    z -
                    d / 2 -
                    PLAYER_RADIUS,

                maxZ:
                    z +
                    d / 2 +
                    PLAYER_RADIUS,

                cx: x,

                cz: z,

                w: w,

                d: d
            });
        }


        /* ============================================================
           BOUNDARY WALLS
        ============================================================ */

        function createBoundaryWalls() {

            let wallMat =
                new THREE.MeshStandardMaterial({

                    map: concreteTex,

                    roughness: 0.72,

                    metalness: 0.12
                });


            let h = 14;

            let t = 4;


            let wallN =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        80,
                        h,
                        t
                    ),
                    wallMat
                );


            wallN.position.set(
                0,
                h / 2,
                -MAP_LIMIT - t / 2
            );


            let wallS =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        80,
                        h,
                        t
                    ),
                    wallMat
                );


            wallS.position.set(
                0,
                h / 2,
                MAP_LIMIT + t / 2
            );


            let wallE =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        t,
                        h,
                        80
                    ),
                    wallMat
                );


            wallE.position.set(
                MAP_LIMIT + t / 2,
                h / 2,
                0
            );


            let wallW =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        t,
                        h,
                        80
                    ),
                    wallMat
                );


            wallW.position.set(
                -MAP_LIMIT - t / 2,
                h / 2,
                0
            );


            [
                wallN,
                wallS,
                wallE,
                wallW
            ].forEach(
                w => {

                    w.castShadow = true;

                    w.receiveShadow = true;

                    scene.add(w);
                }
            );


            addBoxCollider(
                0,
                -MAP_LIMIT - t / 2,
                80,
                t
            );


            addBoxCollider(
                0,
                MAP_LIMIT + t / 2,
                80,
                t
            );


            addBoxCollider(
                MAP_LIMIT + t / 2,
                0,
                t,
                80
            );


            addBoxCollider(
                -MAP_LIMIT - t / 2,
                0,
                t,
                80
            );
        }


        createBoundaryWalls();


        /* ============================================================
           BUILDINGS
        ============================================================ */

        function createBuildingBlock(
            x,
            z,
            w,
            h,
            d
        ) {

            let bldg =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        w,
                        h,
                        d
                    ),
                    bldgMat
                );


            bldg.position.set(
                x,
                h / 2,
                z
            );


            bldg.castShadow = true;

            bldg.receiveShadow = true;

            scene.add(bldg);


            addBoxCollider(
                x,
                z,
                w,
                d
            );


            /* 창문 */

            for (
                let y = 3;
                y < h - 2;
                y += 3.5
            ) {

                for (
                    let wx = -w / 2 + 2;
                    wx < w / 2 - 1.5;
                    wx += 3.2
                ) {

                    let win =
                        new THREE.Mesh(
                            new THREE.BoxGeometry(
                                1.4,
                                2.0,
                                0.15
                            ),
                            glassMat
                        );


                    let sideZ =
                        (x > 0)
                        ? z - d / 2 - 0.08
                        : z + d / 2 + 0.08;


                    win.position.set(
                        x + wx,
                        y,
                        sideZ
                    );


                    scene.add(win);
                }
            }


            if (
                Math.random() > 0.3
            ) {

                let sign =
                    new THREE.Mesh(
                        new THREE.BoxGeometry(
                            0.2,
                            2.5,
                            4.0
                        ),
                        signNeon
                    );


                sign.position.set(
                    x +
                    (
                        x > 0
                        ? -w / 2 - 0.1
                        : w / 2 + 0.1
                    ),

                    h * 0.6,

                    z
                );


                scene.add(sign);
            }
        }


        createBuildingBlock(
            -25,
            -22,
            18,
            18,
            18
        );


        createBuildingBlock(
            -25,
            0,
            18,
            22,
            16
        );


        createBuildingBlock(
            -25,
            22,
            18,
            16,
            18
        );


        createBuildingBlock(
            25,
            -22,
            18,
            16,
            18
        );


        createBuildingBlock(
            25,
            0,
            18,
            24,
            16
        );


        createBuildingBlock(
            25,
            22,
            18,
            18,
            18
        );


        /* ============================================================
           SPAWNS
        ============================================================ */

        const ALLEY_SPAWNS = [

            new THREE.Vector3(
                -26,
                0,
                -11
            ),

            new THREE.Vector3(
                -26,
                0,
                11
            ),

            new THREE.Vector3(
                26,
                0,
                -11
            ),

            new THREE.Vector3(
                26,
                0,
                11
            )
        ];


        /* ============================================================
           DESTROYED TRUCK
        ============================================================ */

        function createDestroyedTruck(
            x,
            z,
            angle
        ) {

            let truck =
                new THREE.Group();


            let body =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        2.8,
                        1.6,
                        5.8
                    ),
                    burntMetal
                );


            body.position.y = 1.0;

            body.castShadow = true;

            body.receiveShadow = true;

            truck.add(body);


            let cab =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        2.6,
                        1.4,
                        2.2
                    ),
                    heavySteel
                );


            cab.position.set(
                0,
                1.9,
                -1.8
            );


            cab.castShadow = true;

            truck.add(cab);


            truck.position.set(
                x,
                0,
                z
            );


            truck.rotation.y =
                angle;


            truck.rotation.z =
                0.1;


            scene.add(truck);


            addBoxCollider(
                x,
                z,
                3.4,
                6.2
            );
        }


        /* ============================================================
           BARRICADE
        ============================================================ */

        function createBarricade(
            x,
            z,
            angle
        ) {

            let bar =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        3.6,
                        1.3,
                        0.8
                    ),
                    bldgMat
                );


            bar.position.set(
                x,
                0.65,
                z
            );


            bar.rotation.y =
                angle;


            bar.castShadow = true;

            bar.receiveShadow = true;

            scene.add(bar);


            let w =
                Math.abs(
                    Math.cos(angle) *
                    3.6
                ) +
                Math.abs(
                    Math.sin(angle) *
                    0.8
                );


            let d =
                Math.abs(
                    Math.sin(angle) *
                    3.6
                ) +
                Math.abs(
                    Math.cos(angle) *
                    0.8
                );


            addBoxCollider(
                x,
                z,
                w,
                d
            );
        }


        /* ============================================================
           BURNING BARREL
        ============================================================ */

        function createBurningBarrel(
            x,
            z
        ) {

            let barrel =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.5,
                        0.5,
                        1.4,
                        16
                    ),
                    burntMetal
                );


            barrel.position.set(
                x,
                0.7,
                z
            );


            barrel.castShadow = true;

            scene.add(barrel);


            let fire =
                new THREE.Mesh(
                    new THREE.ConeGeometry(
                        0.4,
                        0.8,
                        8
                    ),
                    fireEmissive
                );


            fire.position.set(
                x,
                1.6,
                z
            );


            scene.add(fire);


            let light =
                new THREE.PointLight(
                    0xff4500,
                    2.0,
                    8
                );


            light.position.set(
                x,
                1.8,
                z
            );


            scene.add(light);


            addBoxCollider(
                x,
                z,
                1.2,
                1.2
            );
        }


        /* ============================================================
           STREET LIGHT
        ============================================================ */

        function createStreetLight(
            x,
            z
        ) {

            let lanternGroup =
                new THREE.Group();


            let pole =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.06,
                        0.08,
                        5.0,
                        12
                    ),
                    darkIron
                );


            pole.position.set(
                x,
                2.5,
                z
            );


            pole.castShadow = true;

            lanternGroup.add(
                pole
            );


            let cap =
                new THREE.Mesh(
                    new THREE.ConeGeometry(
                        0.45,
                        0.3,
                        6
                    ),
                    darkIron
                );


            cap.position.set(
                x,
                5.2,
                z
            );


            lanternGroup.add(
                cap
            );


            let glass =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.25,
                        0.18,
                        0.6,
                        6
                    ),
                    glassMat
                );


            glass.position.set(
                x,
                4.75,
                z
            );


            lanternGroup.add(
                glass
            );


            let bulb =
                new THREE.Mesh(
                    new THREE.SphereGeometry(
                        0.14,
                        12,
                        12
                    ),
                    lanternGlowMat
                );


            bulb.position.set(
                x,
                4.75,
                z
            );


            lanternGroup.add(
                bulb
            );


            let light =
                new THREE.PointLight(
                    0xff9900,
                    2.8,
                    15
                );


            light.position.set(
                x,
                4.75,
                z
            );


            lanternGroup.add(
                light
            );


            scene.add(
                lanternGroup
            );


            addBoxCollider(
                x,
                z,
                0.2,
                0.2
            );
        }


        /* ============================================================
           MAP OBJECTS
        ============================================================ */

        createDestroyedTruck(
            -5,
            6,
            0.4
        );

        createDestroyedTruck(
            7,
            -10,
            -0.6
        );

        createDestroyedTruck(
            -12,
            22,
            1.2
        );

        createDestroyedTruck(
            10,
            -26,
            -0.3
        );

        createDestroyedTruck(
            -8,
            -20,
            0.8
        );

        createDestroyedTruck(
            12,
            18,
            -1.1
        );


        createBarricade(
            -2,
            -18,
            0.2
        );

        createBarricade(
            3,
            16,
            -0.4
        );

        createBarricade(
            -13,
            0,
            1.57
        );

        createBarricade(
            13,
            0,
            1.57
        );


        createBurningBarrel(
            -8,
            -4
        );

        createBurningBarrel(
            9,
            8
        );

        createBurningBarrel(
            -3,
            25
        );

        createBurningBarrel(
            4,
            -22
        );


        createStreetLight(-14, -26);
        createStreetLight(-14, -18);
        createStreetLight(-14, -4);
        createStreetLight(-14, 4);
        createStreetLight(-14, 18);
        createStreetLight(-14, 26);

        createStreetLight(14, -26);
        createStreetLight(14, -18);
        createStreetLight(14, -4);
        createStreetLight(14, 4);
        createStreetLight(14, 18);
        createStreetLight(14, 26);

        createStreetLight(-25, -11);
        createStreetLight(-25, 11);

        createStreetLight(25, -11);
        createStreetLight(25, 11);

        createStreetLight(-36, -22);
        createStreetLight(-36, 0);
        createStreetLight(-36, 22);

        createStreetLight(36, -22);
        createStreetLight(36, 0);
        createStreetLight(36, 22);


        /* ============================================================
           HEAVY BOT
        ============================================================ */

        function createHeavyBot(
            spawnPos
        ) {

            let bot =
                new THREE.Group();


            bot.userData = {
                hp: 120
            };


            let redEye =
                new THREE.MeshStandardMaterial({

                    color: 0xff0033,

                    emissive: 0xff0033,

                    emissiveIntensity: 4.0
                });


            let reactorGlow =
                new THREE.MeshStandardMaterial({

                    color: 0x00f5a0,

                    emissive: 0x00f5a0,

                    emissiveIntensity: 3.0
                });


            /* HEAD */

            let headGroup =
                new THREE.Group();


            let headMesh =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        0.44,
                        0.4,
                        0.44
                    ),
                    heavySteel
                );


            headMesh.castShadow =
                true;


            let neckJoint =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.16,
                        0.16,
                        0.35,
                        12
                    ),
                    darkIron
                );


            neckJoint.position.set(
                0,
                -0.25,
                0
            );


            let visor =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.08,
                        0.08,
                        0.38,
                        16
                    ),
                    redEye
                );


            visor.rotateZ(
                Math.PI / 2
            );


            visor.position.set(
                0,
                0.05,
                -0.22
            );


            headGroup.add(
                headMesh,
                neckJoint,
                visor
            );


            headGroup.position.y =
                2.05;


            headGroup.userData = {
                type: 'head'
            };


            /* BODY */

            let bodyGroup =
                new THREE.Group();


            let torso =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        0.85,
                        1.05,
                        0.55
                    ),
                    darkIron
                );


            torso.position.y =
                1.35;


            torso.castShadow =
                true;


            let core =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.15,
                        0.15,
                        0.12,
                        16
                    ),
                    reactorGlow
                );


            core.rotateX(
                Math.PI / 2
            );


            core.position.set(
                0,
                1.4,
                -0.28
            );


            let pelvisJoint =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        0.7,
                        0.3,
                        0.45
                    ),
                    heavySteel
                );


            pelvisJoint.position.y =
                0.8;


            bodyGroup.add(
                torso,
                core,
                pelvisJoint
            );


            bodyGroup.userData = {
                type: 'body'
            };


            /* LEGS */

            let legGroup =
                new THREE.Group();


            let legL =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.14,
                        0.11,
                        1.05,
                        12
                    ),
                    chromeMetal
                );


            legL.position.set(
                -0.25,
                0.45,
                0
            );


            legL.castShadow =
                true;


            let legR =
                legL.clone();


            legR.position.set(
                0.25,
                0.45,
                0
            );


            legGroup.add(
                legL,
                legR
            );


            legGroup.userData = {
                type: 'legs'
            };


            bot.add(
                headGroup,
                bodyGroup,
                legGroup
            );


            let p =
                spawnPos ||
                ALLEY_SPAWNS[
                    Math.floor(
                        Math.random() *
                        ALLEY_SPAWNS.length
                    )
                ];


            bot.position.copy(p);


            scene.add(bot);


            return bot;
        }


        /* ============================================================
           GUNS
        ============================================================ */

        function createGuns() {

            let guns = [];


            /* GUN 1 */

            let g1 =
                new THREE.Group();


            let b1 =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.03,
                        0.035,
                        2.4,
                        24
                    ),
                    chromeMetal
                );


            b1.rotateX(
                Math.PI / 2
            );


            b1.position.set(
                0,
                0,
                -1.2
            );


            let r1 =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        0.16,
                        0.22,
                        0.9
                    ),
                    heavySteel
                );


            r1.position.set(
                0,
                0,
                -0.1
            );


            let sc1 =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.07,
                        0.07,
                        0.85,
                        24
                    ),
                    darkIron
                );


            sc1.rotateX(
                Math.PI / 2
            );


            sc1.position.set(
                0,
                0.2,
                -0.2
            );


            g1.add(
                b1,
                r1,
                sc1
            );


            /* GUN 2 */

            let g2 =
                new THREE.Group();


            let b2 =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.025,
                        0.03,
                        1.8,
                        24
                    ),
                    heavySteel
                );


            b2.rotateX(
                Math.PI / 2
            );


            b2.position.set(
                0,
                0,
                -0.9
            );


            let sc2 =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.06,
                        0.06,
                        0.65,
                        24
                    ),
                    brassGold
                );


            sc2.rotateX(
                Math.PI / 2
            );


            sc2.position.set(
                0,
                0.18,
                -0.15
            );


            g2.add(
                b2,
                sc2
            );


            /* GUN 3 */

            let g3 =
                new THREE.Group();


            let b3 =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.04,
                        0.04,
                        2.0,
                        24
                    ),
                    darkIron
                );


            b3.rotateX(
                Math.PI / 2
            );


            b3.position.set(
                0,
                0,
                -1.0
            );


            let neonTube =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.02,
                        0.02,
                        1.6,
                        16
                    ),
                    signNeon
                );


            neonTube.rotateX(
                Math.PI / 2
            );


            neonTube.position.set(
                0,
                0.06,
                -1.0
            );


            g3.add(
                b3,
                neonTube
            );


            return {

                gunList: [
                    g1,
                    g2,
                    g3
                ],

                names: [
                    "M200 HEAVY",
                    "EBR TACTICAL",
                    "CYBER LASER"
                ]
            };
        }


        let gunData =
            createGuns();


        let guns =
            gunData.gunList;


        let gunNames =
            gunData.names;


        let currentGunIdx = 0;


        let gunContainer =
            new THREE.Group();


        guns.forEach(
            (g, i) => {

                g.visible =
                    (i === 0);

                gunContainer.add(g);
            }
        );


        const NORMAL_GUN_POS =
            new THREE.Vector3(
                0.35,
                -0.28,
                -0.5
            );


        const AIM_GUN_POS =
            new THREE.Vector3(
                0,
                -0.19,
                -0.32
            );


        gunContainer.position.copy(
            NORMAL_GUN_POS
        );


        camera.add(
            gunContainer
        );


        scene.add(
            camera
        );


        /* ============================================================
           WEAPON SWITCH
        ============================================================ */

        document.addEventListener(
            'keydown',
            (e) => {

                if (
                    [
                        'Digit1',
                        'Digit2',
                        'Digit3'
                    ].includes(e.code)
                ) {

                    let idx =
                        parseInt(
                            e.code.replace(
                                'Digit',
                                ''
                            )
                        ) - 1;


                    guns[
                        currentGunIdx
                    ].visible = false;


                    currentGunIdx =
                        idx;


                    guns[
                        currentGunIdx
                    ].visible = true;


                    document.getElementById(
                        'gun-name'
                    ).innerText =
                        gunNames[
                            currentGunIdx
                        ];
                }
            }
        );


        /* ============================================================
           GAME VARIABLES
        ============================================================ */

        let hp = 100;

        let score = 0;

        let isGameOver = false;


        let keys = {

            KeyW: false,

            KeyS: false,

            KeyA: false,

            KeyD: false,

            ShiftLeft: false,

            ShiftRight: false,

            Space: false
        };


        function resetKeys() {

            for (
                let k in keys
            ) {

                keys[k] = false;
            }
        }


        let bots = [];

        let sparks = [];

        let isAiming = false;


        /* ============================================================
           BOT SPAWN
        ============================================================ */

        for (
            let i = 0;
            i < 4;
            i++
        ) {

            bots.push(
                createHeavyBot(
                    ALLEY_SPAWNS[i]
                )
            );
        }


        setInterval(
            () => {

                if (
                    bots.length < 6 &&
                    !isGameOver
                ) {

                    bots.push(
                        createHeavyBot()
                    );
                }

            },
            2200
        );


        /* ============================================================
           MOVEMENT INPUT
        ============================================================ */

        document.addEventListener(
            'keydown',
            (e) => {

                if (
                    keys.hasOwnProperty(
                        e.code
                    )
                ) {

                    keys[e.code] = true;
                }
            }
        );


        document.addEventListener(
            'keyup',
            (e) => {

                if (
                    keys.hasOwnProperty(
                        e.code
                    )
                ) {

                    keys[e.code] = false;
                }
            }
        );


        window.addEventListener(
            'blur',
            resetKeys
        );


        document.addEventListener(
            'mouseleave',
            resetKeys
        );


        /* ============================================================
           SPARK EFFECT
        ============================================================ */

        function createSparks(
            pos,
            colorHex
        ) {

            let pGeo =
                new THREE.BufferGeometry();


            let count = 30;


            let positions =
                new Float32Array(
                    count * 3
                );


            let velocities = [];


            for (
                let i = 0;
                i < count;
                i++
            ) {

                positions[i * 3] =
                    pos.x;

                positions[i * 3 + 1] =
                    pos.y;

                positions[i * 3 + 2] =
                    pos.z;


                velocities.push(
                    new THREE.Vector3(
                        (Math.random() - 0.5) * 0.5,
                        (Math.random() - 0.5) * 0.5,
                        (Math.random() - 0.5) * 0.5
                    )
                );
            }


            pGeo.setAttribute(
                'position',
                new THREE.BufferAttribute(
                    positions,
                    3
                )
            );


            let pMat =
                new THREE.PointsMaterial({

                    color:
                        colorHex ||
                        0x00f5a0,

                    size: 0.25,

                    transparent: true,

                    opacity: 1
                });


            let pSystem =
                new THREE.Points(
                    pGeo,
                    pMat
                );


            scene.add(
                pSystem
            );


            sparks.push({

                system:
                    pSystem,

                vels:
                    velocities,

                life: 1.0
            });
        }


        /* ============================================================
           HIT FEEDBACK
        ============================================================ */

        function showHitFeedback(
            text,
            color
        ) {

            let fb =
                document.getElementById(
                    'hit-feedback'
                );


            fb.innerText =
                text;


            fb.style.color =
                color;


            fb.style.opacity =
                '1';


            setTimeout(
                () => {

                    fb.style.opacity =
                        '0';

                },
                500
            );
        }


        /* ============================================================
           SHOOTING
        ============================================================ */

        let raycaster =
            new THREE.Raycaster();


        let canShoot = true;


        /* ADS */

        document.addEventListener(
            'mousedown',
            (e) => {

                if (
                    e.button === 2
                ) {

                    isAiming = true;


                    camera.fov = 20;


                    camera.updateProjectionMatrix();


                    gunContainer.position.copy(
                        AIM_GUN_POS
                    );


                    document.getElementById(
                        'scope-overlay'
                    ).style.display =
                        'block';


                    document.getElementById(
                        'crosshair'
                    ).style.display =
                        'none';
                }
            }
        );


        document.addEventListener(
            'mouseup',
            (e) => {

                if (
                    e.button === 2
                ) {

                    isAiming = false;


                    camera.fov = 65;


                    camera.updateProjectionMatrix();


                    gunContainer.position.copy(
                        NORMAL_GUN_POS
                    );


                    document.getElementById(
                        'scope-overlay'
                    ).style.display =
                        'none';


                    document.getElementById(
                        'crosshair'
                    ).style.display =
                        'block';
                }
            }
        );


        /* SHOOT */

        document.addEventListener(
            'click',
            (e) => {

                if (
                    e.button !== 0
                )
                    return;


                if (
                    isGameOver
                ) {

                    resetGame();

                    return;
                }


                if (
                    !canShoot
                )
                    return;


                canShoot = false;


                gunContainer.position.z +=
                    0.25;


                gunContainer.rotation.x =
                    0.3;


                setTimeout(
                    () => {

                        gunContainer.position.copy(
                            isAiming
                            ? AIM_GUN_POS
                            : NORMAL_GUN_POS
                        );


                        gunContainer.rotation.x =
                            0;


                        canShoot = true;

                    },
                    380
                );


                raycaster.setFromCamera(
                    new THREE.Vector2(0, 0),
                    camera
                );


                let allBotMeshes = [];


                bots.forEach(
                    b => {

                        b.traverse(
                            child => {

                                if (
                                    child.isMesh
                                ) {

                                    allBotMeshes.push(
                                        child
                                    );
                                }
                            }
                        );
                    }
                );


                let intersects =
                    raycaster.intersectObjects(
                        allBotMeshes
                    );


                if (
                    intersects.length > 0
                ) {

                    let hitPoint =
                        intersects[0].point;


                    let hitMesh =
                        intersects[0].object;


                    let partGroup =
                        hitMesh.parent;


                    while (
                        partGroup &&
                        ![
                            'head',
                            'body',
                            'legs'
                        ].includes(
                            partGroup.userData?.type
                        )
                    ) {

                        partGroup =
                            partGroup.parent;
                    }


                    let hitBot =
                        hitMesh.parent;


                    while (
                        hitBot &&
                        !bots.includes(
                            hitBot
                        )
                    ) {

                        hitBot =
                            hitBot.parent;
                    }


                    if (
                        hitBot &&
                        partGroup
                    ) {

                        let hitType =
                            partGroup.userData.type;


                        let dmg = 0;

                        let sparkColor =
                            0x00f5a0;


                        if (
                            hitType === 'head'
                        ) {

                            dmg = 120;

                            sparkColor =
                                0xff0055;


                            showHitFeedback(
                                "CRITICAL HEADSHOT! -120",
                                "#ff0055"
                            );


                        } else if (
                            hitType === 'body'
                        ) {

                            dmg = 60;

                            sparkColor =
                                0xffaa00;


                            showHitFeedback(
                                "ARMOR IMPACT -60",
                                "#ffaa00"
                            );


                        } else if (
                            hitType === 'legs'
                        ) {

                            dmg = 30;

                            sparkColor =
                                0x00d2ff;


                            showHitFeedback(
                                "LEG HIT -30",
                                "#00d2ff"
                            );
                        }


                        createSparks(
                            hitPoint,
                            sparkColor
                        );


                        hitBot.userData.hp -=
                            dmg;


                        if (
                            hitBot.userData.hp <= 0
                        ) {

                            scene.remove(
                                hitBot
                            );


                            bots =
                                bots.filter(
                                    b =>
                                        b !== hitBot
                                );


                            score += 1;


                            document.getElementById(
                                'score'
                            ).innerText =
                                score;
                        }
                    }
                }
            }
        );


        /* ============================================================
           RESET GAME
        ============================================================ */

        function resetGame() {

            bots.forEach(
                b => scene.remove(b)
            );


            bots = [];


            hp = 100;

            score = 0;

            isGameOver = false;


            resetKeys();


            document.getElementById(
                'hp-fill'
            ).style.width =
                '100%';


            document.getElementById(
                'score'
            ).innerText =
                '0';


            document.getElementById(
                'game-over'
            ).style.display =
                'none';


            camera.position.set(
                0,
                PLAYER_HEIGHT,
                0
            );


            yVelocity = 0;

            isGrounded = true;


            pitch = 0;

            yaw = 0;


            camera.quaternion.setFromEuler(
                new THREE.Euler(
                    0,
                    0,
                    0
                )
            );


            for (
                let i = 0;
                i < 4;
                i++
            ) {

                bots.push(
                    createHeavyBot(
                        ALLEY_SPAWNS[i]
                    )
                );
            }
        }


        /* ============================================================
           COLLISION
        ============================================================ */

        function checkCollisionAndMove(
            currentPos,
            moveVector
        ) {

            let nextPos =
                currentPos.clone()
                .add(moveVector);


            for (
                let c of colliders
            ) {

                if (
                    nextPos.x > c.minX &&
                    nextPos.x < c.maxX &&
                    nextPos.z > c.minZ &&
                    nextPos.z < c.maxZ
                ) {

                    let checkX =
                        currentPos.clone()
                        .add(
                            new THREE.Vector3(
                                moveVector.x,
                                0,
                                0
                            )
                        );


                    if (
                        checkX.x > c.minX &&
                        checkX.x < c.maxX &&
                        currentPos.z > c.minZ &&
                        currentPos.z < c.maxZ
                    ) {

                        moveVector.x = 0;
                    }


                    let checkZ =
                        currentPos.clone()
                        .add(
                            new THREE.Vector3(
                                0,
                                0,
                                moveVector.z
                            )
                        );


                    if (
                        currentPos.x > c.minX &&
                        currentPos.x < c.maxX &&
                        checkZ.z > c.minZ &&
                        checkZ.z < c.maxZ
                    ) {

                        moveVector.z = 0;
                    }
                }
            }


            return currentPos.add(
                moveVector
            );
        }


        /* ============================================================
           ANIMATION LOOP
        ============================================================ */

        function animate() {

            requestAnimationFrame(
                animate
            );


            /* 🌧️ 비 업데이트 */

            updateRain();


            if (
                isGameOver
            )
                return;


            /* PLAYER FORWARD */

            let forward =
                new THREE.Vector3(
                    0,
                    0,
                    -1
                )
                .applyQuaternion(
                    camera.quaternion
                );


            forward.y = 0;

            forward.normalize();


            let right =
                new THREE.Vector3(
                    1,
                    0,
                    0
                )
                .applyQuaternion(
                    camera.quaternion
                );


            right.y = 0;

            right.normalize();


            /* MOVEMENT */

            let move =
                new THREE.Vector3();


            if (
                keys.KeyW
            )
                move.add(
                    forward
                );


            if (
                keys.KeyS
            )
                move.sub(
                    forward
                );


            if (
                keys.KeyD
            )
                move.add(
                    right
                );


            if (
                keys.KeyA
            )
                move.sub(
                    right
                );


            if (
                move.lengthSq() > 0
            ) {

                let currentSpeed =
                    (
                        keys.ShiftLeft ||
                        keys.ShiftRight
                    )
                    ? 0.13
                    : 0.095;


                move.normalize()
                    .multiplyScalar(
                        currentSpeed
                    );


                checkCollisionAndMove(
                    camera.position,
                    move
                );
            }


            /* JUMP */

            if (
                keys.Space &&
                isGrounded
            ) {

                yVelocity =
                    JUMP_FORCE;


                isGrounded =
                    false;
            }


            if (
                !isGrounded
            ) {

                yVelocity -=
                    GRAVITY;


                camera.position.y +=
                    yVelocity;


                if (
                    camera.position.y <=
                    PLAYER_HEIGHT
                ) {

                    camera.position.y =
                        PLAYER_HEIGHT;


                    yVelocity = 0;


                    isGrounded =
                        true;
                }
            }


            /* ========================================================
               SPARK UPDATE
            ======================================================== */

            sparks.forEach(
                (sp, idx) => {

                    sp.life -=
                        0.05;


                    let pos =
                        sp.system
                        .geometry
                        .attributes
                        .position
                        .array;


                    for (
                        let i = 0;
                        i < sp.vels.length;
                        i++
                    ) {

                        pos[i * 3] +=
                            sp.vels[i].x;

                        pos[i * 3 + 1] +=
                            sp.vels[i].y;

                        pos[i * 3 + 2] +=
                            sp.vels[i].z;
                    }


                    sp.system
                        .geometry
                        .attributes
                        .position
                        .needsUpdate = true;


                    sp.system
                        .material
                        .opacity =
                        sp.life;


                    if (
                        sp.life <= 0
                    ) {

                        scene.remove(
                            sp.system
                        );


                        sparks.splice(
                            idx,
                            1
                        );
                    }
                }
            );


            /* ========================================================
               BOT AI
            ======================================================== */

            bots.forEach(
                bot => {

                    let dir =
                        new THREE.Vector3()
                        .subVectors(
                            camera.position,
                            bot.position
                        );


                    dir.y = 0;


                    let dist =
                        dir.length();


                    dir.normalize();


                    if (
                        dist > 1.8
                    ) {

                        let botMove =
                            dir.multiplyScalar(
                                0.038
                            );


                        checkCollisionAndMove(
                            bot.position,
                            botMove
                        );

                    } else {

                        hp -=
                            0.4;


                        document.getElementById(
                            'hp-fill'
                        ).style.width =
                            Math.max(
                                0,
                                hp
                            ) + '%';


                        if (
                            hp <= 0
                        ) {

                            isGameOver =
                                true;


                            document.getElementById(
                                'game-over'
                            ).style.display =
                                'block';
                        }
                    }


                    bot.lookAt(
                        camera.position.x,
                        0,
                        camera.position.z
                    );
                }
            );


            /* ========================================================
               RENDER
            ======================================================== */

            renderer.render(
                scene,
                camera
            );
        }


        /* ============================================================
           WINDOW RESIZE
        ============================================================ */

        window.addEventListener(
            'resize',
            () => {

                camera.aspect =
                    window.innerWidth /
                    window.innerHeight;


                camera.updateProjectionMatrix();


                renderer.setSize(
                    window.innerWidth,
                    window.innerHeight
                );
            }
        );


        /* START */

        animate();

    </script>

</body>
</html>
"""

components.html(
    game_html,
    height=720,
    scrolling=False
)
