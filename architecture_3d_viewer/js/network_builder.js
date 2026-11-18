/**
 * 3D Neural Architecture Procedural Builder
 * Generates physical 3D tensor volumes, holographic wireframes, conduits, and animated particle streams.
 * Includes enhanced multi-line clinical telemetry banners and animated flow markers.
 */

class NetworkBuilder {
    constructor(sceneManager, archData) {
        this.sm = sceneManager;
        this.data = archData;

        // Container groups
        this.networkGroup = new THREE.Group();
        this.conduitsGroup = new THREE.Group();
        this.particlesGroup = new THREE.Group();
        this.labelsGroup = new THREE.Group();
        this.arrowsGroup = new THREE.Group();

        this.sm.scene.add(this.networkGroup);
        this.sm.scene.add(this.conduitsGroup);
        this.sm.scene.add(this.particlesGroup);
        this.sm.scene.add(this.labelsGroup);
        this.sm.scene.add(this.arrowsGroup);

        // Raycastable meshes
        this.interactiveMeshes = [];
        this.layerMeshesById = {};

        // Dataflow particle systems
        this.streamParticles = [];
        this.isSimulatingWave = false;
        this.waveProgress = 0;

        this.init();
    }

    init() {
        this.createLayers();
        this.createConduits();
        this.createDataflowStreams();
        this.createLayerLabels();
        this.createDirectionalArrows();

        // Register updater in scene render loop
        this.sm.updatables.push((delta, elapsed) => this.update(delta, elapsed));
    }

    createCTScanTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');

        // Background
        ctx.fillStyle = '#05070a';
        ctx.fillRect(0, 0, 256, 256);

