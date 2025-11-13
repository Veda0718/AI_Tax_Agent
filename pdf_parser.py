"""
File: pdf_parser.py
Description:
    Extracts and interprets key financial fields from uploaded tax
    documents (W-2, 1099-INT, 1099-NEC) using GPT-4o for both text
    extraction and parsing. This version removes the dependency on
    Tesseract OCR by leveraging GPT's multimodal vision capabilities.

Key Responsibilities:
    - Extract text directly from digital PDFs using pdfplumber.
    - If text extraction fails, use GPT-4o to read scanned pages.
    - Parse document semantics using GPT-4o to return structured JSON.
    - Support multiple documents and unify results.

Output JSON Structure:
    {
      "documents": [
        {
          "file_name": "w2_form.pdf",
          "form_type": "W-2",
          "payer": "ACME Corp",
          "wages": 52300.50,
          "federal_income_tax_withheld": 4300.75
        },
        {
          "file_name": "1099int_form.pdf",
          "form_type": "1099-INT",
          "payer": "Bank of America",
          "interest_income": 126.43
        }
      ]
    }

Dependencies:
    pdfplumber, fitz (PyMuPDF), Pillow, openai, langchain_openai, dotenv

Author: Veda Sahaja Bandi
"""

import os, re, json, pdfplumber, fitz, base64
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv, dotenv_values
load_dotenv(override=True)

# Load environment variables
# load_dotenv()
print("Has OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))


# Initialize OpenAI clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# --------------------------------------------------------------------
# Text Extraction Utilities
# --------------------------------------------------------------------
def extract_text_from_pdf(file_path):
    """Extract text from digital PDF using pdfplumber; fallback to GPT vision if empty."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    if not text.strip():
        print(f"[INFO] No text layer found in {os.path.basename(file_path)} — using GPT vision fallback.")
        text = extract_with_gpt_vision(file_path)

    return text


def extract_with_gpt_vision(file_path):
    """Use GPT-4o to read text content from scanned or image-based PDFs."""
    text_out = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            b64_image = base64.b64encode(img_bytes).decode("utf-8")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract all visible text from this U.S. tax form image "
                                    "(numbers, labels, and values). Keep layout context where possible."
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
                        ],
                    }
                ],
            )
            text_out += response.choices[0].message.content.strip() + "\n"

    return text_out


# --------------------------------------------------------------------
# JSON Cleaning Utility
# --------------------------------------------------------------------
def safe_json_parse(text):
    """Extract and clean JSON block from model output safely."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


# --------------------------------------------------------------------
# Core GPT Parsing Logic
# --------------------------------------------------------------------
def parse_single_document(file_path):
    """Parse a single PDF tax document into structured JSON."""
    text = extract_text_from_pdf(file_path)

    prompt = ChatPromptTemplate.from_template("""
    You are a professional U.S. tax document parser. The text below contains
    data from either a W-2, 1099-INT, or 1099-NEC form. Identify which form
    it is and extract only the relevant numeric fields. Always output strictly
    valid JSON with numeric values. Do not include null or "N/A" fields.

    Examples:

    W-2:
    {{
      "form_type": "W-2",
      "payer": "ACME Corp",
      "wages": 52300.50,
      "federal_income_tax_withheld": 4300.75
    }}

    1099-INT:
    {{
      "form_type": "1099-INT",
      "payer": "Bank of America",
      "interest_income": 126.43
    }}

    1099-NEC:
    {{
      "form_type": "1099-NEC",
      "payer": "Freelance Client LLC",
      "nonemployee_compensation": 8200.00,
      "federal_income_tax_withheld": 0.00
    }}

    TEXT:
    {text}
    """)

    messages = prompt.format_messages(text=text)

    try:
        resp = llm.invoke(messages)
        parsed = safe_json_parse(resp.content)
        parsed["file_name"] = os.path.basename(file_path)
        return parsed
    except Exception as e:
        print(f"[ERROR] Parsing failed for {file_path}: {e}")
        return {"file_name": os.path.basename(file_path), "error": str(e)}


# --------------------------------------------------------------------
# Multi-file Parser
# --------------------------------------------------------------------
def parse_multiple_documents(file_paths):
    """Parse multiple PDFs and return unified JSON structure."""
    results = []
    for path in file_paths:
        print(f"[INFO] Parsing {os.path.basename(path)} ...")
        parsed = parse_single_document(path)
        if parsed:
            results.append(parsed)
    return {"documents": results}


# --------------------------------------------------------------------
# Manual Test (Run Directly)
# --------------------------------------------------------------------
if __name__ == "__main__":
    sample_files = ["samples/W2_sample.pdf", "samples/1099INT_sample.pdf"]
    result = parse_multiple_documents(sample_files)
    print(json.dumps(result, indent=2))
