import match_all_sources as m

# Let's inspect the selected row for each reference
for i in range(1, 63):
    cands = m.mappings.get(i, [])
    # We want to select the best cand:
    # 1. If SLR_Tables_Final.xlsx is in filenames, and the reference is in [42..62] range or matches
    # actually, SLR_Tables_Final.xlsx has very specific rows.
    # Let's see:
    best_cand = None
    
    # Priority 1: SLR_Tables_Final.xlsx (especially for 42-62)
    for c in cands:
        if c[0] == 'SLR_Tables_Final.xlsx':
            best_cand = c
            break
            
    # Priority 2: Selected_Literature_Summary_v3.csv (especially for 1-20)
    if not best_cand:
        for c in cands:
            if c[0] == 'Selected_Literature_Summary_v3.csv':
                best_cand = c
                break
                
    # Priority 3: table.csv, table2.csv, table3.csv
    if not best_cand:
        for c in cands:
            if c[0] in ['table.csv', 'table2.csv', 'table3.csv']:
                best_cand = c
                break
                
    if best_cand:
        filename, row = best_cand
        author_val = row.get('Study/Author (Year)', row.get('Author/Year', row.get('Study / Author (Year)', 'Unknown')))
        print(f'[{i}] -> Source: {filename} | Author: {author_val}')
    else:
        print(f'[{i}] -> NO MATCH')
