import csv
import re
import pypdf
import unicodedata

# 1. Extract reference bibliography from PDF to get citation numbers
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

# Surnames manual overrides due to layout/extraction limitations in PDF
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

# The explicit ordering from 22 to 41 as requested by the user
subset_papers = [
    (22, "Gu, Y., et al. (2021)"),
    (23, "Lee, J., et al. (2020)"),
    (24, "Fang, L., et al. (2023)"),
    (25, "Luo, R., et al. (2022)"),
    (26, "Hatsutani, T., et al. (2023)"),
    (27, "Sharma, K., et al. (2025)"),
    (28, "Elton, D.C., et al. (2022)"),
    (29, "Alzu'bi, D., et al. (2022)"),
    (30, "Heller, N., et al. (2023)"),
    (31, "Abdalla, P.A., et al. (2025)"),
    (32, "Ma, J., et al. (2022)"),
    (33, "Rathva, V. & Degadwala, D.S. (2025)"),
    (34, "Hossain, T., et al. (2024)"),
    (35, "Pimpalkar, A., et al. (2025)"),
    (36, "Bhandari, M., et al. (2023)"),
    (37, "Martín, Ó.A. & Sánchez, J. (2025)"),
    (38, "Abdelrahman, A. & Viriri, S. (2023)"),
    (39, "Zhao, T., et al. (2023)"),
    (40, "Chen, Z. & Liu, H. (2021)"),
    (41, "Sharon, J. J. & Anbarasi, L. J. (2025)")
]

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
            
            author = row_dict.get('Study/Author (Year)', '').strip()
            metrics = row_dict.get('Performance Metrics', '').strip()
            modality = row_dict.get('Imaging Modality', '').strip()
            dataset_val = row_dict.get(col_ds, '').strip()
            class_info = row_dict.get('Class Information', '').strip()
            counts_val = row_dict.get(col_counts, '').strip()
            
            rows.append({
                'author': author,
                'metrics': metrics,
                'modality': modality,
                'dataset_raw': dataset_val,
                'class_info': class_info,
                'counts_raw': counts_val
            })
        return rows

all_csv_rows = []
all_csv_rows.extend(read_csv('table.csv', 'Dataset', 'Image Counts & Class Breakdown'))
all_csv_rows.extend(read_csv('table2.csv', 'Dataset Details', 'Image Counts & Breakdown'))
all_csv_rows.extend(read_csv('table3.csv', 'Dataset Details', 'Image Counts & Breakdown'))

# Escape LaTeX characters (leaving pipe character unescaped so it renders as a vertical bar)
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

