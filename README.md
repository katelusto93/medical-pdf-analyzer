# Medical PDF Analyzer

Script that:

1. Reads PDF medical documents
2. Performs OCR if the PDF does not contain text
3. Saves the extracted text into `.txt` files
4. Generates a combined summary

## Installation

pip install -r requirements.txt


## OCR Installation

### Windows

Install:

Tesseract  
https://github.com/tesseract-ocr/tesseract

Poppler  
https://github.com/oschwartz10612/poppler-windows

Then set environment variables:

set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  
set POPPLER_PATH=C:\Program Files\poppler-25.12.0\Library\bin


### Linux

sudo apt install tesseract-ocr  
sudo apt install poppler-utils


### Mac

brew install tesseract  
brew install poppler


## Usage

Place the PDF files into the folder