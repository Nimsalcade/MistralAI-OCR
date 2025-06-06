# Mistral OCR App

The **Mistral OCR App** is a Streamlit-based web application that leverages the [Mistral OCR API](https://docs.mistralai.com/) to extract text from both PDF documents and images. Users can either provide a URL or upload a local file. The app displays the original document (or image) in a preview alongside the extracted OCR results and offers a seamless download option—all without refreshing the page.

### 🚀 Try the Mistral OCR App Live!  

🔗 **Live Demo:** [Mistral OCR App](https://nimsalcade-mistralai-ocr.streamlit.app/)  

Experience the power of **Mistral OCR** in action! Upload PDFs or images and extract text seamlessly with this interactive **Streamlit-based OCR app**.  

![Mistral OCR App Demo](demo.png)


## Features

- **Dual File Support:** Process both PDFs and images.
- **Multiple Input Methods:** Choose between URL input or local file uploads.
- **Real-Time Preview:** Display the original file (via an iframe for PDFs or using `st.image` for images).
- **OCR Extraction:** Get OCR results presented in a clean, two-column layout.
- **Downloadable Results:** Download the OCR output in multiple formats (JSON, TXT, Markdown).
- **Interactive Interface:** Built with Streamlit for a smooth and interactive user experience.
- **Large PDF Support:** Automatically splits and processes large PDFs (300+ pages) in smaller chunks.
- **Original Filename Preservation:** Download files maintain the original document names.
- **API Key Management:** Uses Streamlit secrets for secure API key storage.

## Installation

### Prerequisites

- Python 3.7 or later
- [Streamlit](https://streamlit.io/)
- [Mistralai Python Client](https://pypi.org/project/mistralai/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Nimsalcade/MistralAI-OCR.git
   cd MistralAI-OCR
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**

   On macOS/Linux:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Required Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Your Mistral API Key:**

   For local development:
   - Enter your API key in the app when prompted

   For Streamlit Cloud deployment:
   - Add your API key to Streamlit secrets (see Deployment section)

## Usage

To run the app locally, use the following command:

```bash
streamlit run main.py
```

### How It Works

1. **API Key Entry:**  
   When you launch the app locally, you'll be prompted to enter your Mistral API key. In production, the API key is securely stored in Streamlit secrets.

2. **File Type & Source Selection:**  
   Choose whether you want to process a **PDF** or an **Image** and select the source type—either via a URL or by uploading a file.

3. **Advanced PDF Settings (for large documents):**  
   For PDFs, you can configure the chunk size for splitting large documents. This helps process PDFs with hundreds of pages.

4. **Processing:**  
   Click the **Extract Text** button to send the document to the Mistral OCR API. The app then:
   - Displays a preview of the document in the left column.
   - Shows the extracted OCR results in the right column.
   - Provides download links for the OCR output in multiple formats.

5. **Download:**  
   Click the download link to save the OCR result as JSON, TXT, or MD file. Downloads preserve the original filename.

## Deployment to Streamlit Cloud

This app is designed to be deployed on Streamlit Cloud:

1. **Fork or Clone the Repository:**
   - Fork this repository to your GitHub account

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch (main), and set the main file path to "main.py"
   - Click "Deploy!"

3. **Add Your API Key to Streamlit Secrets:**
   - After deployment, go to your app settings
   - Navigate to "Secrets"
   - Add the following content:
     ```
     MISTRAL_API_KEY = "your-actual-mistral-api-key"
     ```
   - Click "Save"

The app will automatically use the API key from secrets without prompting users to enter it.

## Code Overview

- **main.py:**  
  The main Streamlit application file that contains the logic for:
  - User input handling (file type, source type)
  - Document preparation (base64 encoding for local uploads)
  - PDF splitting for large documents
  - Calling the Mistral OCR API
  - Displaying the preview and OCR results
  - Providing download links with original filenames

- **README.md:**  
  This file, which provides detailed instructions and documentation for the project.

- **requirements.txt:**  
  A list of the required Python packages.

## Contributing

Contributions are welcome! If you have suggestions or find issues, please feel free to:
- Open an issue in the repository.
- Submit a pull request with improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Streamlit](https://streamlit.io/) for making interactive web app development easy.
- [Mistralai](https://github.com/mistralai) for their powerful OCR API and Python client.
- [PyPDF2](https://github.com/py-pdf/pypdf) for PDF manipulation capabilities.

## Contact

For any questions or support, please open an issue in this repository.
