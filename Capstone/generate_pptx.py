import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette (Elegant Light Editorial Theme)
BG_RGB = (250, 249, 246)       # Warm alabaster/cream
CARD_BG = (255, 255, 255)      # Pure white
BORDER_RGB = (230, 229, 224)   # Fine gray border
TEXT_MAIN = (45, 55, 72)       # Charcoal body text
TEXT_MUTED = (120, 113, 108)   # Stone gray text
TEXT_HIGHLIGHT = (15, 23, 42)  # Slate navy header
TEAL_RGB = (15, 118, 110)      # Medical teal accent
GREEN_RGB = (21, 128, 61)      # Forest green
RED_RGB = (185, 28, 28)        # Crimson burgundy
PURPLE_RGB = (91, 33, 182)     # Indigo violet
AMBER_RGB = (180, 83, 9)       # Warm gold/amber

# Helper function to set slide background
def set_slide_bg(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(*BG_RGB)

# Helper function to add a card shape
def create_card(slide, left, top, width, height, bg_rgb=CARD_BG, border_rgb=BORDER_RGB):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(*bg_rgb)
    if border_rgb:
        shape.line.color.rgb = RGBColor(*border_rgb)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

# Helper function to add slide title
def add_slide_header(slide, title, category=None):
    if category:
        # Category label (e.g., section number)
        tx_cat = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.3))
        tf_cat = tx_cat.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = 'Arial'
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(*TEAL_RGB)
        
        # Main title
        tx_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.65), Inches(12), Inches(0.6))
        tf_title = tx_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = 'Arial'
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(*TEXT_HIGHLIGHT)
    else:
        tx_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.45), Inches(12), Inches(0.8))
        tf_title = tx_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = 'Arial'
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(*TEXT_HIGHLIGHT)

# Helper function to create content block
def add_content_box(slide, left, top, width, height):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.1)
    tf.margin_right = Inches(0.1)
    tf.margin_top = Inches(0.1)
    tf.margin_bottom = Inches(0.1)
    return tf

# Helper function to add a standard text paragraph
def add_para(tf, text, font_size=11, font_color=TEXT_MAIN, bold=False, space_after=6, font_name='Calibri', italic=False):
    p = tf.paragraphs[0] if (len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "") else tf.add_paragraph()
    p.text = text
    p.font.name = font_name
    p.font.size = Pt(font_size)
    p.font.color.rgb = RGBColor(*font_color)
    p.font.bold = bold
    p.font.italic = italic
    p.space_after = Pt(space_after)
    return p

# Helper function to add a formatted bullet point with support for bold prefixes
def add_bullet(tf, text, bullet_char="•", font_size=11, font_color=TEXT_MAIN, space_after=4, bullet_color=TEAL_RGB):
    p = tf.paragraphs[0] if (len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "") else tf.add_paragraph()
    p.space_after = Pt(space_after)
    
    # Add bullet run
    r_bullet = p.add_run()
    r_bullet.text = f"{bullet_char}  "
    r_bullet.font.name = 'Calibri'
    r_bullet.font.size = Pt(font_size)
    r_bullet.font.color.rgb = RGBColor(*bullet_color)
    r_bullet.font.bold = True
    
    # Automatic bolding of prefix if colon exists (e.g. "Time Intensive: Manual interpretation...")
    if ":" in text and len(text.split(":")[0]) < 30:
        parts = text.split(":", 1)
        r_bold = p.add_run()
        r_bold.text = parts[0] + ":"
        r_bold.font.name = 'Calibri'
        r_bold.font.size = Pt(font_size)
        r_bold.font.color.rgb = RGBColor(*TEXT_HIGHLIGHT)
        r_bold.font.bold = True
        
        r_text = p.add_run()
        r_text.text = parts[1]
        r_text.font.name = 'Calibri'
        r_text.font.size = Pt(font_size)
        r_text.font.color.rgb = RGBColor(*font_color)
    else:
        r_text = p.add_run()
        r_text.text = text
        r_text.font.name = 'Calibri'
        r_text.font.size = Pt(font_size)
        r_text.font.color.rgb = RGBColor(*font_color)

# ==========================================
# SLIDE 1: Title & Project Introduction
# ==========================================
slide_layout = prs.slide_layouts[6] # Blank Layout
slide1 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide1)

# Large Center Badge
tx_badge = slide1.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.13), Inches(0.4))
tf_badge = tx_badge.text_frame
tf_badge.word_wrap = True
p_badge = tf_badge.paragraphs[0]
p_badge.alignment = PP_ALIGN.CENTER
p_badge.text = "CAPSTONE PROJECT PRESENTATION"
p_badge.font.name = 'Arial'
p_badge.font.size = Pt(11)
p_badge.font.bold = True
p_badge.font.color.rgb = RGBColor(*TEAL_RGB)

# Main Title
tx_title = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.33), Inches(1.5))
tf_title = tx_title.text_frame
tf_title.word_wrap = True
p_title = tf_title.paragraphs[0]
p_title.alignment = PP_ALIGN.CENTER
p_title.text = "AI-Based Kidney Abnormality Detection, Segmentation, Explainability & Clinical Decision Support System"
p_title.font.name = 'Arial'
p_title.font.size = Pt(28)
p_title.font.bold = True
p_title.font.color.rgb = RGBColor(*TEXT_HIGHLIGHT)

