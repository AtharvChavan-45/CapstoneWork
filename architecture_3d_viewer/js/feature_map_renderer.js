/**
 * PCSA-KidneyNeXt: Procedural Medical Feature Map & Grad-CAM Visualizer
 * Generates realistic visual activation maps, multi-scale receptive field outputs,
 * and Grad-CAM heatmaps for every stage and block of the network.
 */

class FeatureMapRenderer {
    // Utility to map value 0..1 to Jet colormap (Blue -> Cyan -> Green -> Yellow -> Red)
    static getJetColor(val) {
        val = Math.max(0, Math.min(1, val));
        let r, g, b;
        if (val < 0.125) {
            r = 0; g = 0; b = 0.5 + 4 * val;
        } else if (val < 0.375) {
            r = 0; g = 4 * (val - 0.125); b = 1;
        } else if (val < 0.625) {
            r = 4 * (val - 0.375); g = 1; b = 1 - 4 * (val - 0.375);
        } else if (val < 0.875) {
            r = 1; g = 1 - 4 * (val - 0.625); b = 0;
        } else {
            r = 1 - 2 * (val - 0.875); g = 0; b = 0;
        }
        return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
    }

    // Viridis colormap for feature maps (Purple -> Teal -> Yellow)
    static getViridisColor(val) {
        val = Math.max(0, Math.min(1, val));
        const r = Math.round(255 * Math.pow(val, 0.8) * 0.95);
        const g = Math.round(255 * Math.sin(val * Math.PI * 0.9));
        const b = Math.round(255 * (1 - Math.pow(val, 1.2)) * 0.9 + 20);
        return [r, g, b];
    }

