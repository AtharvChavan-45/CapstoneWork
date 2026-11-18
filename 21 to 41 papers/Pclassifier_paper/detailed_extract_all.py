import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

for idx, f in enumerate(files):
    reader = pypdf.PdfReader(f)
    text = ""
    for p in reader.pages:
        text += (p.extract_text() or "") + "\n"
        
    print("="*80)
    print(f"PAPER {idx+1}: {f} (Pages: {len(reader.pages)})")
    
    # 1. Title, Authors, Year, Journal
    # Let's extract first 1000 characters
    print("\n--- 1. METADATA ---")
    print(text[:1200].strip())
    
    # Search for specific terms
    print("\n--- 2. DATASET USED ---")
    # find where dataset is described
    for m in re.finditer(r"(?:dataset|data collection|data acquisition|database|image dataset).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['kaggle', 'normal', 'cyst', 'tumor', 'stone', '12446', '12,446', '3709', '3,709', 'kauh', 'kits', 'mhc']):
            print("  DATASET SNIPPET:", snip[:300])
            break

    # Search for split details
    print("\n--- 3. DATASET SPLITTING & LEAKAGE ---")
    for m in re.finditer(r"(?:train|test|split|validation|ratio|k-fold|cross-validation|leakage|patient-level|groupkfold|slice).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['80', '70', '90', '10-fold', '5-fold', 'ratio', 'leakage', 'patient', 'split']):
            if 'train' in snip.lower() and ('test' in snip.lower() or 'val' in snip.lower() or 'fold' in snip.lower()):
                print("  SPLIT SNIPPET:", snip[:350])
                break

    # Search for ROI / Segmentation / Preprocessing
    print("\n--- 4. PREPROCESSING & ROI CROPPING ---")
    for m in re.finditer(r"(?:preprocess|roi|crop|yolo|u-net|contour|otsu|segment|bounding|resize|normalization).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['crop', 'roi', 'segment', 'otsu', 'yolo', 'resize', '224', '512', 'contour', 'bounding']):
            print("  PREP SNIPPET:", snip[:350])
            break

    # Search for Windowing / HU / Normalization
    print("\n--- 5. WINDOWING & HU ---")
    for m in re.finditer(r"(?:window|hounsfield|hu | hu,|hu\)|wl|ww|normalization|rgb|rescaling).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['hounsfield', 'hu', 'window', 'level', 'width', 'rgb', 'imagenet', '0, 1', '255']):
            print("  HU/NORM SNIPPET:", snip[:350])
            break

    # Search for External Validation
    print("\n--- 6. EXTERNAL VALIDATION ---")
    found_ext = False
    for m in re.finditer(r"(?:external|out-of-distribution|cross-dataset|kits|kauh|mendeley|tcia|generalization|another dataset|independent dataset).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['external dataset', 'another dataset', 'independent dataset', 'cross-dataset', 'kits', 'kauh', 'mendeley', 'tcia', 'generalization']):
            print("  EXT SNIPPET:", snip[:350])
            found_ext = True
            break
    if not found_ext:
        print("  EXT SNIPPET: None found.")

    # Search for Results and Accuracy
    print("\n--- 7. ACCURACY & PERFORMANCE ---")
    for m in re.finditer(r"(?:accuracy of|achieved an accuracy|accuracy:|test accuracy|overall accuracy|classification accuracy).{0,300}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        print("  ACC SNIPPET:", snip[:250])
        break

    # Limitations
    print("\n--- 8. LIMITATIONS ---")
    for m in re.finditer(r"(?:limitation|drawback|future work|future research|constraint).{0,500}", text, re.I):
        snip = re.sub(r'\s+', ' ', m.group(0))
        if any(k in snip.lower() for k in ['limitation', 'drawback', 'future work', 'lack of', 'scarcity', 'generaliz']):
            print("  LIM SNIPPET:", snip[:350])
            break

