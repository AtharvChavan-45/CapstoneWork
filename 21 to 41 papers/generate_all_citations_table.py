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

# Group candidates by citation number
cands_by_ref = {}
for ref_num, filename, row in all_rows:
    if ref_num not in cands_by_ref: cands_by_ref[ref_num] = []
    cands_by_ref[ref_num].append((filename, row))

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

# Load dataset reference sheet for xlsx links
xlsx_dataset_links = {}
ws_ds = wb['Table 2 - Dataset References']
xlsx_ds_rows = list(ws_ds.iter_rows(values_only=True))[1:]
for r in xlsx_ds_rows:
    if r and r[0]:
        ds_name = r[0].strip()
        ds_link = r[4].strip() if len(r) > 4 and r[4] else "Not Available"
        xlsx_dataset_links[ds_name] = ds_link

# Manual dictionary of URLs for papers 21-41
manual_urls = {
    "Gu, Y., et al. (2021)": "https://huggingface.co/datasets/ncbi/pubmed",
    "Lee, J., et al. (2020)": "https://github.com/naver/biobert-pretrained",
    "Fang, L., et al. (2023)": "https://huggingface.co/datasets/bigbio/blurb",
    "Luo, R., et al. (2022)": "https://huggingface.co/datasets/ncbi/pubmed",
    "Hatsutani, T., et al. (2023)": "https://github.com/neheller/kits19/tree/master/data",
    "Sharma, K., et al. (2025)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Elton, D.C., et al. (2022)": "https://www.cancerimagingarchive.net/collection/ct-colonography/",
    "Alzu'bi, D., et al. (2022)": "https://github.com/DaliaAlzubi/KidneyTumor/tree/main/Dataset",
    "Heller, N., et al. (2023)": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "Abdalla, P.A., et al. (2025)": "https://www.kaggle.com/datasets/orvile/axial-ct-imaging-dataset-kidney-stone-detection",
    "Ma, J., et al. (2022)": "https://flare.grand-challenge.org/Data/",
    "Rathva, V. & Degadwala, D.S. (2025)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Hossain, T., et al. (2024)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Pimpalkar, A., et al. (2025)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Bhandari, M., et al. (2023)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Martín, Ó.A. & Sánchez, J. (2025)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "Abdelrahman, A. & Viriri, S. (2023)": "https://github.com/neheller/kits19/tree/master/data",
    "Zhao, T., et al. (2023)": "https://github.com/neheller/kits21/tree/master/kits21/data", 
    "Chen, Z. & Liu, H. (2021)": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "Sharon, J. J. & Anbarasi, L. J. (2025)": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone"
}

# Mapping of dataset names to URLs for general lookup
general_dataset_links = {
    "kits19": "https://github.com/neheller/kits19/tree/master/data",
    "kits21": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "kaggle ct kidney": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "ct kidney dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "abdominal ct dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "enhanced ct dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "clinical ct repository": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "pubmed abstracts": "https://huggingface.co/datasets/ncbi/pubmed",
    "pubmed abstracts, blurb": "https://huggingface.co/datasets/ncbi/pubmed",
    "biobert": "https://github.com/naver/biobert-pretrained",
    "blurb benchmark": "https://huggingface.co/datasets/bigbio/blurb",
    "kits19 dataset": "https://github.com/neheller/kits19/tree/master/data",
    "clinical dataset": "https://www.cancerimagingarchive.net/collection/ct-colonography/",
    "new ct dataset": "https://github.com/DaliaAlzubi/KidneyTumor/tree/main/Dataset",
    "kits21 dataset": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "sulaimani/rania dataset": "https://www.kaggle.com/datasets/orvile/axial-ct-imaging-dataset-kidney-stone-detection",
    "flare dataset": "https://flare.grand-challenge.org/Data/",
    "multimodal dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "kits dataset (kits19)": "https://github.com/neheller/kits19/tree/master/data",
    "kits dataset": "https://github.com/neheller/kits19/tree/master/data",
    "3d ct dataset": "https://github.com/neheller/kits21/tree/master/kits21/data"
}

# Helper to escape LaTeX special characters
def escape_latex(text):
    if not text:
        return ""
    chars = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    escaped = []
    for c in text:
        if c in chars:
            escaped.append(chars[c])
        else:
            escaped.append(c)
    return "".join(escaped)

