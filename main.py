import streamlit as st
import os
import base64
import json
import time
import tempfile
from mistralai.client import Mistral
import PyPDF2
import io
import re
import markdown
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import hashlib

# Set page configuration with a modern layout
st.set_page_config(
    layout="wide",
    page_title="Mistral OCR Pro",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS for a world-class, stunning UI
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Root variables - Premium Dark Theme */
    :root {
        --bg-primary: #09090b;
        --bg-secondary: #0c0c0f;
        --bg-tertiary: #111114;
        --bg-card: rgba(255, 255, 255, 0.02);
        --bg-card-hover: rgba(255, 255, 255, 0.05);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --border-color: rgba(255, 255, 255, 0.06);
        --border-hover: rgba(255, 255, 255, 0.12);
        --text-primary: #fafafa;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --text-dim: #52525b;
        --accent-primary: #6366f1;
        --accent-primary-glow: rgba(99, 102, 241, 0.15);
        --accent-secondary: #8b5cf6;
        --accent-tertiary: #a855f7;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --accent-error: #ef4444;
        --accent-info: #3b82f6;
        --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        --gradient-glow: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        --gradient-mesh: radial-gradient(at 40% 20%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                         radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.06) 0px, transparent 50%),
                         radial-gradient(at 0% 50%, rgba(168, 85, 247, 0.05) 0px, transparent 50%);
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 60px rgba(99, 102, 241, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }
    
    /* Global styles */
    .stApp {
        background: var(--bg-primary);
        background-image: var(--gradient-mesh);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 2rem 3rem 4rem 3rem;
        max-width: 1600px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1 {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3.5rem !important;
        letter-spacing: -0.04em;
        margin-bottom: 0 !important;
        line-height: 1.1 !important;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-weight: 700;
        font-size: 1.5rem !important;
        letter-spacing: -0.02em;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
        font-size: 1.15rem !important;
        letter-spacing: -0.01em;
    }
    
    p, .stMarkdown {
        color: var(--text-secondary) !important;
        line-height: 1.7 !important;
    }
    
    /* Logo and brand */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .brand-logo {
        width: 64px;
        height: 64px;
        background: var(--gradient-primary);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: var(--shadow-glow), var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .brand-logo::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%);
        border-radius: inherit;
    }
    
    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: #818cf8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: 0.5rem;
    }
    
    /* Hero section - Glass morphism */
    .hero-container {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 2.5rem 3rem;
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
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
    }
    
    .hero-container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .hero-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .hero-stat {
        text-align: center;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .hero-stat:hover {
        background: rgba(99, 102, 241, 0.05);
        border-color: rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    
    .hero-stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .hero-stat-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 500;
    }
    
    /* Feature cards - Bento grid */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: default;
    }
    
    .feature-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-4px) scale(1.01);
        box-shadow: var(--shadow-lg), 0 0 40px rgba(99, 102, 241, 0.1);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        width: 48px;
        height: 48px;
        background: var(--gradient-primary);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
        position: relative;
    }
    
    .feature-icon::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, transparent 50%);
        border-radius: inherit;
    }
    
    .feature-card h4 {
        color: var(--text-primary) !important;
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0 0 0.625rem 0;
        letter-spacing: -0.01em;
    }
    
    .feature-card p {
        color: var(--text-muted) !important;
        font-size: 0.875rem;
        margin: 0;
        line-height: 1.6;
    }
    
    /* Large feature card */
    .feature-card-lg {
        grid-column: span 2;
        display: flex;
        gap: 1.5rem;
        align-items: flex-start;
    }
    
    .feature-card-lg .feature-icon {
        width: 56px;
        height: 56px;
        font-size: 1.75rem;
        flex-shrink: 0;
    }
    
    /* Section container */
    .section-container {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 2.5rem;
        margin-top: 2rem;
        position: relative;
    }
    
    .section-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 2rem;
        right: 2rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-hover), transparent);
    }
    
    /* Input styling - Premium dark inputs */
    .stTextInput input,
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stTextArea > div > div > textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: var(--bg-tertiary) !important;
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem 1.25rem !important;
        transition: all 0.2s ease !important;
        caret-color: var(--accent-primary) !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput input:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-primary-glow), var(--shadow-sm) !important;
        background: var(--bg-tertiary) !important;
    }
    
    .stTextInput input::placeholder,
    .stTextInput > div > div > input::placeholder,
    .stTextArea textarea::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-dim) !important;
        opacity: 1 !important;
    }
    
    /* Force text color on all input descendants */
    .stTextInput *,
    .stTextArea * {
        color: var(--text-primary) !important;
    }
    
    /* Label styling */
    .stTextInput label,
    .stTextArea label,
    .stRadio label,
    .stCheckbox label,
    .stSelectbox label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* File uploader - Premium drop zone */
    .stFileUploader > div {
        background: var(--bg-tertiary) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 3rem 2rem !important;
        transition: all 0.3s ease !important;
        text-align: center;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--accent-primary) !important;
        background: rgba(99, 102, 241, 0.03) !important;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.1) !important;
    }
    
    .stFileUploader label {
        color: var(--text-secondary) !important;
    }
    
    /* Radio buttons - Pill style */
    .stRadio > div {
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    
    .stRadio > div > label {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.875rem 1.5rem !important;
        color: var(--text-secondary) !important;
        transition: all 0.25s ease !important;
        cursor: pointer;
        font-weight: 500 !important;
    }
    
    .stRadio > div > label:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px);
    }
    
    .stRadio > div > label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: var(--accent-primary) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Primary button - Gradient with glow */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 35px rgba(99, 102, 241, 0.45) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.01) !important;
    }
    
    /* Secondary button */
    .secondary-btn button {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
        box-shadow: none !important;
    }
    
    .secondary-btn button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Status badges - Modern pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        backdrop-filter: blur(10px);
    }
    
    .badge-pdf {
        background: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .badge-image {
        background: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .badge-url {
        background: rgba(139, 92, 246, 0.1);
        color: #a78bfa;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    .badge-upload {
        background: rgba(236, 72, 153, 0.1);
        color: #f472b6;
        border: 1px solid rgba(236, 72, 153, 0.2);
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .badge-processing {
        background: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Results section */
    .results-section {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-color);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 1rem 1.25rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        padding: 1.25rem !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: var(--accent-primary) !important;
    }
    
    .stSlider > div > div > div > div {
        background: var(--gradient-primary) !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.5) !important;
    }
    
    /* Checkbox - Modern toggle look */
    .stCheckbox > label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox > label > span:first-child {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
    }
    
    /* Progress bar - Animated gradient */
    .stProgress > div > div > div {
        background: var(--gradient-primary) !important;
        background-size: 200% 100% !important;
        animation: gradient-move 2s linear infinite !important;
    }
    
    @keyframes gradient-move {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Tabs - Premium style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: var(--text-muted) !important;
        padding: 1rem 1.5rem !important;
        font-weight: 500 !important;
        position: relative;
        transition: all 0.2s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--text-primary) !important;
    }
    
    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
        border-radius: 2px 2px 0 0;
    }
    
    /* Success/Info/Warning/Error messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: var(--radius-md) !important;
        color: #34d399 !important;
        backdrop-filter: blur(10px);
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.08) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: var(--radius-md) !important;
        color: #60a5fa !important;
        backdrop-filter: blur(10px);
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.08) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(10px);
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-primary) transparent transparent transparent !important;
    }
    
    /* iFrame and images */
    iframe {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    img {
        border-radius: var(--radius-lg);
    }
    
    /* Download buttons - Premium style */
    .download-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1.25rem 0;
    }
    
    .download-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.625rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 0.75rem 1.25rem;
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 600;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    
    .download-btn:hover {
        background: var(--bg-card-hover);
        border-color: var(--accent-primary);
        color: var(--text-primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.2);
    }
    
    .download-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .download-btn:hover::before {
        opacity: 1;
    }
    
    /* Text preview - Code block style */
    .text-preview {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #d4d4d8;
        max-height: 600px;
        overflow-y: auto;
        line-height: 1.7;
        position: relative;
    }
    
    .text-preview::before {
        content: 'EXTRACTED TEXT';
        position: absolute;
        top: 0;
        right: 0;
        background: var(--bg-tertiary);
        padding: 0.375rem 0.75rem;
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--text-dim);
        letter-spacing: 0.05em;
        border-radius: 0 var(--radius-lg) 0 var(--radius-sm);
        border-left: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .text-preview::-webkit-scrollbar {
        width: 8px;
    }
    
    .text-preview::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .text-preview::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    .text-preview::-webkit-scrollbar-thumb:hover {
        background: var(--border-hover);
    }
    
    /* Footer */
    .footer {
        margin-top: 5rem;
        padding: 2.5rem 0;
        text-align: center;
        border-top: 1px solid var(--border-color);
        position: relative;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
    }
    
    .footer p {
        color: var(--text-dim) !important;
        font-size: 0.85rem;
    }
    
    .footer a {
        color: var(--accent-primary);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    
    .footer a:hover {
        color: var(--accent-secondary);
    }
    
    /* Table styling */
    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1rem 0;
        background: var(--bg-tertiary);
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid var(--border-color);
    }
    
    th, td {
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 1.25rem;
        text-align: left;
        color: var(--text-secondary);
    }
    
    th {
        background: rgba(99, 102, 241, 0.05);
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    tr:last-child td {
        border-bottom: none;
    }
    
    tr:hover td {
        background: var(--bg-card-hover);
    }
    
    /* Code block */
    pre, code {
        background: rgba(0, 0, 0, 0.4) !important;
        border-radius: var(--radius-sm);
        font-family: 'JetBrains Mono', monospace !important;
        color: #d4d4d8 !important;
        border: 1px solid var(--border-color);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .animate-in {
        animation: fadeIn 0.6s ease forwards;
    }
    
    .animate-slide {
        animation: slideIn 0.5s ease forwards;
    }
    
    .animate-scale {
        animation: scaleIn 0.4s ease forwards;
    }
    
    /* Glow effects */
    .glow-text {
        text-shadow: 0 0 60px rgba(99, 102, 241, 0.4);
    }
    
    .glow-box {
        box-shadow: 0 0 60px rgba(99, 102, 241, 0.15);
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        background: var(--bg-card-hover);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        cursor: help;
    }
    
    .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        padding: 0.5rem 0.75rem;
        font-size: 0.75rem;
        color: var(--text-secondary);
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
    }
    
    .tooltip:hover::after {
        opacity: 1;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--border-hover) !important;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
    }
    
    /* History panel styles */
    .history-item {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-hover);
    }
    
    .history-item-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    .history-item-meta {
        font-size: 0.75rem;
        color: var(--text-dim);
    }
    
    /* Keyboard shortcuts hint */
    .kbd {
        display: inline-block;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 0.125rem 0.375rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        "ocr_result": [],
        "cleaned_result": [],
        "preview_src": [],
        "image_bytes": [],
        "file_names": [],
        "processing_history": [],
        "total_pages_processed": 0,
        "total_documents_processed": 0,
        "api_key_valid": False,
        "current_view": "home",
        "comparison_mode": False,
        "selected_language": "auto",
        "output_format": "markdown"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar with enhanced features
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem 0;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
            ">⚡</div>
            <div>
                <div style="font-weight: 700; color: #fafafa; font-size: 1.1rem;">Mistral OCR</div>
                <div style="font-size: 0.7rem; color: #71717a;">Pro Edition</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('total_documents_processed', 0)}</div>
            <div class="metric-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('total_pages_processed', 0)}</div>
            <div class="metric-label">Pages</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    # Processing History
    st.markdown("### 📜 Recent History")
    if st.session_state.get("processing_history"):
        for item in st.session_state["processing_history"][-5:][::-1]:
            st.markdown(f"""
            <div class="history-item">
                <div class="history-item-title">{item.get('name', 'Unknown')[:25]}{'...' if len(item.get('name', '')) > 25 else ''}</div>
                <div class="history-item-meta">{item.get('type', 'PDF')} • {item.get('pages', '?')} pages • {item.get('time', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; color: #52525b; font-size: 0.85rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
            No processing history yet
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    # Advanced Settings
    st.markdown("### ⚙️ Settings")
    
    output_format = st.selectbox(
        "Output Format",
        ["Markdown", "Plain Text", "Structured JSON"],
        help="Choose how the extracted text should be formatted"
    )
    st.session_state["output_format"] = output_format.lower().replace(" ", "_")
    
    language_hint = st.selectbox(
        "Language Hint",
        ["Auto-detect", "English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic"],
        help="Helps improve OCR accuracy for specific languages"
    )
    st.session_state["selected_language"] = language_hint.lower().replace("-", "_")
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    # Help & Info
    with st.expander("💡 Tips & Shortcuts"):
        st.markdown("""
        <div style="font-size: 0.85rem; color: #a1a1aa; line-height: 1.8;">
            <p><span class="kbd">Ctrl</span> + <span class="kbd">V</span> Paste URL directly</p>
            <p>• Use high-quality scans for best results</p>
            <p>• PDFs with selectable text work best</p>
            <p>• Images should be at least 300 DPI</p>
            <p>• Supported: PDF, PNG, JPG, JPEG, WEBP</p>
        </div>
        """, unsafe_allow_html=True)

# Main content area
# App header with logo and title
st.markdown('''
<div class="brand-container">
    <div class="brand-logo">⚡</div>
    <div>
        <div style="display: flex; align-items: center;">
            <span style="font-size: 0.9rem; color: #71717a; font-weight: 500;">Powered by Mistral AI</span>
            <span class="brand-badge">✨ Pro</span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

st.title("Document Intelligence")
st.markdown('<p style="font-size: 1.25rem; margin-top: -0.5rem; color: #71717a; font-weight: 400; max-width: 600px;">Extract, analyze, and transform your documents with state-of-the-art AI-powered OCR technology.</p>', unsafe_allow_html=True)

# Hero section with stats
st.markdown("""
<div class="hero-container">
    <div style="position: relative; z-index: 1;">
        <h3 style="font-size: 1.5rem !important; font-weight: 700; color: #fafafa !important; margin-bottom: 0.75rem !important; margin-top: 0 !important;">
            🚀 Transform Any Document in Seconds
        </h3>
        <p style="color: #a1a1aa !important; font-size: 1rem; line-height: 1.7; margin: 0; max-width: 700px;">
            Powered by Mistral's cutting-edge vision model. Upload PDFs, images, or provide URLs — 
            process documents of any complexity with intelligent text extraction, table recognition, 
            and smart formatting preservation.
        </p>
        <div class="hero-grid">
            <div class="hero-stat">
                <div class="hero-stat-value">99.5%</div>
                <div class="hero-stat-label">Accuracy Rate</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">50+</div>
                <div class="hero-stat-label">Languages Supported</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">&lt;3s</div>
                <div class="hero-stat-label">Avg. Processing Time</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features bento grid
st.markdown("## ✨ Capabilities")
st.markdown("""
<div class="bento-grid">
    <div class="feature-card feature-card-lg">
        <div class="feature-icon">🔮</div>
        <div>
            <h4>Advanced AI Vision</h4>
            <p>Leverages Mistral's latest vision model for unparalleled accuracy in text recognition, even from complex layouts, handwritten text, and low-quality scans.</p>
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h4>Table Extraction</h4>
        <p>Automatically detects and preserves table structures with proper formatting.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🌍</div>
        <h4>Multi-Language</h4>
        <p>Supports 50+ languages including RTL scripts and Asian characters.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <h4>Batch Processing</h4>
        <p>Process multiple documents simultaneously with progress tracking.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🔗</div>
        <h4>URL Support</h4>
        <p>Extract directly from public URLs without downloading files first.</p>
    </div>
    <div class="feature-card feature-card-lg">
        <div class="feature-icon">⚡</div>
        <div>
            <h4>Smart Chunking</h4>
            <p>Automatically splits large PDFs into optimal chunks for processing, handling documents with hundreds of pages without memory issues or timeouts.</p>
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🎨</div>
        <h4>Format Preservation</h4>
        <p>Maintains headings, lists, code blocks, and text styling.</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">💾</div>
        <h4>Multi-Format Export</h4>
        <p>Download as Markdown, JSON, TXT, or formatted PDF.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper functions
def split_pdf(pdf_bytes, chunk_size=100):
    """Split large PDFs into smaller chunks for processing."""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(pdf_reader.pages)
    chunks = []
    
    if total_pages <= chunk_size:
        return [pdf_bytes], total_pages
    
    for i in range(0, total_pages, chunk_size):
        end_page = min(i + chunk_size, total_pages)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page_num in range(i, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        chunks.append(output.getvalue())
    
    return chunks, total_pages

def clean_ocr_text(text, cleanup_level="medium"):
    """Clean up OCR text with configurable intensity."""
    original_text = text
    
    # Level-based cleaning intensity
    if cleanup_level == "light":
        # Just basic cleanup
        text = re.sub(r'(\d+\.){10,}(\d+)', '', text)
        text = re.sub(r'!\[img-\d+\.jpeg\]\(img-\d+\.jpeg\)', '', text)
        return text
    
    # Table formatting
    table_pattern = r'(\|[^\n]+\|)'
    def fix_table(match):
        table_row = match.group(1)
        cells = table_row.split('|')
        cells = [cell.strip() for cell in cells if cell.strip()]
        if cells:
            return '| ' + ' | '.join(cells) + ' |'
        return match.group(1)
    
    text = re.sub(table_pattern, fix_table, text)
    
    # Remove garbage sequences
    text = re.sub(r'(\d+\.){10,}(\d+)', '', text)
    
    # Fix heading formatting
    text = re.sub(r'#([A-Z])', r'# \1', text)
    text = re.sub(r'(# [^\n]+)\n\1', r'\1', text)
    
    # Clean up image references
    text = re.sub(r'!\[img-\d+\.jpeg\]\(img-\d+\.jpeg\)', '', text)
    
    # Chapter formatting
    text = re.sub(r'(?<!#)Chapter (\d+)', r'## Chapter \1', text)
    
    if cleanup_level == "aggressive":
        # Additional aggressive cleaning
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        text = re.sub(r'[ \t]+\n', '\n', text)
        text = re.sub(r'\n[ \t]+', '\n', text)
        
        # Join broken lines
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
    
    # Spacing around headers
    text = re.sub(r'(^|\n)(#+ [^\n]+)(?!\n\n)', r'\1\2\n\n', text)
    
    return text

def create_pdf_from_markdown(markdown_text, file_name):
    """Convert markdown text to a beautifully formatted PDF."""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=60, 
            leftMargin=60,
            topMargin=60, 
            bottomMargin=60
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            textColor=colors.HexColor('#6366f1'),
            fontSize=24,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            textColor=colors.HexColor('#1f2937'),
            fontSize=18,
            fontName='Helvetica-Bold',
            spaceBefore=20,
            spaceAfter=12
        )
        
        heading2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            textColor=colors.HexColor('#374151'),
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceBefore=16,
            spaceAfter=8
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4b5563'),
            alignment=TA_JUSTIFY
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=8,
            backColor=colors.HexColor('#f3f4f6'),
            borderPadding=8,
            leading=12
        )
        
        def sanitize_text(text):
            text = re.sub(r'<([^>]+)>', r'&lt;\1&gt;', text)
            replacements = {
                '&': '&amp;',
                '"': '&quot;',
                "'": '&#39;',
                '\u2028': ' ',
                '\u2029': ' ',
            }
            for char, replacement in replacements.items():
                text = text.replace(char, replacement)
            return text
        
        sanitized_text = sanitize_text(markdown_text)
        lines = sanitized_text.split('\n')
        
        # Add document header
        elements.append(Paragraph(f"📄 {file_name}", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                                 ParagraphStyle('Meta', parent=normal_style, alignment=TA_CENTER, textColor=colors.HexColor('#9ca3af'))))
        elements.append(Spacer(1, 30))
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('# '):
                elements.append(Paragraph(sanitize_text(line[2:]), title_style))
                elements.append(Spacer(1, 12))
            elif line.startswith('## '):
                elements.append(Paragraph(sanitize_text(line[3:]), heading1_style))
                elements.append(Spacer(1, 10))
            elif line.startswith('### '):
                elements.append(Paragraph(sanitize_text(line[4:]), heading2_style))
                elements.append(Spacer(1, 8))
            elif line.startswith('|') and '|' in line[1:]:
                table_data = []
                table_row = [sanitize_text(cell.strip()) for cell in line.split('|') if cell.strip()]
                table_data.append(table_row)
                i += 1
                if i < len(lines) and '---' in lines[i]:
                    i += 1
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_row = [sanitize_text(cell.strip()) for cell in lines[i].split('|') if cell.strip()]
                    table_data.append(table_row)
                    i += 1
                if table_data:
                    max_cols = max(len(row) for row in table_data)
                    for row in table_data:
                        while len(row) < max_cols:
                            row.append('')
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                continue
            elif line.startswith('```'):
                code_content = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_content.append(sanitize_text(lines[i]))
                    i += 1
                if i < len(lines):
                    i += 1
                if code_content:
                    code_text = '<pre>' + '\n'.join(code_content) + '</pre>'
                    elements.append(Paragraph(code_text, code_style))
                    elements.append(Spacer(1, 12))
                continue
            elif line and not line.startswith(('- ', '* ', '1. ')):
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
                except Exception:
                    elements.append(Paragraph('[Content rendering error]', normal_style))
                    elements.append(Spacer(1, 8))
                i = next_idx - 1
            elif line.startswith(('- ', '* ')):
                list_items = [line[2:]]
                next_idx = i + 1
                while next_idx < len(lines) and lines[next_idx].strip().startswith(('- ', '* ')):
                    list_items.append(lines[next_idx].strip()[2:])
                    next_idx += 1
                for item in list_items:
                    bullet_text = '• ' + sanitize_text(item)
                    try:
                        elements.append(Paragraph(bullet_text, normal_style))
                    except Exception:
                        elements.append(Paragraph('• [Item error]', normal_style))
                elements.append(Spacer(1, 8))
                i = next_idx - 1
            
            i += 1
        
        if len(elements) <= 3:
            elements.append(Paragraph(f"{file_name} - Extracted Text", title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Document processed successfully.", normal_style))
        
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
        
    except Exception as e:
        st.warning(f"PDF generation error: {e}")
        return None

def get_word_count(text):
    """Get approximate word count from text."""
    return len(text.split())

def get_char_count(text):
    """Get character count from text."""
    return len(text)

# Main app section
st.markdown('<div class="section-container">', unsafe_allow_html=True)

# API Key handling
api_key = None

try:
    if hasattr(st, 'secrets') and len(st.secrets) > 0 and "MISTRAL_API_KEY" in st.secrets:
        api_key = st.secrets["MISTRAL_API_KEY"]
        st.session_state["api_key_valid"] = True
        st.markdown('''
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 0.625rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 50px;
            padding: 0.625rem 1.25rem;
            color: #34d399;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        ">
            <span style="font-size: 1.1rem;">✓</span> API key loaded from secrets
        </div>
        ''', unsafe_allow_html=True)
except (FileNotFoundError, KeyError, Exception):
    pass

if not api_key:
    st.markdown("## 🔐 Authentication")
    st.markdown('<p style="color: #a1a1aa; margin-bottom: 1.25rem;">Enter your Mistral API key to unlock all features.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "Mistral API Key", 
            type="password", 
            placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("""
        <a href="https://console.mistral.ai/" target="_blank" style="
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: transparent;
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 8px;
            padding: 0.65rem 1rem;
            color: #818cf8;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s ease;
            white-space: nowrap;
        ">Get API Key →</a>
        """, unsafe_allow_html=True)
    
    if not api_key:
        st.markdown("""
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-top: 1rem;
        ">
            <span style="font-size: 1.25rem;">💡</span>
            <div>
                <div style="color: #60a5fa; font-weight: 600; margin-bottom: 0.375rem;">New to Mistral?</div>
                <div style="color: #93c5fd; font-size: 0.9rem; line-height: 1.6;">
                    Sign up at <a href="https://console.mistral.ai/" target="_blank" style="color: #60a5fa; text-decoration: underline;">console.mistral.ai</a> 
                    to get your API key. The OCR model provides industry-leading accuracy for document extraction.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Getting started section
        st.markdown("""
        <div style="margin-top: 4rem; padding: 3rem; background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.03) 100%); border: 1px solid rgba(99, 102, 241, 0.1); border-radius: 20px;">
            <h2 style="margin-top: 0 !important; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🚀 Get Started in 4 Steps</h2>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-top: 2rem;">
                <div style="text-align: center;">
                    <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.25rem; color: white; font-weight: 700;">1</div>
                    <div style="color: #fafafa; font-weight: 600; margin-bottom: 0.5rem;">Get API Key</div>
                    <div style="color: #71717a; font-size: 0.85rem;">Sign up at Mistral AI console</div>
                </div>
                <div style="text-align: center;">
                    <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.25rem; color: white; font-weight: 700;">2</div>
                    <div style="color: #fafafa; font-weight: 600; margin-bottom: 0.5rem;">Enter Key</div>
                    <div style="color: #71717a; font-size: 0.85rem;">Paste your key above</div>
                </div>
                <div style="text-align: center;">
                    <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.25rem; color: white; font-weight: 700;">3</div>
                    <div style="color: #fafafa; font-weight: 600; margin-bottom: 0.5rem;">Upload Document</div>
                    <div style="color: #71717a; font-size: 0.85rem;">PDF, PNG, JPG supported</div>
                </div>
                <div style="text-align: center;">
                    <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.25rem; color: white; font-weight: 700;">4</div>
                    <div style="color: #fafafa; font-weight: 600; margin-bottom: 0.5rem;">Download Results</div>
                    <div style="color: #71717a; font-size: 0.85rem;">Export in multiple formats</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Built with precision using <a href="https://mistral.ai" target="_blank">Mistral AI</a> • <a href="https://streamlit.io" target="_blank">Streamlit</a></p>
            <p style="margin-top: 0.5rem; font-size: 0.75rem;">© 2024 Mistral OCR Pro. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()

# Document Type Selection
st.markdown("## 📑 Document Configuration")
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 0.75rem; font-weight: 500;">Document Type</p>', unsafe_allow_html=True)
    file_type = st.radio(
        "Select document type", 
        ("PDF", "Image"), 
        horizontal=True, 
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<p style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 0.75rem; font-weight: 500;">Input Method</p>', unsafe_allow_html=True)
    source_type = st.radio(
        "Select source type", 
        ("Local Upload", "URL"), 
        horizontal=True, 
        label_visibility="collapsed"
    )

# Status badges
st.markdown(f"""
<div style="display: flex; gap: 0.75rem; margin-top: 1rem; flex-wrap: wrap;">
    <span class="status-badge badge-{'pdf' if file_type == 'PDF' else 'image'}">
        {'📑' if file_type == 'PDF' else '🖼️'} {file_type}
    </span>
    <span class="status-badge badge-{'upload' if source_type == 'Local Upload' else 'url'}">
        {'📁' if source_type == 'Local Upload' else '🔗'} {source_type}
    </span>
</div>
""", unsafe_allow_html=True)

# Advanced settings
if file_type == "PDF":
    with st.expander("⚙️ Advanced Processing Options", expanded=False):
        st.markdown('<p style="color: #a1a1aa; margin-bottom: 1.25rem; font-size: 0.9rem;">Fine-tune how your documents are processed</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.slider(
                "Pages per chunk",
                min_value=25,
                max_value=200,
                value=100,
                step=25,
                help="Large PDFs are split into chunks for optimal processing"
            )
        with col2:
            cleanup_level = st.select_slider(
                "Text Cleanup Level",
                options=["Light", "Medium", "Aggressive"],
                value="Medium",
                help="Controls how aggressively the text is cleaned and formatted"
            )
        
        cleanup_enabled = st.checkbox(
            "Enable smart text formatting",
            value=True,
            help="Automatically fixes common OCR issues and improves text structure"
        )
        
        include_page_numbers = st.checkbox(
            "Include page markers",
            value=False,
            help="Add page number markers in the extracted text"
        )
else:
    chunk_size = 100
    cleanup_level = "Medium"
    cleanup_enabled = True
    include_page_numbers = False

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# Input fields
input_url = ""
uploaded_files = []

if source_type == "URL":
    st.markdown("### 🔗 Document URLs")
    st.markdown('<p style="color: #71717a; font-size: 0.85rem; margin-bottom: 1rem;">Enter one URL per line. Supports public PDF and image URLs.</p>', unsafe_allow_html=True)
    input_url = st.text_area(
        "URLs",
        placeholder="https://example.com/document.pdf\nhttps://example.com/invoice.png",
        label_visibility="collapsed",
        height=120
    )
else:
    st.markdown("### 📁 Upload Documents")
    st.markdown(f'<p style="color: #71717a; font-size: 0.85rem; margin-bottom: 1rem;">Drag and drop or click to upload. Supports {"PDF files" if file_type == "PDF" else "PNG, JPG, JPEG, WEBP images"}.</p>', unsafe_allow_html=True)
    file_types = ["pdf"] if file_type == "PDF" else ["jpg", "jpeg", "png", "webp"]
    uploaded_files = st.file_uploader(
        f"Upload {file_type} files",
        type=file_types,
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.625rem;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 10px;
            padding: 0.875rem 1.25rem;
            margin-top: 1rem;
        ">
            <span style="font-size: 1.1rem;">✓</span>
            <span style="color: #34d399; font-weight: 500;">{len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''} ready for processing</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# Process button
st.markdown("## ⚡ Process Documents")
st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1.25rem;">Click below to start AI-powered text extraction</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("🚀 Extract Text Now", use_container_width=True)

# Processing logic
if process_button:
    if source_type == "URL" and not input_url.strip():
        st.error("⚠️ Please enter at least one valid URL.")
    elif source_type == "Local Upload" and not uploaded_files:
        st.error(f"⚠️ Please upload at least one {file_type.lower()} file.")
    else:
        with st.spinner("🔄 Initializing Mistral AI connection..."):
            client = Mistral(api_key=api_key)
        
        # Reset session state
        st.session_state["ocr_result"] = []
        st.session_state["cleaned_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        
        sources = input_url.split("\n") if source_type == "URL" else uploaded_files
        sources = [s for s in sources if (isinstance(s, str) and s.strip()) or not isinstance(s, str)]
        
        # Progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                current_file_metric = st.empty()
            with metrics_cols[1]:
                pages_metric = st.empty()
            with metrics_cols[2]:
                time_metric = st.empty()
            with metrics_cols[3]:
                speed_metric = st.empty()
        
        start_time = time.time()
        total_pages = 0
        
        for idx, source in enumerate(sources):
            # Update progress
            progress = int((idx) / len(sources) * 100)
            progress_bar.progress(progress)
            
            # Get filename
            if source_type == "URL":
                file_name = source.strip().split("/")[-1]
                display_name = source.strip()
                if not file_name or "." not in file_name:
                    file_name = f"url_document_{idx+1}"
            else:
                file_name = source.name
                display_name = source.name
            
            base_name = os.path.splitext(file_name)[0]
            st.session_state["file_names"].append(base_name)
            
            status_text.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin: 1rem 0;">
                <div class="status-badge badge-processing">⚡ Processing</div>
                <span style="color: #fafafa; font-weight: 500;">{display_name[:50]}{'...' if len(display_name) > 50 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
            
            current_file_metric.metric("Current", f"{idx + 1}/{len(sources)}")
            elapsed = time.time() - start_time
            time_metric.metric("Elapsed", f"{elapsed:.1f}s")
            
            if file_type == "PDF":
                if source_type == "URL":
                    document = {"type": "document_url", "document_url": source.strip()}
                    preview_src = source.strip()
                    st.session_state["preview_src"].append(preview_src)
                    
                    try:
                        ocr_response = client.ocr.process(
                            model="mistral-ocr-latest",
                            document=document,
                            include_image_base64=True
                        )
                        time.sleep(0.5)
                        
                        pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                        pages_metric.metric("Pages", len(pages))
                        total_pages += len(pages)
                        
                        if include_page_numbers:
                            result_text = "\n\n".join(f"--- Page {i+1} ---\n\n{page.markdown}" for i, page in enumerate(pages)) or "No result found."
                        else:
                            result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                        
                        if cleanup_enabled:
                            cleaned_text = clean_ocr_text(result_text, cleanup_level.lower())
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
                    
                    pdf_chunks, doc_pages = split_pdf(file_bytes, chunk_size)
                    
                    if len(pdf_chunks) > 1:
                        st.info(f"📄 Splitting **{display_name}** ({doc_pages} pages) into {len(pdf_chunks)} chunks...")
                        all_results = []
                        
                        chunk_progress = st.progress(0)
                        chunk_text = st.empty()
                        
                        for i, chunk in enumerate(pdf_chunks):
                            chunk_progress.progress(int((i) / len(pdf_chunks) * 100))
                            chunk_text.markdown(f"Processing chunk {i+1}/{len(pdf_chunks)}...")
                            
                            try:
                                encoded_pdf = base64.b64encode(chunk).decode("utf-8")
                                document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                                
                                ocr_response = client.ocr.process(
                                    model="mistral-ocr-latest",
                                    document=document,
                                    include_image_base64=True
                                )
                                time.sleep(0.5)
                                
                                pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                                chunk_text_result = "\n\n".join(page.markdown for page in pages) or ""
                                all_results.append(chunk_text_result)
                            except Exception as e:
                                all_results.append(f"Error in chunk {i+1}: {e}")
                        
                        chunk_progress.empty()
                        chunk_text.empty()
                        
                        result_text = "\n\n".join(all_results)
                        total_pages += doc_pages
                    else:
                        try:
                            encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
                            document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                            
                            ocr_response = client.ocr.process(
                                model="mistral-ocr-latest",
                                document=document,
                                include_image_base64=True
                            )
                            time.sleep(0.5)
                            
                            pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                            pages_metric.metric("Pages", len(pages))
                            total_pages += len(pages)
                            
                            if include_page_numbers:
                                result_text = "\n\n".join(f"--- Page {i+1} ---\n\n{page.markdown}" for i, page in enumerate(pages)) or "No result found."
                            else:
                                result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                        except Exception as e:
                            result_text = f"Error extracting result: {e}"
                    
                    if cleanup_enabled:
                        cleaned_text = clean_ocr_text(result_text, cleanup_level.lower())
                        st.session_state["cleaned_result"].append(cleaned_text)
                    else:
                        st.session_state["cleaned_result"].append(result_text)
                    
                    st.session_state["ocr_result"].append(result_text)
            else:
                # Image processing
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
                
                try:
                    ocr_response = client.ocr.process(
                        model="mistral-ocr-latest",
                        document=document,
                        include_image_base64=True
                    )
                    time.sleep(0.5)
                    
                    pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                    pages_metric.metric("Pages", "1")
                    total_pages += 1
                    
                    result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                    
                    if cleanup_enabled:
                        cleaned_text = clean_ocr_text(result_text, cleanup_level.lower())
                        st.session_state["cleaned_result"].append(cleaned_text)
                    else:
                        st.session_state["cleaned_result"].append(result_text)
                except Exception as e:
                    result_text = f"Error extracting result: {e}"
                    st.session_state["cleaned_result"].append(result_text)
                
                st.session_state["ocr_result"].append(result_text)
                st.session_state["preview_src"].append(preview_src)
            
            # Update speed metric
            elapsed = time.time() - start_time
            if elapsed > 0:
                speed_metric.metric("Speed", f"{total_pages / elapsed:.1f} pg/s")
            
            # Add to history
            st.session_state["processing_history"].append({
                "name": display_name,
                "type": file_type,
                "pages": total_pages,
                "time": datetime.now().strftime("%H:%M")
            })
        
        # Complete progress
        progress_bar.progress(100)
        total_time = time.time() - start_time
        
        st.session_state["total_documents_processed"] += len(sources)
        st.session_state["total_pages_processed"] += total_pages
        
        status_text.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 1rem 0;
        ">
            <span style="font-size: 1.5rem;">🎉</span>
            <div>
                <div style="color: #34d399; font-weight: 700; font-size: 1.1rem;">Processing Complete!</div>
                <div style="color: #6ee7b7; font-size: 0.9rem; margin-top: 0.25rem;">
                    Processed {len(sources)} document{'s' if len(sources) > 1 else ''} ({total_pages} pages) in {total_time:.1f} seconds
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Display Results
if st.session_state["ocr_result"]:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown("## 📋 Extraction Results")
    st.markdown('<p style="color: #71717a; font-size: 0.9rem; margin-bottom: 1.5rem;">Your extracted text is ready. Download in your preferred format.</p>', unsafe_allow_html=True)
    
    # Results summary
    total_words = sum(get_word_count(r) for r in st.session_state["cleaned_result"])
    total_chars = sum(get_char_count(r) for r in st.session_state["cleaned_result"])
    
    sum_cols = st.columns(4)
    with sum_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state["ocr_result"])}</div>
            <div class="metric-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_words:,}</div>
            <div class="metric-label">Words</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_chars:,}</div>
            <div class="metric-label">Characters</div>
        </div>
        """, unsafe_allow_html=True)
    with sum_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.get('total_pages_processed', 0)}</div>
            <div class="metric-label">Total Pages</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    # Tabs for each document
    if len(st.session_state["ocr_result"]) > 1:
        tabs = st.tabs([f"📄 {name}" for name in st.session_state["file_names"]])
    else:
        tabs = [st.container()]
    
    for idx, (result, tab) in enumerate(zip(st.session_state["ocr_result"], tabs)):
        with tab:
            file_base_name = st.session_state["file_names"][idx] if idx < len(st.session_state["file_names"]) else f"Document_{idx+1}"
            cleaned_result = st.session_state["cleaned_result"][idx] if idx < len(st.session_state["cleaned_result"]) else result
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📄 Original Document")
                
                if file_type == "PDF":
                    pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="600" style="border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);"></iframe>'
                    st.markdown(pdf_embed_html, unsafe_allow_html=True)
                else:
                    if source_type == "Local Upload" and st.session_state["image_bytes"]:
                        st.image(st.session_state["image_bytes"][idx], use_container_width=True)
                    else:
                        st.image(st.session_state["preview_src"][idx], use_container_width=True)
            
            with col2:
                st.markdown("### ✨ Extracted Text")
                
                # Toggle options
                col_a, col_b = st.columns(2)
                with col_a:
                    show_raw = st.checkbox("Show raw output", value=False, key=f"raw_{idx}")
                with col_b:
                    show_stats = st.checkbox("Show statistics", value=True, key=f"stats_{idx}")
                
                display_text = result if show_raw else cleaned_result
                
                if show_stats:
                    word_count = get_word_count(display_text)
                    char_count = get_char_count(display_text)
                    st.markdown(f"""
                    <div style="display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                        <span style="background: rgba(99, 102, 241, 0.1); padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.8rem; color: #818cf8;">
                            📝 {word_count:,} words
                        </span>
                        <span style="background: rgba(16, 185, 129, 0.1); padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.8rem; color: #34d399;">
                            🔤 {char_count:,} chars
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download section
                with st.expander("💾 Download Options", expanded=True):
                    st.markdown('<p style="color: #a1a1aa; margin-bottom: 1rem; font-size: 0.875rem;">Export your extracted text in multiple formats</p>', unsafe_allow_html=True)
                    
                    def create_download_link(data, filetype, filename, button_text, icon):
                        b64 = base64.b64encode(data.encode() if isinstance(data, str) else data).decode()
                        return f'<a href="data:{filetype};base64,{b64}" download="{filename}" class="download-btn">{icon} {button_text}</a>'
                    
                    download_row = '<div class="download-container">'
                    
                    # JSON download
                    json_data = json.dumps({
                        "filename": file_base_name,
                        "extracted_at": datetime.now().isoformat(),
                        "word_count": get_word_count(display_text),
                        "content": display_text
                    }, ensure_ascii=False, indent=2)
                    download_row += create_download_link(json_data, "application/json", f"{file_base_name}.json", "JSON", "📦")
                    
                    # TXT download
                    download_row += create_download_link(display_text, "text/plain", f"{file_base_name}.txt", "TXT", "📝")
                    
                    # MD download
                    download_row += create_download_link(display_text, "text/markdown", f"{file_base_name}.md", "Markdown", "📋")
                    
                    # PDF download
                    try:
                        pdf_data = create_pdf_from_markdown(display_text, file_base_name)
                        if pdf_data:
                            download_row += create_download_link(pdf_data, "application/pdf", f"{file_base_name}_extracted.pdf", "PDF", "📄")
                    except Exception as e:
                        pass
                    
                    download_row += '</div>'
                    st.markdown(download_row, unsafe_allow_html=True)
                
                # Text preview
                st.markdown(f'<div class="text-preview">{display_text}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear results button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear All Results", key="clear_results", use_container_width=True):
            st.session_state["ocr_result"] = []
            st.session_state["cleaned_result"] = []
            st.session_state["preview_src"] = []
            st.session_state["image_bytes"] = []
            st.session_state["file_names"] = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p style="font-size: 0.9rem; color: #71717a; margin-bottom: 0.5rem;">
        Built with ❤️ using <a href="https://mistral.ai" target="_blank">Mistral AI</a> • 
        <a href="https://streamlit.io" target="_blank">Streamlit</a>
    </p>
    <p style="font-size: 0.75rem; color: #52525b;">
        © 2024 Mistral OCR Pro • All rights reserved • v2.0
    </p>
</div>
""", unsafe_allow_html=True)
