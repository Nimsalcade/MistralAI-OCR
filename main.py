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
    page_title="Mistral OCR",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more appealing UI
st.markdown("""
<style>
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #4527A0;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #5E35B1;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #673AB7;
        font-weight: 500;
    }
    
    /* Cards for features */
    .feature-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #5E35B1;
    }
    
    .feature-card h4 {
        color: #4527A0;
        margin-top: 0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 6px;
    }
    
    .stFileUploader > div {
        border-radius: 6px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #5E35B1;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #4527A0;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(94, 53, 177, 0.25);
    }
    
    /* Results section */
    .results-section {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E0E0E0;
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        text-align: center;
        border-top: 1px solid #E0E0E0;
        color: #9E9E9E;
        font-size: 0.8rem;
    }
    
    /* Custom expander styling */
    .custom-expander {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-pdf {
        background-color: #E3F2FD;
        color: #1565C0;
    }
    
    .badge-image {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    
    /* Make iframe and images corners rounded */
    iframe, img {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# App header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;">'
                '<span style="font-size: 3.5rem;">📝</span></div>', unsafe_allow_html=True)
with col2:
    st.title("Mistral OCR")
    st.markdown('<p style="font-size: 1.2rem; margin-top: -0.8rem; color: #5E35B1;">Extract text from PDFs and images with powerful AI</p>', unsafe_allow_html=True)

# App description card
st.markdown("""
<div class="feature-card" style="background-color: #EDE7F6; margin-bottom: 2rem;">
    <h3 style="margin-top: 0;">Transform Documents into Text in Seconds</h3>
    <p>
        Mistral OCR leverages advanced AI to extract text from PDFs and images with high accuracy. 
        Upload files directly or provide URLs, then download the extracted text in multiple formats.
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
            <h4>PDF & Image Support</h4>
            <p>Extract text from both PDFs and images with a single tool.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>URL & File Upload</h4>
            <p>Process documents from URLs or upload files directly from your device.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>Large PDF Processing</h4>
            <p>Automatically splits and processes large PDFs with hundreds of pages.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>Multiple Export Formats</h4>
            <p>Download results as JSON, TXT, or Markdown files.</p>
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

# Main app section with card-like appearance
st.markdown('<div style="background-color: #F5F5F5; padding: 2rem; border-radius: 12px; margin-top: 2rem;">', unsafe_allow_html=True)

# 1. API Key Input with better styling
st.markdown("## 🔑 API Key")
st.markdown("Enter your Mistral API key to start processing documents.")
api_key = st.text_input("Mistral API Key", type="password", placeholder="Enter your API key here")
if not api_key:
    st.info("👆 Please enter your API key above to continue.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add additional information at the bottom
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h2>How to Get Started</h2>
        <ol>
            <li>Obtain a Mistral API key from <a href="https://console.mistral.ai/" target="_blank">console.mistral.ai</a></li>
            <li>Enter your API key in the form above</li>
            <li>Select your document type and upload method</li>
            <li>Process your documents and download the extracted text</li>
        </ol>
    </div>
    
    <div class="footer">
        <p>© 2024 Mistral OCR | Powered by Mistral AI</p>
    </div>
    """, unsafe_allow_html=True)
    
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

# 2. Document Type Selection with visual indicators
st.markdown("## 📄 Document Type")
file_type_col1, file_type_col2 = st.columns(2)
with file_type_col1:
    file_type = st.radio("Select document type", ("PDF", "Image"))
    st.markdown(f"""
    <div style="margin-top: 0.5rem;">
        <span class="status-badge badge-{'pdf' if file_type == 'PDF' else 'image'}">
            {file_type} Selected
        </span>
    </div>
    """, unsafe_allow_html=True)

# 3. Source Selection with better organization
st.markdown("## 📦 Document Source")
source_type_col1, source_type_col2 = st.columns(2)
with source_type_col1:
    source_type = st.radio("Select source type", ("URL", "Local Upload"))
    st.markdown(f"""
    <div style="margin-top: 0.5rem;">
        <span class="status-badge" style="background-color: #EDE7F6; color: #5E35B1;">
            {source_type}
        </span>
    </div>
    """, unsafe_allow_html=True)

# PDF Chunk Size Configuration with better UI
if file_type == "PDF":
    with st.expander("⚙️ Advanced PDF Settings"):
        st.markdown("Configure how large PDFs are processed:")
        chunk_size = st.slider("Pages per chunk", 50, 200, 100, 
                              help="For PDFs with many pages, the document will be automatically split into chunks of this many pages")
        st.caption("Large PDFs will be split into chunks to optimize processing.")

# Input fields based on selection
input_url = ""
uploaded_files = []

if source_type == "URL":
    st.markdown("### Enter Document URLs")
    input_url = st.text_area("One URL per line", 
                             placeholder="https://example.com/document.pdf\nhttps://example.com/image.jpg")
    if file_type == "PDF":
        st.caption("Supported formats: PDF files from public URLs")
    else:
        st.caption("Supported formats: JPG, JPEG, PNG images from public URLs")
else:
    st.markdown("### Upload Documents")
    file_types = ["pdf"] if file_type == "PDF" else ["jpg", "jpeg", "png"]
    uploaded_files = st.file_uploader(f"Upload {file_type} files", 
                                      type=file_types, 
                                      accept_multiple_files=True)
    st.caption(f"Drag and drop your {', '.join(file_types).upper()} files here")

# Process button with improved styling
st.markdown("## 🚀 Process Documents")
process_button = st.button("Extract Text", use_container_width=True)

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
                    except Exception as e:
                        result_text = f"Error extracting result: {e}"
                
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
    
    # Create tabs for each document
    if len(st.session_state["ocr_result"]) > 1:
        tabs = st.tabs([f"Document {idx+1}: {name}" for idx, name in enumerate(st.session_state["file_names"])])
    else:
        tabs = [st.container()]
    
    for idx, (result, tab) in enumerate(zip(st.session_state["ocr_result"], tabs)):
        with tab:
            # Get filename for output
            if idx < len(st.session_state["file_names"]):
                file_base_name = st.session_state["file_names"][idx]
            else:
                file_base_name = f"Document_{idx+1}"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### Original Document")
                
                if file_type == "PDF":
                    with st.container():
                        pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="600" frameborder="0" style="border-radius: 8px; border: 1px solid #E0E0E0;"></iframe>'
                        st.markdown(pdf_embed_html, unsafe_allow_html=True)
                else:
                    if source_type == "Local Upload" and st.session_state["image_bytes"]:
                        st.image(st.session_state["image_bytes"][idx], use_column_width=True)
                    else:
                        st.image(st.session_state["preview_src"][idx], use_column_width=True)
            
            with col2:
                st.markdown(f"### Extracted Text")
                
                # Download section with better UI
                with st.expander("💾 Download Options", expanded=True):
                    st.markdown("Save the extracted text in your preferred format:")
                    
                    def create_download_link(data, filetype, filename, button_text):
                        b64 = base64.b64encode(data.encode()).decode()
                        href = f'<a href="data:{filetype};base64,{b64}" download="{filename}" style="text-decoration: none;">'
                        href += f'<div style="background-color: #F3F4F6; border-radius: 6px; padding: 0.5rem 1rem; display: inline-block; margin-right: 1rem; border: 1px solid #E0E0E0;">'
                        href += f'<span style="color: #5E35B1; font-weight: 500;">{button_text}</span></div></a>'
                        return href
                    
                    download_row = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">'
                    
                    # JSON download
                    json_data = json.dumps({"ocr_result": result}, ensure_ascii=False, indent=2)
                    download_row += create_download_link(json_data, "application/json", f"{file_base_name}.json", "JSON")
                    
                    # TXT download
                    download_row += create_download_link(result, "text/plain", f"{file_base_name}.txt", "TXT")
                    
                    # MD download
                    download_row += create_download_link(result, "text/markdown", f"{file_base_name}.md", "Markdown")
                    
                    download_row += '</div>'
                    st.markdown(download_row, unsafe_allow_html=True)
                
                # Text preview with scrolling
                st.markdown('<div style="height: 480px; overflow-y: auto; padding: 1rem; border-radius: 8px; border: 1px solid #E0E0E0; background-color: #FAFAFA; font-family: monospace;">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add a clear results button
    if st.button("Clear Results", key="clear_results"):
        st.session_state["ocr_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        st.experimental_rerun()

# Footer section
st.markdown("""
<div class="footer">
    <p>© 2024 Mistral OCR | Powered by Mistral AI</p>
</div>
""", unsafe_allow_html=True)
