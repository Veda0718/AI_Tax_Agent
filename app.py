"""
File: app.py
Description:
    Flask web application that allows users to upload multiple tax
    documents (W-2, 1099-INT, 1099-NEC), automatically parses and extracts
    key fields using GPT (via pdf_parser.py), computes total income, tax
    liability, and refund, and generates a downloadable IRS Form 1040.

Key Responsibilities:
    - Handle file uploads and user inputs (filing status).
    - Use GPT-powered parser to extract financial data.
    - Compute federal tax liability using 2024 tax brackets.
    - Generate a completed Form 1040 PDF and serve it for download.

Dependencies:
    Flask, pdf_parser, tax_logic, form1040_generator.

Author: Veda Sahaja Bandi
"""

import os, json
from flask import Flask, render_template, request, send_file, send_from_directory
from pdf_parser import parse_multiple_documents
from tax_logic import compute_liability
from form1040_generator import generate_1040

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------------------------
# Utility: safely convert any field to float
# --------------------------------------------------------------------
def to_float(value):
    """Convert numeric fields to float, treating missing or invalid values as 0."""
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    """Main route: handle file upload, parsing, and tax calculation."""
    if request.method == "POST":
        filing_status = request.form.get("filing_status", "single")
        uploaded_files = request.files.getlist("files")

        # Store all uploaded file paths
        uploaded_paths = []
        for f in uploaded_files:
            if f.filename.strip() == "":
                continue
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            uploaded_paths.append(path)

        if not uploaded_paths:
            return render_template("index.html", error="Please upload at least one PDF file.")

        # 🔹 Parse all uploaded PDFs using GPT-powered parser
        parsed_all = parse_multiple_documents(uploaded_paths)

        total_income = 0
        withheld = 0
        parsed_docs = parsed_all.get("documents", [])

        # 🔹 Aggregate fields from each parsed document
        for doc in parsed_docs:
            total_income += (
                to_float(doc.get("wages")) +
                to_float(doc.get("interest_income")) +
                to_float(doc.get("nonemployee_compensation"))
            )
            withheld += to_float(doc.get("federal_income_tax_withheld"))

        # 🔹 Compute tax summary
        summary = compute_liability(filing_status, [total_income], withheld)

        # 🔹 Generate Form 1040 PDF
        pdf_path = generate_1040(summary)

        # 🔹 Render result page with summary + per-file details
        return render_template(
            "result.html",
            summary=summary,
            pdf_path=pdf_path,
            parsed_docs=parsed_docs
        )

    return render_template("index.html")


# @app.route("/download")
# def download():
#     """Serve generated Form 1040 for download."""
#     return send_file("output_1040.pdf", as_attachment=True)

# @app.route("/download")
# def download():
#     """Serve generated Form 1040 for preview and download."""
#     return send_from_directory("static", "output_1040.pdf", mimetype="application/pdf")
# --------------------------------------------------------------------
# Serve PDF for Inline Preview (iframe)
# --------------------------------------------------------------------
@app.route("/preview_pdf")
def preview_pdf():
    """Serve the generated Form 1040 inline for preview in iframe."""
    return send_from_directory(
        "static",
        "output_1040.pdf",
        mimetype="application/pdf",
        as_attachment=False  # ✅ Show inline
    )


# --------------------------------------------------------------------
# Serve PDF for Download
# --------------------------------------------------------------------
@app.route("/download")
def download():
    """Serve the generated Form 1040 as a downloadable file."""
    return send_from_directory(
        "static",
        "output_1040.pdf",
        mimetype="application/pdf",
        as_attachment=True,  # ✅ Force browser download
        download_name="Form1040.pdf"
    )


# --------------------------------------------------------------------
# Main Entry
# --------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
