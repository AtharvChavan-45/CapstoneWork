import csv
import re
import openpyxl
import pypdf
import unicodedata

# 1. Load references from PDF bibliography
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

# Manual overrides for citation indices based on previous mapping
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
    'Ye, Y., et al. (2026)': 58,
    'Raj et al. (2022) [Paper 42]': 60,
    'Ji et al. (2024) [Paper 43]': 16,
    'Gohil et al. (2024) [Paper 44]': 17,
    'Azad et al. (2023) [Paper 45]': 29,
    'Al-Ebada et al. (2026) [Paper 46]': 34,
    'Hossain et al. (2025) [Paper 47]': 49,
    'He et al. (2023) [Paper 48]': 28,
    'Lan et al. (2024) [Paper 49]': 30,
    'Papanastasiou et al. (2024) [Paper 50]': 43,
    'Elmaagac et al. (2026) [Paper 51]': 32,
    'Abdelrahman et al. (2022) [Paper 52]': 15,
    'Xie et al. (2020) [Paper 53]': 53,
    'Nguyen et al. (2024) [Paper 54]': 54,
    'Gao et al. (2026) [Paper 56]': 55,
    'Almukadi et al. (2025) [Paper 59]': 59,
    'Li et al. (2022) [Paper 60]': 31,
    'Liang (2025) [Paper 61]': 13,
    'Paper 62 (Author NR)': 62,
}

def get_ref_num(author_name):
    author_name = author_name.strip()
    if author_name in manual_overrides:
        return manual_overrides[author_name]
        
    norm_author = normalize(author_name)
    year_match = re.search(r'\b(20\d\d|19\d\d)\b', author_name)
    year = year_match.group(1) if year_match else None
    
    clean_author = re.sub(r'[\(\)\d\.,]|et al|&|\[paper \d+\]', ' ', norm_author).strip()
    author_tokens = [t for t in clean_author.split() if len(t) > 2 and t not in ['et', 'al']]
    
    best_match_idx = None
    best_match_score = 0
    for ref_num, ref_val in ref_dict.items():
        norm_ref = normalize(ref_val).replace("et al", " et al")
        has_year = year and year in norm_ref
        matching_tokens = sum(1 for t in author_tokens if t in norm_ref)
        if matching_tokens > 0:
            score = matching_tokens + (2 if has_year else 0)
            if score > best_match_score:
                best_match_score = score
                best_match_idx = ref_num
                
    if best_match_idx is not None and best_match_score >= 2:
        return best_match_idx
    return None

# Load CSV files and find their mappings
def read_csv(filename, col_ds, col_counts, col_author):
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = [h.strip() for h in next(reader)]
        rows = []
        for row in reader:
            if not row: continue
            row_dict = dict(zip(headers, row))
            author = row_dict.get(col_author, '').strip()
            ref_num = get_ref_num(author)
            if ref_num:
                rows.append((ref_num, filename, row_dict))
        return rows

all_rows = []
all_rows.extend(read_csv('table.csv', 'Dataset', 'Image Counts & Class Breakdown', 'Study/Author (Year)'))
all_rows.extend(read_csv('table2.csv', 'Dataset Details', 'Image Counts & Breakdown', 'Study/Author (Year)'))
all_rows.extend(read_csv('table3.csv', 'Dataset Details', 'Image Counts & Breakdown', 'Study/Author (Year)'))
all_rows.extend(read_csv('Selected_Literature_Summary_v3.csv', 'Dataset Details', 'Total Count', 'Author/Year'))

# Load Excel file Table 1
wb = openpyxl.load_workbook('SLR_Tables_Final.xlsx', read_only=True)
ws = wb['Table 1 - Literature Comparison']
xlsx_headers = [h.strip() for h in next(ws.iter_rows(values_only=True))]
for r in ws.iter_rows(values_only=True):
    if not r or r[0] == 'Study / Author (Year)': continue
    row_dict = dict(zip(xlsx_headers, r))
    author = row_dict['Study / Author (Year)'].strip()
    ref_num = get_ref_num(author)
    if ref_num:
        all_rows.append((ref_num, 'SLR_Tables_Final.xlsx', row_dict))

# Load Paper_Author_Dataset_Details.csv for dataset links of papers 1-20
details_by_author = {}
with open('Paper_Author_Dataset_Details.csv') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if row:
            author = row[1].strip()
            details_and_link = row[2].strip()
            details_by_author[author] = details_and_link

# Group candidates by citation number
cands_by_ref = {}
for ref_num, filename, row in all_rows:
    if ref_num not in cands_by_ref: cands_by_ref[ref_num] = []
    cands_by_ref[ref_num].append((filename, row))

# Print grouping sizes
for i in range(1, 63):
    print(f'[{i}] cands count: {len(cands_by_ref.get(i, []))}')
