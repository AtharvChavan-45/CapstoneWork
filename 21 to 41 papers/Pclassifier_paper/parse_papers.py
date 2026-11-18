import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

for f in files:
    reader = pypdf.PdfReader(f)
    text = ""
    for idx, page in enumerate(reader.pages):
        text += f"\n[PAGE {idx+1}]\n" + (page.extract_text() or "")
    
    print("="*60)
    print(f"FILE: {f}")
    
    # Title and authors
    print("--- FIRST 600 CHARS ---")
    print(text[:600].strip())
    
    # Dataset section search
    print("\n--- DATASET MENTIONS ---")
    data_matches = re.findall(r"(?:dataset|data collection|data acquisition|data description|material|subjects|experimental data).{0,500}", text, re.IGNORECASE | re.DOTALL)
    for m in data_matches[:3]:
        print("MATCH:", re.sub(r'\s+', ' ', m)[:250])
        
    # Split / Validation mentions
    print("\n--- SPLIT / LEAKAGE / VALIDATION MENTIONS ---")
    split_matches = re.findall(r"(?:split|train|test|validation|k-fold|cross-validation|leakage|patient|groupkfold).{0,300}", text, re.IGNORECASE | re.DOTALL)
    # print some representative matches
    unique_snippets = []
    for m in split_matches:
        snip = re.sub(r'\s+', ' ', m)[:200]
        if any(term in snip.lower() for term in ['80', '70', '90', 'ratio', 'k-fold', 'leakage', 'patient', 'split']):
            if snip not in unique_snippets and len(unique_snippets) < 4:
                unique_snippets.append(snip)
    for s in unique_snippets:
        print("SPLIT SNIP:", s)

    # Preprocessing / ROI mentions
    print("\n--- PREPROCESSING / ROI / CROP / HU / WINDOW ---")
    prep_matches = re.findall(r"(?:preprocess|roi|crop|yolo|u-net|otsu|segment|contour|window|hounsfield|hu|224|512|resize).{0,300}", text, re.IGNORECASE | re.DOTALL)
    prep_snippets = []
    for m in prep_matches:
        snip = re.sub(r'\s+', ' ', m)[:200]
        if any(term in snip.lower() for term in ['preprocess', 'roi', 'crop', 'otsu', 'window', 'hounsfield', 'hu', 'resize']):
            if snip not in prep_snippets and len(prep_snippets) < 4:
                prep_snippets.append(snip)
    for s in prep_snippets:
        print("PREP SNIP:", s)

    # Accuracy / Results / Limitations
    print("\n--- RESULTS & LIMITATIONS ---")
    res_matches = re.findall(r"(?:accuracy|accurac|limitation|future work|conclusion).{0,300}", text, re.IGNORECASE | re.DOTALL)
    res_snippets = []
    for m in res_matches:
        snip = re.sub(r'\s+', ' ', m)[:200]
        if any(term in snip.lower() for term in ['accura', 'limit', 'future']):
            if snip not in res_snippets and len(res_snippets) < 4:
                res_snippets.append(snip)
    for s in res_snippets:
        print("RES SNIP:", s)

