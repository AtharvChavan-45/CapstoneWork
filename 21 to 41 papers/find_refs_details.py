import re
import pypdf

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

unmatched = [
    'Li', 'Macin', 'Gu', 'Alzubi', 'Ma', 'Martin', 'Ji', 'He', 'Elmaagac', 'Ye'
]

for name in unmatched:
    print(f"=== Matches for '{name}' ===")
    for idx, ref in ref_dict.items():
        if name.lower() in ref.lower():
            print(f"[{idx}]: {ref}")
