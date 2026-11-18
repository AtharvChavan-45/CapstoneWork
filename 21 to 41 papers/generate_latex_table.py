import csv
import re

# Dataset links mapping based on user input and standard public datasets
# We map the exact dataset name or the paper index to the URL.
# The user's list maps index 21-41 to specific rows in table3.csv.
# Let's align them.
# In table3.csv:
# Row 14 (Noorelahi) corresponds to index 21.
# Row 15 (Gu) corresponds to index 22.
# Row 16 (Lee) corresponds to index 23.
# Row 17 (Fang) corresponds to index 24.
# Row 18 (Luo) corresponds to index 25.
# Row 19 (Hatsutani) corresponds to index 26.
# Row 20 (Sharma) corresponds to index 27.
# Row 21 (Elton) corresponds to index 28.
# Row 22 (Alzu'bi) corresponds to index 29.
# Row 23 (Heller) corresponds to index 30.
# Row 24 (Abdalla) corresponds to index 31.
# Row 25 (Ma) corresponds to index 32.
# Row 26 (Rathva) corresponds to index 33.
# Row 27 (Hossain) corresponds to index 34.
# Row 28 (Pimpalkar) corresponds to index 35.
# Row 29 (Bhandari) corresponds to index 36.
# Row 30 (Martín) corresponds to index 37.
# Row 31 (Abdelrahman) corresponds to index 38.
# Row 32 (Zhao) corresponds to index 39.
# Row 33 (Chen) corresponds to index 40.
# Row 34 (Sharon) corresponds to index 41.

