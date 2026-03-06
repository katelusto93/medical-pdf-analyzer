# Medical PDF Analyzer

A Python script that extracts text from medical PDF documents and generates a combined summary.

## Overview

This tool:

- Reads medical PDFs from a folder
- Extracts text directly from PDFs when available
- Uses OCR (Tesseract) for scanned documents
- Saves extracted text into `.txt` files
- Generates a **single combined summary** of all documents using an LLM
- Designed for **Polish medical documents** with **Russian summary output**

---

# Installation

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
pytesseract
PyPDF2
pdf2image
requests
```

---

# OCR Setup

## Windows

Install:

**Tesseract**
https://github.com/tesseract-ocr/tesseract

**Poppler**
https://github.com/oschwartz10612/poppler-windows

Set environment variables:

```bash
set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
set POPPLER_PATH=C:\Program Files\poppler-xx\Library\bin
```

---

## Linux

```bash
sudo apt install tesseract-ocr
sudo apt install poppler-utils
```

---

## Mac

```bash
brew install tesseract
brew install poppler
```

---

# Environment Variables

| Variable | Description |
|--------|--------|
| `OPENAI_API_KEY` | OpenAI API key used for summary generation |
| `TESSERACT_PATH` | Path to Tesseract executable |
| `POPPLER_PATH` | Path to Poppler binaries |

Example:

```bash
export OPENAI_API_KEY=your_api_key
```

---

# Usage

Place PDF files in the `pdf` folder.

Run the script:

```bash
python read_pdfs.py
```

---

# Output

```
txt/          extracted text files
summary.txt   combined medical summary
```

---

# Options

| Option | Description |
|------|------|
| `--input` | Input PDF directory |
| `--output` | Output text directory |
| `--mode` | Extraction mode: `auto` \| `native` \| `ocr` |
| `--llm-model` | LLM model (default: `gpt-4o-mini`) |
| `--no-llm` | Disable AI summary |

---

# Example

Run OCR mode explicitly:

```bash
python read_pdfs.py --mode ocr
```

---

# How It Works

The script:

1. Detects PDFs in the input folder
2. Attempts native text extraction
3. Falls back to OCR if necessary
4. Saves text from each document
5. Generates a **single medical summary** based only on document content

Processing is **parallelized**, making it efficient even for large document sets.

---

# Use Case

The tool is designed for:

- organizing medical records
- extracting text from scanned hospital documents
- preparing summaries for doctors
- consolidating medical history into a single report