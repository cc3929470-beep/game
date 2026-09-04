import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TACTICAL AIM RANGE", layout="wide")

st.title("🎯 TACTICAL AIM TRAINING RANGE")
st.caption("WASD 이동 | Shift 질주 | 마우스 시점 | 좌클릭 사격 | R 재시작")

html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<style>
html, body {
    margin: 0;
    overflow: hidden;
    background: #101419;
    font-family: Arial;
    color: #fff;
}

#ui {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 5;
}

#top {
    position: absolute;
    top: 22px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
}

#timer {
    font-size: 38px;
    font-weight: 900;
    letter-spacing: 2px;
}

#score {
    font-size: 16px;
    color: #ffcc66;
    margin-top: 6px;
}

#cross {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 14px;
    height: 14px;
    transform: translate(-50%, -50%);
}

#cross:before,
#cross:after {
    content: "";
    position: absolute;
    background: #fff;
    box-shadow: 0 0 5px #fff;
}

#cross:before {
    width: 2px;
    height: 18px;
    left: 6px;
    top: -2px;
}

#cross:after {
    height: 2px;
    width: 18px;
    top: 6px;
    left: -2px;
}

#hint {
    position: absolute;
    bottom: 22px;
    left: 50%;
    transform: translateX(-50%);
    color: #aab4bd;
    font-size: 12px;
}
</style>
</head>

<body>

<div id="ui">

    <div id="top">
        <div id="timer">60.0</div>
        <div id="score">
            SCORE 0 · HITS 0 · ACCURACY 0%
        </div>
    </div>

    <div id="cross"></div>

    <div id="hint">
        CLICK TO SHOOT · WASD MOVE · R RESTART
    </div>

</div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<script>

// ================================
// SCENE
// ================================

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x8d9ba1);

scene.fog = new THREE.Fog(
    0x8d9ba1,
    35,
    110
);


// ================================
// CAMERA
// ================================

const camera = new THREE.PerspectiveCamera(
    75,
    innerWidth / innerHeight,
    .1,
    200
);

camera.position.set(
    0,
    1.7,
    9
);


// ================================
// RENDERER
// ================================

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: "high-performance"
});

renderer.setSize(
    innerWidth,
    innerHeight
);

renderer.setPixelRatio(
    Math.min(devicePixelRatio, 2)
);

renderer.shadowMap.enabled = true;

renderer.shadowMap.type =
    THREE.PCFSoftShadowMap;

renderer.outputEncoding =
    THREE.sRGBEncoding;

renderer.toneMapping =
    THREE.ACESFilmicToneMapping;

renderer.toneMappingExposure = 1.15;

document.body.appendChild(
    renderer.domElement
);


// ================================
// LIGHTING
// ================================

scene.add(
    new THREE.HemisphereLight(
        0xddeeff,
        0x3b3028,
        2
    )
);


const sun = new THREE.DirectionalLight(
    0xffffff,
    3
);

sun.position.set(
    15,
    25,
    10
);

sun.castShadow = true;

sun.shadow.mapSize.set(
    2048,
    2048
);

scene.add(sun);


// ================================
// FLOOR
// ================================

const floorMat =
    new THREE.MeshStandardMaterial({
        color: 0x69767a,
        roughness: .9
    });


const floor = new THREE.Mesh(

    new THREE.PlaneGeometry(
        100,
        100
    ),

    floorMat
);

floor.rotation.x = -Math.PI / 2;

floor.receiveShadow = true;

scene.add(floor);


// ================================
// MAP OBJECT FUNCTION
// ================================

function box(
    x,
    y,
    z,
    w,
    h,
    d,
    color = 0x5c6468
) {

    const m = new THREE.Mesh(

        new THREE.BoxGeometry(
            w,
            h,
            d
        ),

        new THREE.MeshStandardMaterial({
            color,
            roughness: .75
        })

    );

    m.position.set(
        x,
        y,
        z
    );

    m.castShadow = true;

    m.receiveShadow = true;

    scene.add(m);

    return m;
}


// ================================
// TRAINING RANGE MAP
// ================================

box(
    0,
    5,
    -28,
    42,
    10,
    1,
    0x4a5357
);

box(
    -20,
    4,
    -5,
    1,
    8,
    46,
    0x596166
);

box(
    20,
    4,
    -5,
    1,
    8,
    46,
    0x596166
);

box(
    0,
    4,
    -8,
    12,
    8,
    .7,
    0x3e474b
);

box(
    -10,
    2.2,
    -14,
    5,
    4,
    .7,
    0x50595d
);

box(
    10,
    2.2,
    -14,
    5,
    4,
    .7,
    0x50595d
);


for (
    let i = -18;
    i <= 18;
    i += 6
) {

    box(
        i,
        1,
        -22,
        1.4,
        2,
        .8,
        0x4c565a
    );

}


// ================================
// TARGET MATERIALS
// ================================

const orange =
    new THREE.MeshStandardMaterial({

        color: 0xff9f1c,

        emissive: 0x331500

    });


const dark =
    new THREE.MeshStandardMaterial({

        color: 0x1d2428,

        roughness: .5

    });


// ================================
// TARGET SYSTEM
// ================================

const targets = [];

const targetGroup =
    new THREE.Group();

scene.add(targetGroup);