# Subtitle
tx_sub = slide1.shapes.add_textbox(Inches(1.0), Inches(3.7), Inches(11.33), Inches(0.8))
tf_sub = tx_sub.text_frame
tf_sub.word_wrap = True
p_sub = tf_sub.paragraphs[0]
p_sub.alignment = PP_ALIGN.CENTER
p_sub.text = "An Integrated Deep Learning and Biomedical NLP Framework for Kidney CT Analysis"
p_sub.font.name = 'Calibri'
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = RGBColor(*TEXT_MUTED)

# Target Classes
tx_classes = slide1.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(11.33), Inches(0.5))
tf_classes = tx_classes.text_frame
p_cls = tf_classes.paragraphs[0]
p_cls.alignment = PP_ALIGN.CENTER
r_c1 = p_cls.add_run()
r_c1.text = "TARGET CLASSES:   "
r_c1.font.bold = True
r_c1.font.size = Pt(10)
r_c1.font.color.rgb = RGBColor(*TEXT_MUTED)
for cls_name in ["Cyst", "Normal", "Stone", "Tumor"]:
    r_item = p_cls.add_run()
    r_item.text = f" [{cls_name}] "
    r_item.font.bold = True
    r_item.font.size = Pt(10.5)
    r_item.font.color.rgb = RGBColor(*TEAL_RGB)

# Objective Card
create_card(slide1, Inches(2.66), Inches(5.2), Inches(8.0), Inches(1.1))
tf_obj = add_content_box(slide1, Inches(2.76), Inches(5.25), Inches(7.8), Inches(1.0))
add_para(tf_obj, "🎯 Project Objective", font_size=11, font_color=TEAL_RGB, bold=True, space_after=3)
add_para(tf_obj, "Develop an integrated AI-assisted system that analyzes kidney CT scans, detects abnormalities, segments pathological regions, explains predictions, quantifies pathology extent, extracts clinical information, and provides context-aware recommendations.", font_size=9.5, font_color=TEXT_MAIN)

# Footer info
tx_foot = slide1.shapes.add_textbox(Inches(0.6), Inches(6.8), Inches(12.13), Inches(0.3))
p_foot = tx_foot.text_frame.paragraphs[0]
p_foot.text = "Advisor Eval Mode • August 2026"
p_foot.font.size = Pt(9)
p_foot.font.color.rgb = RGBColor(*TEXT_MUTED)

# ==========================================
# SLIDE 2: Problem Statement & Motivation
# ==========================================
slide2 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide2)
add_slide_header(slide2, "Problem Statement & Motivation", "02. Background")

# Left Column - Challenges
create_card(slide2, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.3))
tf_col1 = add_content_box(slide2, Inches(0.75), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_col1, "🚨 Current Siloed Workflow & Challenges", font_size=14, font_color=RED_RGB, bold=True, space_after=12)
add_bullet(tf_col1, "Time Intensive: Manual interpretation of multi-slice CT scans causes clinical delays.")
add_bullet(tf_col1, "Lack of Spatial Mapping: Standalone classification lists categories but fails to map pathology boundaries.")
add_bullet(tf_col1, "Black-Box Predictions: High-accuracy deep models lack explainability, hindering clinical trust.")
add_bullet(tf_col1, "Separated Context: Patient clinical notes and imaging data are processed in disconnected systems.")
add_bullet(tf_col1, "Inaccurate Assessment: Qualitative staging lacks exact volumetric or area ratio measurements.")
add_bullet(tf_col1, "Tool Disjointedness: Multiple separate models do not provide a unified diagnostic workflow.")

# Right Column - Proposal
create_card(slide2, Inches(6.9), Inches(1.4), Inches(5.8), Inches(5.3))
tf_col2 = add_content_box(slide2, Inches(7.05), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_col2, "💡 Proposed Integrated Framework (NephroVision)", font_size=14, font_color=GREEN_RGB, bold=True, space_after=12)
add_para(tf_col2, "Establish a single consolidated AI pipeline connecting image vision with generative medical advice:", font_size=11, space_after=10)
add_bullet(tf_col2, "CT Classification via PCSA-KidneyNeXt module (99.92% Acc).", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Explainability via target layer Grad-CAM visual heatmaps.", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Localization via conditional YOLOv11 segmentation routing.", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Quantification via OpenCV contour pixel ratio calculations.", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Entity Parsing via Biomedical NER from clinical history text.", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Generative Advisory using DeepSeek API context-aware diets.", bullet_char="✓", bullet_color=GREEN_RGB)
add_bullet(tf_col2, "Interactive Graphics via Plotly 3D spatial reconstructions.", bullet_char="✓", bullet_color=GREEN_RGB)

# ==========================================
# SLIDE 3: Project Objectives
# ==========================================
slide3 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide3)
add_slide_header(slide3, "Project Objectives", "03. Targets")

objs = [
    ("Obj 1", "Multi-Class Classification", "Classify kidney CT scans into Normal, Cyst, Stone, and Tumor using KidneyNeXt.", TEAL_RGB),
    ("Obj 2", "Explainable AI", "Deploy Grad-CAM attention heatmaps to localize features driving model decisions.", RED_RGB),
    ("Obj 3", "Lesion Segmentation", "Segment exact boundary regions of cysts and tumors using YOLO model routing.", GREEN_RGB),
    ("Obj 4", "Area Quantification", "Calculate pathology area and pathology-to-kidney ratio via OpenCV.", AMBER_RGB),
    ("Obj 5", "Clinical NLP", "Extract clinical entities and medical contexts from unstructured text notes.", PURPLE_RGB),
    ("Obj 6", "AI Dietitian", "Generate personalized diabetic and renal diets using rules & DeepSeek.", AMBER_RGB),
    ("Obj 7", "Interactive 3D Plot", "Construct and render interactive 3D spatial boundaries using Plotly Scatter3D.", TEAL_RGB),
    ("Obj 8", "Smart Merger", "Combine cyst and tumor annotations programmatically to build a unified dataset.", GREEN_RGB),
]

