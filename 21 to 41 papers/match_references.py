import csv
import re
import pypdf

# Load references from PDF
reader = pypdf.PdfReader('survey paper.pdf')
ref_text = ''
for i in range(8, len(reader.pages)):
    ref_text += reader.pages[i].extract_text()

# Let's extract references with regex like [1], [2], etc.
# Format: [1] S. Degadwala, ...
ref_blocks = re.split(r'\[(\d+)\]', ref_text)
ref_dict = {}
current_idx = None
for block in ref_blocks:
    block = block.strip()
    if block.isdigit():
        current_idx = int(block)
    elif current_idx is not None:
        # Save reference text under its index
        ref_dict[current_idx] = block.replace('\n', ' ')

print(f'Extracted {len(ref_dict)} references from PDF.')

# Let's read all rows from CSVs
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

# Match each row to a reference index
matched_count = 0
unmatched_rows = []
for idx, r in enumerate(rows):
    author_str = r.get('Study/Author (Year)', '').strip()
    # Extract last name or key author names to match
    # e.g., "Soumya Challaru Sreenivas (2025)" -> "Sreenivas" or "Challaru"
    # "Alqahtani, A., et al. (2025)" -> "Alqahtani"
    # "Verma, S. & Singh, P. K. (2025)" -> "Verma"
    match_found = False
    
    # We will search for a combination of authors and year in each reference
    for ref_num, ref_val in ref_dict.items():
        # Clean author string and look for keywords in reference
        # Clean author name (remove initials, et al., years)
        clean_author = re.sub(r'[\(\)\d\.,]|et al|&', ' ', author_str).strip()
        author_tokens = [t for t in clean_author.split() if len(t) > 2]
        
        # Check if year is in reference
        year_match = re.search(r'\b(20\d\d|19\d\d)\b', author_str)
        year = year_match.group(1) if year_match else None
        
        if year and year in ref_val:
            # Check if any main author token is in reference
            matches_author = any(t.lower() in ref_val.lower() for t in author_tokens)
            if matches_author:
                r['ref_num'] = ref_num
                r['ref_text'] = ref_val
                matched_count += 1
                match_found = True
                break
    
    if not match_found:
        unmatched_rows.append(author_str)

print(f'Successfully matched {matched_count}/{len(rows)} rows.')
if unmatched_rows:
    print('Unmatched rows:', unmatched_rows)
else:
    print('All rows successfully matched!')
