import streamlit as st
import os
import base64
import json
import time
import tempfile
from mistralai import Mistral
import PyPDF2
import io

# Set page configuration with a modern layout
st.set_page_config(
    layout="wide", 
    page_title="Mistral OCR App", 
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a cleaner, more modern look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1 {
        font-weight: 700;
        color: #4527A0;
        margin-bottom: 0.2rem;
    }
    
    h2, h3 {
        font-weight: 600;
        color: #5E35B1;
    }
    
    .stButton>button {
        background-color: #673AB7;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #5E35B1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .result-card {
        border-left: 4px solid #673AB7;
        background-color: #F8F9FA;
    }
    
    .stExpander {
        border: 1px solid #EEEEEE;
        border-radius: 8px;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #666;
        font-size: 0.8rem;
    }
    
    .success-msg {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .info-msg {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    
    .warning-msg {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FFC107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Modern app header with icon
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown('<div style="font-size:3.2rem; text-align:center; color:#673AB7;">📝</div>', unsafe_allow_html=True)
with col2:
    st.title("Mistral OCR App")
    st.markdown("<p style='color:#666; margin-top:-0.5rem;'>Extract text from PDFs and images with AI-powered accuracy</p>", unsafe_allow_html=True)

# Credit
st.markdown(
    "<div style='font-size:0.8rem; color:#666;'>Built by <a href='https://github.com/AIAnytime' style='color:#673AB7; text-decoration:none;'>AI Anytime</a> | "
    "Enhanced by <a href='https://github.com/Nimsalcade' style='color:#673AB7; text-decoration:none;'>Nimsalcade</a></div>", 
    unsafe_allow_html=True
)

# App description
with st.expander("ℹ️ About this app"):
    st.markdown("""
    This application uses **Mistral AI's OCR technology** to extract text from documents and images.
    
    **Features:**
    * Process both PDFs and images
    * Upload local files or provide URLs
    * Automatic splitting of large PDFs
    * Quick download in multiple formats
    
    To use this app, enter your Mistral API key below, select your document type and source, then click 'Process'.
    """)

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

# Card-style container for API key input
st.markdown('<div class="card">', unsafe_allow_html=True)
# 1. API Key Input
api_key = st.text_input("🔑 Enter your Mistral API Key", type="password", help="Your API key is kept private and not stored")
st.markdown('</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="info-msg">⚠️ Please enter your API key to continue.</div>', unsafe_allow_html=True)
    # Add a sample image to make the empty state more appealing
    st.image("https://i.imgur.com/ymjJLri.png", caption="Sample OCR Processing", use_column_width=True)
    st.stop()

# Initialize session state variables for persistence
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = []
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = []
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = []
if "file_names" not in st.session_state:
    st.session_state["file_names"] = []

# Input options in a card container
st.markdown('<div class="card">', unsafe_allow_html=True)

# Two columns for input options
col1, col2 = st.columns(2)

with col1:
    # 2. Choose file type: PDF or Image
    file_type = st.radio("📄 Select document type", ("PDF", "Image"), horizontal=True)

with col2:
    # 3. Select source type: URL or Local Upload
    source_type = st.radio("📂 Select source", ("Upload File", "Enter URL"), horizontal=True)

# PDF Chunk Size Configuration
if file_type == "PDF":
    with st.expander("⚙️ Advanced PDF Settings"):
        chunk_size = st.slider("Pages per chunk for large PDFs", 50, 200, 100, 
                              help="For PDFs with many pages, the document will be automatically split into chunks of this many pages")

input_url = ""
uploaded_files = []

# File input section
if source_type == "Enter URL":
    input_url = st.text_area("🔗 Enter one or multiple URLs (separate with new lines)", 
                            placeholder="https://example.com/document.pdf")
else:
    file_types = ["pdf"] if file_type == "PDF" else ["jpg", "jpeg", "png"]
    uploaded_files = st.file_uploader(f"📤 Upload {file_type} file(s)", 
                                    type=file_types, 
                                    accept_multiple_files=True)
    if not uploaded_files:
        st.info(f"Please upload one or more {file_type.lower()} files to process")

st.markdown('</div>', unsafe_allow_html=True)

# 4. Process Button & OCR Handling
process_button = st.button("🔍 Process Document", type="primary", use_container_width=True)

if process_button:
    if source_type == "Enter URL" and not input_url.strip():
        st.markdown('<div class="warning-msg">⚠️ Please enter at least one valid URL.</div>', unsafe_allow_html=True)
    elif source_type == "Upload File" and not uploaded_files:
        st.markdown('<div class="warning-msg">⚠️ Please upload at least one file.</div>', unsafe_allow_html=True)
    else:
        client = Mistral(api_key=api_key)
        st.session_state["ocr_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        
        sources = input_url.split("\n") if source_type == "Enter URL" else uploaded_files
        
        overall_progress = st.progress(0, "Starting processing...")
        
        for idx, source in enumerate(sources):
            # Calculate progress percentage
            progress_value = idx / len(sources)
            overall_progress.progress(progress_value, f"Processing file {idx+1} of {len(sources)}")
            
            # Store original filename
            if source_type == "Enter URL":
                # For URLs, extract filename from the end of the URL
                file_name = source.strip().split("/")[-1]
                # If no clear filename, use a default with index
                if not file_name or "." not in file_name:
                    file_name = f"url_document_{idx+1}"
            else:
                # For uploaded files, use the original filename
                file_name = source.name
            
            # Store filename without extension for later use
            base_name = os.path.splitext(file_name)[0]
            st.session_state["file_names"].append(base_name)
            
            if file_type == "PDF":
                if source_type == "Enter URL":
                    document = {"type": "document_url", "document_url": source.strip()}
                    preview_src = source.strip()
                    st.session_state["preview_src"].append(preview_src)
                    
                    with st.spinner(f"Processing {source}..."):
                        try:
                            ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                            time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                            
                            pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                            result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                        except Exception as e:
                            result_text = f"Error extracting result: {e}"
                        
                        st.session_state["ocr_result"].append(result_text)
                else:
                    file_bytes = source.read()
                    preview_src = f"data:application/pdf;base64,{base64.b64encode(file_bytes).decode('utf-8')}"
                    st.session_state["preview_src"].append(preview_src)
                    
                    # Check PDF size and split if needed
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    total_pages = len(pdf_reader.pages)
                    
                    if total_pages > chunk_size:
                        st.markdown(f'<div class="info-msg">📊 Splitting {source.name} ({total_pages} pages) into smaller chunks...</div>', unsafe_allow_html=True)
                        pdf_chunks = split_pdf(file_bytes, chunk_size)
                        all_results = []
                        
                        chunk_progress = st.progress(0, "Processing chunks...")
                        
                        for i, chunk in enumerate(pdf_chunks):
                            # Update chunk progress
                            chunk_progress_value = (i + 1) / len(pdf_chunks)
                            chunk_progress.progress(chunk_progress_value, f"Chunk {i+1}/{len(pdf_chunks)}")
                            
                            with st.spinner(f"Processing chunk {i+1}/{len(pdf_chunks)} of {source.name}..."):
                                try:
                                    encoded_pdf = base64.b64encode(chunk).decode("utf-8")
                                    document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                                    
                                    ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                                    time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                                    
                                    pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                                    chunk_text = "\n\n".join(page.markdown for page in pages) or ""
                                    all_results.append(chunk_text)
                                except Exception as e:
                                    all_results.append(f"Error extracting result for chunk {i+1}: {e}")
                        
                        result_text = "\n\n".join(all_results)
                    else:
                        with st.spinner(f"Processing {source.name}..."):
                            try:
                                encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")
                                document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                                
                                ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                                time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                                
                                pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                                result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                            except Exception as e:
                                result_text = f"Error extracting result: {e}"
                    
                    st.session_state["ocr_result"].append(result_text)
            else:
                if source_type == "Enter URL":
                    document = {"type": "image_url", "image_url": source.strip()}
                    preview_src = source.strip()
                else:
                    file_bytes = source.read()
                    mime_type = source.type
                    encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                    document = {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded_image}"}
                    preview_src = f"data:{mime_type};base64,{encoded_image}"
                    st.session_state["image_bytes"].append(file_bytes)
            
                with st.spinner(f"Processing {source if source_type == 'Enter URL' else source.name}..."):
                    try:
                        ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                        time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                        
                        pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                        result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                    except Exception as e:
                        result_text = f"Error extracting result: {e}"
                
                st.session_state["ocr_result"].append(result_text)
                st.session_state["preview_src"].append(preview_src)
        
        # Complete the progress and show success message
        overall_progress.progress(1.0, "Processing complete!")
        st.markdown('<div class="success-msg">✅ Document processing complete! Results are displayed below.</div>', unsafe_allow_html=True)

# 5. Display Preview and OCR Results if available
if st.session_state["ocr_result"]:
    for idx, result in enumerate(st.session_state["ocr_result"]):
        # Get filename for output
        if idx < len(st.session_state["file_names"]):
            file_base_name = st.session_state["file_names"][idx]
        else:
            file_base_name = f"Output_{idx+1}"
        
        st.markdown(f"### Document {idx+1}: {file_base_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📄 Document Preview")
            if file_type == "PDF":
                pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="600" frameborder="0"></iframe>'
                st.markdown(pdf_embed_html, unsafe_allow_html=True)
            else:
                if source_type == "Upload File" and len(st.session_state["image_bytes"]) > idx:
                    st.image(st.session_state["image_bytes"][idx], caption=file_base_name, use_column_width=True)
                else:
                    st.image(st.session_state["preview_src"][idx], caption=file_base_name, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="card result-card">', unsafe_allow_html=True)
            st.subheader("📋 Extracted Text")
            
            # Result tabs
            tab1, tab2 = st.tabs(["Text", "Download Options"])
            
            with tab1:
                st.markdown(f"<div style='height: 550px; overflow-y: auto; padding: 1rem;'>{result}</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### Download Results")
                
                def create_download_link(data, filetype, filename, icon, description):
                    b64 = base64.b64encode(data.encode()).decode()
                    href = f'<a href="data:{filetype};base64,{b64}" download="{filename}" style="text-decoration:none;"><div style="display:flex; align-items:center; padding:0.5rem; background-color:#F5F5F5; border-radius:5px; margin-bottom:0.5rem;"><div style="font-size:1.5rem; margin-right:0.5rem;">{icon}</div><div><strong>{filename}</strong><br><span style="font-size:0.8rem; color:#666;">{description}</span></div></div></a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                json_data = json.dumps({"ocr_result": result}, ensure_ascii=False, indent=2)
                create_download_link(json_data, "application/json", f"{file_base_name}.json", "📊", "Structured JSON format")
                create_download_link(result, "text/plain", f"{file_base_name}.txt", "📝", "Plain text format")
                create_download_link(result, "text/markdown", f"{file_base_name}.md", "📄", "Markdown format")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Powered by <a href="https://docs.mistralai.com/" target="_blank" style="color:#673AB7; text-decoration:none;">Mistral AI OCR</a> | 
    <a href="https://github.com/Nimsalcade/MistralAI-OCR" target="_blank" style="color:#673AB7; text-decoration:none;">GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
