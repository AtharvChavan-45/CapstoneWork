import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

def extract_sections(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for i, p in enumerate(reader.pages):
        full_text += f"\n--- [PAGE {i+1}] ---\n" + (p.extract_text() or "")
    return full_text

for f in files:
    text = extract_sections(f)
    print("="*80)
    print(f"FILE: {f}")
    
    # 1. Dataset section
    print(">>> DATASET SECTION SNIPPETS:")
    for m in re.finditer(r"(dataset|data collection|data description|material|experimental setup)", text, re.IGNORECASE):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 600)
        snippet = text[start:end].replace('\n', ' ')
        if any(term in snippet.lower() for term in ['kaggle', 'normal', 'cyst', 'tumor', 'stone', '12,446', '12446', '3,709', 'kauh', 'kits', 'ultrasound']):
            print("  [DATA]", snippet[:350])
            break

    # 2. Splitting / Partitioning / Cross-validation / Leakage
    print(">>> SPLIT / LEAKAGE SNIPPETS:")
    for m in re.finditer(r"(split|train|test|ratio|k-fold|cross-validation|leakage|patient)", text, re.IGNORECASE):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 400)
        snippet = text[start:end].replace('\n', ' ')
        if any(term in snippet.lower() for term in ['80:20', '70:30', '80%', '70%', '10-fold', '5-fold', 'k-fold', 'patient', 'leakage', 'random']):
            print("  [SPLIT]", snippet[:300])
            break

    # 3. Preprocessing / ROI / Segmentation / Cropping / Resizing
    print(">>> PREPROCESSING / ROI SNIPPETS:")
    for m in re.finditer(r"(preprocess|roi|crop|yolo|u-net|otsu|contour|segment|resize|224|512)", text, re.IGNORECASE):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 400)
        snippet = text[start:end].replace('\n', ' ')
        if any(term in snippet.lower() for term in ['resize', 'crop', 'roi', 'yolo', 'otsu', 'segment', 'contour', '224', '512']):
            print("  [PREP]", snippet[:300])
            break

    # 4. Windowing / HU / Hounsfield / Normalization
    print(">>> WINDOWING / HU / NORMALIZATION SNIPPETS:")
    found_hu = False
    for m in re.finditer(r"(window|hounsfield|hu|level|width|normaliz)", text, re.IGNORECASE):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 400)
        snippet = text[start:end].replace('\n', ' ')
        if any(term in snippet.lower() for term in ['hounsfield', 'hu', 'window', 'level', 'width', 'rgb', 'imagenet', 'min-max', '[0, 1]']):
            print("  [HU/NORM]", snippet[:300])
            found_hu = True
            break
    if not found_hu:
        print("  [HU/NORM] No specific HU/windowing match found.")

    # 5. External validation
    print(">>> EXTERNAL DATASET VALIDATION:")
    for m in re.finditer(r"(external|generaliz|out-of-distribution|cross-dataset|kits|kauh|mendeley|tcia)", text, re.IGNORECASE):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 400)
        snippet = text[start:end].replace('\n', ' ')
        if any(term in snippet.lower() for term in ['external', 'kits', 'kauh', 'mendeley', 'generaliz', 'cross-dataset']):
            print("  [EXT]", snippet[:300])
            break