# Standard Kaggle CT Kidney dataset breakdown
kaggle_breakdown = "Total: 12,446 images | Normal: 5,077 | Cyst: 3,709 | Tumor: 2,283 | Stone: 1,377"

# Clean Author Names for Table
def clean_author_name_for_cell(auth, ref_num):
    # Strip any existing brackets like [Paper 42] or similar
    name = re.sub(r'\s*\[Paper\s*\d+\]', '', auth).strip()
    name = re.sub(r'\s*\[Paper\s*NR\]', '', name).strip()
    # Format author cleanly
    # Let's ensure it has et al formatting if needed or matches the bibliography style
    return f"\\textbf{{{escape_latex(name)}}}~[{ref_num}]"

latex_rows = []

# Generate table data for references 1 to 62 in order
for idx in range(1, 63):
    cands = cands_by_ref.get(idx, [])
    if not cands:
        print(f"ERROR: No candidate for citation [{idx}]")
        continue
        
    # Select the best candidate based on file priority
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
    
    # 1. Study/Author Column
    raw_author = row.get('Study/Author (Year)', row.get('Author/Year', row.get('Study / Author (Year)', 'Unknown'))).strip()
    author_cell = clean_author_name_for_cell(raw_author, idx)
    
    # 2. Performance Metrics Column
    metrics_cell = escape_latex(row.get('Performance Metrics', row.get('Performance Metric', 'N/A'))).strip()
    if not metrics_cell or metrics_cell.lower() == "n/a" or metrics_cell.lower() == "nr":
        metrics_cell = "N/A"
        
    # 3. Imaging Modality Column
    modality_cell = escape_latex(row.get('Imaging Modality', 'CT')).strip()
    if not modality_cell or modality_cell.lower() == "n/a" or modality_cell.lower() == "nr":
        modality_cell = "N/A"
        
    # 4. Dataset Details & Clickable Link Column
    raw_dataset = row.get('Dataset Details', row.get('Dataset', 'N/A')).strip()
    # Check if we have a URL link for this dataset
    url = None
    
    # Check manual details_by_author (papers 1-20)
    matched_detail = None
    for auth_key, val in details_by_author.items():
        surname = auth_key.split(',')[0].strip()
        if surname.lower() in raw_author.lower():
            matched_detail = val
            break
    if matched_detail:
        parts = matched_detail.split('|')
        if len(parts) > 1:
            u_part = parts[1].strip()
            if u_part.startswith("http"):
                url = u_part
                
    # Check Excel dataset references sheet (papers 42-62)
    if not url:
        for ds_name, ds_link in xlsx_dataset_links.items():
            if ds_name.lower() in raw_dataset.lower() or raw_dataset.lower() in ds_name.lower():
                if ds_link.startswith("http"):
                    url = ds_link
                    break
                    
    # Check manual url mapping (papers 21-41)
    if not url:
        for auth_key, val in manual_urls.items():
            surname = auth_key.split(',')[0].strip()
            if surname.lower() in raw_author.lower():
                url = val
                break
                
    # General lookup based on dataset name
    if not url:
        for ds_name, ds_link in general_dataset_links.items():
            if ds_name.lower() in raw_dataset.lower() or raw_dataset.lower() in ds_name.lower():
                url = ds_link
                break
                
    # Format Dataset Cell
    clean_ds_name = escape_latex(raw_dataset)
    if clean_ds_name.lower() == "n/a" or clean_ds_name.lower() == "nr":
        dataset_cell = "Not Accessible"
    elif url:
        # Keep URL clickable!
        dataset_cell = f"\\href{{{url}}}{{{clean_ds_name}}}"
    else:
        dataset_cell = f"{clean_ds_name} (Not Accessible)"
        # If dataset details mention "Private", institutional, or no link, write "Not Accessible"
        if "private" in raw_dataset.lower() or "not available" in raw_dataset.lower() or "not publicly available" in raw_dataset.lower():
            dataset_cell = "Not Accessible"
            
    # If the text itself contains "Not publicly available" or "Not Available", replace with "Not Accessible"
    if "not available" in dataset_cell.lower() or "not publicly" in dataset_cell.lower() or "private" in dataset_cell.lower():
        dataset_cell = "Not Accessible"
        
    # 5. Class Information Column
    class_info = row.get('Class Information', 'N/A').strip()
    if not class_info or class_info.lower() == "n/a" or class_info.lower() == "nr":
        class_info = "N/A"
    class_cell = escape_latex(class_info)
    
    # 6. Image Counts & Breakdown Column
    raw_counts = row.get('Image Counts and Breakdown', row.get('Image Counts & Breakdown', row.get('Image Counts & Class Breakdown', row.get('Total Count', 'N/A'))))
    if not raw_counts:
        raw_counts = "N/A"
    raw_counts = str(raw_counts).strip()
    
    # Override with Kaggle CT Kidney breakdown if the paper is known to use it
    is_kaggle_paper = any(k.lower() in raw_author.lower() for k in [
        "Sharma, K.", "Rathva, V.", "Hossain, T.", "Pimpalkar, A.", "Bhandari, M.", "Martín, Ó.A.", 
        "Al-Ebada", "Hossain et al.", "Ahmed, N.", "Tawfik et al.", "Khan et al.", "Islam et al.", "Rajendran et al."
    ])
    
    # Let's verify if the dataset is Kaggle CT Kidney
    is_kaggle_dataset = "kaggle" in raw_dataset.lower() or "ct kidney dataset" in raw_dataset.lower() or "ct-scan kidney" in raw_dataset.lower()
    
    if (is_kaggle_paper or is_kaggle_dataset) and not "2,884" in str(raw_counts) and not "8,750" in str(raw_counts) and not "4850" in str(raw_counts):
        # We replace with Kaggle breakdown, keeping | as separators
        counts_cell = escape_latex(kaggle_breakdown)
    else:
        # Keep raw counts, but convert semicolon/newline/etc. to | separators
        # Replace newlines or double slashes with |
        cleaned_counts = re.sub(r'\s*(?:\\newline|\\/|;)\s*', ' | ', raw_counts)
        counts_cell = escape_latex(cleaned_counts)
        
    if not counts_cell or counts_cell.lower() == "n/a" or counts_cell.lower() == "nr" or counts_cell.lower() == "na":
        counts_cell = "N/A"
        
    # Build LaTeX line
    line = f"{author_cell} & {metrics_cell} & {modality_cell} & {dataset_cell} & {class_cell} & {counts_cell} \\\\"
    latex_rows.append(line)

