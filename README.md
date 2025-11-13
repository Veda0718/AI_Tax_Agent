# AI Tax Return Agent — Prototype

An end-to-end **AI-powered tax preparation prototype** that automates the ingestion of U.S. tax documents (W-2, 1099-INT, 1099-NEC), extracts key fields using GPT, computes federal tax liability for the 2024 tax year, and generates a simplified **Form 1040 PDF**.  
This project demonstrates how LLMs, OCR, and deterministic tax logic can streamline accounting workflows.

---

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

---

## Tech Stack
- **Python, Flask**
- **OpenAI**
- **pdfplumber, PyMuPDF (fitz), Pillow**
- **ReportLab**
- **Bootstrap 5**

---

## 📥 Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

