import streamlit as st
import os
import base64
import json
import time
import tempfile
from mistralai import Mistral
import PyPDF2
import io
import re
import markdown
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set page configuration with a modern layout
st.set_page_config(
    layout="wide",
    page_title="Mistral OCR",
    page_icon="✦",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a stunning, modern UI
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables */
    :root {
        --bg-primary: #0a0a0b;
        --bg-secondary: #111113;
        --bg-card: rgba(255, 255, 255, 0.03);
        --bg-card-hover: rgba(255, 255, 255, 0.06);
        --border-color: rgba(255, 255, 255, 0.08);
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --accent-orange: #f97316;
        --accent-orange-glow: rgba(249, 115, 22, 0.15);
        --accent-teal: #14b8a6;
        --accent-rose: #f43f5e;
        --gradient-start: #f97316;
        --gradient-end: #fb923c;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(180deg, #0a0a0b 0%, #0f0f11 50%, #0a0a0b 100%);
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 3rem 4rem 3rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 3rem !important;
        letter-spacing: -0.03em;
        margin-bottom: 0 !important;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-weight: 600;
        font-size: 1.5rem !important;
        letter-spacing: -0.02em;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 500;
        font-size: 1.1rem !important;
    }
    
    p, .stMarkdown {
        color: var(--text-secondary) !important;
    }
    
    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, rgba(20, 184, 166, 0.05) 100%);
        border: 1px solid rgba(249, 115, 22, 0.2);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(249, 115, 22, 0.5), transparent);
    }
    
    .hero-title {
        font-size: 1.4rem !important;
        font-weight: 600;
        color: #fafafa !important;
        margin-bottom: 0.75rem !important;
    }
    
    .hero-subtitle {
        color: #a1a1aa !important;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Feature cards - glass morphism */
    .feature-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(249, 115, 22, 0.3);
        transform: translateY(-2px);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent-orange) 0%, var(--accent-teal) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card h4 {
        color: #fafafa !important;
        font-weight: 600;
        font-size: 1rem;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .feature-card p {
        color: #71717a !important;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.5;
    }
    
    .feature-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--accent-orange) 0%, var(--accent-teal) 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Section container */
    .section-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
    }
    
    /* Input styling - force dark theme */
    .stTextInput input,
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stTextArea > div > div > textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #1a1a1c !important;
        background-color: #1a1a1c !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #fafafa !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 0.875rem 1rem !important;
        transition: all 0.2s ease !important;
        caret-color: #f97316 !important;
    }
    
    .stTextInput input:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-orange) !important;
        box-shadow: 0 0 0 3px var(--accent-orange-glow) !important;
        background: #1a1a1c !important;
    }
    
    .stTextInput input::placeholder,
    .stTextInput > div > div > input::placeholder,
    .stTextArea textarea::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #71717a !important;
        opacity: 1 !important;
    }
    
    /* Force text color on all input descendants */
    .stTextInput *,
    .stTextArea * {
        color: #fafafa !important;
    }
    
    /* Label styling */
    .stTextInput label,
    .stTextArea label {
        color: #a1a1aa !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--accent-orange) !important;
        background: rgba(249, 115, 22, 0.05) !important;
    }
    
    .stFileUploader label {
        color: var(--text-secondary) !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.25rem !important;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease !important;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(249, 115, 22, 0.1) !important;
        border-color: var(--accent-orange) !important;
        color: var(--text-primary) !important;
    }
    
    /* Primary button */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ea580c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: -0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.35) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    
    .badge-pdf {
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .badge-image {
        background: rgba(34, 197, 94, 0.1);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.2);
    }
    
    .badge-url {
        background: rgba(168, 85, 247, 0.1);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.2);
    }
    
    .badge-upload {
        background: rgba(20, 184, 166, 0.1);
        color: #2dd4bf;
        border: 1px solid rgba(20, 184, 166, 0.2);
    }
    
    /* Results section */
    .results-section {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: var(--accent-orange) !important;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: var(--text-secondary) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-orange) 0%, var(--accent-teal) 100%) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
        padding: 0.75rem 1.25rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(249, 115, 22, 0.1) !important;
        border-color: var(--accent-orange) !important;
        color: var(--text-primary) !important;
    }
    
    /* Success/Info/Warning messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid rgba(34, 197, 94, 0.2) !important;
        border-radius: 12px !important;
        color: #4ade80 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px !important;
        color: #60a5fa !important;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border: 1px solid rgba(251, 191, 36, 0.2) !important;
        border-radius: 12px !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-orange) transparent transparent transparent !important;
    }
    
    /* iFrame and images */
    iframe {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    img {
        border-radius: 12px;
    }
    
    /* Download links container */
    .download-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    
    .download-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.625rem 1rem;
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .download-btn:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: var(--accent-orange);
        color: var(--text-primary);
        transform: translateY(-1px);
    }
    
    /* Code/text preview */
    .text-preview {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #d4d4d8;
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.6;
    }
    
    .text-preview::-webkit-scrollbar {
        width: 6px;
    }
    
    .text-preview::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .text-preview::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    
    /* Footer */
    .footer {
        margin-top: 4rem;
        padding: 2rem 0;
        text-align: center;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .footer p {
        color: #52525b !important;
        font-size: 0.85rem;
    }
    
    .footer a {
        color: var(--accent-orange);
        text-decoration: none;
    }
    
    /* Table styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        overflow: hidden;
    }
    
    th, td {
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 0.75rem 1rem;
        text-align: left;
        color: var(--text-secondary);
    }
    
    th {
        background: rgba(255, 255, 255, 0.03);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Code block */
    pre, code {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace !important;
        color: #d4d4d8 !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* Glow effect for headers */
    .glow-text {
        text-shadow: 0 0 40px rgba(249, 115, 22, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# App header with logo and title
st.markdown('''
<div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
    <div style="
        width: 56px; 
        height: 56px; 
        background: linear-gradient(135deg, #f97316 0%, #14b8a6 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        box-shadow: 0 8px 32px rgba(249, 115, 22, 0.25);
    ">✦</div>
</div>
''', unsafe_allow_html=True)

st.title("Mistral OCR")
st.markdown('<p style="font-size: 1.15rem; margin-top: -0.5rem; color: #71717a; font-weight: 400;">Extract text from PDFs and images with powerful AI</p>', unsafe_allow_html=True)

# Hero section with gradient
st.markdown("""
<div class="hero-container">
    <h3 class="hero-title">🚀 Transform Documents into Text in Seconds</h3>
    <p class="hero-subtitle">
        Powered by Mistral's state-of-the-art OCR model. Upload files directly or provide URLs, 
        process documents of any size, and download extracted text in multiple formats.
    </p>
</div>
""", unsafe_allow_html=True)

# Features section
with st.container():
    st.markdown("## ✨ Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h4>PDF & Image Support</h4>
            <p>Extract text from both PDFs and images with a single tool. Supports JPG, PNG, and multi-page PDFs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔗</div>
            <h4>URL & File Upload</h4>
            <p>Process documents from public URLs or upload files directly from your device—flexibility at your fingertips.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h4>Large PDF Processing</h4>
            <p>Automatically splits and processes large PDFs with hundreds of pages into manageable chunks.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✨</div>
            <h4>Smart Text Cleanup</h4>
            <p>Intelligently cleans up and formats extracted text—tables, headings, and paragraphs preserved.</p>
        </div>
        """, unsafe_allow_html=True)

# Function to split large PDFs into smaller chunks
def split_pdf(pdf_bytes, chunk_size=100):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(pdf_reader.pages)
    chunks = []
    
    # If PDF is small enough, return as a single chunk
    if total_pages <= chunk_size:
        return [pdf_bytes]
    
    # Split into chunks
    for i in range(0, total_pages, chunk_size):
        end_page = min(i + chunk_size, total_pages)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page_num in range(i, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        chunks.append(output.getvalue())
    
    return chunks

# Function to clean up OCR text and improve formatting
def clean_ocr_text(text):
    # Keep track of original text for comparison
    original_text = text
    
    # 1. Fix table formatting
    # Look for table-like structures with | characters
    table_pattern = r'(\|[^\n]+\|)'
    
    def fix_table(match):
        table_row = match.group(1)
        # Make sure cells are properly spaced
        cells = table_row.split('|')
        cells = [cell.strip() for cell in cells if cell.strip()]
        if cells:
            return '| ' + ' | '.join(cells) + ' |'
        return match.group(1)
    
    text = re.sub(table_pattern, fix_table, text)
    
    # 2. Remove random numeric sequences (like 18.1.1.1.1.1.2.1.2...)
    text = re.sub(r'(\d+\.){10,}(\d+)', '', text)
    
    # 3. Fix heading formatting (ensure proper spacing after #)
    text = re.sub(r'#([A-Z])', r'# \1', text)
    
    # 4. Fix duplicate headings that appear consecutively
    text = re.sub(r'(# [^\n]+)\n\1', r'\1', text)
    
    # 5. Clean up image references
    text = re.sub(r'!\[img-\d+\.jpeg\]\(img-\d+\.jpeg\)', '', text)
    
    # 6. Fix chapter and section formatting
    # Make "Chapter X" into a heading if it's not already
    text = re.sub(r'(?<!#)Chapter (\d+)', r'## Chapter \1', text)
    
    # 7. Fix spacing around headers
    text = re.sub(r'(#+) ([^\n]+)(?!\n\n)', r'\1 \2\n\n', text)
    
    # 8. Convert markdown tables to proper format
    lines = text.split('\n')
    for i in range(len(lines)):
        if '|' in lines[i] and i > 0 and i < len(lines) - 1:
            # Check if this is a table header row
            if ':--:' in lines[i] or ':--' in lines[i] or '--:' in lines[i]:
                continue
            
            # Check if this is already a properly formatted table
            if lines[i-1].count('|') >= 2 and lines[i].count('|') >= 2:
                # This is likely a table, make sure headers have separator
                if not ((':--:' in lines[i]) or (':--' in lines[i]) or ('--:' in lines[i])):
                    # Insert a separator row after the header
                    cols = lines[i-1].count('|') - 1
                    if cols > 0:
                        separator = '| ' + ' | '.join(['---' for _ in range(cols)]) + ' |'
                        lines.insert(i, separator)
    
    text = '\n'.join(lines)
    
    # 9. Clean up weird line breaks in paragraphs
    # Join lines that don't end with period, question mark, or exclamation
    lines = text.split('\n')
    i = 0
    while i < len(lines) - 1:
        if (lines[i] and not lines[i].startswith('#') and 
            not lines[i].startswith('|') and not lines[i].startswith('```') and
            not lines[i].startswith('- ') and not lines[i].startswith('* ') and
            not lines[i].startswith('1. ') and not lines[i].endswith('.') and
            not lines[i].endswith('?') and not lines[i].endswith('!') and
            not lines[i].endswith(':') and lines[i+1] and
            not lines[i+1].startswith('#') and not lines[i+1].startswith('|') and
            not lines[i+1].startswith('```') and not lines[i+1].startswith('- ') and
            not lines[i+1].startswith('* ') and not lines[i+1].startswith('1. ')):
            lines[i] = lines[i] + ' ' + lines[i+1]
            lines.pop(i+1)
        else:
            i += 1
    
    text = '\n'.join(lines)
    
    # 10. Add proper spacing between sections
    text = re.sub(r'(^|\n)(#+ [^\n]+)(?!\n\n)', r'\1\2\n\n', text)
    
    # 11. Ensure double line breaks after headings
    for i in range(4, 0, -1):  # Handle h4, h3, h2, h1
        hashes = '#' * i
        text = re.sub(f'{hashes} ([^\\n]+)\\n(?!\\n)', f'{hashes} \\1\n\n', text)
    
    # If the text didn't change much, return the original to avoid unnecessary changes
    if len(text) > len(original_text) * 0.9 and len(text) < len(original_text) * 1.1:
        return text
    else:
        return original_text

# Function to convert markdown to PDF
def create_pdf_from_markdown(markdown_text, file_name):
    """Convert markdown text to a PDF file using ReportLab."""
    try:
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.textColor = colors.HexColor('#4527A0')
        
        heading1_style = styles['Heading1']
        heading1_style.textColor = colors.HexColor('#5E35B1')
        
        heading2_style = styles['Heading2']
        heading2_style.textColor = colors.HexColor('#673AB7')
        
        normal_style = styles['Normal']
        
        # Create a code style
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=8,
            backColor=colors.HexColor('#F5F5F5'),
            borderPadding=5,
        )
        
        # Sanitize the markdown text - thoroughly remove HTML-like tags that could cause errors
        def sanitize_text(text):
            # Replace HTML tags with escaped versions
            text = re.sub(r'<([^>]+)>', r'&lt;\1&gt;', text)
            
            # Replace common problematic characters
            replacements = {
                '&': '&amp;',
                '"': '&quot;',
                "'": '&#39;',
                '\u2028': ' ',  # Line separator
                '\u2029': ' ',  # Paragraph separator
            }
            
            for char, replacement in replacements.items():
                text = text.replace(char, replacement)
                
            return text
        
        sanitized_text = sanitize_text(markdown_text)
        
        # Process the markdown text
        lines = sanitized_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle headings
            if line.startswith('# '):
                elements.append(Paragraph(sanitize_text(line[2:]), title_style))
                elements.append(Spacer(1, 12))
            elif line.startswith('## '):
                elements.append(Paragraph(sanitize_text(line[3:]), heading1_style))
                elements.append(Spacer(1, 10))
            elif line.startswith('### '):
                elements.append(Paragraph(sanitize_text(line[4:]), heading2_style))
                elements.append(Spacer(1, 8))
            
            # Handle tables
            elif line.startswith('|') and '|' in line[1:]:
                # Collect all table rows
                table_data = []
                table_row = line.split('|')
                table_row = [sanitize_text(cell.strip()) for cell in table_row if cell.strip()]
                table_data.append(table_row)
                
                # Move to next line
                i += 1
                if i < len(lines) and '---' in lines[i]:  # Skip separator row
                    i += 1
                
                # Continue collecting table rows
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_row = lines[i].split('|')
                    table_row = [sanitize_text(cell.strip()) for cell in table_row if cell.strip()]
                    table_data.append(table_row)
                    i += 1
                
                # Create the table
                if table_data:
                    # Make sure all rows have the same number of columns
                    max_cols = max(len(row) for row in table_data)
                    for row in table_data:
                        while len(row) < max_cols:
                            row.append('')
                    
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                
                # Continue without incrementing i since we already advanced it
                continue
            
            # Handle code blocks
            elif line.startswith('```'):
                code_content = []
                # Move to next line (first line of code)
                i += 1
                
                # Continue collecting code lines until end marker
                while i < len(lines) and not lines[i].startswith('```'):
                    code_content.append(sanitize_text(lines[i]))
                    i += 1
                
                # Skip the closing code marker
                if i < len(lines):
                    i += 1
                
                # Join code content and add as a paragraph with code style
                if code_content:
                    code_text = '<pre>' + '\n'.join(code_content) + '</pre>'
                    elements.append(Paragraph(code_text, code_style))
                    elements.append(Spacer(1, 12))
                
                # Continue without incrementing i since we already advanced it
                continue
            
            # Handle normal paragraphs
            elif line and not line.startswith(('- ', '* ', '1. ')):
                # Check if this is a paragraph that continues on the next line
                paragraph_text = line
                next_idx = i + 1
                while (next_idx < len(lines) and 
                       lines[next_idx].strip() and 
                       not lines[next_idx].strip().startswith(('# ', '## ', '### ', '- ', '* ', '1. ', '|', '```'))):
                    paragraph_text += ' ' + lines[next_idx].strip()
                    next_idx += 1
                
                try:
                    elements.append(Paragraph(sanitize_text(paragraph_text), normal_style))
                    elements.append(Spacer(1, 8))
                except Exception as e:
                    # If a paragraph fails, try with an extra level of escaping
                    elements.append(Paragraph(f"[Paragraph rendering error: {str(e)[:50]}...]", normal_style))
                    elements.append(Spacer(1, 8))
                
                # Skip the lines we've already processed
                i = next_idx - 1
            
            # Handle lists
            elif line.startswith(('- ', '* ')):
                list_items = []
                list_items.append(line[2:])
                
                # Collect all list items
                next_idx = i + 1
                while next_idx < len(lines) and lines[next_idx].strip().startswith(('- ', '* ')):
                    list_items.append(lines[next_idx].strip()[2:])
                    next_idx += 1
                
                # Add list items with bullet points
                for item in list_items:
                    bullet_text = '• ' + sanitize_text(item)
                    try:
                        elements.append(Paragraph(bullet_text, normal_style))
                    except Exception:
                        elements.append(Paragraph('• [Item rendering error]', normal_style))
                
                elements.append(Spacer(1, 8))
                
                # Skip the lines we've already processed
                i = next_idx - 1
            
            # Move to next line
            i += 1
        
        # Add a title if none exists
        if len(elements) == 0:
            elements.append(Paragraph(f"{file_name} - Extracted Text", title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("The document was processed successfully but may contain content that couldn't be fully rendered.", normal_style))
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        st.warning(f"Error generating PDF: {e}")
        return None

# Main app section with card-like appearance
st.markdown('<div class="section-container">', unsafe_allow_html=True)

# API Key handling - try to get from Streamlit secrets first
api_key = None

# Check if the API key is in Streamlit secrets
try:
    if hasattr(st, 'secrets') and len(st.secrets) > 0 and "MISTRAL_API_KEY" in st.secrets:
        api_key = st.secrets["MISTRAL_API_KEY"]
        st.markdown('''
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.2);
            border-radius: 10px;
            padding: 0.625rem 1rem;
            color: #4ade80;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
        ">
            <span>✓</span> API key loaded from secrets
        </div>
        ''', unsafe_allow_html=True)
except (FileNotFoundError, KeyError, Exception):
    pass

if not api_key:
    # 1. API Key Input with better styling if not in secrets
    st.markdown("## 🔑 API Key")
    st.markdown('<p style="color: #a1a1aa; margin-bottom: 1rem;">Enter your Mistral API key to start processing documents.</p>', unsafe_allow_html=True)
    api_key = st.text_input("Mistral API Key", type="password", placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx", label_visibility="collapsed")
    if not api_key:
        st.markdown('''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            color: #60a5fa;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        ">
            <span>ℹ️</span> Enter your API key above to continue
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add additional information at the bottom
        st.markdown("""
        <div style="margin-top: 3rem; padding: 2rem; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 16px;">
            <h2 style="margin-top: 0 !important;">🚀 How to Get Started</h2>
            <div style="color: #a1a1aa; line-height: 1.8;">
                <p style="margin: 0.75rem 0;"><span style="color: #f97316; font-weight: 600;">1.</span> Obtain a Mistral API key from <a href="https://console.mistral.ai/" target="_blank" style="color: #f97316; text-decoration: none;">console.mistral.ai</a></p>
                <p style="margin: 0.75rem 0;"><span style="color: #f97316; font-weight: 600;">2.</span> Enter your API key in the form above</p>
                <p style="margin: 0.75rem 0;"><span style="color: #f97316; font-weight: 600;">3.</span> Select your document type and upload method</p>
                <p style="margin: 0.75rem 0;"><span style="color: #f97316; font-weight: 600;">4.</span> Process your documents and download the extracted text</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Built with ♥ using <a href="https://mistral.ai" target="_blank">Mistral AI</a> · © 2024</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()

# Initialize session state variables for persistence
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = []
if "cleaned_result" not in st.session_state:
    st.session_state["cleaned_result"] = []
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = []
if "file_names" not in st.session_state:
    st.session_state["file_names"] = []

# 2. Document Type Selection with visual indicators
st.markdown("## 📄 Document Type")
st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1rem;">Select the type of document you want to process</p>', unsafe_allow_html=True)
file_type = st.radio("Select document type", ("PDF", "Image"), horizontal=True, label_visibility="collapsed")
st.markdown(f"""
<div style="margin-top: 0.75rem;">
    <span class="status-badge badge-{'pdf' if file_type == 'PDF' else 'image'}">
        {'📑' if file_type == 'PDF' else '🖼️'} {file_type} Selected
    </span>
</div>
""", unsafe_allow_html=True)

# 3. Source Selection with better organization
st.markdown("## 📦 Document Source")
st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1rem;">Choose how you want to provide your document</p>', unsafe_allow_html=True)
source_type = st.radio("Select source type", ("URL", "Local Upload"), horizontal=True, label_visibility="collapsed")
st.markdown(f"""
<div style="margin-top: 0.75rem;">
    <span class="status-badge badge-{'url' if source_type == 'URL' else 'upload'}">
        {'🔗' if source_type == 'URL' else '📁'} {source_type}
    </span>
</div>
""", unsafe_allow_html=True)

# PDF Chunk Size Configuration with better UI
if file_type == "PDF":
    with st.expander("⚙️ Advanced PDF Settings", expanded=False):
        st.markdown('<p style="color: #a1a1aa; margin-bottom: 1rem;">Configure how large PDFs are processed</p>', unsafe_allow_html=True)
        chunk_size = st.slider("Pages per chunk", 50, 200, 100, 
                              help="For PDFs with many pages, the document will be automatically split into chunks of this many pages")
        st.markdown('<p style="color: #52525b; font-size: 0.8rem; margin-top: 0.5rem;">💡 Large PDFs will be split into chunks to optimize processing</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Add text cleanup options
        st.markdown('<p style="color: #fafafa; font-weight: 500; margin-bottom: 0.75rem;">Text Cleanup Options</p>', unsafe_allow_html=True)
        cleanup_enabled = st.checkbox("Enable advanced text formatting cleanup", value=True,
                                     help="Cleans up and formats extracted text to better match the original document")
        
        if cleanup_enabled:
            cleanup_level = st.select_slider(
                "Cleanup Level",
                options=["Light", "Medium", "Aggressive"],
                value="Medium",
                help="Light: minimal changes, Medium: balanced cleanup, Aggressive: maximum formatting"
            )

# Input fields based on selection
input_url = ""
uploaded_files = []

if source_type == "URL":
    st.markdown("### 🔗 Enter Document URLs")
    input_url = st.text_area("One URL per line", 
                             placeholder="https://example.com/document.pdf\nhttps://example.com/image.jpg",
                             label_visibility="collapsed",
                             height=100)
    if file_type == "PDF":
        st.markdown('<p style="color: #52525b; font-size: 0.8rem; margin-top: 0.5rem;">📎 Supported: PDF files from public URLs</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #52525b; font-size: 0.8rem; margin-top: 0.5rem;">📎 Supported: JPG, JPEG, PNG images from public URLs</p>', unsafe_allow_html=True)
else:
    st.markdown("### 📁 Upload Documents")
    file_types = ["pdf"] if file_type == "PDF" else ["jpg", "jpeg", "png"]
    uploaded_files = st.file_uploader(f"Upload {file_type} files", 
                                      type=file_types, 
                                      accept_multiple_files=True,
                                      label_visibility="collapsed")
    st.markdown(f'<p style="color: #52525b; font-size: 0.8rem; margin-top: 0.5rem;">📎 Drag and drop your {", ".join(file_types).upper()} files here</p>', unsafe_allow_html=True)

# Process button with improved styling
st.markdown("---")
st.markdown("## 🚀 Process Documents")
st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1rem;">Click below to extract text from your documents</p>', unsafe_allow_html=True)
process_button = st.button("✨ Extract Text", use_container_width=True)

# 4. Process Button & OCR Handling
if process_button:
    if source_type == "URL" and not input_url.strip():
        st.error("⚠️ Please enter at least one valid URL.")
    elif source_type == "Local Upload" and not uploaded_files:
        st.error(f"⚠️ Please upload at least one {file_type.lower()} file.")
    else:
        with st.spinner("Connecting to Mistral AI..."):
            client = Mistral(api_key=api_key)
        
        st.session_state["ocr_result"] = []
        st.session_state["cleaned_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        
        sources = input_url.split("\n") if source_type == "URL" else uploaded_files
        
        # Create a progress bar
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        for idx, source in enumerate(sources):
            # Update progress
            progress_percentage = int((idx) / len(sources) * 100)
            progress_bar.progress(progress_percentage)
            
            # Store original filename
            if source_type == "URL":
                # For URLs, extract filename from the end of the URL
                file_name = source.strip().split("/")[-1]
                display_name = source.strip()
                # If no clear filename, use a default with index
                if not file_name or "." not in file_name:
                    file_name = f"url_document_{idx+1}"
            else:
                # For uploaded files, use the original filename
                file_name = source.name
                display_name = source.name
            
            # Store filename without extension for later use
            base_name = os.path.splitext(file_name)[0]
            st.session_state["file_names"].append(base_name)
            
            progress_text.markdown(f"Processing **{display_name}**...")
            
            if file_type == "PDF":
                if source_type == "URL":
                    document = {"type": "document_url", "document_url": source.strip()}
                    preview_src = source.strip()
                    st.session_state["preview_src"].append(preview_src)
                    
                    with st.spinner(f"Extracting text from {display_name}..."):
                        try:
                            ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                            time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                            
                            pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                            result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                            
                            # Apply text cleanup if enabled
                            if 'cleanup_enabled' in locals() and cleanup_enabled:
                                cleaned_text = clean_ocr_text(result_text)
                                st.session_state["cleaned_result"].append(cleaned_text)
                            else:
                                st.session_state["cleaned_result"].append(result_text)
                                
                        except Exception as e:
                            result_text = f"Error extracting result: {e}"
                            st.session_state["cleaned_result"].append(result_text)
                        
                        st.session_state["ocr_result"].append(result_text)
                else:
                    file_bytes = source.read()
                    preview_src = f"data:application/pdf;base64,{base64.b64encode(file_bytes).decode('utf-8')}"
                    st.session_state["preview_src"].append(preview_src)
                    
                    # Check PDF size and split if needed
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    total_pages = len(pdf_reader.pages)
                    
                    if total_pages > chunk_size:
                        st.info(f"📄 Splitting **{display_name}** ({total_pages} pages) into smaller chunks...")
                        pdf_chunks = split_pdf(file_bytes, chunk_size)
                        all_results = []
                        
                        # Create a sub-progress bar for chunks
                        chunk_progress = st.progress(0)
                        chunk_text = st.empty()
                        
                        for i, chunk in enumerate(pdf_chunks):
                            chunk_percentage = int((i) / len(pdf_chunks) * 100)
                            chunk_progress.progress(chunk_percentage)
                            chunk_text.markdown(f"Processing chunk {i+1}/{len(pdf_chunks)} (pages {i*chunk_size+1}-{min((i+1)*chunk_size, total_pages)})...")
                            
                            try:
                                encoded_pdf = base64.b64encode(chunk).decode("utf-8")
                                document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                                
                                ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                                time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                                
                                pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                                chunk_text_result = "\n\n".join(page.markdown for page in pages) or ""
                                all_results.append(chunk_text_result)
                            except Exception as e:
                                all_results.append(f"Error extracting result for chunk {i+1}: {e}")
                        
                        # Clean up chunk progress indicators
                        chunk_progress.empty()
                        chunk_text.empty()
                        
                        result_text = "\n\n".join(all_results)
                    else:
                        with st.spinner(f"Extracting text from {display_name}..."):
                            try:
                                encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
                                document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                                
                                ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                                time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                                
                                pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                                result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                            except Exception as e:
                                result_text = f"Error extracting result: {e}"
                    
                    # Apply text cleanup if enabled
                    if 'cleanup_enabled' in locals() and cleanup_enabled:
                        cleaned_text = clean_ocr_text(result_text)
                        st.session_state["cleaned_result"].append(cleaned_text)
                    else:
                        st.session_state["cleaned_result"].append(result_text)
                        
                    st.session_state["ocr_result"].append(result_text)
            else:
                if source_type == "URL":
                    document = {"type": "image_url", "image_url": source.strip()}
                    preview_src = source.strip()
                else:
                    file_bytes = source.read()
                    mime_type = source.type
                    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                    document = {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded_image}"}
                    preview_src = f"data:{mime_type};base64,{encoded_image}"
                    st.session_state["image_bytes"].append(file_bytes)
            
                with st.spinner(f"Extracting text from {display_name}..."):
                    try:
                        ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                        time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                        
                        pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                        result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                        
                        # Apply text cleanup if enabled
                        if 'cleanup_enabled' in locals() and cleanup_enabled:
                            cleaned_text = clean_ocr_text(result_text)
                            st.session_state["cleaned_result"].append(cleaned_text)
                        else:
                            st.session_state["cleaned_result"].append(result_text)
                    except Exception as e:
                        result_text = f"Error extracting result: {e}"
                        st.session_state["cleaned_result"].append(result_text)
                
                st.session_state["ocr_result"].append(result_text)
                st.session_state["preview_src"].append(preview_src)
        
        # Complete the progress
        progress_bar.progress(100)
        progress_text.markdown("✅ Processing complete!")
        time.sleep(1)
        progress_bar.empty()
        progress_text.empty()
        
        st.success("🎉 Text extraction complete! Results are shown below.")

# Close the main app container
st.markdown('</div>', unsafe_allow_html=True)

# 5. Display Preview and OCR Results if available
if st.session_state["ocr_result"]:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown("## 📋 Results")
    st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1.5rem;">Your extracted text is ready for download</p>', unsafe_allow_html=True)
    
    # Create tabs for each document
    if len(st.session_state["ocr_result"]) > 1:
        tabs = st.tabs([f"📄 {name}" for idx, name in enumerate(st.session_state["file_names"])])
    else:
        tabs = [st.container()]
    
    for idx, (result, tab) in enumerate(zip(st.session_state["ocr_result"], tabs)):
        with tab:
            # Get filename for output
            if idx < len(st.session_state["file_names"]):
                file_base_name = st.session_state["file_names"][idx]
            else:
                file_base_name = f"Document_{idx+1}"
            
            # Get the cleaned result
            cleaned_result = st.session_state["cleaned_result"][idx] if idx < len(st.session_state["cleaned_result"]) else result
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### 📄 Original Document")
                
                if file_type == "PDF":
                    with st.container():
                        pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="600" frameborder="0" style="border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);"></iframe>'
                        st.markdown(pdf_embed_html, unsafe_allow_html=True)
                else:
                    if source_type == "Local Upload" and st.session_state["image_bytes"]:
                        st.image(st.session_state["image_bytes"][idx], use_container_width=True)
                    else:
                        st.image(st.session_state["preview_src"][idx], use_container_width=True)
            
            with col2:
                st.markdown(f"### ✨ Extracted Text")
                
                # Add toggle for raw vs cleaned text
                show_raw = st.checkbox("Show raw OCR output", value=False, key=f"raw_toggle_{idx}")
                
                display_text = result if show_raw else cleaned_result
                
                # Download section with better UI
                with st.expander("💾 Download Options", expanded=True):
                    st.markdown('<p style="color: #a1a1aa; margin-bottom: 1rem; font-size: 0.9rem;">Save the extracted text in your preferred format</p>', unsafe_allow_html=True)
                    
                    def create_download_link(data, filetype, filename, button_text, icon):
                        b64 = base64.b64encode(data.encode() if isinstance(data, str) else data).decode()
                        href = f'<a href="data:{filetype};base64,{b64}" download="{filename}" class="download-btn">'
                        href += f'{icon} {button_text}</a>'
                        return href
                    
                    download_row = '<div class="download-container">'
                    
                    # JSON download
                    json_data = json.dumps({"ocr_result": display_text}, ensure_ascii=False, indent=2)
                    download_row += create_download_link(json_data, "application/json", f"{file_base_name}.json", "JSON", "📦")
                    
                    # TXT download
                    download_row += create_download_link(display_text, "text/plain", f"{file_base_name}.txt", "TXT", "📝")
                    
                    # MD download
                    download_row += create_download_link(display_text, "text/markdown", f"{file_base_name}.md", "Markdown", "📋")
                    
                    # PDF download
                    pdf_error = None
                    try:
                        # Generate PDF from markdown
                        pdf_data = create_pdf_from_markdown(display_text, file_base_name)
                        if pdf_data:
                            download_row += create_download_link(pdf_data, "application/pdf", f"{file_base_name}.pdf", "PDF", "📄")
                    except Exception as e:
                        pdf_error = str(e)
                    
                    download_row += '</div>'
                    st.markdown(download_row, unsafe_allow_html=True)
                    
                    # Show PDF error below the download buttons if there was one
                    if pdf_error:
                        st.warning(f"PDF generation error: {pdf_error}")
                
                # Text preview with scrolling
                st.markdown('<div class="text-preview">', unsafe_allow_html=True)
                st.markdown(display_text)
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a clear results button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Results", key="clear_results", use_container_width=True):
            st.session_state["ocr_result"] = []
            st.session_state["cleaned_result"] = []
            st.session_state["preview_src"] = []
            st.session_state["image_bytes"] = []
            st.session_state["file_names"] = []
            st.rerun()

# Footer section
st.markdown("""
<div class="footer">
    <p>Built with ♥ using <a href="https://mistral.ai" target="_blank">Mistral AI</a> · <a href="https://streamlit.io" target="_blank">Streamlit</a> · © 2024</p>
</div>
""", unsafe_allow_html=True)
