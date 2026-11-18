import match_all_sources as m

for i in range(1, 63):
    cands = m.mappings.get(i, [])
    filenames = [c[0] for c in cands]
    print(f'[{i}] cands count: {len(cands)}, files: {filenames}')
