import csv
import re
import pypdf
import unicodedata

# 1. Extract reference bibliography from PDF to get exact mapping and citation numbers
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

rows = []
rows.extend(read_csv('table.csv', 'Dataset', 'Image Counts & Class Breakdown'))
rows.extend(read_csv('table2.csv', 'Dataset Details', 'Image Counts & Breakdown'))
rows.extend(read_csv('table3.csv', 'Dataset Details', 'Image Counts & Breakdown'))

# Match each row to its citation index
for r in rows:
    author_str = r['author']
    
    if author_str in manual_overrides:
        r['ref_num'] = manual_overrides[author_str]
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
        has_year = year and year in norm_ref
        matching_tokens = sum(1 for t in author_tokens if t in norm_ref)
        if matching_tokens > 0:
            score = matching_tokens + (2 if has_year else 0)
            if score > best_match_score:
                best_match_score = score
                best_match_idx = ref_num
                
    if best_match_idx is not None and best_match_score >= 2:
        r['ref_num'] = best_match_idx
    else:
        r['ref_num'] = 999

# Sort rows by citation index
rows.sort(key=lambda x: x['ref_num'])

# Escape LaTeX characters
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
    "Noorelahi, Y., et al. (2025)": [("KAUH Hospital Data", "https://link.springer.com/article/10.1007/s00261-025-05243-w")],
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

