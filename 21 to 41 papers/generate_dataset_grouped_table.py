import re

# We define each row for the table. Public datasets will have clickable links.
# Slashes are spaced as " / " to ensure LaTeX line wrapping works correctly.

table_rows = [
    # 1. Kaggle CT Kidney
    (
        r"\href{https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone}{Kaggle CT Kidney Dataset} (Dhaka Hospital PACS)",
        r"CT (Contrast / Non-contrast)",
        r"Normal, Cyst, Tumor, Stone (4 Classes; some studies use binary subsets)",
        r"Total: 12,446 images | Normal: 5,077 | Cyst: 3,709 | Tumor: 2,283 | Stone: 1,377",
        r"Accuracies ranging from 91.47\% to 99.84\%; F1-scores up to $>$ 0.99; High diagnostic consistency across CNN and ViT architectures",
        r"[4], [5], [9], [19], [20], [21], [22], [26], [27], [33], [34], [35], [41], [42], [44], [45], [49], [52]"
    ),
    # 2. KiTS19
    (
        r"\href{https://github.com/neheller/kits19/tree/master/data}{KiTS19 Challenge} (Kidney Tumor Segmentation 2019)",
        r"Corticomedullary CT",
        r"Kidney, Tumor (2 Segmentation Classes)",
        r"300 CT cases total | 210 training / 90 testing",
        r"Kidney Dice: up to 0.974 | Tumor Dice: 0.615 to 0.846 | Composite Dice: 0.907",
        r"[16], [23], [40], [53]"
    ),
    # 3. KiTS21
    (
        r"\href{https://github.com/neheller/kits21/tree/master/kits21/data}{KiTS21 Challenge} (Kidney Tumor Segmentation 2021)",
        r"Corticomedullary CT",
        r"Kidney, Tumor, Cyst (3 Segmentation Classes)",
        r"300 CT cases (Official training cohort with multi-annotator consensus)",
        r"Kidney Dice: up to 0.968 | Tumor Dice: up to 0.829 | Cyst Dice: up to 0.701",
        r"[11], [17], [24], [25]"
    ),
    # 4. C4KC-KiTS
    (
        r"\href{https://www.cancerimagingarchive.net/collection/c4kc-kits/}{C4KC-KiTS} (The Cancer Imaging Archive)",
        r"CT",
        r"11 Clinical / Anatomical Segmentation Classes",
        r"Routine clinical nephrectomy scans from heterogeneous institutions",
        r"Peak classification and segmentation accuracy up to 99.60\%",
        r"[57]"
    ),
    # 5. Synapse & FLARE
    (
        r"\href{https://www.synapse.org/#!Synapse:syn3193805/wiki/217789}{Synapse Multi-Organ \& FLARE Benchmarks} (includes ISIC \& CVC)",
        r"Abdominal CT, Dermoscopy, Colonoscopy",
        r"Multi-organ abdominal segmentation (8 organs including kidneys), skin lesions, polyps",
        r"Synapse: 30 CT cases | ISIC 2018: 2,694 images | CVC-ClinicDB: 612 images",
        r"Kidney Dice: 77.8\% to 85.2\% | Overall multi-organ Dice up to 85.17\%; IoU up to 84.93\%",
        r"[29], [30], [51]"
    ),
    # 6. KAUH
    (
        r"\href{https://github.com/DaliaAlzubi/KidneyTumor/tree/main/Dataset}{King Abdulaziz University Hospital (KAUH)} \& Associated CT Sets",
        r"CT Scans",
        r"Tumor, Normal, Malignant (up to 4 classes)",
        r"Total: 8,400 clinical images",
        r"Outperformed ResNet50 baselines; Maximum classification accuracy of 98.29\%",
        r"[2], [18]"
    ),
    # 7. Roboflow Ultrasound
    (
        r"\href{https://universe.roboflow.com/proyecto-1/tesis-iz9ji}{Multi-Center Ultrasound Repository} (Roboflow)",
        r"Ultrasound (US)",
        r"Cysts, Stones, Tumors (3 Classes)",
        r"$>$ 10,000 ultrasound frames from multi-center cohorts",
        r"Peak F1-score of 0.95 across multi-class detection tasks",
        r"[3]"
    ),
    # 8. BUSI, BUS, & Dataset B
    (
        r"\href{https://www.sciencedirect.com/science/article/pii/S2352340919312181}{BUSI, BUS, \& Dataset B} (Ultrasound Repositories)",
        r"Grayscale B-mode Ultrasound",
        r"Benign, Malignant, Normal (2 and 3 Class tasks)",
        r"BUSI: 780 (487 benign, 210 malignant, 133 normal) | BUS: 562 | Dataset B: 163",
        r"Ultrasound segmentation Dice: 78.69\% to 82.34\%; IoU ranging from 67.94\% to 72.54\%",
        r"[28]"
    ),
    # 9. Zenodo
    (
        r"\href{https://zenodo.org/record/6042410}{Zenodo Open-Access Abdominal CT} (Guangzhou Medical Univ.)",
        r"Unenhanced Abdominal CT",
        r"Kidney, Kidney Stone, Background",
        r"260 CT scans total | 209 with stones / 51 without (7:3 train/val split)",
        r"Kidney Dice: 96.54\% | Stone Dice: 80.59\% | Specificity: 99.99\% | Stone Sensitivity: 79.73\%",
        r"[31]"
    ),
    # 10. Sulaimani
    (
        r"\href{https://www.kaggle.com/datasets/orvile/axial-ct-imaging-dataset-kidney-stone-detection}{Sulaimani / Rania Dataset}",
        r"Axial CT",
        r"Kidney Stones",
        r"3,364 original axial CT images; expanded to 35,457 via augmentation",
        r"High sensitivity and robust feature detection in stone identification frameworks",
        r"[50]"
    ),
    # 11. TCIA CT Colonography
    (
        r"\href{https://www.cancerimagingarchive.net/collection/ct-colonography/}{TCIA CT Colonography} (Clinical Stone Cohort)",
        r"Non-contrast CT",
        r"Kidney Stones",
        r"551 clinical CT scans",
        r"Automated detection sensitivity reaching 88.1\%",
        r"[36]"
    ),
    # 12. NIDDK / CRISP
    (
        r"\href{https://www.niddkrepository.org/studies/crisp/}{NIDDK / CRISP Repository} (Radiologic Imaging of PKD)",
        r"MRI (T1-weighted \& T2-weighted)",
        r"Kidney, Cortex, Medulla (3 Anatomical Classes)",
        r"\textasciitilde{}241 MRI volumes from multicenter PKD studies",
        r"High precision anatomical segmentation: Dice 0.974 (kidney), 0.963 (cortex), 0.950 (medulla)",
        r"[60]"
    ),
    # 13. NHANES & SEER
    (
        r"\href{https://www.cdc.gov/nchs/nhanes/index.htm}{NHANES} \& \href{https://seer.cancer.gov/}{SEER} Cancer Databases",
        r"Epidemiological Surveys, Clinical Records, Proteomics",
        r"Kidney Stones (NHANES); Renal Cell Carcinoma (SEER)",
        r"NHANES: 12,110 participants | SEER: $>$ 22,000 RCC patient records",
        r"NHANES: Stone prevalence 8.8\% (OR: 1.55) | SEER: Prognostic AUC of 0.746 for RCC survival models",
        r"[7], [8]"
    ),
    # 14. Text NLP
    (
        r"\href{https://huggingface.co/datasets/ncbi/pubmed}{Biomedical NLP \& Clinical Text Corpora} (PubMed, PMC, BLURB, MACCROBAT)",
        r"Biomedical Text \& Clinical Notes (NLP)",
        r"Symptoms, Diseases, Medications, Named Entity Recognition (NER), Question Answering",
        r"Up to 14M abstracts / 4.5B words (PubMed/PMC); 300 clinical notes (MACCROBAT); 13 benchmark datasets (BLURB)",
        r"SOTA performance on QA and BLURB benchmarks; 86.6\% accuracy on clinical DiRAG tasks",
        r"[37], [38], [39], [47], [48]"
    ),
    # 15. Histopathology
    (
        r"\href{https://drive.google.com/drive/folders/1BQZGKHKOUji9rDA5IVltlLnXLk7_Elic}{Histopathology} \& Urine Microscopy Repositories",
        r"Histopathology (H\&E stained) \& Microscopic Urine Images",
        r"5 Cancer Grades (Grade 0–4); 14 Urine Particle Classes",
        r"Histopathology: 3,000 images (600 / class) | Urine Microscopy: 7,201 images",
        r"Histopathology: Acc 88.90\%, F1 72.01\% | Urine Microscopy: 60\% mAP@50 across 14 particle classes",
        r"[46], [59]"
    ),
    
    # === SEPARATED PRIVATE DATASETS ===
    # Rehman [6]
    (
        r"Public CT Repository (Not Accessible)",
        r"CT",
        r"Stones (binary / multi)",
        r"Total: \textasciitilde{}5,000 images",
        r"Acc: 90–95\%",
        r"[6]"
    ),
    # Chen [12]
    (
        r"Private Australian Clinical Data (Not Accessible)",
        r"Multimodal (CT / MRI)",
        r"Renal masses / tumors",
        r"27 patients",
        r"10.07\% mean abs. diff.",
        r"[12]"
    ),
    # Liang [13]
    (
        r"Private Multi-Center Dataset (Not Accessible)",
        r"CT multi-phase (plain scan + secretory phase CTU)",
        r"Renal Cell Carcinoma; Urothelial Carcinoma; Urinary Tract Stones (3 disease categories)",
        r"1024 cases: 326 RCC | 278 urothelial carcinoma | 420 urinary stones | 717 train / 102 val / 205 test",
        r"Lightweight dual-branch: Dice 89.7\%; IoU 82.9\%; inference 47.9ms; Full model: Dice 90.3\%; IoU 83.6\%; F1 +3.2\% vs EfficientNet-B3",
        r"[13]"
    ),
    # Farjad [14]
    (
        r"CT Scan Images (Axial Slices) (Not Accessible)",
        r"CT",
        r"Binary (Normal vs. abnormal)",
        r"Total: 150 images | Normal: 75 | Abnormal: 75",
        r"Acc: 90\%",
        r"[14]"
    ),
    # Elmaagac [32]
    (
        r"Private Retrospective Clinical Dataset (Not Accessible)",
        r"CT (KUB / fluoroscopy for PCNL)",
        r"Stone-free vs. Non-stone-free outcomes (2 classes)",
        r"340 patients (retrospective clinical study)",
        r"AUC: 0.786; Sensitivity: 75\%; Specificity: 76\%",
        r"[32]"
    ),
    # Nguyen [54]
    (
        r"Private KUB X-Ray Dataset (Not Accessible)",
        r"X-ray (KUB plain film)",
        r"Kidney stone detection (binary: stone present / absent)",
        r"152 KUB X-rays | Train: 28 (->240 augmented) | Val: 24 | Test: 100",
        r"YOLOv7-R+CBAM: Precision 92.2\%; Sensitivity 87.6\%; F1 89.8\%; mAP50 91.2\%; With 2x SR (ESRGAN): mAP50 95.0\%",
        r"[54]"
    ),
    # Gao [55]
    (
        r"Private Renal Tumor Ultrasound Dataset (Not Accessible)",
        r"Ultrasound (grayscale B-mode renal)",
        r"Benign renal tumor; Malignant renal tumor (2 classes)",
        r"345 patients (127 benign | 218 malignant) | 3504 images after augmentation",
        r"Segmentation IoU: 94.23\%; Classification Accuracy: 81.8\%; Sensitivity: 82.2\%; Specificity: 80.6\%; AUC: 0.88",
        r"[55]"
    ),
    # Chen [56]
    (
        r"Private Clinical Dataset (Not Accessible)",
        r"Ultrasound",
        r"3 Classes (Kidney organ, parenchyma, renal sinus)",
        r"Total: 1,000 images | Training: 850 | Test: 150",
        r"Dice: 96.25\% (kidney), 92.9\% (parenchyma)",
        r"[56]"
    ),
    # Ye [58]
    (
        r"Annotated CT Slices (Not Accessible)",
        r"CT",
        r"Kidney Stone",
        r"Total: 4,000 slices",
        r"mAP@0.5: 0.91",
        r"[58]"
    ),
    # Noorelahi [61]
    (
        r"Private Abdominal CT PACS Protocols (Not Accessible)",
        r"CT / PACS",
        r"Radiation dose parameters",
        r"200 patients",
        r"Dose variability results",
        r"[61]"
    ),
    
    # 17. Survey Papers
    (
        r"Survey Papers \& Literature Reviews (No Primary Experimental Dataset)",
        r"Multimodal (CT, MRI, US, X-ray, PET-CT)",
        r"N / A (Aggregated review metrics across disease classifications)",
        r"Summaries of up to 112+ reviewed articles across various medical imaging domains",
        r"Compiles state-of-the-art literature metrics (reported Dice scores up to 0.987 across primary studies)",
        r"[1], [10], [15], [43], [62]"
    )
]