        // Abdominal boundary (oval)
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.ellipse(128, 128, 110, 85, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Left & Right Kidneys
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.ellipse(80, 125, 28, 48, -0.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(176, 125, 28, 48, 0.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Renal parenchyma gradient (Cyst lesion)
        const grad = ctx.createRadialGradient(80, 115, 5, 80, 125, 30);
        grad.addColorStop(0, 'rgba(56, 189, 248, 0.75)');
        grad.addColorStop(0.5, 'rgba(30, 41, 59, 0.85)');
        grad.addColorStop(1, 'rgba(15, 23, 42, 0.95)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(80, 115, 14, 0, Math.PI * 2);
        ctx.fill();

        // Grid lines overlay
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(128, 20); ctx.lineTo(128, 236);
        ctx.moveTo(20, 128); ctx.lineTo(236, 128);
        ctx.stroke();

        // Crosshairs & Text
        ctx.fillStyle = '#38bdf8';
        ctx.font = 'bold 12px monospace';
        ctx.fillText('AXIAL CT: 224x224', 20, 28);
        ctx.fillText('L', 225, 132);
        ctx.fillText('R', 18, 132);

        return new THREE.CanvasTexture(canvas);
    }

    createLayers() {
        const ctTexture = this.createCTScanTexture();

        this.data.layers.forEach((layer) => {
            const { w, h, d } = layer.size;
            const geo = new THREE.BoxGeometry(w, h, d);

            let materials;
            if (layer.id === 'input') {
                const baseMat = new THREE.MeshPhysicalMaterial({
                    color: 0x0f172a,
                    metalness: 0.2,
                    roughness: 0.3,
                    transmission: 0.6,
                    transparent: true,
                    opacity: 0.85
                });
                const ctMat = new THREE.MeshBasicMaterial({ map: ctTexture });
                materials = [baseMat, baseMat, baseMat, baseMat, ctMat, ctMat];
            } else {
                materials = new THREE.MeshPhysicalMaterial({
                    color: layer.color,
                    emissive: layer.color,
                    emissiveIntensity: 0.2,
                    metalness: 0.1,
                    roughness: 0.2,
                    transmission: 0.55,
                    transparent: true,
                    opacity: 0.85,
                    ior: 1.4
                });
            }

            const mesh = new THREE.Mesh(geo, materials);
            mesh.position.set(layer.position.x, layer.position.y, layer.position.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            mesh.userData = {
                layerData: layer,
                originalColor: layer.color,
                originalScale: new THREE.Vector3(1, 1, 1),
                isLayer: true
            };

            // Glowing Wireframe Edge Cage
            const wireGeo = new THREE.EdgesGeometry(geo);
            const wireMat = new THREE.LineBasicMaterial({
                color: layer.wireColor,
                linewidth: 2,
                transparent: true,
                opacity: 0.9
            });
            const wireframe = new THREE.LineSegments(wireGeo, wireMat);
            mesh.add(wireframe);
            mesh.wireframe = wireframe;

            // Internal Grid / Slices to visualize Channel Depth
            if (layer.dimensions.c > 3 && layer.dimensions.c <= 768) {
                const sliceCount = Math.min(8, Math.floor(w * 1.5));
                for (let s = 1; s < sliceCount; s++) {
                    const sliceGeo = new THREE.PlaneGeometry(h * 0.96, d * 0.96);
                    const sliceMat = new THREE.MeshBasicMaterial({
                        color: layer.color,
                        transparent: true,
                        opacity: 0.08,
                        side: THREE.DoubleSide
                    });
                    const sliceMesh = new THREE.Mesh(sliceGeo, sliceMat);
                    sliceMesh.rotation.y = Math.PI / 2;
                    sliceMesh.position.x = -w / 2 + (w / sliceCount) * s;
                    mesh.add(sliceMesh);
                }
            }

            // Special node rendering for Classification Head
            if (layer.id === 'classifier' && layer.nodes) {
                const nodeColors = [0x38bdf8, 0x22c55e, 0xf59e0b, 0xef4444];
                layer.nodes.forEach((node, nIdx) => {
                    const sphereGeo = new THREE.SphereGeometry(0.42, 16, 16);
                    const sphereMat = new THREE.MeshStandardMaterial({
                        color: nodeColors[nIdx],
                        emissive: nodeColors[nIdx],
                        emissiveIntensity: 0.65,
                        metalness: 0.3,
                        roughness: 0.2
                    });
                    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
                    sphere.position.set(0.9, (nIdx - 1.5) * 1.0, 0);
                    mesh.add(sphere);
                });
            }

            // Stage 4 Grad-CAM Pulsing Halo Ring
            if (layer.id === 'stage4') {
                const ringGeo = new THREE.RingGeometry(2.4, 2.7, 32);
                const ringMat = new THREE.MeshBasicMaterial({
                    color: 0xec4899,
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.75
                });
                this.stage4Halo = new THREE.Mesh(ringGeo, ringMat);
                this.stage4Halo.rotation.y = Math.PI / 2;
                this.stage4Halo.position.set(0, 0, 0);
                mesh.add(this.stage4Halo);
            }

            this.networkGroup.add(mesh);
            this.interactiveMeshes.push(mesh);
            this.layerMeshesById[layer.id] = mesh;
        });
    }

    createConduits() {
        for (let i = 0; i < this.data.layers.length - 1; i++) {
            const current = this.data.layers[i];
            const next = this.data.layers[i + 1];

            const curX = current.position.x + current.size.w / 2;
            const nextX = next.position.x - next.size.w / 2;
            const length = nextX - curX;
            const midX = curX + length / 2;

            const rStart = current.size.h * 0.35;
            const rEnd = next.size.h * 0.35;

            const conduitGeo = new THREE.CylinderGeometry(rEnd, rStart, length, 16, 1, true);
            conduitGeo.rotateZ(Math.PI / 2);

            const conduitMat = new THREE.MeshBasicMaterial({
                color: current.color,
                wireframe: true,
                transparent: true,
                opacity: 0.16
            });

            const conduit = new THREE.Mesh(conduitGeo, conduitMat);
            conduit.position.set(midX, 0, 0);
            this.conduitsGroup.add(conduit);
        }
    }

    createDirectionalArrows() {
        // Floating glowing arrow markers pointing along the flow
        for (let i = 0; i < this.data.layers.length - 1; i++) {
            const current = this.data.layers[i];
            const next = this.data.layers[i + 1];
            const curX = current.position.x + current.size.w / 2;
            const nextX = next.position.x - next.size.w / 2;
            const midX = (curX + nextX) / 2;

            const coneGeo = new THREE.ConeGeometry(0.35, 0.9, 12);
            coneGeo.rotateZ(-Math.PI / 2); // Point right (+X)
            const coneMat = new THREE.MeshBasicMaterial({
                color: 0x38bdf8,
                transparent: true,
                opacity: 0.8
            });
            const arrow = new THREE.Mesh(coneGeo, coneMat);
            arrow.position.set(midX, current.size.h / 2 + 0.8, 0);
            this.arrowsGroup.add(arrow);
        }
    }

    createDataflowStreams() {
        const particleCountPerStream = 25;
        this.streamPaths = [];

        for (let i = 0; i < this.data.layers.length - 1; i++) {
            const current = this.data.layers[i];
            const next = this.data.layers[i + 1];

            const p1 = new THREE.Vector3(current.position.x + current.size.w / 2, 0, 0);
            const p2 = new THREE.Vector3(next.position.x - next.size.w / 2, 0, 0);
            const curve = new THREE.LineCurve3(p1, p2);

            const geo = new THREE.BufferGeometry();
            const posArray = new Float32Array(particleCountPerStream * 3);

            for (let j = 0; j < particleCountPerStream; j++) {
                const t = j / particleCountPerStream;
                const pt = curve.getPoint(t);
                posArray[j * 3] = pt.x;
                posArray[j * 3 + 1] = pt.y + (Math.random() - 0.5) * 0.6;
                posArray[j * 3 + 2] = pt.z + (Math.random() - 0.5) * 0.6;
            }

            geo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

            const mat = new THREE.PointsMaterial({
                color: next.color,
                size: 0.38,
                transparent: true,
                opacity: 0.88,
                blending: THREE.AdditiveBlending
            });

            const pSystem = new THREE.Points(geo, mat);
            pSystem.userData = {
                curve: curve,
                stageIndex: i,
                baseColor: next.color
            };

            this.particlesGroup.add(pSystem);
            this.streamParticles.push(pSystem);
        }
    }

    createLayerLabels() {
        // Informative, multi-line telemetry cards above each stage
        this.data.layers.forEach((layer) => {
            const canvas = document.createElement('canvas');
            canvas.width = 360;
            canvas.height = 110;
            const ctx = canvas.getContext('2d');

            // Background
            ctx.fillStyle = 'rgba(11, 17, 29, 0.9)';
            ctx.roundRect(6, 6, 348, 98, 12);
            ctx.fill();
            ctx.strokeStyle = layer.id === 'stage4' ? '#ec4899' : 'rgba(56, 189, 248, 0.45)';
            ctx.lineWidth = layer.id === 'stage4' ? 3 : 2;
            ctx.stroke();

            // Stage Title
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 22px Outfit, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(layer.name.split(':')[0], 180, 36);

            // Tensor Dimensions & Resolution
            ctx.fillStyle = layer.id === 'stage4' ? '#f472b6' : '#38bdf8';
            ctx.font = 'bold 18px JetBrains Mono, monospace';
            ctx.fillText(layer.shape, 180, 64);

            // Receptive Field & Specs
            ctx.fillStyle = '#94a3b8';
            ctx.font = '14px Inter, sans-serif';
            const extra = layer.resolution ? `${layer.resolution} • ${layer.receptiveField}` : `Params: ${(layer.params || 0).toLocaleString()}`;
            ctx.fillText(extra, 180, 88);

            const texture = new THREE.CanvasTexture(canvas);
            const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.95 });
            const sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(6.8, 2.1, 1);
            sprite.position.set(layer.position.x, layer.size.h / 2 + 2.8, 0);

            this.labelsGroup.add(sprite);
        });
    }

    triggerInferenceWave(caseData, onComplete) {
        this.isSimulatingWave = true;
        this.waveProgress = 0;

        const duration = 2800;
        const startTime = performance.now();

        const animateWave = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(1, elapsed / duration);
            this.waveProgress = progress;

            const activeStageIdx = Math.floor(progress * this.data.layers.length);
            this.data.layers.forEach((layer, idx) => {
                const mesh = this.layerMeshesById[layer.id];
                if (mesh) {
                    if (idx === activeStageIdx) {
                        mesh.material.emissiveIntensity = 0.9;
                        mesh.scale.set(1.08, 1.08, 1.08);
                    } else {
                        mesh.material.emissiveIntensity = 0.2;
                        mesh.scale.set(1, 1, 1);
                    }
                }
            });

            if (progress < 1) {
                requestAnimationFrame(animateWave);
            } else {
                this.isSimulatingWave = false;
                this.data.layers.forEach((layer) => {
                    const mesh = this.layerMeshesById[layer.id];
                    if (mesh) {
                        mesh.material.emissiveIntensity = 0.2;
                        mesh.scale.set(1, 1, 1);
                    }
                });
                if (onComplete) onComplete();
            }
        };

        requestAnimationFrame(animateWave);
    }

    update(delta, elapsed) {
        const speed = this.isSimulatingWave ? 2.5 : 0.8;

        this.streamParticles.forEach((pSystem) => {
            const positions = pSystem.geometry.attributes.position.array;
            const count = positions.length / 3;
            const curve = pSystem.userData.curve;

            for (let i = 0; i < count; i++) {
                let t = ((elapsed * speed * 0.4 + i / count) % 1);
                const pt = curve.getPoint(t);
                positions[i * 3] = pt.x;
                positions[i * 3 + 1] = pt.y + Math.sin(elapsed * 3 + i) * 0.15;
                positions[i * 3 + 2] = pt.z + Math.cos(elapsed * 3 + i) * 0.15;
            }

            pSystem.geometry.attributes.position.needsUpdate = true;
        });

        // Halo rotation on Stage 4
        if (this.stage4Halo) {
            this.stage4Halo.rotation.z += delta * 1.5;
            this.stage4Halo.scale.setScalar(1.0 + Math.sin(elapsed * 3) * 0.08);
        }

        if (this.sm.stage4Glow) {
            this.sm.stage4Glow.intensity = 1.8 + Math.sin(elapsed * 2.5) * 0.6;
        }
    }

    setWireframeVisible(visible) {
        this.interactiveMeshes.forEach((mesh) => {
            if (mesh.wireframe) {
                mesh.wireframe.visible = visible;
            }
        });
    }

    setDataflowVisible(visible) {
        this.particlesGroup.visible = visible;
        this.arrowsGroup.visible = visible;
    }

    setVisible(visible) {
        this.networkGroup.visible = visible;
        this.conduitsGroup.visible = visible;
        this.particlesGroup.visible = visible;
        this.labelsGroup.visible = visible;
        this.arrowsGroup.visible = visible;
    }
}