    // 1. Raw CT Scan
    static drawCT(ctx, width, height, caseType, isMisclass) {
        ctx.fillStyle = '#05070a';
        ctx.fillRect(0, 0, width, height);

        const scale = width / 224;

        // Outer abdominal wall
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2 * scale;
        ctx.beginPath();
        ctx.ellipse(112 * scale, 112 * scale, 95 * scale, 75 * scale, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Spine / vertebrae
        ctx.fillStyle = '#475569';
        ctx.beginPath();
        ctx.arc(112 * scale, 160 * scale, 14 * scale, 0, Math.PI * 2);
        ctx.fill();

        // Left kidney parenchyma
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.ellipse(70 * scale, 110 * scale, 24 * scale, 42 * scale, -0.15, 0, Math.PI * 2);
        ctx.fill();

        // Right kidney parenchyma
        ctx.beginPath();
        ctx.ellipse(154 * scale, 110 * scale, 24 * scale, 42 * scale, 0.15, 0, Math.PI * 2);
        ctx.fill();

        // Lesion specific rendering
        if (caseType === 'Cyst' || caseType === 'cyst_case') {
            const rad = (isMisclass ? 15 : 13) * scale;
            const grad = ctx.createRadialGradient(70 * scale, 100 * scale, 2 * scale, 70 * scale, 100 * scale, rad);
            if (isMisclass) {
                grad.addColorStop(0, '#f59e0b');
                grad.addColorStop(0.3, '#b45309');
                grad.addColorStop(0.7, '#0f172a');
                grad.addColorStop(1, '#1e293b');
            } else {
                grad.addColorStop(0, '#38bdf8');
                grad.addColorStop(0.8, '#0369a1');
                grad.addColorStop(1, '#1e293b');
            }
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(70 * scale, 100 * scale, rad, 0, Math.PI * 2);
            ctx.fill();
        } else if (caseType === 'Stone' || caseType === 'stone_case') {
            ctx.fillStyle = '#ffffff';
            ctx.shadowColor = '#f59e0b';
            ctx.shadowBlur = 10 * scale;
            ctx.beginPath();
            ctx.arc(154 * scale, 112 * scale, 5 * scale, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        } else if (caseType === 'Tumor' || caseType === 'tumor_case') {
            ctx.fillStyle = '#ef4444';
            ctx.beginPath();
            ctx.ellipse(70 * scale, 120 * scale, 18 * scale, 14 * scale, 0.4, 0, Math.PI * 2);
            ctx.fill();
            // Heterogeneous internal necrotic core
            ctx.fillStyle = '#7f1d1d';
            ctx.beginPath();
            ctx.arc(68 * scale, 122 * scale, 6 * scale, 0, Math.PI * 2);
            ctx.fill();
        }

        // Overlay text
        ctx.fillStyle = '#38bdf8';
        ctx.font = `${Math.max(9, Math.round(10 * scale))}px monospace`;
        ctx.fillText('AXIAL CT: 224×224', 8 * scale, 16 * scale);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(`PATIENT SLICE`, 8 * scale, height - 8 * scale);
    }

    // 2. Dual-Stem Edge & Capsule Feature Map (56×56)
    static drawStemFeature(ctx, width, height, caseType, isMisclass) {
        ctx.fillStyle = '#080c14';
        ctx.fillRect(0, 0, width, height);

        const imgData = ctx.createImageData(width, height);
        const data = imgData.data;

        const scale = 224 / width;
        const centerX1 = (70 / 224) * width;
        const centerY1 = (110 / 224) * height;
        const centerX2 = (154 / 224) * width;
        const centerY2 = (110 / 224) * height;

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = (y * width + x) * 4;

                // Compute distance to kidney boundaries
                const d1 = Math.sqrt(Math.pow((x - centerX1) * 1.5, 2) + Math.pow(y - centerY1, 2));
                const d2 = Math.sqrt(Math.pow((x - centerX2) * 1.5, 2) + Math.pow(y - centerY2, 2));

                // Edge response: high near kidney borders
                const edge1 = Math.exp(-Math.pow(d1 - height * 0.22, 2) / 20);
                const edge2 = Math.exp(-Math.pow(d2 - height * 0.22, 2) / 20);
                let val = Math.max(edge1, edge2) * 0.75;

                // Add grid texture for 56x56 downsampled representation
                if ((x % 3 === 0) || (y % 3 === 0)) val *= 0.85;

                // Lesion signature
                if (caseType === 'Stone' || caseType === 'stone_case') {
                    const dStone = Math.sqrt(Math.pow(x - centerX2, 2) + Math.pow(y - centerY2, 2));
                    if (dStone < 7) val = 1.0;
                } else if (caseType === 'Cyst' || caseType === 'cyst_case') {
                    const dCyst = Math.sqrt(Math.pow(x - centerX1, 2) + Math.pow(y - (centerY1 - 8), 2));
                    if (Math.abs(dCyst - 10) < 3) val = 0.95;
                } else if (caseType === 'Tumor' || caseType === 'tumor_case') {
                    const dTumor = Math.sqrt(Math.pow(x - centerX1, 2) + Math.pow(y - (centerY1 + 10), 2));
                    if (dTumor < 14) val = 0.8 + Math.random() * 0.2;
                }

                const [r, g, b] = this.getViridisColor(val);
                data[idx] = r;
                data[idx + 1] = g;
                data[idx + 2] = b;
                data[idx + 3] = 255;
            }
        }
        ctx.putImageData(imgData, 0, 0);

        // Grid overlay
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, 0, width, height);