card_w = Inches(2.78)
card_h = Inches(2.4)
spacing_x = Inches(0.2)
spacing_y = Inches(0.2)

for i, (tag, title, desc, col) in enumerate(objs):
    row = i // 4
    col_idx = i % 4
    
    left = Inches(0.6) + col_idx * (card_w + spacing_x)
    top = Inches(1.5) + row * (card_h + spacing_y)
    
    create_card(slide3, left, top, card_w, card_h)
    
    tf = add_content_box(slide3, left + Inches(0.1), top + Inches(0.1), card_w - Inches(0.2), card_h - Inches(0.2))
    # Add Badge style
    add_para(tf, tag.upper(), font_size=9, font_color=col, bold=True, space_after=3)
    add_para(tf, title, font_size=12, font_color=TEXT_HIGHLIGHT, bold=True, space_after=6)
    add_para(tf, desc, font_size=9.5, font_color=TEXT_MAIN)

# ==========================================
# SLIDE 4: Proposed System Architecture
# ==========================================
slide4 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide4)
add_slide_header(slide4, "Proposed System Architecture", "04. Pipeline Design")

# Left text explanation card
create_card(slide4, Inches(0.6), Inches(1.4), Inches(4.2), Inches(5.3))
tf_arch = add_content_box(slide4, Inches(0.75), Inches(1.55), Inches(3.9), Inches(5.0))
add_para(tf_arch, "Integrated Pipeline Overview", font_size=14, font_color=TEXT_HIGHLIGHT, bold=True, space_after=12)
add_para(tf_arch, "The system is split into three unified core modules:", font_size=11, space_after=8)
add_bullet(tf_arch, "Image Pipeline: Ingests CT images, runs classification, maps activation features, and segments abnormal tissues.")
add_bullet(tf_arch, "Clinical NLP Pipeline: Ingests patient reports, parses clinical named entities, and formats history context.")
add_bullet(tf_arch, "Advisory Dashboard: Merges vision contours and parsed notes text, routes to DeepSeek for dietary advice, and renders Plotly 3D plots.")

# Right architecture diagram overlay
arch_img_path = "/Users/atharv/Desktop/Capstone/3dfg.drawio.png"
if os.path.exists(arch_img_path):
    slide4.shapes.add_picture(arch_img_path, Inches(5.1), Inches(1.4), Inches(7.6), Inches(5.3))
else:
    create_card(slide4, Inches(5.1), Inches(1.4), Inches(7.6), Inches(5.3))
    tf_err = add_content_box(slide4, Inches(5.2), Inches(1.5), Inches(7.4), Inches(5.1))
    add_para(tf_err, "System Architecture Diagram (3dfg.drawio.png missing)", font_size=12, font_color=RED_RGB, bold=True)

# ==========================================
# SLIDE 5: End-to-End Data Flow
# ==========================================
slide5 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide5)
add_slide_header(slide5, "End-to-End Data Flow", "05. Execution Pathway")

# Left card - Sequential stepper pathway (condensed to 8 major stages for readability)
create_card(slide5, Inches(0.6), Inches(1.4), Inches(7.8), Inches(5.3))
tf_flow = add_content_box(slide5, Inches(0.75), Inches(1.55), Inches(7.5), Inches(5.0))
add_para(tf_flow, "Chronological Step-by-Step Pathway", font_size=14, font_color=TEXT_HIGHLIGHT, bold=True, space_after=10)

steps = [
    ("1. Raw Ingestion", "CT slice images are preprocessed and clinical reports are structured."),
    ("2. Vision Classification", "PCSA-KidneyNeXt network detects targets (Normal/Stone/Cyst/Tumor)."),
    ("3. Feature Verification", "Grad-CAM generates activation heatmaps to ignore scanner bed artifacts."),
    ("4. Specialist Routing", "If classification is Cyst/Tumor, triggers conditional YOLOv11 routers."),
    ("5. Contour Calculation", "OpenCV extracts contour polygons of kidney tissues and pathology masks."),
    ("6. NLP Named Entity Recognition", "Transformers parse biomedical entities (symptoms, drugs, history)."),
    ("7. LLM Advisory Logic", "DeepSeek API combines note metadata and computed ratios for care warnings."),
    ("8. Dashboard Composition", "Interactive 3D plots and final recommendations are loaded in UI.")
]

for title, desc in steps:
    p = tf_flow.add_paragraph()
    p.space_after = Pt(3)
    r1 = p.add_run()
    r1.text = f"▪  {title}: "
    r1.font.bold = True
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = RGBColor(*TEAL_RGB)
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(*TEXT_MAIN)

# Right top card - Calculation
create_card(slide5, Inches(8.6), Inches(1.4), Inches(4.1), Inches(2.4))
tf_calc = add_content_box(slide5, Inches(8.75), Inches(1.5), Inches(3.8), Inches(2.2))
add_para(tf_calc, "📐 Pathology Ratio Calculation", font_size=12, font_color=TEAL_RGB, bold=True, space_after=8)
add_para(tf_calc, "Computed dynamically from segmentation mask pixel contour areas:", font_size=10, space_after=8)
add_para(tf_calc, "Ratio (%) = (Pathology Area / Kidney Area) × 100", font_size=10.5, font_color=TEAL_RGB, bold=True, space_after=4, font_name='Courier New')

