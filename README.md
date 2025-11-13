# AI Tax Return Agent - Prototype

An end-to-end **AI-powered tax preparation prototype** that automates the ingestion of U.S. tax documents (W-2, 1099-INT, 1099-NEC), extracts key fields using GPT, computes federal tax liability for the 2024 tax year, and generates a simplified **Form 1040 PDF**. This project demonstrates how LLMs, OCR, and deterministic tax logic can streamline accounting workflows.

The prototype is currently deployed and accessible here: https://ai-tax-agent-g5ad.onrender.com

## Features
- **Upload multiple tax PDFs**
- **Hybrid extraction pipeline**
  - Extract text using `pdfplumber`
  - Fallback to **GPT-4o** for scanned or image-based PDFs
- **GPT-powered structured JSON parsing**
- **Accurate 2024 tax calculation logic**
- **Form 1040 PDF generation using ReportLab**
- **Inline PDF preview + download button**
- Handles missing values, malformed PDFs, and mixed forms gracefully.

## Tech Stack
- **Python, Flask**
- **OpenAI**
- **pdfplumber, PyMuPDF (fitz), Pillow**
- **ReportLab**
- **Bootstrap 5**

## 📥 Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
### 2. Set your OpenAI API key
Create a .env file:
```bash
OPENAI_API_KEY=your_key_here
```
### 3. Run the Flask server
```bash
python app.py
```
### 4. Open in browser
```bash
http://127.0.0.1:5000
```
    
## Disclaimer
This prototype is for demonstration purposes only. It is not an official tax filing tool, and the calculations are simplified.

