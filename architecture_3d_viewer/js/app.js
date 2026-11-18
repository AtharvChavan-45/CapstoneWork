/**
 * Master Application Controller
 * Coordinates Three.js scene, user interactions, raycasting, HUD binding, simulation engine,
 * and the interactive Presenter Defense Mode with Examiner Talking Points.
 */

class AppController {
    constructor() {
        this.sceneManager = null;
        this.networkBuilder = null;
        this.explodedView = null;

        // Current State
        this.currentMode = 'overview';
        this.selectedCase = 'cyst_case';
        this.currentSlideIdx = 0;
        this.isPresenterActive = false;

        // Raycasting & Mouse State
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.hoveredMesh = null;
        this.selectedMesh = null;

        // UI References
        this.tooltip = document.getElementById('canvas-tooltip');
        this.hud = document.getElementById('layer-hud');
        this.inferenceModal = document.getElementById('inference-modal');
        this.pipelineModal = document.getElementById('pipeline-modal');
        this.benchmarkModal = document.getElementById('benchmark-modal');
        this.explodedLegend = document.getElementById('exploded-legend');
        this.presenterDock = document.getElementById('presenter-dock');

        this.init();
    }

    init() {
        // 1. Initialize 3D Scene
        this.sceneManager = new SceneManager('canvas-container');

        // 2. Initialize Network & Exploded Views
        this.networkBuilder = new NetworkBuilder(this.sceneManager, ARCHITECTURE_DATA);
        this.explodedView = new ExplodedPCSAView(this.sceneManager, ARCHITECTURE_DATA);

        // 3. Bind UI & Keyboard Events
        this.bindEvents();

        // 4. Default inspection: Stage 4 Bottleneck
        const defaultStage4 = ARCHITECTURE_DATA.layers.find(l => l.id === 'stage4');
        if (defaultStage4) {
            this.populateHUD(defaultStage4);
        }

        console.log("🧬 PCSA-KidneyNeXt 3D Visualizer Ready for Defense & Presentation!");
    }

