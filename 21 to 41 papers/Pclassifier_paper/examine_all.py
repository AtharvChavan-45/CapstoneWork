import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

for idx, f in enumerate(files):
    reader = pypdf.PdfReader(f)
    text = ""
    for p in reader.pages:
        text += (p.extract_text() or "") + "\n"
        
    print("="*100)
    print(f"[{idx+1}] FILE: {f}")
    
    # Title & Authors
    lines = [l.strip() for l in text[:2000].split('\n') if l.strip()]
    print("FIRST LINES:")
    for l in lines[:10]:
        print("  ", l)
        
    # Check dataset details
    print("\n--- DATASET SECTION EXCERPTS ---")
    matches = re.findall(r"(?:dataset|data collection|materials and methods|experimental data|database).{0,1500}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['12,446', '12446', '3,709', '3709', 'kaggle', 'normal', 'cyst', 'tumor', 'stone', 'kauh', 'kits']):
            print(">>>", clean[:500])
            print()
            break
            
    # Check split details
    print("--- SPLIT DETAILS ---")
    matches = re.findall(r"(?:split|train|test|validation|ratio|k-fold|cross-validation|leakage|patient|slice|groupkfold).{0,500}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['80:20', '70:30', '80%', '70%', '10-fold', '5-fold', 'ratio', 'leakage', 'split into', 'divided into', 'partitioned']):
            print(">>>", clean[:400])
            print()
            break

    # Check Preprocessing & ROI
    print("--- PREPROCESSING / ROI / CROPPING ---")
    matches = re.findall(r"(?:preprocess|roi|crop|yolo|u-net|contour|otsu|bounding|segment|mask|resize|dimension|input size|224|512).{0,500}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['crop', 'roi', 'yolo', 'u-net', 'otsu', 'resize', 'contour', 'segment', 'bounding box', '224x224', '512x512']):
            print(">>>", clean[:400])
            print()
            break

    # Check Windowing / HU / Normalization
    print("--- WINDOWING / HU / NORMALIZATION ---")
    matches = re.findall(r"(?:window|hounsfield|hu | hu,|hu\)|wl|ww|normalization|rgb|rescaling|intensity|standardization).{0,500}", text, re.I | re.S)
    found_hu = False
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['hounsfield', 'hu', 'window', 'level', 'width', 'rgb', 'imagenet', '255', '[0, 1]']):
            print(">>>", clean[:400])
            print()
            found_hu = True
            break
    if not found_hu:
        print(">>> None found specifically for windowing/HU.")

    # Check External Validation
    print("--- EXTERNAL VALIDATION ---")
    matches = re.findall(r"(?:external|out-of-distribution|cross-dataset|kits|kauh|mendeley|tcia|generaliz|independent dataset).{0,500}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['external dataset', 'tested on', 'evaluated on', 'kits', 'kauh', 'mendeley', 'tcia', 'another dataset', 'cross-dataset']):
            print(">>>", clean[:400])
            print()
            break

    # Check Results & Accuracy
    print("--- RESULTS / ACCURACY ---")
    matches = re.findall(r"(?:accuracy of|achieved an accuracy|accuracy:|test accuracy|overall accuracy|classification accuracy|f1-score|f1 score).{0,300}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['%', 'percent', '9', '8']):
            print(">>>", clean[:300])
            print()
            break

    # Check Limitations
    print("--- LIMITATIONS / FUTURE WORK ---")
    matches = re.findall(r"(?:limitation|drawback|future work|future research|constraint).{0,500}", text, re.I | re.S)
    for m in matches:
        clean = re.sub(r'\s+', ' ', m)
        if any(w in clean.lower() for w in ['limitation', 'drawback', 'future', 'scarcity', 'generaliz']):
            print(">>>", clean[:400])
            print()
            break

