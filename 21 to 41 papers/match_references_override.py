import csv
import re
import pypdf
import unicodedata

# Load references from PDF
reader = pypdf.PdfReader('survey paper.pdf')
ref_text = ''
for i in range(8, len(reader.pages)):
    ref_text += reader.pages[i].extract_text()

ref_blocks = re.split(r'\[(\d+)\]', ref_text)
ref_dict = {}
current_idx = None
for block in ref_blocks:
    block = block.strip()
    if block.isdigit():
        current_idx = int(block)
    elif current_idx is not None:
        ref_dict[current_idx] = block.replace('\n', ' ')

def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.replace("’", "'").replace("`", "'")
    return text.lower()

manual_overrides = {
    'Li, D., et al. (2022)': 31,
    'Maçin, G., et al. (2025)': 52,
    'Gu, Y., et al. (2021)': 47,
    "Alzu'bi, D., et al. (2022)": 18,
    'Ma, J., et al. (2022)': 51,
    'Martín, Ó.A. & Sánchez, J. (2025)': 42,
    'Ji, Z., et al. (2024)': 16,
    'He et al. (2023)': 28,
    'Elmaağaç et al. (2026)': 32,
    'Ye, Y., et al. (2026)': 58
}

def read_csv(filename, col_ds, col_counts):
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = [h.strip() for h in next(reader)]
        rows = []
        for r in reader:
            if not r: continue
            row_dict = {}
            for h, val in zip(headers, r):
                row_dict[h] = val
            rows.append(row_dict)
        return rows

rows = []
rows.extend(read_csv('table.csv', 'Dataset', 'Image Counts & Class Breakdown'))
rows.extend(read_csv('table2.csv', 'Dataset Details', 'Image Counts & Breakdown'))
rows.extend(read_csv('table3.csv', 'Dataset Details', 'Image Counts & Breakdown'))

matched_count = 0
unmatched_rows = []

for r in rows:
    author_str = r.get('Study/Author (Year)', '').strip()
    
    if author_str in manual_overrides:
        ref_num = manual_overrides[author_str]
        r['ref_num'] = ref_num
        r['ref_text'] = ref_dict[ref_num]
        matched_count += 1
        continue
        
    norm_author = normalize(author_str)
    year_match = re.search(r'\b(20\d\d|19\d\d)\b', author_str)
    year = year_match.group(1) if year_match else None
    clean_author = re.sub(r'[\(\)\d\.,]|et al|&', ' ', norm_author).strip()
    author_tokens = [t for t in clean_author.split() if len(t) > 2 and t not in ['et', 'al']]
    
    best_match_idx = None
    best_match_score = 0
    
    for ref_num, ref_val in ref_dict.items():
        norm_ref = normalize(ref_val).replace("et al", " et al")
        
        has_year = True
        if year and year not in norm_ref:
            has_year = False
            
        matching_tokens = sum(1 for t in author_tokens if t in norm_ref)
        
        if matching_tokens > 0:
            score = matching_tokens + (2 if has_year else 0)
            if score > best_match_score:
                best_match_score = score
                best_match_idx = ref_num
                
    if best_match_idx is not None and best_match_score >= 2:
        r['ref_num'] = best_match_idx
        r['ref_text'] = ref_dict[best_match_idx]
        matched_count += 1
    else:
        unmatched_rows.append(author_str)

print(f'Successfully matched {matched_count}/{len(rows)} rows.')
if unmatched_rows:
    print('Unmatched rows:', unmatched_rows)
else:
    print('All rows successfully matched!')