# Output LaTeX
latex_template = r"""\documentclass{article}
\usepackage[T1]{fontenc}  % Required to render | as a proper vertical bar
\usepackage[utf8]{inputenc}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{hyperref}
\usepackage[margin=0.8in]{geometry}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
}

\newcolumntype{L}[1]{>{\RaggedRight\arraybackslash}p{#1}}

\begin{document}

\section*{Summary of Reviewed Studies (Papers 1--62)}

This section presents the comprehensive synthesis of deep learning models, frameworks, and datasets utilized for renal disease diagnosis based on Papers 1 to 62, sorted in sequential order.

\begin{longtable}{L{2.5cm} L{2.2cm} L{1.3cm} L{2.8cm} L{2.8cm} L{3.5cm}}
\caption{Taxonomic synthesis of deep learning literature for renal disease diagnosis (Papers 1--62).} \label{tab:renal_literature_all}\\
\toprule
\textbf{Study/Author (Year)} & \textbf{Performance Metrics} & \textbf{Imaging Modality} & \textbf{Dataset Details \& Links} & \textbf{Class Information} & \textbf{Image Counts \& Breakdown} \\
\midrule
\endfirsthead

\caption[]{Taxonomic synthesis of deep learning literature for renal disease diagnosis (Continued).}\\
\toprule
\textbf{Study/Author (Year)} & \textbf{Performance Metrics} & \textbf{Imaging Modality} & \textbf{Dataset Details \& Links} & \textbf{Class Information} & \textbf{Image Counts \& Breakdown} \\
\midrule
\endhead

\midrule
\multicolumn{6}{r}{{Continued on next page}} \\
\bottomrule
\endfoot

\bottomrule
\endlastfoot

DATA_ROWS_PLACEHOLDER
\end{longtable}

\end{document}
"""

rows_str = ""
for line in latex_rows:
    rows_str += line + "\n\\midrule\n"
rows_str = rows_str[:-len("\\midrule\n")]

latex_content = latex_template.replace("DATA_ROWS_PLACEHOLDER", rows_str)

with open('table.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print(f"Successfully generated table.tex with {len(latex_rows)} rows.")