# Right bottom card - Alerts
create_card(slide5, Inches(8.6), Inches(4.0), Inches(4.1), Inches(2.7))
tf_alert = add_content_box(slide5, Inches(8.75), Inches(4.1), Inches(3.8), Inches(2.5))
add_para(tf_alert, "⚠️ Severity Alert Rules", font_size=12, font_color=RED_RGB, bold=True, space_after=8)
add_bullet(tf_alert, "Ratio > 30%: High Risk alert triggered. Recommends evaluation for Radical Nephrectomy.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_alert, "Ratio <= 30%: Moderate Risk alert. Recommends evaluation for Partial Nephrectomy.", bullet_char="▪", bullet_color=AMBER_RGB)
add_para(tf_alert, "*Prototype guidelines only, not clinically validated.", font_size=8.5, font_color=TEXT_MUTED, italic=True, space_after=0)

# ==========================================
# SLIDE 6: Dataset & Data Preparation
# ==========================================
slide6 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide6)
add_slide_header(slide6, "Dataset & Data Preparation", "06. Data Engineering")

# Left Column - Merger
create_card(slide6, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.3))
tf_prep = add_content_box(slide6, Inches(0.75), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_prep, "🔀 Smart Dataset Merger Algorithm", font_size=14, font_color=TEAL_RGB, bold=True, space_after=12)
add_para(tf_prep, "Cyst and tumor segmentation tags were annotated in conflicting layouts. We built an automated pipeline script:", font_size=11, space_after=10)
add_bullet(tf_prep, "YAML Parsing: Automatically parses original dataset paths and standardizes label indices.")
add_bullet(tf_prep, "Class Remapping: Remaps indices to a unified system: Class 0 -> kidney, Class 1 -> tumor, Class 2 -> cyst.")
add_bullet(tf_prep, "Collision Prevention: Prefixes filenames with dataset sources (e.g. cyst_, tumor_) dynamically before mapping files.")
add_bullet(tf_prep, "Unified Splits: Outputs standard train/val/test splits and builds matching config YAML.")

# Right Column - Directory
create_card(slide6, Inches(6.9), Inches(1.4), Inches(5.8), Inches(5.3))
tf_dir = add_content_box(slide6, Inches(7.05), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_dir, "📁 Unified Directory Structure", font_size=14, font_color=TEXT_HIGHLIGHT, bold=True, space_after=12)

# Gray terminal box mockup
create_card(slide6, Inches(7.1), Inches(2.2), Inches(5.4), Inches(4.1), bg_rgb=BG_RGB, border_rgb=BORDER_RGB)
tf_term = add_content_box(slide6, Inches(7.2), Inches(2.3), Inches(5.2), Inches(3.9))
tree_text = """combined_dataset/
├── data.yaml            # Remapped configuration
├── train/
│   ├── images/          # tumor_img1.jpg, cyst_img2.jpg
│   └── labels/          # Remapped text coordinates
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/"""
add_para(tf_term, tree_text, font_size=10, font_color=TEAL_RGB, font_name='Courier New')

# ==========================================
# SLIDE 7: Dataset Statistics
# ==========================================
slide7 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide7)
add_slide_header(slide7, "Dataset Statistics", "07. Data Scale")

# Three columns
# Col 1: Classifier Dataset
create_card(slide7, Inches(0.6), Inches(1.4), Inches(3.8), Inches(5.3))
tf_stat1 = add_content_box(slide7, Inches(0.75), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_stat1, "Dataset 1: Classifier", font_size=13, font_color=TEAL_RGB, bold=True, space_after=12)
add_para(tf_stat1, "12,446", font_size=32, font_color=TEAL_RGB, bold=True, space_after=4)
add_para(tf_stat1, "TOTAL CT SCAN IMAGES", font_size=9.5, font_color=TEXT_MUTED, bold=True, space_after=15)
add_bullet(tf_stat1, "Split Ratio: 80% Train/Val (9,956) | 20% Test (2,490)")
add_bullet(tf_stat1, "Distribution: Normal (5,077), Cyst (3,709), Tumor (2,283), Stone (1,377)")

# Col 2: Segmenters Dataset
create_card(slide7, Inches(4.76), Inches(1.4), Inches(3.8), Inches(5.3))
tf_stat2 = add_content_box(slide7, Inches(4.91), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_stat2, "Dataset 2 & 3: Segmenters", font_size=13, font_color=PURPLE_RGB, bold=True, space_after=12)
add_para(tf_stat2, "5,344", font_size=32, font_color=PURPLE_RGB, bold=True, space_after=4)
add_para(tf_stat2, "UNIFIED SEGMENTATION IMAGES", font_size=9.5, font_color=TEXT_MUTED, bold=True, space_after=15)
add_bullet(tf_stat2, "Tumor Set: 2,262 images (1584 Train / 338 Val / 340 Test)")
add_bullet(tf_stat2, "Cyst Set: 3,082 images (2158 Train / 462 Val / 462 Test)")

# Col 3: Class Distribution list/chart
create_card(slide7, Inches(8.93), Inches(1.4), Inches(3.8), Inches(5.3))
tf_stat3 = add_content_box(slide7, Inches(9.08), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_stat3, "Primary Class Distribution", font_size=13, font_color=TEXT_HIGHLIGHT, bold=True, space_after=15)

dist_data = [
    ("Normal", "5,077 slices", TEAL_RGB),
    ("Cyst", "3,709 slices", GREEN_RGB),
    ("Tumor", "2,283 slices", PURPLE_RGB),
    ("Stone", "1,377 slices", RED_RGB)
]

