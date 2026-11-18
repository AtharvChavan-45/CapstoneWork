import csv
import openpyxl

# Load Selected_Literature_Summary_v3.csv
with open('Selected_Literature_Summary_v3.csv') as f:
    r = csv.reader(f)
    next(r)
    v3_rows = list(r)

# Load table.csv
with open('table.csv') as f:
    r = csv.reader(f)
    next(r)
    t1_rows = list(r)

# Load table2.csv
with open('table2.csv') as f:
    r = csv.reader(f)
    next(r)
    t2_rows = list(r)

# Load table3.csv
with open('table3.csv') as f:
    r = csv.reader(f)
    next(r)
    t3_rows = list(r)

# Load SLR_Tables_Final.xlsx (Sheet: Table 1 - Literature Comparison)
wb = openpyxl.load_workbook('SLR_Tables_Final.xlsx', read_only=True)
ws = wb['Table 1 - Literature Comparison']
xlsx_rows = list(ws.iter_rows(values_only=True))[1:] # skip header

print(f'Selected_Literature_Summary_v3.csv: {len(v3_rows)} rows')
print(f'table.csv: {len(t1_rows)} rows')
print(f'table2.csv: {len(t2_rows)} rows')
print(f'table3.csv: {len(t3_rows)} rows')
print(f'SLR_Tables_Final.xlsx: {len(xlsx_rows)} rows')

# Let's count total entries
total_candidate_rows = len(v3_rows) + len(t1_rows) + len(t2_rows) + len(t3_rows) + len(xlsx_rows)
print(f'Total candidate rows: {total_candidate_rows}')
