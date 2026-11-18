import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# ==========================================
# 1. RETRIEVE METRICS FROM JUPYTER NOTEBOOK
# ==========================================

# Training history (46 epochs from the cell 13 training output)
train_losses = [
    0.5787, 0.3544, 0.2344, 0.2120, 0.1859, 0.1549, 0.1426, 0.1250, 
    0.1061, 0.0982, 0.0654, 0.0401, 0.0435, 0.0300, 0.0406, 0.0418, 
    0.0334, 0.0363, 0.0360, 0.0256, 0.0308, 0.0376, 0.0129, 0.0169, 
    0.0110, 0.0102, 0.0097, 0.0132, 0.0091, 0.0092, 0.0085, 0.0063, 
    0.0051, 0.0055, 0.0078, 0.0060, 0.0057, 0.0069, 0.0042, 0.0028, 
    0.0042, 0.0038, 0.0036, 0.0039, 0.0055, 0.0046
]
val_losses = [
    0.6192, 0.1562, 0.6021, 0.3537, 0.2201, 0.1108, 0.2586, 0.9829, 
    0.2041, 0.3746, 0.1729, 0.1000, 0.0802, 0.0447, 0.0522, 0.0422, 
    0.1263, 0.0401, 0.2764, 0.5955, 0.5082, 0.2644, 0.0357, 0.0302, 
    0.0383, 0.0616, 0.0339, 0.0637, 0.0263, 0.0275, 0.0245, 0.0247, 
    0.0271, 0.0217, 0.0304, 0.0271, 0.0312, 0.0231, 0.0254, 0.0248, 
    0.0248, 0.0257, 0.0266, 0.0264, 0.0269, 0.0258
]

train_accs = [
    0.7799, 0.8644, 0.9140, 0.9196, 0.9308, 0.9432, 0.9460, 0.9539, 
    0.9648, 0.9628, 0.9752, 0.9854, 0.9848, 0.9888, 0.9881, 0.9849, 
    0.9891, 0.9872, 0.9874, 0.9905, 0.9894, 0.9872, 0.9961, 0.9944, 
    0.9970, 0.9971, 0.9973, 0.9961, 0.9970, 0.9977, 0.9971, 0.9983, 
    0.9984, 0.9983, 0.9976, 0.9976, 0.9986, 0.9976, 0.9989, 0.9997, 
    0.9989, 0.9991, 0.9990, 0.9986, 0.9981, 0.9986
]
val_accs = [
    0.7583, 0.9404, 0.7847, 0.8524, 0.9213, 0.9592, 0.8929, 0.6719, 
    0.9448, 0.8865, 0.9327, 0.9622, 0.9762, 0.9869, 0.9859, 0.9903, 
    0.9662, 0.9873, 0.9032, 0.8393, 0.8447, 0.9032, 0.9936, 0.9956, 
    0.9936, 0.9836, 0.9950, 0.9869, 0.9980, 0.9973, 0.9980, 0.9977, 
    0.9977, 0.9973, 0.9967, 0.9977, 0.9963, 0.9977, 0.9983, 0.9973, 
    0.9980, 0.9983, 0.9983, 0.9983, 0.9973, 0.9983
]

epochs = np.arange(1, len(train_losses) + 1)

# Confusion Matrix counts from test evaluation (2490 samples total)
class_names = ['Cyst', 'Normal', 'Stone', 'Tumor']
cm = np.array([
    [740,   0,   2,   0],  # Cyst
    [  0, 1016,   0,   0],  # Normal
    [  0,   0, 275,   0],  # Stone
    [  0,   0,   0, 457]   # Tumor
])

# ==========================================
# 2. CONSTRUCT 2x2 MATPLOTLIB SUBPLOTS
# ==========================================

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
plt.subplots_adjust(hspace=0.3, wspace=0.25)

# --- Subplot (a): Loss Progression ---
axes[0, 0].plot(epochs, train_losses, '.-', color='#1f77b4', label='Train Loss')
axes[0, 0].plot(epochs, val_losses, '--', color='#d62728', marker='.', label='Val Loss')
axes[0, 0].set_title('(a) Loss Progression', fontsize=14, fontweight='bold', pad=10)
axes[0, 0].set_xlabel('Epochs', fontsize=12)
axes[0, 0].set_ylabel('Cross-Entropy Loss', fontsize=12)
axes[0, 0].grid(True, linestyle='--', alpha=0.5)
axes[0, 0].legend(fontsize=10)

# --- Subplot (b): Accuracy Progression ---
axes[0, 1].plot(epochs, train_accs, '.-', color='#1f77b4', label='Train Acc')
axes[0, 1].plot(epochs, val_accs, '--', color='#d62728', marker='.', label='Val Acc')
axes[0, 1].set_title('(b) Accuracy Progression', fontsize=14, fontweight='bold', pad=10)
axes[0, 1].set_xlabel('Epochs', fontsize=12)
axes[0, 1].set_ylabel('Accuracy (Ratio)', fontsize=12)
axes[0, 1].grid(True, linestyle='--', alpha=0.5)
axes[0, 1].legend(fontsize=10)

# --- Subplot (c): Multi-Class ROC Curves ---
# Reconstruct perfect ROC curves representing AUC = 1.0000 for each class
# Real plotting of coordinates to match perfect top-left shapes
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
labels = ['Cyst (AUC = 1.0000)', 'Normal (AUC = 1.0000)', 'Stone (AUC = 1.0000)', 'Tumor (AUC = 1.0000)']

for i in range(4):
    # Draw a line from (0,0) -> (0,1) -> (1,1) representing perfect ROC
    axes[1, 0].plot([0, 0, 1], [0, 1, 1], color=colors[i], lw=2, label=labels[i])

# Draw Random Guess line
axes[1, 0].plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1, label='Random Guess')
axes[1, 0].set_title('(c) Multi-Class ROC Curves', fontsize=14, fontweight='bold', pad=10)
axes[1, 0].set_xlabel('False Positive Rate', fontsize=12)
axes[1, 0].set_ylabel('True Positive Rate', fontsize=12)
axes[1, 0].grid(True, linestyle='--', alpha=0.5)
axes[1, 0].legend(loc='lower right', fontsize=9)

# --- Subplot (d): Confusion Matrix ---
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Oranges', cbar=True,
    xticklabels=class_names, yticklabels=class_names,
    ax=axes[1, 1], annot_kws={"size": 11, "weight": "bold"}
)
axes[1, 1].set_title('(d) Confusion Matrix', fontsize=14, fontweight='bold', pad=10)
axes[1, 1].set_xlabel('AI Predicted Class', fontsize=12)
axes[1, 1].set_ylabel('Actual Class', fontsize=12)

# Save figure to file
output_path = '/Users/atharv/Desktop/Capstone/2x2_metrics_dashboard.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Dashboard generated successfully and saved to {output_path}!")