for label, val, col in dist_data:
    add_para(tf_stat3, f"■  {label}", font_size=11, font_color=col, bold=True, space_after=1)
    add_para(tf_stat3, f"    {val}", font_size=10, font_color=TEXT_MAIN, space_after=12)

# ==========================================
# SLIDE 8: AI Models and Technology Stack
# ==========================================
slide8 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide8)
add_slide_header(slide8, "AI Models and Technology Stack", "08. Engineering Stack")

# Col 1: Vision Stack
create_card(slide8, Inches(0.6), Inches(1.4), Inches(3.8), Inches(5.3))
tf_t1 = add_content_box(slide8, Inches(0.75), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_t1, "👁️ Vision Intelligence", font_size=14, font_color=TEAL_RGB, bold=True, space_after=15)
add_bullet(tf_t1, "PCSA-KidneyNeXt: Custom classifier architecture mapping local (convolutions) and global structures (PCSA).")
add_bullet(tf_t1, "Grad-CAM Explainability: Extracts gradients of activations targeting stage4 layer.")
add_bullet(tf_t1, "YOLOv11 Specialist Segmenters: High-speed localization algorithms dedicated to tumor and cyst structures.")

# Col 2: NLP & LLM Stack
create_card(slide8, Inches(4.76), Inches(1.4), Inches(3.8), Inches(5.3))
tf_t2 = add_content_box(slide8, Inches(4.91), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_t2, "🧠 Biomedical NLP & GenAI", font_size=14, font_color=PURPLE_RGB, bold=True, space_after=15)
add_bullet(tf_t2, "Hugging Face NER Model: Parses notes using d4data/biomedical-ner-all framework.")
add_bullet(tf_t2, "DeepSeek LLM: Interfaces via REST API to yield context-matching recommendations.")
add_bullet(tf_t2, "Keyword Filters: Cross-checks symptoms with rule triggers (e.g. sodium restrictions for hypertension text).")

# Col 3: dev & visualization
create_card(slide8, Inches(8.93), Inches(1.4), Inches(3.8), Inches(5.3))
tf_t3 = add_content_box(slide8, Inches(9.08), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_t3, "🛠️ Dev & Visualizations", font_size=14, font_color=GREEN_RGB, bold=True, space_after=15)
add_bullet(tf_t3, "Core Backends: Implemented in PyTorch, Torchvision, OpenCV, and PIL frameworks.")
add_bullet(tf_t3, "Visual Panels: Renders custom Plotly Scatter3D geometries and Matplotlib heatmaps.")
add_bullet(tf_t3, "Dataset Platforms: Ingests config metadata, Roboflow mappings, and automated splits.")

# ==========================================
# SLIDE 9: Stage 1 — Classification and Explainable AI
# ==========================================
slide9 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide9)
add_slide_header(slide9, "Stage 1 — Classification & Explainable AI", "09. Classification & CAM")

# Left Card: Hyperparameters (Double width)
create_card(slide9, Inches(0.6), Inches(1.4), Inches(7.8), Inches(5.3))
tf_cls_workflow = add_content_box(slide9, Inches(0.75), Inches(1.55), Inches(7.5), Inches(5.0))
add_para(tf_cls_workflow, "🧠 Classifier Workflow & Hyperparameters", font_size=14, font_color=TEAL_RGB, bold=True, space_after=10)
add_para(tf_cls_workflow, "Images are downsampled and feature vectors are extracted hierarchically. Hyperparameter details:", font_size=11, space_after=10)
add_bullet(tf_cls_workflow, "Four Stages: Resizes channels gradually (96 -> 192 -> 384 -> 768 channels).")
add_bullet(tf_cls_workflow, "Parallel Convolutions: Gathers features using max pool, average pool, and 3x3/5x5 groups.")
add_bullet(tf_cls_workflow, "Pyramid Channel & Spatial Attention: Concentrates computational weights on abnormal textures.")
add_bullet(tf_cls_workflow, "Optimizer & Loss: AdamW optimizer combined with standard CrossEntropyLoss function.")
add_bullet(tf_cls_workflow, "Trainable Weights: Contains 2,114,580 trainable weight parameters.")

# Right Card: Explainability
create_card(slide9, Inches(8.6), Inches(1.4), Inches(4.1), Inches(5.3))
tf_cam_explain = add_content_box(slide9, Inches(8.75), Inches(1.55), Inches(3.8), Inches(5.0))
add_para(tf_cam_explain, "🔍 Anatomical Validation", font_size=14, font_color=RED_RGB, bold=True, space_after=12)
add_bullet(tf_cam_explain, "Activations Mapping: Captures spatial features of pcsa_classifier.stage4 layer.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_cam_explain, "Artifact Rejection: Ensures network weights target internal kidney pathology, ignoring CT table or scanner hardware boundaries.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_cam_explain, "Clinical Transparency: Provides heatmaps enabling clinicians to visually verify classification decisions.", bullet_char="▪", bullet_color=RED_RGB)

# ==========================================
# SLIDE 10: Stage 2 — Pathology Segmentation
# ==========================================
slide10 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide10)
add_slide_header(slide10, "Stage 2 — Pathology Segmentation", "10. Route & Segment")

