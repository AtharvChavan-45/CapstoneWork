import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Data from our exact analysis of the 62 papers
data = {
    'Kaggle CT Kidney': 16,
    'Surveys & Reviews': 14,
    'KiTS (KiTS19 / KiTS21)': 10,
    'Custom / Private Clinical': 7,
    'PubMed / BioBERT (NLP)': 4,
    'KAUH Hospital Dataset': 3,
    'Synapse Multi-organ': 2,
    'Other Public (FLARE, SEER, BUSI, etc.)': 6
}

# Sort data by values in descending order
sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=False) # False for ascending in horizontal bar so highest is on top
categories = [x[0] for x in sorted_data]
counts = [x[1] for x in sorted_data]

# Set professional publication styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 11

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

# Use a clean, modern palette
colors = sns.color_palette("viridis", len(counts))

# Plot horizontal bars
bars = ax.barh(categories, counts, color=colors, edgecolor='none', height=0.6)

# Customize spines (borders) - keep it clean and borderless
for spine in ['top', 'right', 'bottom', 'left']:
    ax.spines[spine].set_visible(False)

# Add horizontal gridlines
ax.grid(axis='x', linestyle='--', alpha=0.5, color='#ccc')
ax.set_axisbelow(True)

# Add counts at the end of each bar
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.3,
        bar.get_y() + bar.get_height() / 2,
        f'{int(width)}',
        ha='left',
        va='center',
        fontsize=11,
        fontweight='bold',
        color='#333'
    )

# Customize axes labels and titles
ax.set_title('Dataset Frequency in Renal Disease Research (Papers 1–62)', fontsize=14, fontweight='bold', pad=20, color='#111')
ax.set_xlabel('Number of Research Papers', fontsize=12, fontweight='bold', labelpad=10, color='#222')
ax.tick_params(axis='both', which='both', length=0, labelsize=11, labelcolor='#333')

# Tighter layout and save
plt.tight_layout()
plt.savefig('dataset_usage.png', bbox_inches='tight', dpi=300)
print("Successfully generated dataset_usage.png")
