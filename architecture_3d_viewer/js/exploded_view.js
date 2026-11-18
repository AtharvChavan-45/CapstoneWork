/**
 * 3D Exploded View: PCSA-KidneyNeXt Block Decomposition
 * Visually unravels the 4 parallel pathways, 1x1 compression, dual-attention engine, and residual skip connection.
 * Includes floating 3D labels and directional signal flow conduits for presentation clarity.
 */

class ExplodedPCSAView {
    constructor(sceneManager, archData) {
        this.sm = sceneManager;
        this.data = archData;

        this.group = new THREE.Group();
        this.group.visible = false;
        this.sm.scene.add(this.group);

        this.interactiveMeshes = [];
        this.flowParticles = [];
        this.labelSprites = [];

        this.init();
    }

    init() {
        this.createInputNode();
        this.createFourBranches();
        this.createCompressionNode();
        this.createDualAttentionEngine();
        this.createResidualSkipConnection();
        this.createOutputNode();
        this.createConnectingRibbons();
        this.create3DBadgeLabels();

        // Register updater in scene render loop
        this.sm.updatables.push((delta, elapsed) => this.update(delta, elapsed));
    }

    createBadgeSprite(title, subtitle, colorHex, bgColor = 'rgba(14, 20, 34, 0.88)') {
        const canvas = document.createElement('canvas');
        canvas.width = 380;
        canvas.height = 110;
        const ctx = canvas.getContext('2d');

        // Background rounded box with glowing border
        ctx.fillStyle = bgColor;
        ctx.roundRect(6, 6, 368, 98, 12);
        ctx.fill();
        ctx.strokeStyle = colorHex;
        ctx.lineWidth = 3;
        ctx.stroke();

        // Title text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 24px Outfit, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(title, 190, 42);

        // Subtitle text
        ctx.fillStyle = colorHex;
        ctx.font = 'bold 18px JetBrains Mono, monospace';
        ctx.fillText(subtitle, 190, 78);

        const texture = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.95 });
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(6.8, 2.0, 1);
        return sprite;
    }

    createInputNode() {
        const geo = new THREE.BoxGeometry(2.5, 4.5, 4.5);
        const mat = new THREE.MeshPhysicalMaterial({
            color: 0x38bdf8,
            emissive: 0x0284c7,
            emissiveIntensity: 0.25,
            roughness: 0.2,
            transmission: 0.5,
            transparent: true,
            opacity: 0.85
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(-18, 0, 0);

        // Wireframe
        const wire = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x0284c7, linewidth: 2 }));
        mesh.add(wire);

        mesh.userData = {
            name: "Input Feature Map (X)",
            type: "Block Input",
            shape: "[B, C_in, H, W]",
            formula: "X \\in \\mathbb{R}^{B \\times C_{in} \\times H \\times W}",
            desc: "Input features arriving at the KidneyNeXt block. Serves as dual inputs: distributed into the 4 multi-receptive branches and channeled into the residual skip connection.",
            isExplodedComponent: true
        };

        this.group.add(mesh);
        this.interactiveMeshes.push(mesh);
        this.inputMesh = mesh;
    }

    createFourBranches() {
        const branchConfigs = [
            { id: "maxpool", name: "Branch 1: 3×3 MaxPool", subtitle: "High-Density Peaks (Stone)", y: 7.5, color: 0x38bdf8, wire: 0x0284c7, formula: "P_{max} = \\text{MaxPool2d}(k=3, s=stride, p=1)", role: "Extracts dominant spatial peaks and high-attenuation calcification frontiers." },
            { id: "avgpool", name: "Branch 2: 3×3 AvgPool", subtitle: "Diffuse Parenchyma Contrast", y: 2.5, color: 0x818cf8, wire: 0x4f46e5, formula: "P_{avg} = \\text{AvgPool2d}(k=3, s=stride, p=1)", role: "Preserves diffuse background renal parenchymal baseline contrast." },
            { id: "conv3", name: "Branch 3: 3×3 GroupConv", subtitle: "Micro-Lesion Margins", y: -2.5, color: 0x10b981, wire: 0x059669, formula: "G_{3\\times 3} = \\text{Conv2d}(k=3, \\text{groups}=C_{in})", role: "Isolates localized kidney micro-textures and cystic wall borders." },
            { id: "conv5", name: "Branch 4: 5×5 GroupConv", subtitle: "Extended Regional Context", y: -7.5, color: 0xf59e0b, wire: 0xd97706, formula: "G_{5\\times 5} = \\text{Conv2d}(k=5, \\text{groups}=C_{in})", role: "Broader receptive field capturing mass margins and renal pelvis morphology." }
        ];

        this.branchMeshes = [];

        branchConfigs.forEach((cfg) => {
            const geo = new THREE.BoxGeometry(3.5, 2.2, 2.2);
            const mat = new THREE.MeshPhysicalMaterial({
                color: cfg.color,
                emissive: cfg.color,
                emissiveIntensity: 0.25,
                roughness: 0.25,
                transmission: 0.55,
                transparent: true,
                opacity: 0.85
            });
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.set(-8, cfg.y, 0);

            const wire = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: cfg.wire, linewidth: 2 }));
            mesh.add(wire);

            mesh.userData = {
                name: cfg.name,
                type: "Multi-Receptive Parallel Pathway",
                shape: "[B, C_in, H', W']",
                formula: cfg.formula,
                desc: cfg.role,
                isExplodedComponent: true,
                badgeTitle: cfg.name,
                badgeSub: cfg.subtitle,
                badgeColor: cfg.wire
            };

            this.group.add(mesh);
            this.interactiveMeshes.push(mesh);
            this.branchMeshes.push(mesh);
        });
    }

    createCompressionNode() {
        const geo = new THREE.BoxGeometry(3.2, 5.5, 3.8);
        const mat = new THREE.MeshPhysicalMaterial({
            color: 0xa855f7, // Purple
            emissive: 0x7e22ce,
            emissiveIntensity: 0.28,
            roughness: 0.2,
            transmission: 0.6,
            transparent: true,
            opacity: 0.85
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(2, 0, 0);

        const wire = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x9333ea, linewidth: 2 }));
        mesh.add(wire);

        mesh.userData = {
            name: "Channel Fusion & 1×1 Compression",
            type: "Pointwise Convolution + BN + GELU",
            shape: "[B, C_out, H', W']",
            formula: "F = \\text{GELU}(\\text{BN}(\\text{Conv}_{1\\times 1}([P_{max}, P_{avg}, G_3, G_5])))",
            desc: "Concatenates all 4 parallel pathways into a dense 4x feature tensor, then linearly compresses channels down to C_out with Batch Normalization and GELU activation.",
            isExplodedComponent: true
        };

        this.group.add(mesh);
        this.interactiveMeshes.push(mesh);
        this.compressionMesh = mesh;
    }

    createDualAttentionEngine() {
        // Channel Attention
        const cGeo = new THREE.BoxGeometry(3.4, 2.8, 2.8);
        const cMat = new THREE.MeshPhysicalMaterial({
            color: 0xec4899, // Pink
            emissive: 0xbe185d,
            emissiveIntensity: 0.35,
            roughness: 0.2,
            transmission: 0.55,
            transparent: true,
            opacity: 0.88
        });
        const cMesh = new THREE.Mesh(cGeo, cMat);
        cMesh.position.set(10, 3.2, 0);
        cMesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(cGeo), new THREE.LineBasicMaterial({ color: 0xdb2777, linewidth: 2 })));

        cMesh.userData = {
            name: "Pyramid Channel Attention (PCSA-C)",
            type: "Dual-Pooling MLP Weighting",
            shape: "[B, C_out, 1, 1]",
            formula: "M_c = \\sigma(\\text{MLP}(\\text{AvgPool}(F)) + \\text{MLP}(\\text{MaxPool}(F)))",
            desc: "Extracts global spatial context via both Average and Max pooling, passed through a shared MLP with 16x reduction. Dynamically boosts channels sensitive to pathological indicators.",
            isExplodedComponent: true
        };

        this.group.add(cMesh);
        this.interactiveMeshes.push(cMesh);
        this.channelAttnMesh = cMesh;

        // Spatial Attention
        const sGeo = new THREE.BoxGeometry(3.4, 2.8, 2.8);
        const sMat = new THREE.MeshPhysicalMaterial({
            color: 0xf43f5e, // Rose
            emissive: 0xe11d48,
            emissiveIntensity: 0.35,
            roughness: 0.2,
            transmission: 0.55,
            transparent: true,
            opacity: 0.88
        });
        const sMesh = new THREE.Mesh(sGeo, sMat);
        sMesh.position.set(10, -3.2, 0);
        sMesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(sGeo), new THREE.LineBasicMaterial({ color: 0xe11d48, linewidth: 2 })));

        sMesh.userData = {
            name: "Multiscale Spatial Attention (PCSA-S)",
            type: "Dual-Kernel (3×3 + 5×5) Spatial Re-weighting",
            shape: "[B, 1, H', W']",
            formula: "M_s = \\sigma(\\text{Conv}_{3\\times 3}([M_{max}, M_{avg}]) + \\text{Conv}_{5\\times 5}([M_{max}, M_{avg}]))",
            desc: "Concatenates inter-channel max and average maps, followed by parallel 3x3 and 5x5 convolutions to produce a multiscale 2D spatial attention mask focusing precisely on lesion coordinates.",
            isExplodedComponent: true
        };

        this.group.add(sMesh);
        this.interactiveMeshes.push(sMesh);
        this.spatialAttnMesh = sMesh;
    }

    createResidualSkipConnection() {
        const curve = new THREE.CubicBezierCurve3(
            new THREE.Vector3(-18, 2.5, 0),
            new THREE.Vector3(-10, 13, 5),
            new THREE.Vector3(10, 13, 5),
            new THREE.Vector3(18, 2.5, 0)
        );

        const tubeGeo = new THREE.TubeGeometry(curve, 48, 0.28, 8, false);
        const tubeMat = new THREE.MeshStandardMaterial({
            color: 0x00f5a0, // Vibrant Surgical Teal
            emissive: 0x00f5a0,
            emissiveIntensity: 0.7,
            roughness: 0.2,
            metalness: 0.8
        });
        const tube = new THREE.Mesh(tubeGeo, tubeMat);
        this.group.add(tube);

        // Glowing animated pulses along the skip connection
        this.skipPulses = [];
        for (let i = 0; i < 3; i++) {
            const pulseGeo = new THREE.SphereGeometry(0.45, 16, 16);
            const pulseMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const pulse = new THREE.Mesh(pulseGeo, pulseMat);
            this.group.add(pulse);
            this.skipPulses.push(pulse);
        }
        this.skipCurve = curve;
    }

    createOutputNode() {
        const geo = new THREE.BoxGeometry(2.8, 5.0, 5.0);
        const mat = new THREE.MeshPhysicalMaterial({
            color: 0x22c55e,
            emissive: 0x16a34a,
            emissiveIntensity: 0.35,
            roughness: 0.2,
            transmission: 0.55,
            transparent: true,
            opacity: 0.88
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(18, 0, 0);

        const wire = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0x16a34a, linewidth: 2 }));
        mesh.add(wire);

        mesh.userData = {
            name: "Residual Addition & Block Output (Y)",
            type: "Attention Fused Output",
            shape: "[B, C_out, H', W']",
            formula: "Y = M_s \\odot (M_c \\odot F) + \\text{Shortcut}(X)",
            desc: "The final output combining the PCSA dual-attended features with the identity shortcut. Passed directly to the subsequent hierarchical stage.",
            isExplodedComponent: true
        };

        this.group.add(mesh);
        this.interactiveMeshes.push(mesh);
        this.outputMesh = mesh;
    }

    createConnectingRibbons() {
        const lineMat = new THREE.LineBasicMaterial({
            color: 0x38bdf8,
            transparent: true,
            opacity: 0.38
        });

        // Input to 4 branches
        this.branchMeshes.forEach((bMesh) => {
            const points = [this.inputMesh.position, bMesh.position];
            const geo = new THREE.BufferGeometry().setFromPoints(points);
            this.group.add(new THREE.Line(geo, lineMat));

            // Branch to compression
            const points2 = [bMesh.position, this.compressionMesh.position];
            const geo2 = new THREE.BufferGeometry().setFromPoints(points2);
            this.group.add(new THREE.Line(geo2, lineMat));
        });

        // Compression to Channel & Spatial Attention
        this.group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([this.compressionMesh.position, this.channelAttnMesh.position]), lineMat));
        this.group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([this.compressionMesh.position, this.spatialAttnMesh.position]), lineMat));

        // Attention to Output
        this.group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([this.channelAttnMesh.position, this.outputMesh.position]), lineMat));
        this.group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([this.spatialAttnMesh.position, this.outputMesh.position]), lineMat));
    }

    create3DBadgeLabels() {
        // Pinned 3D badge cards floating next to each major component

        // 1. Input Badge
        const inBadge = this.createBadgeSprite("Input Tensor X", "[B, C_in, H, W]", "#38bdf8");
        inBadge.position.set(-18, 3.8, 0);
        this.group.add(inBadge);

        // 2. 4 Branch Badges
        const branchLabels = [
            { text: "Branch 1: MaxPool 3×3", sub: "Peak Densities", y: 9.3, color: "#38bdf8" },
            { text: "Branch 2: AvgPool 3×3", sub: "Diffuse Background", y: 4.3, color: "#818cf8" },
            { text: "Branch 3: DW-Conv 3×3", sub: "Micro Margins", y: -0.7, color: "#10b981" },
            { text: "Branch 4: DW-Conv 5×5", sub: "Regional Context", y: -5.7, color: "#f59e0b" }
        ];

        branchLabels.forEach((b) => {
            const s = this.createBadgeSprite(b.text, b.sub, b.color);
            s.position.set(-8, b.y, 0);
            s.scale.set(6.2, 1.8, 1);
            this.group.add(s);
        });

        // 3. Compression Badge
        const compBadge = this.createBadgeSprite("Channel Fusion", "1×1 Conv ➔ C_out", "#c084fc");
        compBadge.position.set(2, 4.4, 0);
        this.group.add(compBadge);

        // 4. Channel Attention Badge
        const cBadge = this.createBadgeSprite("Channel Attention", "MLP(Avg + Max)", "#ec4899");
        cBadge.position.set(10, 5.5, 0);
        this.group.add(cBadge);

        // 5. Spatial Attention Badge
        const sBadge = this.createBadgeSprite("Spatial Attention", "Conv 3×3 + 5×5", "#f43f5e");
        sBadge.position.set(10, -5.2, 0);
        this.group.add(sBadge);

        // 6. Residual Skip Badge
        const skipBadge = this.createBadgeSprite("Residual Skip Connection", "Identity / 1×1 Projection", "#00f5a0");
        skipBadge.position.set(0, 13.5, 5);
        this.group.add(skipBadge);

        // 7. Output Badge
        const outBadge = this.createBadgeSprite("Output Tensor Y", "[B, C_out, H', W']", "#22c55e");
        outBadge.position.set(18, 4.2, 0);
        this.group.add(outBadge);
    }

    update(delta, elapsed) {
        if (!this.group.visible) return;

        // Animate multiple pulse packets along the arched skip curve
        if (this.skipPulses && this.skipCurve) {
            this.skipPulses.forEach((pulse, idx) => {
                const offset = idx / this.skipPulses.length;
                const t = (elapsed * 0.45 + offset) % 1;
                const pt = this.skipCurve.getPoint(t);
                pulse.position.copy(pt);
            });
        }
    }

    setVisible(visible) {
        this.group.visible = visible;
    }
}