general_dataset_links = {
    "Kaggle CT Kidney Dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "CT Kidney Dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "KiTS19 Dataset": "https://github.com/neheller/kits19/tree/master/data",
    "KiTS19 Challenge": "https://github.com/neheller/kits19/tree/master/data",
    "KiTS21 Challenge Data": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "KiTS21 Dataset": "https://github.com/neheller/kits21/tree/master/kits21/data",
    "FLARE Dataset": "https://flare.grand-challenge.org/Data/",
    "Synapse Dataset": "https://www.synapse.org/",
    "NHANES 2007–2010": "https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2007",
    "SEER Database": "https://seer.cancer.gov/data/",
    "KVASIR-SEG": "https://datasets.simula.no/kvasir-seg/",
    "ACDC": "https://www.creatis.insa-lyon.fr/Challenge/acdc/",
    "ISIC-2018": "https://challenge.isic-archive.com/landing/2018/",
    "CVC-ClinicDB": "https://polyp.grand-challenge.org/CVCClinicDB/",
    "COCO": "https://cocodataset.org/",
    "Roboflow 100": "https://universe.roboflow.com/roboflow-100",
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
        
    raw_lower = raw_dataset.lower()
    parts = []
    
    if "kaggle" in raw_lower:
        url = general_dataset_links["Kaggle CT Kidney Dataset"]
        parts.append(f"\\href{{{url}}}{{Kaggle CT Kidney}}")
        
    if "kits19" in raw_lower:
        url = general_dataset_links["KiTS19 Dataset"]
        parts.append(f"\\href{{{url}}}{{KiTS19}}")
        
    if "kits21" in raw_lower:
        url = general_dataset_links["KiTS21 Dataset"]
        parts.append(f"\\href{{{url}}}{{KiTS21}}")
        
    if "flare" in raw_lower:
        url = general_dataset_links["FLARE Dataset"]
        parts.append(f"\\href{{{url}}}{{FLARE}}")
        
    if "synapse" in raw_lower:
        url = general_dataset_links["Synapse Dataset"]
        parts.append(f"\\href{{{url}}}{{Synapse}}")
        
    if "nhanes" in raw_lower:
        url = general_dataset_links["NHANES 2007–2010"]
        parts.append(f"\\href{{{url}}}{{NHANES}}")
        
    if "seer" in raw_lower:
        url = general_dataset_links["SEER Database"]
        parts.append(f"\\href{{{url}}}{{SEER Database}}")
        
    if "kvasir" in raw_lower:
        url = general_dataset_links["KVASIR-SEG"]
        parts.append(f"\\href{{{url}}}{{KVASIR-SEG}}")
        
    if "acdc" in raw_lower:
        url = general_dataset_links["ACDC"]
        parts.append(f"\\href{{{url}}}{{ACDC}}")
        
    if "isic" in raw_lower:
        url = general_dataset_links["ISIC-2018"]
        parts.append(f"\\href{{{url}}}{{ISIC-2018}}")
        
    if "cvc" in raw_lower:
        url = general_dataset_links["CVC-ClinicDB"]
        parts.append(f"\\href{{{url}}}{{CVC-ClinicDB}}")
        
    if "coco" in raw_lower:
        url = general_dataset_links["COCO"]
        parts.append(f"\\href{{{url}}}{{COCO}}")
        
    if "roboflow" in raw_lower:
        url = general_dataset_links["Roboflow 100"]
        parts.append(f"\\href{{{url}}}{{Roboflow 100}}")
        
    if "c4kc" in raw_lower:
        url = "https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=61080950"
        parts.append(f"\\href{{{url}}}{{C4KC-KiTS}}")
        
    if "pubmed" in raw_lower:
        url = "https://huggingface.co/datasets/ncbi/pubmed"
        parts.append(f"\\href{{{url}}}{{PubMed Abstracts}}")
        
    if "tcia" in raw_lower:
        url = "https://www.cancerimagingarchive.net/"
        parts.append(f"\\href{{{url}}}{{TCIA}}")
        
    if "tcga" in raw_lower:
        url = "https://portal.gdc.cancer.gov/"
        parts.append(f"\\href{{{url}}}{{TCGA}}")

    if parts:
        private_details = []
        if "clinical" in raw_lower or "retrospective" in raw_lower or "kauh" in raw_lower:
            private_details.append("Clinical Data (Private)")
        if "external" in raw_lower or "jordan" in raw_lower:
            private_details.append("External Clinical Repo (Private)")
            
        res = ", ".join(parts)
        if private_details:
            res += " + " + ", ".join(private_details)
        return res
        
    if any(p in raw_lower for p in ["private", "clinical retrospective", "custom", "single-center", "retrospective", "hospital data", "hospital dataset", "cohort", "repository", "institutional", "dhaka hospital", "mhc-ct", "5 tertiary hospitals"]):
        return "Private Dataset"
        
    if not raw_dataset or raw_lower in ["n/a", "none", "no info"]:
        return "Private Dataset"
        
    return "Private Dataset"

# Generate LaTeX lines
latex_lines = []

for idx, r in enumerate(rows):
    ref_num = r['ref_num']
    author_cell = f"\\textbf{{{escape_latex(r['author'])}}}~[{ref_num}]"
    
    metrics_cell = escape_latex(r['metrics'])
    if not metrics_cell or metrics_cell.lower() == "n/a":
        metrics_cell = "N/A"
        
    modality_cell = escape_latex(r['modality'])
    
    dataset_cell = format_dataset_cell(r['author'], r['dataset_raw'])
    
    class_cell = escape_latex(r['class_info'])
    if not class_cell or class_cell.lower() == "n/a":
        class_cell = "N/A"
        
    raw_counts = r['counts_raw']
    counts_cell = escape_latex(raw_counts)
    counts_cell = counts_cell.replace(" | ", " \\newline ")
    counts_cell = counts_cell.replace("|", " \\newline ")
    if not counts_cell or counts_cell.lower() == "n/a":
        counts_cell = "N/A"
        
    line = f"{author_cell} & {metrics_cell} & {modality_cell} & {dataset_cell} & {class_cell} & {counts_cell} \\\\"
    latex_lines.append(line)

# LaTeX Document Template with corrected longtable structure
latex_template = r"""\documentclass{article}
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

\section*{Summary of Reviewed Studies}

This section presents the comprehensive synthesis of deep learning models, frameworks, and datasets utilized for renal disease diagnosis based on the 61 reviewed papers.

\begin{longtable}{L{2.5cm} L{2.5cm} L{1.5cm} L{3.0cm} L{2.8cm} L{3.5cm}}
\caption{Taxonomic synthesis of deep learning literature for renal disease diagnosis.} \label{tab:renal_literature}\\
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

\enddocument
"""

# Format and insert data rows
rows_str = ""
for line in latex_lines:
    rows_str += line + "\n\\midrule\n"
# Remove trailing midrule and add a clean row finish
rows_str = rows_str[:-len("\\midrule\n")]

latex_content = latex_template.replace("DATA_ROWS_PLACEHOLDER", rows_str)

with open('table.tex', 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("Generated table.tex successfully with correct longtable layout.")