    bindEvents() {
        const canvas = this.sceneManager.renderer.domElement;

        // Mouse Move for Raycast Hover
        canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));

        // Click for Layer Selection
        canvas.addEventListener('click', (e) => this.onClick(e));

        // Mode Switcher Tabs
        document.getElementById('tab-overview').addEventListener('click', () => this.switchMode('overview'));
        document.getElementById('tab-exploded').addEventListener('click', () => this.switchMode('exploded'));
        document.getElementById('tab-pipeline').addEventListener('click', () => this.openPipelineModal());

        // Camera Preset Buttons
        document.querySelectorAll('.cam-btn[data-view]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.cam-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const view = btn.getAttribute('data-view');
                this.sceneManager.setCameraPreset(view);
            });
        });

        document.getElementById('cam-reset').addEventListener('click', () => {
            this.sceneManager.setCameraPreset(this.currentMode === 'exploded' ? 'exploded' : 'isometric');
        });

        // Scene Toggles
        document.getElementById('toggle-wireframe').addEventListener('change', (e) => {
            this.networkBuilder.setWireframeVisible(e.target.checked);
        });

        document.getElementById('toggle-dataflow').addEventListener('change', (e) => {
            this.networkBuilder.setDataflowVisible(e.target.checked);
        });

        document.getElementById('toggle-autorotate').addEventListener('change', (e) => {
            this.sceneManager.autoRotate = e.target.checked;
        });

        // HUD Controls
        document.getElementById('hud-close-btn').addEventListener('click', () => {
            this.hud.classList.add('hidden');
        });

        document.getElementById('btn-open-exploded').addEventListener('click', () => {
            this.switchMode('exploded');
        });

        document.getElementById('btn-focus-layer').addEventListener('click', () => {
            if (this.selectedMesh) {
                const targetPos = this.selectedMesh.position.clone();
                const camPos = targetPos.clone().add(new THREE.Vector3(0, 5, 16));
                this.sceneManager.transitionCameraTo(camPos, targetPos);
            }
        });

        // Case Selector Buttons
        document.querySelectorAll('.case-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.case-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                this.selectedCase = card.getAttribute('data-case');
            });
        });

        // Run Forward Pass Simulation
        document.getElementById('btn-run-inference').addEventListener('click', () => {
            this.runInferenceSimulation();
        });

        // Modals Close Buttons
        document.getElementById('modal-close-btn').addEventListener('click', () => {
            this.inferenceModal.classList.remove('active');
        });

        document.getElementById('pipeline-close-btn').addEventListener('click', () => {
            this.pipelineModal.classList.remove('active');
        });

        document.getElementById('benchmark-close-btn').addEventListener('click', () => {
            this.benchmarkModal.classList.remove('active');
        });

        // Modal Sub-Navigation Tabs
        document.querySelectorAll('.modal-nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.modal-nav-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.modal-view-panel').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                const view = tab.getAttribute('data-view');
                const panel = document.getElementById(`modal-view-${view}`);
                if (panel) panel.classList.add('active');
            });
        });

        // Benchmark Modal Trigger
        document.getElementById('btn-benchmark').addEventListener('click', () => {
            this.benchmarkModal.classList.add('active');
        });

        // Presenter Defense Mode Controls
        document.getElementById('btn-presenter').addEventListener('click', () => {
            this.togglePresenterMode();
        });

        document.getElementById('dock-close-btn').addEventListener('click', () => {
            this.presenterDock.classList.remove('active');
            this.isPresenterActive = false;
        });

        document.getElementById('dock-btn-next').addEventListener('click', () => {
            this.nextSlide();
        });

        document.getElementById('dock-btn-prev').addEventListener('click', () => {
            this.prevSlide();
        });

        // Keyboard Shortcuts for Presentation Defense
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                if (this.isPresenterActive) {
                    e.preventDefault();
                    this.nextSlide();
                }
            } else if (e.key === 'ArrowLeft') {
                if (this.isPresenterActive) {
                    e.preventDefault();
                    this.prevSlide();
                }
            } else if (e.key === 'Escape') {
                this.inferenceModal.classList.remove('active');
                this.pipelineModal.classList.remove('active');
                this.benchmarkModal.classList.remove('active');
                this.presenterDock.classList.remove('active');
                this.isPresenterActive = false;
            }
        });
    }

    onMouseMove(e) {
        const rect = this.sceneManager.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.sceneManager.camera);
        const targetMeshes = this.currentMode === 'exploded' 
            ? this.explodedView.interactiveMeshes 
            : this.networkBuilder.interactiveMeshes;

        const intersects = this.raycaster.intersectObjects(targetMeshes);

        if (intersects.length > 0) {
            const hit = intersects[0].object;
            if (this.hoveredMesh !== hit) {
                this.resetHover();
                this.hoveredMesh = hit;
                this.applyHover(hit);
            }

            const data = hit.userData.layerData || hit.userData;
            this.tooltip.querySelector('.tooltip-title').textContent = data.name || "Layer";
            this.tooltip.querySelector('.tooltip-shape').textContent = data.shape || "";
            this.tooltip.style.left = `${e.clientX + 14}px`;
            this.tooltip.style.top = `${e.clientY - 25}px`;
            this.tooltip.classList.add('visible');
        } else {
            this.resetHover();
            this.tooltip.classList.remove('visible');
        }
    }

    applyHover(mesh) {
        document.body.style.cursor = 'pointer';
        if (mesh.material && mesh.material.emissiveIntensity !== undefined) {
            mesh.material.emissiveIntensity = 0.6;
        }
    }

    resetHover() {
        document.body.style.cursor = 'default';
        if (this.hoveredMesh && this.hoveredMesh !== this.selectedMesh) {
            if (this.hoveredMesh.material && this.hoveredMesh.material.emissiveIntensity !== undefined) {
                this.hoveredMesh.material.emissiveIntensity = 0.2;
            }
        }
        this.hoveredMesh = null;
    }

    onClick(e) {
        if (!this.hoveredMesh) return;

        this.selectedMesh = this.hoveredMesh;
        const data = this.selectedMesh.userData.layerData || this.selectedMesh.userData;
        this.populateHUD(data);
        this.hud.classList.remove('hidden');
    }

    populateHUD(data) {
        document.getElementById('hud-stage').textContent = data.stage || data.type || "Layer Component";
        document.getElementById('hud-name').textContent = data.name;
        document.getElementById('hud-type').textContent = data.type;
        document.getElementById('hud-dims').textContent = data.shape;

        if (data.dimensions) {
            document.getElementById('hud-channels').textContent = data.dimensions.c;
            document.getElementById('hud-spatial').textContent = `${data.dimensions.h} × ${data.dimensions.w}`;
            document.getElementById('hud-params').textContent = (data.params || 0).toLocaleString();
        } else {
            document.getElementById('hud-channels').textContent = "Variable";
            document.getElementById('hud-spatial').textContent = "Dynamic";
            document.getElementById('hud-params').textContent = "N/A";
        }

        document.getElementById('hud-math').textContent = data.formula || "";
        document.getElementById('hud-desc').textContent = data.description || data.desc || "";
        document.getElementById('hud-clinical').textContent = data.clinicalRole || "Integral for multi-scale renal pathology feature extraction.";

        // Populate Architectural Telemetry
        const rfElem = document.getElementById('hud-rf');
        const downsampleElem = document.getElementById('hud-downsample');
        const paramPctElem = document.getElementById('hud-param-pct');
        const paramFillElem = document.getElementById('hud-param-fill');

        if (rfElem) rfElem.textContent = data.receptiveField || "Full Context";
        if (downsampleElem) downsampleElem.textContent = data.resolution || "Adaptive";

        const totalModelParams = 2114884;
        const pCount = data.params || 0;
        const pPct = ((pCount / totalModelParams) * 100).toFixed(1);

        if (paramPctElem) paramPctElem.textContent = `${pPct}% (${pCount.toLocaleString()} params)`;
        if (paramFillElem) paramFillElem.style.width = `${Math.max(2, Math.min(100, parseFloat(pPct)))}%`;
    }

    switchMode(mode) {
        this.currentMode = mode;

        document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
        const activeTab = document.getElementById(`tab-${mode}`);
        if (activeTab) activeTab.classList.add('active');

        if (mode === 'overview') {
            this.networkBuilder.setVisible(true);
            this.explodedView.setVisible(false);
            this.explodedLegend.style.display = 'none';
            this.sceneManager.setCameraPreset('isometric');
        } else if (mode === 'exploded') {
            this.networkBuilder.setVisible(false);
            this.explodedView.setVisible(true);
            this.explodedLegend.style.display = 'block';
            this.sceneManager.setCameraPreset('exploded');
        }
    }

    openPipelineModal() {
        this.pipelineModal.classList.add('active');
    }

    togglePresenterMode() {
        this.isPresenterActive = !this.isPresenterActive;
        if (this.isPresenterActive) {
            this.presenterDock.classList.add('active');
            this.goToSlide(0);
        } else {
            this.presenterDock.classList.remove('active');
        }
    }

    goToSlide(index) {
        const slides = ARCHITECTURE_DATA.presentation_slides;
        if (index < 0 || index >= slides.length) return;

        this.currentSlideIdx = index;
        const s = slides[index];

        // Update Dock UI
        document.getElementById('dock-step-badge').textContent = `Slide ${s.step} of ${slides.length}`;
        document.getElementById('dock-title').textContent = s.title;
        document.getElementById('dock-subtitle').textContent = s.subtitle;
        document.getElementById('dock-defense-q').textContent = s.examinerDefense;
        document.getElementById('dock-defense-a').textContent = s.examinerAnswer;

        const bulletsList = document.getElementById('dock-bullets-list');
        bulletsList.innerHTML = '';
        s.bullets.forEach(b => {
            const li = document.createElement('li');
            li.textContent = b;
            bulletsList.appendChild(li);
        });

        // Switch 3D view mode and camera position
        if (s.mode !== this.currentMode) {
            this.switchMode(s.mode);
        }
        this.sceneManager.setCameraPreset(s.cameraPreset);

        // Populate HUD with stage details
        const targetLayer = ARCHITECTURE_DATA.layers.find(l => l.id === s.stageId);
        if (targetLayer) {
            this.populateHUD(targetLayer);
            this.hud.classList.remove('hidden');
        }
    }

    nextSlide() {
        const slides = ARCHITECTURE_DATA.presentation_slides;
        const nextIdx = (this.currentSlideIdx + 1) % slides.length;
        this.goToSlide(nextIdx);
    }

    prevSlide() {
        const slides = ARCHITECTURE_DATA.presentation_slides;
        const prevIdx = (this.currentSlideIdx - 1 + slides.length) % slides.length;
        this.goToSlide(prevIdx);
    }

    runInferenceSimulation() {
        const caseObj = ARCHITECTURE_DATA.demo_cases.find(c => c.id === this.selectedCase);
        if (!caseObj) return;

        const runBtn = document.getElementById('btn-run-inference');
        runBtn.disabled = true;
        runBtn.innerHTML = `<span>⏳</span> Computing...`;

        if (this.currentMode !== 'overview') {
            this.switchMode('overview');
        }

        this.networkBuilder.triggerInferenceWave(caseObj, () => {
            runBtn.disabled = false;
            runBtn.innerHTML = `<span class="play-icon">⚡</span> Run Forward Pass`;
            this.displayInferenceResult(caseObj);
        });
    }

    displayInferenceResult(caseObj) {
        this.currentInferenceCase = caseObj;
        const modal = this.inferenceModal;
        const statusBadge = document.getElementById('modal-status-badge');
        const caseTitle = document.getElementById('modal-case-title');
        const actualTag = document.getElementById('modal-actual-tag');
        const findings = document.getElementById('modal-findings');

        caseTitle.textContent = caseObj.name;
        actualTag.textContent = `Actual: ${caseObj.actual} | Predicted: ${caseObj.predicted}`;
        findings.textContent = caseObj.findings;

        // Reset to Visual Feature Pipeline Tab by default
        document.querySelectorAll('.modal-nav-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.modal-view-panel').forEach(p => p.classList.remove('active'));
        const defTab = document.getElementById('modal-tab-btn-visual-flow');
        const defPanel = document.getElementById('modal-view-visual-flow');
        if (defTab) defTab.classList.add('active');
        if (defPanel) defPanel.classList.add('active');

        if (caseObj.isMisclassified) {
            statusBadge.className = 'modal-badge alert';
            statusBadge.textContent = '⚠️ Misclassification Detected';
            document.getElementById('cm-insight-text').innerHTML = `
                <strong>Rare Corner Case (Actual: Cyst ➔ Predicted: Stone):</strong><br>
                Matches the 2 misclassified cases in your Confusion Matrix ($740/742$ Cyst recall). The hyperdense proteinaceous cyst debris produced attenuation peaks resembling an unobstructed calcium stone.
            `;
        } else {
            statusBadge.className = 'modal-badge';
            statusBadge.textContent = `Diagnosis Verified: ${caseObj.predicted} (${caseObj.confidence})`;
            document.getElementById('cm-insight-text').innerHTML = `
                <strong>High-Confidence Match:</strong> Evaluated on the 2,490 unseen test set. Reflects the model's 99.92% overall accuracy and robust class-separation boundary.
            `;
        }

        // Probabilities Bars
        ['cyst', 'normal', 'stone', 'tumor'].forEach(cls => {
            const capitalized = cls.charAt(0).toUpperCase() + cls.slice(1);
            const prob = caseObj.probabilities[capitalized];
            document.getElementById(`prob-val-${cls}`).textContent = `${prob.toFixed(2)}%`;
            document.getElementById(`prob-bar-${cls}`).style.width = `${prob}%`;
        });

        // 1. Render Top Visual Pipeline Strip (Thumbnails 1..8)
        for (let s = 1; s <= 8; s++) {
            const thumbCanvas = document.getElementById(`thumb-canvas-${s}`);
            if (thumbCanvas) {
                const tctx = thumbCanvas.getContext('2d');
                this.drawStageVisual(tctx, thumbCanvas.width, thumbCanvas.height, s, caseObj);
            }
        }

        // Attach click listeners to pipeline strip nodes
        document.querySelectorAll('.pipeline-strip-node').forEach(node => {
            node.onclick = () => {
                const step = parseInt(node.getAttribute('data-step'));
                this.renderFeaturedStage(step, caseObj);
            };
        });

        // Initially feature Stage 6 (Stage 4 CAM) or Stage 1
        this.renderFeaturedStage(6, caseObj);

        // 2. Render Block-by-Block Visual Trace (8 Stages with Live Canvases)
        const traceContainer = document.getElementById('trace-cards-list');
        if (traceContainer && caseObj.block_trace) {
            traceContainer.innerHTML = '';
            caseObj.block_trace.forEach((b) => {
                const stepInt = parseInt(b.step);
                const card = document.createElement('div');
                card.className = 'trace-block-card';
                card.innerHTML = `
                    <div class="trace-card-grid">
                        <div class="trace-visual-col">
                            <canvas class="trace-block-canvas" id="trace-canvas-${b.step}" width="150" height="150"></canvas>
                            <span class="trace-canvas-caption">STAGE ${b.step} FEATURE MAP</span>
                        </div>
                        <div class="trace-details-col">
                            <div class="trace-block-top">
                                <div class="trace-step-tag">STAGE ${b.step} / 08</div>
                                <div class="trace-name-group">
                                    <h4 class="trace-block-name">${b.name}</h4>
                                    <span class="trace-stage-lbl">${b.stage}</span>
                                </div>
                                <div class="trace-shapes-badge">
                                    <span class="shape-in">${b.input_shape}</span>
                                    <span class="shape-arrow">➔</span>
                                    <span class="shape-out">${b.output_shape}</span>
                                </div>
                            </div>
                            <div class="trace-meta-grid">
                                <div class="trace-meta-col">
                                    <span class="trace-lbl">Transformation:</span>
                                    <strong class="trace-val">${b.operation}</strong>
                                </div>
                                <div class="trace-meta-col">
                                    <span class="trace-lbl">Receptive Field:</span>
                                    <strong class="trace-val highlight-cyan">${b.receptive_field}</strong>
                                </div>
                                <div class="trace-meta-col">
                                    <span class="trace-lbl">Weights:</span>
                                    <strong class="trace-val">${b.params.toLocaleString()} params</strong>
                                </div>
                            </div>
                            <div class="trace-feature-box">
                                <span class="trace-feat-title">Scan Feature Activation:</span>
                                <p class="trace-feat-desc">${b.feature_output}</p>
                            </div>
                        </div>
                    </div>
                `;
                traceContainer.appendChild(card);

                // Render the canvas for this block
                const blockCanvas = document.getElementById(`trace-canvas-${b.step}`);
                if (blockCanvas) {
                    const bctx = blockCanvas.getContext('2d');
                    this.drawStageVisual(bctx, blockCanvas.width, blockCanvas.height, stepInt, caseObj);
                }
            });
        }

        // 3. Render PCSA Visual Decomposition Canvases
        if (caseObj.pcsa_breakdown) {
            const pb = caseObj.pcsa_breakdown;
            const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
            setVal('pcsa-max-metric', pb.branch_max.split(' ')[0]);
            setVal('pcsa-max-desc', pb.branch_max);
            setVal('pcsa-avg-metric', pb.branch_avg.split(' ')[0]);
            setVal('pcsa-avg-desc', pb.branch_avg);
            setVal('pcsa-c3-metric', pb.branch_conv3.split(' ')[0]);
            setVal('pcsa-c3-desc', pb.branch_conv3);
            setVal('pcsa-c5-metric', pb.branch_conv5.split(' ')[0]);
            setVal('pcsa-c5-desc', pb.branch_conv5);
            setVal('pcsa-comp-desc', pb.compression);
            setVal('pcsa-ca-desc', pb.channel_attn);
            setVal('pcsa-sa-desc', pb.spatial_attn);
            setVal('pcsa-skip-desc', pb.residual_skip);

            // Render live canvases for each PCSA component
            const drawBranch = (canvasId, key) => {
                const c = document.getElementById(canvasId);
                if (c && window.FeatureMapRenderer) {
                    const ctx = c.getContext('2d');
                    FeatureMapRenderer.drawPCSABranch(ctx, c.width, c.height, caseObj.actual, caseObj.isMisclassified, key);
                }
            };
            drawBranch('pcsa-canvas-max', 'max');
            drawBranch('pcsa-canvas-avg', 'avg');
            drawBranch('pcsa-canvas-conv3', 'conv3');
            drawBranch('pcsa-canvas-conv5', 'conv5');
            drawBranch('pcsa-canvas-comp', 'max');
            drawBranch('pcsa-canvas-ca', 'channel_attn');
            drawBranch('pcsa-canvas-sa', 'spatial_attn');
            drawBranch('pcsa-canvas-skip', 'residual_skip');
        }

        // 4. Render Diagnostic Report Canvas
        const reportCanvas = document.getElementById('ct-canvas');
        if (reportCanvas && window.FeatureMapRenderer) {
            FeatureMapRenderer.drawCT(reportCanvas.getContext('2d'), reportCanvas.width, reportCanvas.height, caseObj.actual, caseObj.isMisclassified);
        }

        modal.classList.add('active');
    }

    renderFeaturedStage(stepNum, caseObj) {
        document.querySelectorAll('.pipeline-strip-node').forEach(n => {
            n.classList.toggle('active', parseInt(n.getAttribute('data-step')) === stepNum);
        });

        const featCanvas = document.getElementById('pipeline-featured-canvas');
        if (featCanvas) {
            const fctx = featCanvas.getContext('2d');
            this.drawStageVisual(fctx, featCanvas.width, featCanvas.height, stepNum, caseObj);
        }

        const b = caseObj.block_trace ? caseObj.block_trace[stepNum - 1] : null;
        if (b) {
            const stepBadge = document.getElementById('pipeline-step-badge');
            const titleEl = document.getElementById('pipeline-stage-title');
            const typeEl = document.getElementById('pipeline-stage-type');
            const shapeEl = document.getElementById('pipeline-stage-shape');
            const descEl = document.getElementById('pipeline-stage-desc');
            const cmapEl = document.getElementById('pipeline-colormap-tag');

            if (stepBadge) stepBadge.textContent = `STAGE 0${stepNum} OF 08`;
            if (titleEl) titleEl.textContent = b.name;
            if (typeEl) typeEl.textContent = `${b.stage} — ${b.operation}`;
            if (shapeEl) shapeEl.textContent = `Shape: ${b.output_shape} | RF: ${b.receptive_field}`;
            if (descEl) descEl.textContent = b.feature_output;
            if (cmapEl) {
                if (stepNum === 1) cmapEl.textContent = 'Colormap: Patient Hounsfield Grayscale';
                else if (stepNum === 6) cmapEl.textContent = 'Colormap: Grad-CAM Jet Class Activation Heatmap';
                else if (stepNum === 7) cmapEl.textContent = 'Colormap: 768-D Semantic Embedding Spectrum';
                else if (stepNum === 8) cmapEl.textContent = 'Colormap: Softmax Class Confidence Barcode';
                else cmapEl.textContent = 'Colormap: Normalized Viridis Activation Slice';
            }
        }

        // Draw 4 multi-channel tiles for the featured stage
        for (let ch = 0; ch < 4; ch++) {
            const chCanvas = document.getElementById(`ch-tile-${ch}`);
            if (chCanvas && window.FeatureMapRenderer) {
                const chCtx = chCanvas.getContext('2d');
                if (stepNum === 1) {
                    FeatureMapRenderer.drawCT(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else if (stepNum === 2) {
                    FeatureMapRenderer.drawStemFeature(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else if (stepNum === 3) {
                    const modes = ['max', 'avg', 'conv3', 'conv5'];
                    FeatureMapRenderer.drawStage1Feature(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified, modes[ch]);
                } else if (stepNum === 4) {
                    FeatureMapRenderer.drawStage2Feature(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else if (stepNum === 5) {
                    FeatureMapRenderer.drawStage3Feature(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else if (stepNum === 6) {
                    FeatureMapRenderer.drawStage4GradCAM(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else if (stepNum === 7) {
                    FeatureMapRenderer.drawGAPEmbedding(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.isMisclassified);
                } else {
                    FeatureMapRenderer.drawClassifierGauge(chCtx, chCanvas.width, chCanvas.height, caseObj.actual, caseObj.probabilities);
                }
            }
        }
    }

    drawStageVisual(ctx, w, h, stepNum, caseObj) {
        if (!window.FeatureMapRenderer) return;
        const act = caseObj.actual;
        const mis = caseObj.isMisclassified;
        if (stepNum === 1) {
            FeatureMapRenderer.drawCT(ctx, w, h, act, mis);
        } else if (stepNum === 2) {
            FeatureMapRenderer.drawStemFeature(ctx, w, h, act, mis);
        } else if (stepNum === 3) {
            FeatureMapRenderer.drawStage1Feature(ctx, w, h, act, mis, 'max');
        } else if (stepNum === 4) {
            FeatureMapRenderer.drawStage2Feature(ctx, w, h, act, mis);
        } else if (stepNum === 5) {
            FeatureMapRenderer.drawStage3Feature(ctx, w, h, act, mis);
        } else if (stepNum === 6) {
            FeatureMapRenderer.drawStage4GradCAM(ctx, w, h, act, mis);
        } else if (stepNum === 7) {
            FeatureMapRenderer.drawGAPEmbedding(ctx, w, h, act, mis);
        } else if (stepNum === 8) {
            FeatureMapRenderer.drawClassifierGauge(ctx, w, h, act, caseObj.probabilities);
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.app = new AppController();
});
