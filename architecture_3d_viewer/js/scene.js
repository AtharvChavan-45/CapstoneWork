/**
 * Three.js Scene Setup & Render Engine
 * Manages WebGL context, camera rigs, lighting, particle dust, and smooth transitions.
 */

class SceneManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;

        // Three.js Core Components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;

        // Animation & Render State
        this.clock = new THREE.Clock();
        this.animating = true;
        this.autoRotate = false;
        this.updatables = [];

        // Camera Viewpoints Presets
        this.cameraPresets = {
            isometric: { pos: new THREE.Vector3(18, 24, 38), target: new THREE.Vector3(0, 0, 0) },
            flow: { pos: new THREE.Vector3(0, 10, 48), target: new THREE.Vector3(0, 0, 0) },
            top: { pos: new THREE.Vector3(0, 52, 0.1), target: new THREE.Vector3(0, 0, 0) },
            stage4: { pos: new THREE.Vector3(15, 6, 18), target: new THREE.Vector3(15, 0, 0) },
            head: { pos: new THREE.Vector3(29, 6, 16), target: new THREE.Vector3(29, 0, 0) },
            exploded: { pos: new THREE.Vector3(0, 18, 32), target: new THREE.Vector3(0, 0, 0) }
        };

        this.init();
    }

    init() {
        // 1. Create Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x07090e);
        this.scene.fog = new THREE.FogExp2(0x07090e, 0.012);

        // 2. Camera Setup (Perspective)
        this.camera = new THREE.PerspectiveCamera(45, this.width / this.height, 0.1, 1000);
        this.camera.position.copy(this.cameraPresets.isometric.pos);

        // 3. WebGL Renderer with High-DPI & Antialiasing
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
        this.renderer.setSize(this.width, this.height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.15;
        this.container.appendChild(this.renderer.domElement);

        // 4. OrbitControls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxDistance = 140;
        this.controls.minDistance = 8;
        this.controls.maxPolarAngle = Math.PI / 2 + 0.05; // Don't dip far below floor
        this.controls.target.copy(this.cameraPresets.isometric.target);

        // 5. Lighting Rig
        this.setupLighting();

        // 6. Cybernetic Floor Grid & Hologram Effect
        this.setupGridAndFloor();

        // 7. Ambient Particle Space Dust
        this.setupSpaceDust();

        // 8. Event Listeners
        window.addEventListener('resize', () => this.onWindowResize());

        // 9. Start Render Loop
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    setupLighting() {
        // Ambient soft illumination
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
        this.scene.add(ambientLight);

        // Main key light (Cool white directional)
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
        keyLight.position.set(30, 45, 30);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        keyLight.shadow.bias = -0.0005;
        this.scene.add(keyLight);

        // Rim Light (Cyber Cyan Accent)
        const rimCyan = new THREE.DirectionalLight(0x38bdf8, 1.4);
        rimCyan.position.set(-35, 20, -25);
        this.scene.add(rimCyan);

        // Warm Fill Light (Bio-telemetry Accent)
        const fillViolet = new THREE.DirectionalLight(0x818cf8, 0.9);
        fillViolet.position.set(0, -20, 25);
        this.scene.add(fillViolet);

        // Point light at the Grad-CAM stage for dramatic focus
        this.stage4Glow = new THREE.PointLight(0xec4899, 2.0, 30);
        this.stage4Glow.position.set(15, 2, 0);
        this.scene.add(this.stage4Glow);
    }

    setupGridAndFloor() {
        // Holographic infinite grid
        const gridHelper = new THREE.GridHelper(120, 60, 0x38bdf8, 0x1e293b);
        gridHelper.position.y = -6;
        gridHelper.material.opacity = 0.25;
        gridHelper.material.transparent = true;
        this.scene.add(gridHelper);

        // Subtle reflective plane beneath the network
        const floorGeo = new THREE.PlaneGeometry(160, 160);
        const floorMat = new THREE.MeshStandardMaterial({
            color: 0x07090e,
            roughness: 0.85,
            metalness: 0.1,
            transparent: true,
            opacity: 0.8
        });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -6.02;
        floor.receiveShadow = true;
        this.scene.add(floor);
    }

    setupSpaceDust() {
        // Floating bio-telemetry ambient particles
        const particleCount = 350;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);

        const colorPalette = [
            new THREE.Color(0x38bdf8),
            new THREE.Color(0x818cf8),
            new THREE.Color(0x10b981),
            new THREE.Color(0xec4899)
        ];

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 120;
            positions[i * 3 + 1] = Math.random() * 40 - 5;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 90;

            const c = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors[i * 3] = c.r;
            colors[i * 3 + 1] = c.g;
            colors[i * 3 + 2] = c.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.5,
            vertexColors: true,
            transparent: true,
            opacity: 0.45,
            blending: THREE.AdditiveBlending
        });

        this.spaceDust = new THREE.Points(geometry, material);
        this.scene.add(this.spaceDust);

        this.updatables.push((delta) => {
            this.spaceDust.rotation.y += delta * 0.015;
        });
    }

    onWindowResize() {
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.width, this.height);
    }

    animate(time) {
        if (!this.animating) return;
        requestAnimationFrame(this.animate);

        const delta = this.clock.getDelta();

        // Update TWEEN animations
        if (window.TWEEN) {
            TWEEN.update(time);
        }

        // Auto rotate if enabled
        if (this.autoRotate) {
            this.controls.autoRotate = true;
            this.controls.autoRotateSpeed = 1.0;
        } else {
            this.controls.autoRotate = false;
        }

        // Update custom animated elements
        for (let i = 0; i < this.updatables.length; i++) {
            this.updatables[i](delta, time * 0.001);
        }

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    transitionCameraTo(targetPos, targetLookAt, duration = 1200) {
        if (!window.TWEEN) {
            this.camera.position.copy(targetPos);
            this.controls.target.copy(targetLookAt);
            return;
        }

        const startPos = this.camera.position.clone();
        const startTarget = this.controls.target.clone();

        new TWEEN.Tween(startPos)
            .to(targetPos, duration)
            .easing(TWEEN.Easing.Cubic.Out)
            .onUpdate(() => {
                this.camera.position.copy(startPos);
            })
            .start();

        new TWEEN.Tween(startTarget)
            .to(targetLookAt, duration)
            .easing(TWEEN.Easing.Cubic.Out)
            .onUpdate(() => {
                this.controls.target.copy(startTarget);
            })
            .start();
    }

    setCameraPreset(presetName) {
        const preset = this.cameraPresets[presetName];
        if (preset) {
            this.transitionCameraTo(preset.pos, preset.target);
        }
    }
}
