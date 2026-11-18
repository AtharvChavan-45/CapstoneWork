import build_table_data as b
import csv

counts = {}

# Select the best candidate for each of the 62 references
for idx in range(1, 63):
    cands = b.cands_by_ref.get(idx, [])
    if not cands: continue
    
    best_cand = None
    for c in cands:
        if c[0] == 'SLR_Tables_Final.xlsx':
            best_cand = c
            break
    if not best_cand:
        for c in cands:
            if c[0] == 'Selected_Literature_Summary_v3.csv':
                best_cand = c
                break
    if not best_cand:
        for c in cands:
            if c[0] in ['table.csv', 'table2.csv', 'table3.csv']:
                best_cand = c
                break
                
    row = best_cand[1]
    raw_dataset = row.get('Dataset Details', row.get('Dataset', 'N/A')).strip()
    
    # Categorize
    ds_lower = raw_dataset.lower()
    if 'kaggle' in ds_lower or 'ct kidney dataset' in ds_lower or 'ct-scan kidney' in ds_lower or 'abdominal ct dataset' in ds_lower or 'enhanced ct dataset' in ds_lower or 'clinical ct repository' in ds_lower or 'riñones dataset' in ds_lower or 'kidney stone dataset' in ds_lower or 'mhc-ct dataset' in ds_lower:
        category = 'Kaggle CT Kidney'
    elif 'kits19' in ds_lower or 'kits21' in ds_lower or 'kits dataset' in ds_lower or '3d ct dataset' in ds_lower:
        category = 'KiTS (KiTS19 / KiTS21)'
    elif 'private' in ds_lower or 'custom urine sediment' in ds_lower or 'institutional' in ds_lower or 'clinical data from 27 patients' in ds_lower:
        category = 'Custom / Private'
    elif 'pubmed' in ds_lower or 'biobert' in ds_lower or 'blurb' in ds_lower:
        category = 'PubMed'
    elif 'kauh' in ds_lower or 'new ct dataset' in ds_lower:
        category = 'KAUH'
    elif 'maccrobat' in ds_lower:
        category = 'MACCROBAT'
    elif 'nhanes' in ds_lower:
        category = 'NHANES'
    elif 'seer' in ds_lower:
        category = 'SEER'
    elif 'busi' in ds_lower or 'bus dataset' in ds_lower or 'dataset b' in ds_lower:
        category = 'Breast Ultrasound (BUSI)'
    elif 'synapse' in ds_lower:
        category = 'Synapse Multi-organ'
    elif 'isic 2018' in ds_lower:
        category = 'ISIC 2018 Skin Lesion'
    elif 'cvc-clinicdb' in ds_lower:
        category = 'CVC-ClinicDB'
    elif 'flare' in ds_lower:
        category = 'FLARE'
    elif 'c4kc-kits' in ds_lower:
        category = 'C4KC-KiTS (TCIA)'
    else:
        category = 'Other / Survey'
        
    counts[category] = counts.get(category, 0) + 1

# Sort and print
for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f'{cat}: {count}')