# Left Column - Routing
create_card(slide10, Inches(0.6), Inches(1.4), Inches(7.8), Inches(5.3))
tf_route = add_content_box(slide10, Inches(0.75), Inches(1.55), Inches(7.5), Inches(5.0))
add_para(tf_route, "🔀 Conditional Model Routing Protocol", font_size=14, font_color=GREEN_RGB, bold=True, space_after=10)
add_para(tf_route, "The system prevents processing overhead by only routing images to segmentation models when classification detects active abnormalities:", font_size=11, space_after=10)
add_bullet(tf_route, "Cyst Prediction -> Routes image tensor to YOLO Cyst specialist model.", bullet_char="→", bullet_color=GREEN_RGB)
add_bullet(tf_route, "Tumor Prediction -> Routes image tensor to YOLO Tumor specialist model.", bullet_char="→", bullet_color=TEAL_RGB)
add_bullet(tf_route, "Normal or Stone -> Bypasses segmentation pipelines, accelerating inference times.", bullet_char="→", bullet_color=TEXT_MUTED)
add_para(tf_route, "Output Coordinate Data: Specialized segmentation masks generate polygon borders, which are extracted for Stage 3 severity metrics.", font_size=10.5, space_after=6)

# Right Column - Boundaries
create_card(slide10, Inches(8.6), Inches(1.4), Inches(4.1), Inches(5.3))
tf_bounds = add_content_box(slide10, Inches(8.75), Inches(1.55), Inches(3.8), Inches(5.0))
add_para(tf_bounds, "🔍 Specialist Boundary Mapping", font_size=14, font_color=TEXT_HIGHLIGHT, bold=True, space_after=12)
add_bullet(tf_bounds, "YOLOv11 Seg Models: Trained individually to segment localized targets.")
add_bullet(tf_bounds, "Confidence Thresholds: Average confidence scores span 80%-95% for tumor areas and 60%-89% for cyst boundaries.")
add_bullet(tf_bounds, "Contour Arrays: Output masks are flattened into 2D polygon arrays for area calculations.")

# ==========================================
# SLIDE 11: Stage 3 — Quantitative Pathology Analysis
# ==========================================
slide11 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide11)
add_slide_header(slide11, "Stage 3 — Quantitative Pathology Analysis", "11. Quantification")

# Left Column - Math
create_card(slide11, Inches(0.6), Inches(1.4), Inches(7.8), Inches(5.3))
tf_quant = add_content_box(slide11, Inches(0.75), Inches(1.55), Inches(7.5), Inches(5.0))
add_para(tf_quant, "⚙️ Mathematical Quantification Protocol", font_size=14, font_color=TEAL_RGB, bold=True, space_after=10)
add_bullet(tf_quant, "Mask Conversion: Extracts coordinates of closed contours from YOLO segmentation polygon masks.")
add_bullet(tf_quant, "Area Computation: Processes coordinate borders using OpenCV cv2.contourArea() function to yield pixel counts.")
add_bullet(tf_quant, "Tissue Ratio: Computes tissue replacement percentage: Ratio = (Pathology Area / Kidney Area) * 100.")
add_bullet(tf_quant, "Clinical Threshold Rules: Ratios exceeding 30% trigger warnings suggesting evaluation for Radical Nephrectomy. Ratios below 30% trigger warnings for Partial Nephrectomy.")

# Right Column - Sizing card
create_card(slide11, Inches(8.6), Inches(1.4), Inches(4.1), Inches(5.3))
tf_donut = add_content_box(slide11, Inches(8.75), Inches(1.55), Inches(3.8), Inches(5.0))
add_para(tf_donut, "📊 Sizing Metrics & Alerts", font_size=14, font_color=RED_RGB, bold=True, space_after=12)
add_para(tf_donut, "Mock Output Case:", font_size=11, bold=True, space_after=8)
add_bullet(tf_donut, "Kidney Area: 32,450 pixels", bullet_char="▪")
add_bullet(tf_donut, "Tumor Area: 11,260 pixels", bullet_char="▪")
add_bullet(tf_donut, "Ratio: 34.7% tissue replacement", bullet_char="▪")
add_para(tf_donut, "⚠️ Active Severity Alert:", font_size=11, font_color=RED_RGB, bold=True, space_after=4)
add_para(tf_donut, "Ratio exceeds critical 30% threshold. Recommend evaluating patient for Radical Nephrectomy procedures.", font_size=10, font_color=TEXT_MAIN, italic=True)

# ==========================================
# SLIDE 12: Stage 4 — Clinical NLP & AI Dietitian
# ==========================================
slide12 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide12)
add_slide_header(slide12, "Stage 4 — Clinical NLP & AI Dietitian", "12. NLP & Care Advisory")

# Left Column - Notes & Entities
create_card(slide12, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.3))
tf_nlp = add_content_box(slide12, Inches(0.75), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_nlp, "📥 Note Parsing & Entity Extraction", font_size=14, font_color=PURPLE_RGB, bold=True, space_after=10)
add_para(tf_nlp, "Ingested Clinical History Note:", font_size=10, bold=True, space_after=4)
add_para(tf_nlp, '"Patient presents with hematuria and right-sided flank pain. Imaging reveals a 5 cm renal mass. Suspected RCC. Patient has history of Type 2 diabetes, currently controlled with Metformin."', font_size=9.5, font_color=TEXT_MUTED, italic=True, space_after=10)
add_para(tf_nlp, "Extracted NER Clinical Entities (d4data):", font_size=10, bold=True, space_after=4)
add_bullet(tf_nlp, "Symptoms: Hematuria, Flank Pain", bullet_char="🏷️", bullet_color=AMBER_RGB)
add_bullet(tf_nlp, "Anatomy: Renal Mass", bullet_char="🏷️", bullet_color=TEAL_RGB)
add_bullet(tf_nlp, "Disease/Pathology: Suspected RCC, Type 2 Diabetes", bullet_char="🏷️", bullet_color=RED_RGB)
add_bullet(tf_nlp, "Therapeutics: Metformin", bullet_char="🏷️", bullet_color=PURPLE_RGB)