function spawnTarget() {

    const t =
        new THREE.Group();


    const body =
        new THREE.Mesh(

            new THREE.CylinderGeometry(
                .55,
                .55,
                .13,
                32
            ),

            orange
        );


    body.rotation.x =
        Math.PI / 2;

    body.castShadow = true;


    const ring =
        new THREE.Mesh(

            new THREE.TorusGeometry(
                .38,
                .055,
                10,
                32
            ),

            dark
        );


    ring.rotation.x =
        Math.PI / 2;

    ring.position.z = -.08;


    t.add(body);

    t.add(ring);


    let x =
        (Math.random() - .5) * 24;

    let z =
        -8 - Math.random() * 32;

    let y =
        1.2 + Math.random() * 2.8;


    t.position.set(
        x,
        y,
        z
    );


    t.userData = {

        life: 0,

        phase:
            Math.random() * 6.28

    };


    targetGroup.add(t);

    targets.push(t);
}


// 초기 타겟 생성

for (
    let i = 0;
    i < 8;
    i++
) {

    spawnTarget();

}


// ================================
// GAME VARIABLES
// ================================

let score = 0;

let hits = 0;

let shots = 0;

let time = 60;

let running = true;


let yaw = 0;

let pitch = 0;

let look = false;


let prev = {
    x: 0,
    y: 0
};


const keys = {};


// ================================
// KEYBOARD
// ================================

addEventListener(
    "keydown",
    e => {

        keys[e.code] = true;

        if (
            e.code === "KeyR"
        ) {

            reset();

        }

    }
);


addEventListener(
    "keyup",
    e => {

        keys[e.code] = false;

    }
);


// ================================
// MOUSE
// ================================

addEventListener(
    "contextmenu",
    e => e.preventDefault()
);


addEventListener(
    "mousedown",
    e => {

        if (
            e.button === 0
        ) {

            look = true;

            prev = {
                x: e.clientX,
                y: e.clientY
            };

            shoot();

        }

    }
);


addEventListener(
    "mouseup",
    () => {

        look = false;

    }
);


addEventListener(
    "mousemove",
    e => {

        if (!look)
            return;


        yaw -=
            (
                e.clientX -
                prev.x
            ) * .0025;


        pitch =
            Math.max(
                -1.45,

                Math.min(
                    1.45,

                    pitch -
                    (
                        e.clientY -
                        prev.y
                    ) * .0025
                )
            );


        prev = {

            x: e.clientX,

            y: e.clientY

        };


        camera.rotation.set(

            pitch,

            yaw,

            0,

            "YXZ"

        );

    }
);


// ================================
// SHOOTING
// ================================

const ray =
    new THREE.Raycaster();


function shoot() {

    if (!running)
        return;


    shots++;


    ray.setFromCamera(

        new THREE.Vector2(
            0,
            0
        ),

        camera

    );


    const meshes = [];


    targets.forEach(
        t => {

            t.traverse(
                o => {

                    if (
                        o.isMesh
                    ) {

                        meshes.push(o);

                    }

                }
            );

        }
    );


    const h =
        ray.intersectObjects(
            meshes,
            false
        );


    if (h.length) {

        let obj =
            h[0].object;


        while (

            obj.parent &&

            !targets.includes(obj)

        ) {

            obj =
                obj.parent;

        }


        const idx =
            targets.indexOf(obj);


        if (idx >= 0) {

            targetGroup.remove(obj);

            targets.splice(
                idx,
                1
            );


            hits++;

            score += 100;


            setTimeout(

                spawnTarget,

                180

            );

        }

    }

}


// ================================
// RESET
// ================================

function reset() {

    score = 0;

    hits = 0;

    shots = 0;

    time = 60;

    running = true;


    while (
        targets.length
    ) {

        targetGroup.remove(
            targets.pop()
        );

    }


    for (
        let i = 0;
        i < 8;
        i++
    ) {

        spawnTarget();

    }

}


// ================================
// GAME LOOP
// ================================

const clock =
    new THREE.Clock();


function loop() {

    requestAnimationFrame(loop);


    const dt =
        Math.min(
            clock.getDelta(),
            .05
        );


    if (running) {

        time -= dt;


        if (time <= 0) {

            time = 0;

            running = false;

        }


        const f =
            new THREE.Vector3(
                0,
                0,
                -1
            )
            .applyQuaternion(
                camera.quaternion
            );


        f.y = 0;

        f.normalize();


        const r =
            new THREE.Vector3(
                1,
                0,
                0
            )
            .applyQuaternion(
                camera.quaternion
            );


        r.y = 0;

        r.normalize();


        const move =
            new THREE.Vector3();


        if (keys.KeyW)
            move.add(f);

        if (keys.KeyS)
            move.sub(f);

        if (keys.KeyD)
            move.add(r);

        if (keys.KeyA)
            move.sub(r);


        if (
            move.lengthSq()
        ) {

            camera.position.addScaledVector(

                move.normalize(),

                dt *
                (
                    keys.ShiftLeft
                        ? 8
                        : 4
                )

            );

        }


        targets.forEach(
            t => {

                t.userData.life += dt;


                t.position.y +=

                    Math.sin(

                        t.userData.life *
                        2 +

                        t.userData.phase

                    )

                    *

                    dt *

                    .25;


                t.rotation.z =

                    Math.sin(

                        t.userData.life *
                        2

                    )

                    *

                    .12;

            }
        );

    }


    document.getElementById(
        "timer"
    ).textContent =
        time.toFixed(1);


    const acc =
        shots

        ?

        Math.round(
            hits /
            shots *
            100
        )

        :

        0;


    document.getElementById(
        "score"
    ).textContent =

        `SCORE ${score} · HITS ${hits} · ACCURACY ${acc}%`;


    renderer.render(
        scene,
        camera
    );

}


loop();


// ================================
// RESIZE
// ================================

addEventListener(
    "resize",
    () => {

        camera.aspect =
            innerWidth /
            innerHeight;


        camera.updateProjectionMatrix();


        renderer.setSize(
            innerWidth,
            innerHeight
        );

    }
);

</script>

</body>
</html>
"""

components.html(
    html,
    height=800,
    scrolling=False
)
