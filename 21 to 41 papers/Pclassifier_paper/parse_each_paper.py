import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

def get_paper_details(filename):
    reader = pypdf.PdfReader(filename)
    text = ""
    for idx, p in enumerate(reader.pages):
        text += f"\n[PAGE {idx+1}]\n" + (p.extract_text() or "")
        
    print(f"\n################################################################################")
    print(f"FILE: {filename}")
    print(f"################################################################################")
    
    # 1. Title / Authors / Publication
    print("--- TITLE & AUTHORS (FIRST 800 CHARACTERS) ---")
    print(text[:800].strip())
    
    # Look for dataset name and size
    print("\n--- DATASET DETAILS ---")
    data_matches = re.finditer(r"(dataset|data collection|data description|material|experimental setup)", text, re.I)
    for dm in data_matches:
        snip = text[dm.start():dm.start()+800].replace('\n', ' ')
        if any(w in snip.lower() for w in ['kaggle', '12,446', '12446', '3,709', '3709', 'cyst', 'tumor', 'stone', 'normal', 'kauh', 'kits']):
            print("MATCH:", re.sub(' +', ' ', snip)[:600])
            break

    # Look for splitting details
    print("\n--- SPLIT & LEAKAGE DETAILS ---")
    split_matches = re.finditer(r"(split|train|test|k-fold|cross-validation|leakage|patient|slice|ratio)", text, re.I)
    found_split = False
    for sm in split_matches:
        snip = text[max(0, sm.start()-50):min(len(text), sm.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['80:20', '70:30', '80%', '70%', '10-fold', '5-fold', 'k-fold', 'train_test_split', 'patient', 'leakage', 'slice', 'ratio', 'partition']):
            if any(term in snip.lower() for term in ['train', 'test', 'eval', 'split']):
                print("SPLIT MATCH:", re.sub(' +', ' ', snip)[:500])
                found_split = True
                break
    if not found_split:
        print("No explicit split match found via search.")

    # Look for Preprocessing / ROI / Cropping
    print("\n--- PREPROCESSING & ROI CROPPING ---")
    prep_matches = re.finditer(r"(preprocess|roi|crop|yolo|u-net|contour|otsu|segment|bounding|resize|dimension|input size)", text, re.I)
    found_prep = False
    for pm in prep_matches:
        snip = text[max(0, pm.start()-50):min(len(text), pm.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['crop', 'roi', 'yolo', 'u-net', 'otsu', 'resize', 'contour', 'segment', 'bounding', '224', '512']):
            print("PREP MATCH:", re.sub(' +', ' ', snip)[:500])
            found_prep = True
            break
    if not found_prep:
        print("No explicit preprocessing match found via search.")

    # Look for HU / Windowing / Normalization
    print("\n--- HU / WINDOWING / NORMALIZATION ---")
    hu_matches = re.finditer(r"(window|hounsfield|hu | hu,|hu\)|wl|ww|normalization|rgb|rescaling|intensity|standardization)", text, re.I)
    found_hu = False
    for hm in hu_matches:
        snip = text[max(0, hm.start()-50):min(len(text), hm.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['hounsfield', 'hu', 'window', 'level', 'width', 'rgb', 'imagenet', '255', '[0, 1]']):
            print("HU MATCH:", re.sub(' +', ' ', snip)[:500])
            found_hu = True
            break
    if not found_hu:
        print("No explicit windowing/HU match found via search.")

    # Look for External Validation
    print("\n--- EXTERNAL VALIDATION ---")
    ext_matches = re.finditer(r"(external|out-of-distribution|cross-dataset|kits|kauh|mendeley|tcia|generaliz|independent dataset)", text, re.I)
    found_ext = False
    for em in ext_matches:
        snip = text[max(0, em.start()-50):min(len(text), em.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['external dataset', 'tested on', 'evaluated on', 'kits', 'kauh', 'mendeley', 'tcia', 'another dataset', 'cross-dataset', 'unseen dataset']):
            print("EXT MATCH:", re.sub(' +', ' ', snip)[:500])
            found_ext = True
            break
    if not found_ext:
        print("No external dataset validation found.")

    # Look for Results / Accuracy
    print("\n--- RESULTS / ACCURACY ---")
    res_matches = re.finditer(r"(accuracy|f1-score|f1 score|results|performance)", text, re.I)
    for rm in res_matches:
        snip = text[max(0, rm.start()-50):min(len(text), rm.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['accuracy of', 'achieved', 'test accuracy', 'overall accuracy', '99.', '98.', '97.', '96.', '95.', '94.', '93.', '92.', '91.', '90.']):
            print("RES MATCH:", re.sub(' +', ' ', snip)[:500])
            break

    # Look for Limitations
    print("\n--- LIMITATIONS ---")
    lim_matches = re.finditer(r"(limitation|drawback|future work|future research)", text, re.I)
    found_lim = False
    for lm in lim_matches:
        snip = text[max(0, lm.start()-50):min(len(text), lm.end()+350)].replace('\n', ' ')
        if any(w in snip.lower() for w in ['limitation', 'drawback', 'future', 'scarcity', 'generaliz', 'challenge']):
            print("LIM MATCH:", re.sub(' +', ' ', snip)[:500])
            found_lim = True
            break
    if not found_lim:
        print("No limitation snippet found.")

for f in files:
    get_paper_details(f)
