import pypdf
import glob
import re

files = sorted(glob.glob("*.pdf"))

def get_text(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    pages = []
    for i, p in enumerate(reader.pages):
        pages.append(p.extract_text() or "")
    return "\n".join(pages)

for f in files:
    text = get_text(f)
    print("="*80)
    print(f"ANALYSIS FOR: {f}")
    
    # 1. Title, Authors, Year
    first_page = text[:2500]
    print("--- FIRST PAGE SNIPPET ---")
    print(first_page[:800])
    
    # Check dataset
    print("\n--- DATASET DETAILS ---")
    for pattern in [r"dataset", r"12,446", r"12446", r"3,709", r"normal", r"cyst", r"stone", r"tumor", r"mhc", r"kauh", r"kits"]:
        matches = [m.start() for m in re.finditer(pattern, text, re.I)]
        # print counts
    # find where dataset is described in detail
    data_desc = re.findall(r"(?:dataset\s+description|data\s+collection|dataset|materials?\s+and\s+methods?).{0,1000}", text, re.I | re.S)
    for d in data_desc[:2]:
        # Clean up whitespace
        clean_d = re.sub(r'\s+', ' ', d)
        print("DATASET DESC SNIP:", clean_d[:400])

    # Check split & leakage
    print("\n--- SPLITTING & LEAKAGE ---")
    split_matches = re.findall(r"(?:train.{0,30}test|split|ratio|cross-validation|k-fold|patient|slice|leakage|groupkfold).{0,300}", text, re.I | re.S)
    for sm in split_matches[:5]:
        sm_clean = re.sub(r'\s+', ' ', sm)
        if any(w in sm_clean.lower() for term in ['80', '70', '90', '10-fold', '5-fold', 'k-fold', 'patient', 'leakage', 'random', 'test'] for w in [term]):
            print("SPLIT SNIP:", sm_clean[:250])

    # Preprocessing / ROI
    print("\n--- PREPROCESSING & ROI ---")
    prep_matches = re.findall(r"(?:preprocess|roi|crop|yolo|u-net|contour|otsu|bounding|segment|mask|resize|dimension|input\s+size).{0,300}", text, re.I | re.S)
    for pm in prep_matches[:5]:
        pm_clean = re.sub(r'\s+', ' ', pm)
        if any(w in pm_clean.lower() for term in ['crop', 'roi', 'yolo', 'u-net', 'otsu', 'resize', '224', '512', 'contour', 'segment'] for w in [term]):
            print("PREP SNIP:", pm_clean[:250])

    # Windowing / HU / Normalization
    print("\n--- WINDOWING & HU ---")
    hu_matches = re.findall(r"(?:window|hounsfield|hu|level|width|normaliz).{0,300}", text, re.I | re.S)
    for hm in hu_matches[:5]:
        hm_clean = re.sub(r'\s+', ' ', hm)
        if any(w in hm_clean.lower() for term in ['hounsfield', 'hu', 'window', 'level', 'width', 'rgb', 'imagenet', 'standard', '[0, 1]'] for w in [term]):
            print("HU/NORM SNIP:", hm_clean[:250])

    # External dataset & metrics
    print("\n--- EXTERNAL VALIDATION ---")
    ext_matches = re.findall(r"(?:external|generaliz|cross-dataset|kits|kauh|mendeley|tcia).{0,300}", text, re.I | re.S)
    for em in ext_matches[:5]:
        em_clean = re.sub(r'\s+', ' ', em)
        print("EXT SNIP:", em_clean[:250])

    # Metrics & limitations
    print("\n--- METRICS & LIMITATIONS ---")
    lim_matches = re.findall(r"(?:limitation|drawback|future\s+work|conclusion).{0,400}", text, re.I | re.S)
    for lm in lim_matches[:3]:
        lm_clean = re.sub(r'\s+', ' ', lm)
        print("LIM SNIP:", lm_clean[:250])