dataset_links = {
    # Manual links for 21-41 (aligned to their index in table3.csv data rows)
    "Noorelahi, Y., et al. (2025)": [("KAUH Hospital Data", "https://link.springer.com/article/10.1007/s00261-025-05243-w")], # 21
    "Gu, Y., et al. (2021)": [("PubMed Abstracts", "https://huggingface.co/datasets/ncbi/pubmed")], # 22
    "Lee, J., et al. (2020)": [("PubMed + PMC", "https://github.com/naver/biobert-pretrained")], # 23
    "Fang, L., et al. (2023)": [("BLURB Benchmark", "https://huggingface.co/datasets/bigbio/blurb")], # 24
    "Luo, R., et al. (2022)": [("PubMed Abstracts", "https://huggingface.co/datasets/ncbi/pubmed")], # 25
    "Hatsutani, T., et al. (2023)": [("KiTS19 Dataset", "https://github.com/neheller/kits19/tree/master/data")], # 26
    "Sharma, K., et al. (2025)": [("CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 27
    "Elton, D.C., et al. (2022)": [("Clinical Dataset", "https://www.cancerimagingarchive.net/collection/ct-colonography/")], # 28
    "Alzu'bi, D., et al. (2022)": [("New CT Dataset", "https://github.com/DaliaAlzubi/KidneyTumor/tree/main/Dataset")], # 29
    "Heller, N., et al. (2023)": [("KiTS21 Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")], # 30
    "Abdalla, P.A., et al. (2025)": [("Sulaimani/Rania Dataset", "https://www.kaggle.com/datasets/orvile/axial-ct-imaging-dataset-kidney-stone-detection")], # 31
    "Ma, J., et al. (2022)": [("FLARE Dataset", "https://flare.grand-challenge.org/Data/")], # 32
    "Rathva, V. & Degadwala, D.S. (2025)": [("Abdominal CT Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 33
    "Hossain, T., et al. (2024)": [("Enhanced CT Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 34
    "Pimpalkar, A., et al. (2025)": [("Clinical CT Repository", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 35
    "Bhandari, M., et al. (2023)": [("Kaggle CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 36
    "Martín, Ó.A. & Sánchez, J. (2025)": [("Multimodal Dataset", "https://data.mendeley.com/datasets/bhmdr45bh2/1")], # 37
    "Abdelrahman, A. & Viriri, S. (2023)": [("KiTS Dataset", "https://github.com/neheller/kits19/tree/master/data"), ("Body Morphometry", "https://www.kaggle.com/competitions/body-morphometry-kidney-and-tumor/data")], # 38
    "Zhao, T., et al. (2023)": [("3D CT Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")], # 39
    "Chen, Z. & Liu, H. (2021)": [("KiTS21 Dataset", "https://github.com/neheller/kits21/tree/master/kits21/data")], # 40
    "Sharon, J. J. & Anbarasi, L. J. (2025)": [("CT Kidney Dataset", "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone")], # 41
}

# Add other well-known public datasets in table3 or table/table2
general_dataset_links = {
    "Kaggle CT Kidney Dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "CT Kidney Dataset": "https://www.kaggle.com/datasets/nazmul0087/ct-kidney-dataset-normal-cyst-tumor-and-stone",
    "KiTS19 Dataset": "https://github.com/neheller/kits19/tree/master/data",
    "KiTS21 Challenge Data": "https://github.com/neheller/kits21/tree/master/kits21/data",
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

def escape_latex(text):
    if not text:
        return ""
    text = text.replace("\\", "\\textbackslash{}")
    # Escape characters that are special in LaTeX, unless they are already escaped or are URLs
    # We do a safe escape
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
    # Don't escape if it looks like LaTeX code (e.g. contains \href)
    if "\\href" in text:
        return text
    
    # We escape characters one by one safely
    escaped = []
    for c in text:
        if c in chars:
            escaped.append(chars[c])
        else:
            escaped.append(c)
    return "".join(escaped)

def get_dataset_cell(author, dataset_detail):
    # Check if author is in manual links
    if author in dataset_links:
        links = dataset_links[author]
        latex_links = []
        for name, url in links:
            latex_links.append(f"\\href{{{url}}}{{{escape_latex(name)}}}")
        return ", ".join(latex_links)
    
    # Check if there is a known link in general dataset links
    clean_detail = dataset_detail.strip()
    # If the dataset detail is clinical retrospective or contains KAUH or is empty/N/A
    if any(p in clean_detail.lower() for p in ["private", "clinical retrospective", "custom", "single-center", "retrospective", "hospital data", "hospital dataset", "cohort", "repository", "institutional", "dhaka hospital"]):
        return "Private Dataset"
    
    matched_links = []
    for key, url in general_dataset_links.items():
        if key.lower() in clean_detail.lower():
            matched_links.append(f"\\href{{{url}}}{{{escape_latex(key)}}}")
    
    if matched_links:
        return ", ".join(matched_links)
    
    # Default to "Private Dataset" if no link is available
    if not clean_detail or clean_detail.lower() in ["n/a", "none", "no info"]:
        return "Private Dataset"
    
    # If it is a known name but we don't have a link
    return "Private Dataset"

def read_csv(filename, dataset_col, counts_col):
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
            dataset_val = row_dict.get(dataset_col, '').strip()
            class_info = row_dict.get('Class Information', '').strip()
            counts_val = row_dict.get(counts_col, '').strip()
            
            rows.append({
                'author': author,
                'metrics': metrics,
                'modality': modality,
                'dataset_raw': dataset_val,
                'class_info': class_info,
                'counts_raw': counts_val
            })
        return rows

rows_t1 = read_csv('table.csv', 'Dataset', 'Image Counts & Class Breakdown')
rows_t2 = read_csv('table2.csv', 'Dataset Details', 'Image Counts & Breakdown')
rows_t3 = read_csv('table3.csv', 'Dataset Details', 'Image Counts & Breakdown')

all_rows = rows_t1 + rows_t2 + rows_t3
print(f'Total merged rows: {len(all_rows)}')

# Let's process and display first 5 rows to verify
for r in all_rows[:5]:
    ds_cell = get_dataset_cell(r['author'], r['dataset_raw'])
    print(f"Author: {r['author']}")
    print(f"Dataset Raw: {r['dataset_raw']} -> LaTeX Cell: {ds_cell}")
    print('---')