# Output LaTeX
latex_template = r"""\documentclass{article}
\usepackage[T1]{fontenc}  % Required to render | as a proper vertical bar
\usepackage[utf8]{inputenc}
\usepackage{longtable}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{hyperref}
\usepackage[margin=0.5in]{geometry}  % Compact margins

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
}

\newcolumntype{L}[1]{>{\RaggedRight\arraybackslash}p{#1}}

\begin{document}

\section*{Summary of Reviewed Studies Grouped by Dataset (Papers 1--62)}

This section presents the comprehensive synthesis of deep learning models, frameworks, and datasets utilized for renal disease diagnosis across Papers 1 to 62, categorized by primary dataset and imaging modality.

\renewcommand{\arraystretch}{1.2}  % Clean cell padding
\setlength{\tabcolsep}{4pt}          % Tighter column padding to save horizontal space
\footnotesize                        % Publication-style footnotesize font

\begin{longtable}{|L{3.0cm}|L{1.8cm}|L{2.5cm}|L{3.2cm}|L{4.2cm}|L{1.8cm}|}
\hline
\textbf{Dataset Name \& Link} & \textbf{Modality} & \textbf{Target Classes} & \textbf{Sample Size \& Breakdown} & \textbf{Performance Highlights} & \textbf{Utilizing Studies} \\
\hline
\endfirsthead

\hline
\textbf{Dataset Name \& Link} & \textbf{Modality} & \textbf{Target Classes} & \textbf{Sample Size \& Breakdown} & \textbf{Performance Highlights} & \textbf{Utilizing Studies} \\
\hline
\endhead

\hline
\multicolumn{6}{|r|}{{Continued on next page}} \\
\hline
\endfoot

\hline
\endlastfoot

DATA_ROWS_PLACEHOLDER
\end{longtable}

\end{document}
"""

rows_str = ""
for row in table_rows:
    line = f"{row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]} & {row[5]} \\\\"
    rows_str += line + "\n\\hline\n"
rows_str = rows_str[:-len("\\hline\n")]

latex_content = latex_template.replace("DATA_ROWS_PLACEHOLDER", rows_str)

with open('table_grouped.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("Successfully generated table_grouped.tex")
