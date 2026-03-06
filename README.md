Medical PDF Analyzer

A Python script that extracts text from medical PDF documents and generates a combined summary.

The tool:

Reads medical PDFs from a folder

Extracts text directly from the PDF when available

Uses OCR (Tesseract) for scanned documents

Saves extracted text into .txt files

Generates a single combined summary of all documents using an LLM

Designed for Polish medical documents with a Russian summary output.

Installation

Install Python dependencies:

pip install -r requirements.txt

Example requirements.txt:

pytesseract
PyPDF2
pdf2image
requests
OCR Setup
Windows

Install:

Tesseract
https://github.com/tesseract-ocr/tesseract

Poppler
https://github.com/oschwartz10612/poppler-windows

Set environment variables:

set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
set POPPLER_PATH=C:\Program Files\poppler-xx\Library\bin
Linux
sudo apt install tesseract-ocr
sudo apt install poppler-utils
Mac
brew install tesseract
brew install poppler
Environment Variables
OPENAI_API_KEY   OpenAI API key for summary generation
TESSERACT_PATH   Path to Tesseract executable
POPPLER_PATH     Path to Poppler binaries

Example:

export OPENAI_API_KEY=your_api_key
Usage

Place PDF files in the pdf folder.

Run:

python read_pdfs.py

Outputs:

txt/          extracted text files
summary.txt   combined medical summary
Options
--input        input PDF directory
--output       output txt directory
--mode         extraction mode: auto | native | ocr
--llm-model    LLM model (default: gpt-4o-mini)
--no-llm       disable AI summary

Example:

python read_pdfs.py --mode ocr

The script automatically chooses between native PDF text extraction and OCR, processes PDFs in parallel, and produces a single summary based only on document content.