# Right Column - Diet
create_card(slide12, Inches(6.9), Inches(1.4), Inches(5.8), Inches(5.3))
tf_diet = add_content_box(slide12, Inches(7.05), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_diet, "🤖 DeepSeek Postoperative Dietary Alerts", font_size=14, font_color=TEAL_RGB, bold=True, space_after=10)
add_bullet(tf_diet, "Diabetic Diet Control: Restrict simple carbohydrate intakes. Maintain strict glycemic index monitoring to preserve remaining kidney function post-nephrectomy.")
add_bullet(tf_diet, "Renal-Protective Focus: Restrict sodium and phosphorus intakes to control systemic blood pressure and prevent hyperfiltration in the remaining healthy kidney.")
add_bullet(tf_diet, "Clinical Alert: Highly hypervascular renal mass (suspected RCC) requires immediate oncology follow-up and dietary matching with cancer cachexia support guidelines.")
add_para(tf_diet, "⚠️ Disclaimer: Generative advice is for research demonstration only. All clinical decisions must be confirmed by qualified medical professionals.", font_size=8.5, font_color=TEXT_MUTED, italic=True, space_after=0)

# ==========================================
# SLIDE 13: Qualitative Results — Integrated AI Output
# ==========================================
slide13 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide13)
add_slide_header(slide13, "Qualitative Results — Integrated AI Output", "13. Visualization & Output")

# Left Side Image
img_path = "/Users/atharv/Desktop/Capstone/CapFinal.png"
if os.path.exists(img_path):
    slide13.shapes.add_picture(img_path, Inches(0.6), Inches(1.4), Inches(8.0), Inches(5.3))
else:
    create_card(slide13, Inches(0.6), Inches(1.4), Inches(8.0), Inches(5.3))
    tf_err2 = add_content_box(slide13, Inches(0.7), Inches(1.5), Inches(7.8), Inches(5.1))
    add_para(tf_err2, "Diagnostic Dashboard View (CapFinal.png missing)", font_size=12, font_color=RED_RGB, bold=True)

# Right Side Card
create_card(slide13, Inches(8.8), Inches(1.4), Inches(3.9), Inches(5.3))
tf_geom = add_content_box(slide13, Inches(8.95), Inches(1.55), Inches(3.6), Inches(5.0))
add_para(tf_geom, "🌐 3D Spatial Geometry Layer", font_size=14, font_color=TEAL_RGB, bold=True, space_after=12)
add_bullet(tf_geom, "Depth Mapping: Reads 2D coordinate bounds and maps structures across depth layers (Z-axis coordinates).")
add_bullet(tf_geom, "Anatomical Separation: Organizes coordinates placing Kidney tissue at Z = 0 and tumor/cyst borders at Z = 5.")
add_bullet(tf_geom, "Dynamic Display: Generates Plotly Scatter3D visual elements with active cursor hover indices.")
add_bullet(tf_geom, "Surgical Title Embedding: Automatically appends surgical suggestion alerts directly to Plotly slide headers.")

# ==========================================
# SLIDE 14: Quantitative Evaluation & Current Progress
# ==========================================
slide14 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide14)
add_slide_header(slide14, "Quantitative Evaluation & Current Progress", "14. Metrics & Status")

# Left Column - Metrics Table (We can construct a clean PPTX Table!)
create_card(slide14, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.3))
tf_table_title = add_content_box(slide14, Inches(0.75), Inches(1.45), Inches(5.5), Inches(0.5))
add_para(tf_table_title, "📋 Stage 1 Classifier Test Metrics", font_size=13, font_color=TEAL_RGB, bold=True)

# Table coordinates
rows = 6
cols = 5
left_t = Inches(0.75)
top_t = Inches(2.0)
width_t = Inches(5.5)
height_t = Inches(2.8)

table_shape = slide14.shapes.add_table(rows, cols, left_t, top_t, width_t, height_t)
table = table_shape.table

# Set columns width
table.columns[0].width = Inches(1.3)
table.columns[1].width = Inches(1.05)
table.columns[2].width = Inches(1.05)
table.columns[3].width = Inches(1.05)
table.columns[4].width = Inches(1.05)

headers = ["Class", "Precision", "Recall", "F1-Score", "Support"]
metrics_rows = [
    ["Cyst", "1.0000", "0.9973", "0.9987", "742"],
    ["Normal", "1.0000", "1.0000", "1.0000", "1,016"],
    ["Stone", "0.9928", "1.0000", "0.9964", "275"],
    ["Tumor", "1.0000", "1.0000", "1.0000", "457"],
    ["Accuracy", "", "", "0.9992", "2,490"]
]

# Style headers
for col_idx, text in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = text
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.name = 'Calibri'
    p.font.color.rgb = RGBColor(*TEXT_HIGHLIGHT)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(*BORDER_RGB)

# Populate rows
for r_idx, row_data in enumerate(metrics_rows):
    for c_idx, val in enumerate(row_data):
        cell = table.cell(r_idx + 1, c_idx)
        cell.text = val
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(9.5)
        p.font.name = 'Calibri'
        p.font.color.rgb = RGBColor(*TEXT_MAIN)
        if r_idx == 4: # Accuracy Row
            p.font.bold = True
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(*BG_RGB)
            if c_idx == 3 or c_idx == 0:
                p.font.color.rgb = RGBColor(*TEAL_RGB)