        ctx.fillStyle = '#38bdf8';
        ctx.font = '9px monospace';
        ctx.fillText('STEM: [1, 96, 56, 56]', 6, 14);
        ctx.fillText('Dual-Conv GELU', 6, height - 6);
    }

    // 3. Stage 1 Multi-Receptive Feature Map (56×56)
    static drawStage1Feature(ctx, width, height, caseType, isMisclass, mode = 'max') {
        ctx.fillStyle = '#0a0d18';
        ctx.fillRect(0, 0, width, height);

        const imgData = ctx.createImageData(width, height);
        const data = imgData.data;

        const lx = (70 / 224) * width;
        const ly = (100 / 224) * height;
        const rx = (154 / 224) * width;
        const ry = (112 / 224) * height;

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = (y * width + x) * 4;
                let val = 0.15;

                // Base kidney silhouette
                const dl = Math.sqrt(Math.pow((x - lx) * 1.6, 2) + Math.pow(y - (ly + 10), 2));
                const dr = Math.sqrt(Math.pow((x - rx) * 1.6, 2) + Math.pow(y - ry, 2));
                if (dl < width * 0.2) val += 0.25;
                if (dr < width * 0.2) val += 0.25;

                if (mode === 'max') {
                    // MaxPool highlights extreme peaks (calcium)
                    if (caseType === 'Stone' || caseType === 'stone_case') {
                        const d = Math.sqrt(Math.pow(x - rx, 2) + Math.pow(y - ry, 2));
                        if (d < 8) val = 1.0;
                    } else if (isMisclass) {
                        const d = Math.sqrt(Math.pow(x - lx, 2) + Math.pow(y - ly, 2));
                        if (d < 6) val = 0.85; // false peak
                    }
                } else if (mode === 'avg') {
                    // AvgPool highlights smooth background fluid
                    if (caseType === 'Cyst' || caseType === 'cyst_case') {
                        const d = Math.sqrt(Math.pow(x - lx, 2) + Math.pow(y - ly, 2));
                        if (d < 14) val = 0.92;
                    }
                } else if (mode === 'conv3') {
                    // DW-Conv 3x3 detects micro-contours
                    const d = Math.sqrt(Math.pow(x - lx, 2) + Math.pow(y - ly, 2));
                    if (Math.abs(d - 12) < 3) val = 0.96;
                } else {
                    // DW-Conv 5x5 detects broader context
                    const d = Math.sqrt(Math.pow(x - lx, 2) + Math.pow(y - (ly + 15), 2));
                    if (d < 22) val = 0.88;
                }

                const [r, g, b] = this.getViridisColor(val);
                data[idx] = r;
                data[idx + 1] = g;
                data[idx + 2] = b;
                data[idx + 3] = 255;
            }
        }
        ctx.putImageData(imgData, 0, 0);

        ctx.fillStyle = '#10b981';
        ctx.font = '9px monospace';
        ctx.fillText('STAGE 1: [1, 96, 56, 56]', 6, 14);
        ctx.fillText(`4-Way Multi-Receptive (${mode.toUpperCase()})`, 6, height - 6);
    }

    // 4. Stage 2 Local Topology (28×28)
    static drawStage2Feature(ctx, width, height, caseType, isMisclass) {
        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, width, height);

        const blocks = 28;
        const bw = width / blocks;
        const bh = height / blocks;

        for (let by = 0; by < blocks; by++) {
            for (let bx = 0; bx < blocks; bx++) {
                // Normalize 0..1
                const nx = bx / blocks;
                const ny = by / blocks;

                let val = 0.1;
                // Kidney centroids in normalized coordinates
                const d1 = Math.sqrt(Math.pow((nx - 0.31) * 1.5, 2) + Math.pow(ny - 0.49, 2));
                const d2 = Math.sqrt(Math.pow((nx - 0.69) * 1.5, 2) + Math.pow(ny - 0.49, 2));
                if (d1 < 0.22) val += 0.35;
                if (d2 < 0.22) val += 0.35;

                // Pathology focus
                if (caseType === 'Stone' || caseType === 'stone_case') {
                    const ds = Math.sqrt(Math.pow(nx - 0.69, 2) + Math.pow(ny - 0.50, 2));
                    if (ds < 0.1) val = 0.98;
                } else if (caseType === 'Cyst' || caseType === 'cyst_case') {
                    const dc = Math.sqrt(Math.pow(nx - 0.31, 2) + Math.pow(ny - 0.45, 2));
                    if (dc < 0.12) val = 0.94;
                } else if (caseType === 'Tumor' || caseType === 'tumor_case') {
                    const dt = Math.sqrt(Math.pow(nx - 0.31, 2) + Math.pow(ny - 0.55, 2));
                    if (dt < 0.15) val = 0.95;
                }

                const [r, g, b] = this.getViridisColor(val);
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(bx * bw, by * bh, bw - 0.8, bh - 0.8);
            }
        }

        ctx.fillStyle = '#38bdf8';
        ctx.font = '9px monospace';
        ctx.fillText('STAGE 2: [1, 192, 28, 28]', 6, 14);
        ctx.fillText('Downsample 2× Topology', 6, height - 6);
    }

    // 5. Stage 3 Regional Pathology Context (14×14)
    static drawStage3Feature(ctx, width, height, caseType, isMisclass) {
        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, width, height);

        const blocks = 14;
        const bw = width / blocks;
        const bh = height / blocks;

        for (let by = 0; by < blocks; by++) {
            for (let bx = 0; bx < blocks; bx++) {
                const nx = bx / blocks;
                const ny = by / blocks;

                let val = 0.12;
                if (caseType === 'Stone' || caseType === 'stone_case') {
                    const d = Math.sqrt(Math.pow(nx - 0.69, 2) + Math.pow(ny - 0.50, 2));
                    val = Math.max(0.12, 1.0 - d * 2.8);
                } else if (caseType === 'Cyst' || caseType === 'cyst_case') {
                    const d = Math.sqrt(Math.pow(nx - 0.31, 2) + Math.pow(ny - 0.45, 2));
                    val = Math.max(0.12, 1.0 - d * 2.5);
                } else if (caseType === 'Tumor' || caseType === 'tumor_case') {
                    const d = Math.sqrt(Math.pow(nx - 0.31, 2) + Math.pow(ny - 0.55, 2));
                    val = Math.max(0.12, 1.0 - d * 2.2);
                }

                const [r, g, b] = this.getViridisColor(val);
                ctx.fillStyle = `rgb(${r},${g},${b})`;
                ctx.fillRect(bx * bw, by * bh, bw - 1, bh - 1);
            }
        }

        ctx.fillStyle = '#818cf8';
        ctx.font = '9px monospace';
        ctx.fillText('STAGE 3: [1, 384, 14, 14]', 6, 14);
        ctx.fillText('Semantic Pathology Channels', 6, height - 6);
    }

    // 6. Stage 4 Deepest Bottleneck + Grad-CAM Heatmap (7×7 upscaled overlay)
    static drawStage4GradCAM(ctx, width, height, caseType, isMisclass) {
        // Draw underlying CT scan in muted grayscale
        this.drawCT(ctx, width, height, caseType, isMisclass);

        // Overlay Grad-CAM Jet Heatmap with alpha blending
        const overlayCanvas = document.createElement('canvas');
        overlayCanvas.width = width;
        overlayCanvas.height = height;
        const octx = overlayCanvas.getContext('2d');
        const imgData = octx.createImageData(width, height);
        const data = imgData.data;

        const targetX = (caseType === 'Stone' || caseType === 'stone_case') ? 154 : 70;
        const targetY = (caseType === 'Tumor' || caseType === 'tumor_case') ? 120 : (caseType === 'Stone' ? 112 : 100);
        const sigma = (caseType === 'Stone' || caseType === 'stone_case') ? 22 : 36;

        const tx = (targetX / 224) * width;
        const ty = (targetY / 224) * height;
        const s = (sigma / 224) * width;

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = (y * width + x) * 4;
                const distSq = Math.pow(x - tx, 2) + Math.pow(y - ty, 2);
                let heat = Math.exp(-distSq / (2 * Math.pow(s, 2)));

                // If misclassified case, add secondary false-activation lobe
                if (isMisclass) {
                    const distFalse = Math.pow(x - (154 / 224) * width, 2) + Math.pow(y - (112 / 224) * height, 2);
                    heat = Math.max(heat, 0.75 * Math.exp(-distFalse / (2 * Math.pow(s * 0.7, 2))));
                }

                if (heat > 0.15) {
                    const [r, g, b] = this.getJetColor(heat);
                    data[idx] = r;
                    data[idx + 1] = g;
                    data[idx + 2] = b;
                    data[idx + 3] = Math.round(heat * 190); // alpha gradient
                } else {
                    data[idx + 3] = 0;
                }
            }
        }
        octx.putImageData(imgData, 0, 0);

        ctx.drawImage(overlayCanvas, 0, 0);

        // Heatmap colorbar
        const cbW = 8;
        const cbH = height * 0.4;
        const cbX = width - 16;
        const cbY = height * 0.3;
        for (let i = 0; i < cbH; i++) {
            const val = 1 - (i / cbH);
            const [r, g, b] = this.getJetColor(val);
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(cbX, cbY + i, cbW, 1);
        }
        ctx.strokeStyle = '#ffffff';
        ctx.strokeRect(cbX, cbY, cbW, cbH);

        ctx.fillStyle = '#ffffff';
        ctx.font = '8px monospace';
        ctx.fillText('MAX', cbX - 22, cbY + 8);
        ctx.fillText('MIN', cbX - 22, cbY + cbH);

        ctx.fillStyle = '#f59e0b';
        ctx.font = '9px monospace';
        ctx.fillText('STAGE 4: [1, 768, 7, 7]', 6, 14);
        ctx.fillText('Grad-CAM Class Activation Hook', 6, height - 6);
    }

    // 7. GAP 768-D Feature Embedding Vector (Genomic heatstrip / spectrum barcode)
    static drawGAPEmbedding(ctx, width, height, caseType, isMisclass) {
        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, width, height);

        const cols = 64;
        const rows = 12; // 64 * 12 = 768 feature dimensions
        const cw = width / cols;
        const ch = (height - 30) / rows;

        let seed = 42;
        const pseudoRand = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const chIndex = r * cols + c;
                let val = pseudoRand() * 0.3;

                // Specific channel clusters light up based on pathology
                if ((caseType === 'Stone' || caseType === 'stone_case') && chIndex > 200 && chIndex < 340) {
                    val = 0.7 + pseudoRand() * 0.3;
                } else if ((caseType === 'Cyst' || caseType === 'cyst_case') && chIndex > 40 && chIndex < 180) {
                    val = 0.7 + pseudoRand() * 0.3;
                } else if ((caseType === 'Tumor' || caseType === 'tumor_case') && chIndex > 450 && chIndex < 620) {
                    val = 0.75 + pseudoRand() * 0.25;
                }

                const [red, green, blue] = this.getViridisColor(val);
                ctx.fillStyle = `rgb(${red},${green},${blue})`;
                ctx.fillRect(c * cw, 20 + r * ch, cw - 0.5, ch - 0.5);
            }
        }

        ctx.fillStyle = '#38bdf8';
        ctx.font = '9px monospace';
        ctx.fillText('GAP: Flatten [1, 768]', 6, 14);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('768-D Translation-Invariant Representation', 6, height - 4);
    }

    // 8. Classifier Decision Head Visual Radar / Gauge
    static drawClassifierGauge(ctx, width, height, caseType, probs) {
        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, width, height);

        const classes = [
            { name: 'Cyst', val: probs.Cyst, color: '#38bdf8' },
            { name: 'Normal', val: probs.Normal, color: '#10b981' },
            { name: 'Stone', val: probs.Stone, color: '#f59e0b' },
            { name: 'Tumor', val: probs.Tumor, color: '#ef4444' }
        ];

        const barH = 14;
        const startY = 24;
        const maxBarW = width - 110;

        classes.forEach((cls, idx) => {
            const y = startY + idx * 28;

            ctx.fillStyle = '#cbd5e1';
            ctx.font = '10px monospace';
            ctx.fillText(cls.name, 8, y + 10);

            // Track
            ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
            ctx.fillRect(70, y, maxBarW, barH);

            // Fill
            const fillW = Math.max(2, (cls.val / 100) * maxBarW);
            ctx.fillStyle = cls.color;
            ctx.fillRect(70, y, fillW, barH);

            // Value text
            ctx.fillStyle = '#ffffff';
            ctx.font = '9px monospace';
            ctx.fillText(`${cls.val.toFixed(1)}%`, 76 + maxBarW, y + 10);
        });

        ctx.fillStyle = '#10b981';
        ctx.font = '9px monospace';
        ctx.fillText('HEAD: Linear(768 ➔ 4) Softmax', 6, 14);
    }

    // 9. PCSA Branch Visualizer
    static drawPCSABranch(ctx, width, height, caseType, isMisclass, branchKey) {
        if (branchKey === 'max') {
            this.drawStage1Feature(ctx, width, height, caseType, isMisclass, 'max');
        } else if (branchKey === 'avg') {
            this.drawStage1Feature(ctx, width, height, caseType, isMisclass, 'avg');
        } else if (branchKey === 'conv3') {
            this.drawStage1Feature(ctx, width, height, caseType, isMisclass, 'conv3');
        } else if (branchKey === 'conv5') {
            this.drawStage1Feature(ctx, width, height, caseType, isMisclass, 'conv5');
        } else if (branchKey === 'channel_attn') {
            // Draw 96-channel bar spectrum
            ctx.fillStyle = '#060a12';
            ctx.fillRect(0, 0, width, height);
            const bars = 48;
            const bw = width / bars;
            for (let i = 0; i < bars; i++) {
                const hVal = Math.sin(i * 0.25) * 0.4 + 0.5 + (i % 5 === 0 ? 0.3 : 0);
                const barHeight = hVal * (height - 30);
                ctx.fillStyle = '#ec4899';
                ctx.fillRect(i * bw, height - 10 - barHeight, bw - 1, barHeight);
            }
            ctx.fillStyle = '#ec4899';
            ctx.font = '9px monospace';
            ctx.fillText('CHANNEL ATTENTION (MLP)', 6, 14);
        } else if (branchKey === 'spatial_attn') {
            // Draw 2D spatial attention mask
            ctx.fillStyle = '#05070a';
            ctx.fillRect(0, 0, width, height);
            const tx = (caseType === 'Stone' ? 154 : 70) / 224 * width;
            const ty = (caseType === 'Tumor' ? 120 : (caseType === 'Stone' ? 112 : 100)) / 224 * height;
            const grad = ctx.createRadialGradient(tx, ty, 2, tx, ty, width * 0.25);
            grad.addColorStop(0, '#38bdf8');
            grad.addColorStop(0.5, 'rgba(59, 130, 246, 0.5)');
            grad.addColorStop(1, 'rgba(5, 7, 10, 0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(tx, ty, width * 0.25, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#3b82f6';
            ctx.font = '9px monospace';
            ctx.fillText('SPATIAL ATTENTION (3×3+5×5)', 6, 14);
        } else if (branchKey === 'residual_skip') {
            // Draw gradient identity blending
            this.drawStemFeature(ctx, width, height, caseType, isMisclass);
            ctx.fillStyle = 'rgba(0, 245, 160, 0.2)';
            ctx.fillRect(0, 0, width, height);
            ctx.fillStyle = '#00f5a0';
            ctx.font = '9px monospace';
            ctx.fillText('RESIDUAL SHORTCUT: Y = F(X) + X', 6, 14);
        }
    }
}

window.FeatureMapRenderer = FeatureMapRenderer;