dataset_links_by_author = {
    "Gu, Y., et al. (2021)": [("PubMed Abstracts", "https://huggingface.co/datasets/ncbi/pubmed"), ("BLURB", "https://huggingface.co/datasets/bigbio/blurb")],
    "Lee, J., et al. (2020)": [("BioBERT", "https://github.com/naver/biobert-pretrained"), ("PubMed + PMC", "https://huggingface.co/datasets/ncbi/pubmed")],
    "Fang, L., et al. (2023)": [("BLURB Benchmark", "https://huggingface.co/datasets/bigbio/blurb")],
    "Luo, R., et al. (2022)": [("PubMed Abstracts", "https://huggingface.co/datasets/ncbi/pubmed")],
    "Hatsutani, T., et al. (2023)": [("KiTS19 Dataset", "https://github.com/neheller/kits19/tree/master/data")],
    "Sharma, K., et al. (2025)": [("CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")],
    "Elton, D.C., et al. (2022)": [("Clinical Dataset", "https://www.cancerimagingarchive.net/collection/ct-colonography/")],
    "Alzu'bi, D., et al. (2022)": [("New CT Dataset", "https://github.com/DaliaAlzubi/KidneyTumor/tree/main/Dataset")],
    "Heller, N., et al. (2023)": [("KiTS21 Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")],
    "Abdalla, P.A., et al. (2025)": [("Sulaimani/Rania Dataset", "https://www.kaggle.com/datasets/orvile/axial-ct-imaging-dataset-kidney-stone-detection")],
    "Ma, J., et al. (2022)": [("FLARE Dataset", "https://flare.grand-challenge.org/Data/")],
    "Rathva, V. & Degadwala, D.S. (2025)": [("Abdominal CT Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")],
    "Hossain, T., et al. (2024)": [("Enhanced CT Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")],
    "Pimpalkar, A., et al. (2025)": [("Clinical CT Repository", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")],
    "Bhandari, M., et al. (2023)": [("Kaggle CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")],
    "Martín, Ó.A. & Sánchez, J. (2025)": [("Multimodal Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone"), ("Mendeley", "https://data.mendeley.com/datasets/bhmdr45bh2/1")],
    "Abdelrahman, A. & Viriri, S. (2023)": [("KiTS Dataset (Kits19)", "https://github.com/neheller/kits19/tree/master/data"), ("Body Morphometry", "https://www.kaggle.com/competitions/body-morphometry-kidney-and-tumor/data")],
    "Zhao, T., et al. (2023)": [("KiTS21 Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")], 
    "Chen, Z. & Liu, H. (2021)": [("KiTS21 Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")],
    "Sharon, J. J. & Anbarasi, L. J. (2025)": [("CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")]
}

def format_dataset_cell(author, raw_dataset):
    if author in dataset_links_by_author:
        links = dataset_links_by_author[author]
        formatted = []
        for name, url in links:
            formatted.append(f"\\href{{{url}}}{{{escape_latex(name)}}}")
        res = ", ".join(formatted)
        if author == "Zhao, T., et al. (2023)":
            res += " + Private"
        return res
    return "Private Dataset"

# Standard Kaggle CT Kidney dataset breakdown
kaggle_breakdown = "Total: 12,446 images | Normal: 5,077 | Cyst: 3,709 | Tumor: 2,283 | Stone: 1,377"

# Generate LaTeX lines for the subset
latex_lines = []

for paper_num, author_name in subset_papers:
    csv_row = next((r for r in all_csv_rows if r['author'] == author_name), None)
    if not csv_row:
        continue
        
    ref_num = None
    if author_name in manual_overrides:
        ref_num = manual_overrides[author_name]
    else:
        norm_author = normalize(author_name)
        year_match = re.search(r'\b(20\d\d|19\d\d)\b', author_name)
        year = year_match.group(1) if year_match else None
        clean_author = re.sub(r'[\(\)\d\.,]|et al|&', ' ', norm_author).strip()
        author_tokens = [t for t in clean_author.split() if len(t) > 2 and t not in ['et', 'al']]
        
        best_match_idx = None
        best_match_score = 0
        for rn, rv in ref_dict.items():
            norm_ref = normalize(rv).replace("et al", " et al")
            has_year = year and year in norm_ref
            matching_tokens = sum(1 for t in author_tokens if t in norm_ref)
            if matching_tokens > 0:
                score = matching_tokens + (2 if has_year else 0)
                if score > best_match_score:
                    best_match_score = score
                    best_match_idx = rn
        ref_num = best_match_idx if best_match_idx is not None else 999
        
    author_cell = f"\\textbf{{{escape_latex(csv_row['author'])}}}~[{ref_num}]"
    metrics_cell = escape_latex(csv_row['metrics'])
    if not metrics_cell or metrics_cell.lower() == "n/a":
        metrics_cell = "N/A"
        
    modality_cell = escape_latex(csv_row['modality'])
    dataset_cell = format_dataset_cell(csv_row['author'], csv_row['dataset_raw'])
    
    class_cell = escape_latex(csv_row['class_info'])
    if not class_cell or class_cell.lower() == "n/a":
        class_cell = "N/A"
        
    # Get image counts breakdown
    # If the study utilizes the Kaggle CT Kidney Dataset and does not have the count, or has just the general count,
    # we replace it with the full class breakdown.
    raw_counts = csv_row['counts_raw']
    
    # Identify if the study uses Kaggle CT Kidney dataset
    is_kaggle_dataset = author_name in ["Sharma, K., et al. (2025)", "Rathva, V. & Degadwala, D.S. (2025)", 
                                        "Hossain, T., et al. (2024)", "Pimpalkar, A., et al. (2025)", 
                                        "Bhandari, M., et al. (2023)", "Martín, Ó.A. & Sánchez, J. (2025)"]
                                        
    if is_kaggle_dataset:
        counts_cell = escape_latex(kaggle_breakdown)
    else:
        counts_cell = escape_latex(raw_counts)
        
    # Formatting fixes: ensure | is printed as a vertical line by keeping | and using T1 fontenc.
    # Replace any double escaped or weird symbols.
    if not counts_cell or counts_cell.lower() == "n/a":
        counts_cell = "N/A"
        
    line = f"{author_cell} & {metrics_cell} & {modality_cell} & {dataset_cell} & {class_cell} & {counts_cell} \\\\"
    latex_lines.append(line)

# LaTeX Document Template
latex_template = r"""\documentclass{article}
\usepackage[T1]{fontenc}  % Required to render | as a proper vertical bar
\usepackage[utf8]{inputenc}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{ragged2e}
\usepackage{hyperref}
\usepackage[margin=1in]{geometry}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
}

\newcolumntype{L}[1]{>{\RaggedRight\arraybackslash}p{#1}}

\begin{document}

\section*{Summary of Reviewed Studies (Papers 22--41)}

This section presents the comprehensive synthesis of deep learning models, frameworks, and datasets utilized for renal disease diagnosis based on Papers 22 to 41.

\begin{longtable}{L{2.5cm} L{2.5cm} L{1.5cm} L{3.0cm} L{2.8cm} L{3.5cm}}
\caption{Taxonomic synthesis of deep learning literature for renal disease diagnosis (Papers 22--41).} \label{tab:renal_literature_subset}\\
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
for line in latex_lines:
    rows_str += line + "\n\\midrule\n"
rows_str = rows_str[:-len("\\midrule\n")]

latex_content = latex_template.replace("DATA_ROWS_PLACEHOLDER", rows_str)

with open('table.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("Generated table.tex with updated breakdowns successfully.")
