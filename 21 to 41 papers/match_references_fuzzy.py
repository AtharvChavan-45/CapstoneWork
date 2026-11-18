import csv
import re
import pypdf
import unicodedata

# Load references from PDF
reader = pypdf.PdfReader('survey paper.pdf')
ref_text = ''
for i in range(8, len(reader.pages)):
    ref_text += reader.pages[i].extract_text()

# Extract references [1] to [62]
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
    # Normalize unicode characters (accents, curly quotes)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.replace("’", "'").replace("`", "'")
    return text.lower()

# Read CSV files
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
            row_dict['_filename'] = filename
            row_dict['_col_ds'] = col_ds
            row_dict['_col_counts'] = col_counts
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
    norm_author = normalize(author_str)
    
    # Extract year
    year_match = re.search(r'\b(20\d\d|19\d\d)\b', author_str)
    year = year_match.group(1) if year_match else None
    
    # Extract main surname tokens (words longer than 2 characters and not 'et', 'al')
    clean_author = re.sub(r'[\(\)\d\.,]|et al|&', ' ', norm_author).strip()
    author_tokens = [t for t in clean_author.split() if len(t) > 2 and t not in ['et', 'al']]
    
    match_found = False
    best_match_idx = None
    best_match_score = 0
    
    for ref_num, ref_val in ref_dict.items():
        norm_ref = normalize(ref_val)
        
        # Check if year matches
        has_year = True
        if year and year not in norm_ref:
            has_year = False
            
        # Count matching author tokens
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
        unmatched_rows.append((author_str, author_tokens, year))

print(f'Successfully matched {matched_count}/{len(rows)} rows.')
if unmatched_rows:
    print('Unmatched rows:')
    for item in unmatched_rows:
        print(item)
else:
    print('All rows successfully matched!')