# Bottom note on YOLO
tf_yolo_note = add_content_box(slide14, Inches(0.75), Inches(4.9), Inches(5.5), Inches(1.6))
add_para(tf_yolo_note, "📊 YOLO Segmentation Metrics Note:", font_size=10.5, font_color=AMBER_RGB, bold=True, space_after=3)
add_para(tf_yolo_note, "Segmentation models evaluations are ongoing. Zero-shot checks are currently validating class coordinate metrics relative to clinical test sets.", font_size=9.5, font_color=TEXT_MUTED)

# Right Column - Progress checklist
create_card(slide14, Inches(6.9), Inches(1.4), Inches(5.8), Inches(5.3))
tf_prog = add_content_box(slide14, Inches(7.05), Inches(1.55), Inches(5.5), Inches(5.0))
add_para(tf_prog, "🎯 Implementation Status", font_size=14, font_color=GREEN_RGB, bold=True, space_after=12)

checks = [
    ("Classification Pipeline", True),
    ("Grad-CAM Explainability", True),
    ("Tumor & Cyst Segmenters", True),
    ("Pathology Ratio Calculation", True),
    ("Biomedical NER Patient Parser", True),
    ("Rule-Based Diet Restrictions", True),
    ("DeepSeek Generative Recommendations", True),
    ("Plotly 3D Geometry Rendering", True),
    ("Automated Dataset Merger Script", True)
]

for name, completed in checks:
    status_icon = "✓" if completed else "→"
    status_color = GREEN_RGB if completed else TEAL_RGB
    add_bullet(tf_prog, name, bullet_char=status_icon, font_size=10.5, space_after=4, bullet_color=status_color)

add_para(tf_prog, "▪  In Progress: Unified generalist validation tests & multi-center clinical validation evaluations.", font_size=9.5, font_color=TEXT_MUTED, space_after=0)

# ==========================================
# SLIDE 15: Limitations, Future Work & Conclusion
# ==========================================
slide15 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide15)
add_slide_header(slide15, "Limitations, Future Work & Conclusion", "15. Summary & Next Steps")

# Card 1: Limitations
create_card(slide15, Inches(0.6), Inches(1.4), Inches(3.8), Inches(5.3))
tf_lim = add_content_box(slide15, Inches(0.75), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_lim, "⚠️ Identified Limitations", font_size=13, font_color=RED_RGB, bold=True, space_after=12)
add_bullet(tf_lim, "Segmentation accuracy matrices (mAP, IoU) require formal validation sets.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_lim, "3D visualizations displace adjacent 2D contours rather than constructing continuous slice volume models.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_lim, "OpenCV contour dimensions represent pixels rather than metric millimeters.", bullet_char="▪", bullet_color=RED_RGB)
add_bullet(tf_lim, "Surgical ratio alert thresholds require confirmation in medical trials.", bullet_char="▪", bullet_color=RED_RGB)

# Card 2: Future Work
create_card(slide15, Inches(4.76), Inches(1.4), Inches(3.8), Inches(5.3))
tf_fut = add_content_box(slide15, Inches(4.91), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_fut, "🔮 Planned Future Works", font_size=13, font_color=TEAL_RGB, bold=True, space_after=12)
add_bullet(tf_fut, "Generalist Segmentation: Train single multi-class YOLO model replacing twin specialists.", bullet_char="▪", bullet_color=TEAL_RGB)
add_bullet(tf_fut, "DICOM Tag Calibration: Convert spatial pixels to physical mm using slice coordinates.", bullet_char="▪", bullet_color=TEAL_RGB)
add_bullet(tf_fut, "Volumetric stack: Implement full marching cubes 3D kidney reconstructions.", bullet_char="▪", bullet_color=TEAL_RGB)
add_bullet(tf_fut, "Structured Reports: Format predictions directly into HIS medical files.", bullet_char="▪", bullet_color=TEAL_RGB)

# Card 3: Summary
create_card(slide15, Inches(8.93), Inches(1.4), Inches(3.8), Inches(5.3))
tf_sum = add_content_box(slide15, Inches(9.08), Inches(1.55), Inches(3.5), Inches(5.0))
add_para(tf_sum, "🏁 Summary & Key Takeaway", font_size=13, font_color=TEXT_HIGHLIGHT, bold=True, space_after=12)
add_para(tf_sum, "NephroVision connects computer vision, attention mapping, text transformers, and large language models into a unified pipeline.", font_size=10.5, space_after=12)
add_para(tf_sum, "Pipeline Flow Summary:", font_size=10.5, bold=True, space_after=4)
add_para(tf_sum, "CT Scan → PCSA → Grad-CAM → YOLO Seg → OpenCV → Clinical NER → DeepSeek Diet → 3D Model", font_size=9, font_color=TEAL_RGB, bold=True, space_after=15, font_name='Courier New')
create_card(slide15, Inches(9.08), Inches(4.95), Inches(3.5), Inches(1.5), bg_rgb=BG_RGB, border_rgb=BORDER_RGB)
tf_quote = add_content_box(slide15, Inches(9.18), Inches(5.05), Inches(3.3), Inches(1.3))
add_para(tf_quote, '"Proposed framework demonstrates clinical context-aware advice can successfully link medical image analysis and generative text AI models."', font_size=9, font_color=TEXT_MAIN, italic=True)

# Save presentation
prs.save('/Users/atharv/Desktop/Capstone/NephroVision_Presentation.pptx')
print("Successfully generated: /Users/atharv/Desktop/Capstone/NephroVision_Presentation.pptx")
