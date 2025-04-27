import streamlit as st
import os
import base64
import json
import time
import tempfile
from mistralai import Mistral
import PyPDF2
import io

st.set_page_config(layout="wide", page_title="Mistral OCR App", page_icon="🖥️")
st.title("Mistral OCR App")
st.markdown("<h3 style color: white;'>Built by <a href='https://github.com/AIAnytime'>AI Anytime with ❤️ </a></h3>", unsafe_allow_html=True)
with st.expander("Expand Me"):
    st.markdown("""
    This application allows you to extract information from pdf/image based on Mistral OCR. Built by AI Anytime.
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

# 1. API Key Input
api_key = st.text_input("Enter your Mistral API Key", type="password")
if not api_key:
    st.info("Please enter your API key to continue.")
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

# 2. Choose file type: PDF or Image
file_type = st.radio("Select file type", ("PDF", "Image"))

# 3. Select source type: URL or Local Upload
source_type = st.radio("Select source type", ("URL", "Local Upload"))

# PDF Chunk Size Configuration
if file_type == "PDF":
    with st.expander("Advanced PDF Settings"):
        chunk_size = st.slider("Pages per chunk for large PDFs", 50, 200, 100, 
                              help="For PDFs with many pages, the document will be automatically split into chunks of this many pages")

input_url = ""
uploaded_files = []

if source_type == "URL":
    input_url = st.text_area("Enter one or multiple URLs (separate with new lines)")
else:
    uploaded_files = st.file_uploader("Upload one or more files", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)

# 4. Process Button & OCR Handling
if st.button("Process"):
    if source_type == "URL" and not input_url.strip():
        st.error("Please enter at least one valid URL.")
    elif source_type == "Local Upload" and not uploaded_files:
        st.error("Please upload at least one file.")
    else:
        client = Mistral(api_key=api_key)
        st.session_state["ocr_result"] = []
        st.session_state["preview_src"] = []
        st.session_state["image_bytes"] = []
        st.session_state["file_names"] = []
        
        sources = input_url.split("\n") if source_type == "URL" else uploaded_files
        
        for idx, source in enumerate(sources):
            # Store original filename
            if source_type == "URL":
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
                if source_type == "URL":
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
                        st.info(f"Splitting {source.name} ({total_pages} pages) into smaller chunks...")
                        pdf_chunks = split_pdf(file_bytes, chunk_size)
                        all_results = []
                        
                        for i, chunk in enumerate(pdf_chunks):
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
            
                with st.spinner(f"Processing {source if source_type == 'URL' else source.name}..."):
                    try:
                        ocr_response = client.ocr.process(model="mistral-ocr-latest", document=document, include_image_base64=True)
                        time.sleep(1)  # wait 1 second between request to prevent rate limit exceeding
                        
                        pages = ocr_response.pages if hasattr(ocr_response, "pages") else (ocr_response if isinstance(ocr_response, list) else [])
                        result_text = "\n\n".join(page.markdown for page in pages) or "No result found."
                    except Exception as e:
                        result_text = f"Error extracting result: {e}"
                
                st.session_state["ocr_result"].append(result_text)
                st.session_state["preview_src"].append(preview_src)

# 5. Display Preview and OCR Results if available
if st.session_state["ocr_result"]:
    for idx, result in enumerate(st.session_state["ocr_result"]):
        col1, col2 = st.columns(2)
        
        # Get filename for output
        if idx < len(st.session_state["file_names"]):
            file_base_name = st.session_state["file_names"][idx]
        else:
            file_base_name = f"Output_{idx+1}"
        
        with col1:
            st.subheader(f"Input {file_base_name}")
            if file_type == "PDF":
                pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width="100%" height="800" frameborder="0"></iframe>'
                st.markdown(pdf_embed_html, unsafe_allow_html=True)
            else:
                if source_type == "Local Upload" and st.session_state["image_bytes"]:
                    st.image(st.session_state["image_bytes"][idx])
                else:
                    st.image(st.session_state["preview_src"][idx])
        
        with col2:
            st.subheader(f"Download {file_base_name} OCR results")
            
            def create_download_link(data, filetype, filename):
                b64 = base64.b64encode(data.encode()).decode()
                href = f'<a href="data:{filetype};base64,{b64}" download="{filename}">Download {filename}</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            json_data = json.dumps({"ocr_result": result}, ensure_ascii=False, indent=2)
            create_download_link(json_data, "application/json", f"{file_base_name}.json") # json output
            create_download_link(result, "text/plain", f"{file_base_name}.txt") # plain text output
            create_download_link(result, "text/markdown", f"{file_base_name}.md") # markdown output

            # To preview results
            st.write(st.session_state["ocr_result"])
