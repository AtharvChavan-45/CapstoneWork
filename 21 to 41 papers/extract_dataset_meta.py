import build_table_data as b
import csv

# We want to select the best candidate and see what dataset information it has
for i in range(1, 63):
    cands = b.cands_by_ref.get(i, [])
    # Select best candidate
    best_cand = None
    # 1. Excel for 42-62
    for c in cands:
        if c[0] == 'SLR_Tables_Final.xlsx':
            best_cand = c
            break
    # 2. Selected_Literature_Summary_v3.csv for 1-20
    if not best_cand:
        for c in cands:
            if c[0] == 'Selected_Literature_Summary_v3.csv':
                best_cand = c
                break
    # 3. CSVs for others
    if not best_cand:
        for c in cands:
            if c[0] in ['table.csv', 'table2.csv', 'table3.csv']:
                best_cand = c
                break
                
    filename, row = best_cand
    author = row.get('Study/Author (Year)', row.get('Author/Year', row.get('Study / Author (Year)', 'Unknown')))
    dataset_details = row.get('Dataset Details', row.get('Dataset', 'N/A'))
    
    # Try to find a link
    link = "N/A"
    
    # Match against Paper_Author_Dataset_Details.csv (using fuzzy match on author or direct lookup)
    # Let's search by ID first or author substring
    matched_detail = None
    for auth_key, val in b.details_by_author.items():
        # if auth_key's surname is in author
        surname = auth_key.split(',')[0].strip()
        if surname.lower() in author.lower():
            matched_detail = val
            break
            
    if matched_detail:
        # split by |
        parts = matched_detail.split('|')
        if len(parts) > 1:
            link = parts[1].strip()
            
    print(f'[{i}] Author: {author} | Dataset: {dataset_details} | Link: {link}')
