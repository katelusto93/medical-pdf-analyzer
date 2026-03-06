import argparse
import os
import shutil
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

import requests
import pytesseract


# ---------------------------
# Constants
# ---------------------------

MAX_INPUT_CHARS = 50000
MAX_WORKERS = min(4, os.cpu_count() or 1)
MIN_TEXT_LENGTH = 80


# ---------------------------
# Environment configuration
# ---------------------------

def configure_tesseract():

    env_path = os.getenv("TESSERACT_PATH")

    if env_path:
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    found = shutil.which("tesseract")

    if found:
        pytesseract.pytesseract.tesseract_cmd = found
    else:
        print("⚠️ Tesseract not found in PATH")


def get_poppler_path():
    return os.getenv("POPPLER_PATH")


# ---------------------------
# Optional imports
# ---------------------------

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


# ---------------------------
# TEXT VALIDATION
# ---------------------------

def text_looks_gibberish(text: str) -> bool:

    if not text:
        return True

    letters = sum(ch.isalpha() for ch in text)
    total = len(text)

    if total == 0:
        return True

    return (letters / total) < 0.3


# ---------------------------
# PDF TEXT EXTRACTION
# ---------------------------

def extract_text_from_pdf_native(pdf_path: Path) -> str:

    if PdfReader is None:
        print("⚠️ PyPDF2 not installed")
        return ""

    try:

        reader = PdfReader(str(pdf_path))
        parts = []

        for page in reader.pages:

            try:
                text = page.extract_text() or ""
            except Exception as e:
                print(f"Native extraction error: {e}")
                text = ""

            if text.strip():
                parts.append(text)

        return "\n\n".join(parts).strip()

    except Exception as e:
        print(f"Failed reading PDF {pdf_path.name}: {e}")
        return ""


def extract_text_from_pdf_ocr(pdf_path: Path, lang: str = "pol") -> str:

    if convert_from_path is None:
        print("⚠️ OCR unavailable (install pdf2image)")
        return ""

    try:

        images = convert_from_path(
            str(pdf_path),
            dpi=300,
            thread_count=4,
            poppler_path=get_poppler_path(),
        )

    except Exception as e:
        print(f"PDF→image conversion failed for {pdf_path.name}: {e}")
        return ""

    parts: List[str] = []

    for img in images:

        try:
            txt = pytesseract.image_to_string(img, lang=lang) or ""
        except Exception as e:
            print(f"OCR error: {e}")
            txt = ""

        if txt.strip():
            parts.append(txt.strip())

    return "\n\n".join(parts).strip()


def extract_text_from_pdf(pdf_path: Path, mode: str = "auto") -> str:

    if mode == "native":
        return extract_text_from_pdf_native(pdf_path)

    if mode == "ocr":
        return extract_text_from_pdf_ocr(pdf_path)

    native = extract_text_from_pdf_native(pdf_path)

    if native and len(native) > MIN_TEXT_LENGTH and not text_looks_gibberish(native):
        print(f"Native extraction OK → {pdf_path.name}")
        return native

    print(f"OCR fallback → {pdf_path.name}")

    ocr = extract_text_from_pdf_ocr(pdf_path)

    return ocr


# ---------------------------
# OPENAI SUMMARY
# ---------------------------

def call_openai_doctor_summary(
    text_pl: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
) -> Optional[str]:

    if not api_key:
        return None

    if len(text_pl) > MAX_INPUT_CHARS:
        text_pl = text_pl[:MAX_INPUT_CHARS]

    system_prompt = (
        "Ты врач, который объясняет пациенту результаты медицинских документов.\n"
        "Документы на польском языке.\n"
        "Сделай краткое саммари на русском.\n\n"

        "Структура:\n"
        "1. Какие исследования\n"
        "2. Основные результаты\n"
        "3. Отклонения\n"
        "4. Тенденции по годам\n"
        "5. Рекомендации\n"
        "6. Общая оценка серьезности\n\n"

        "В разделе 'Общая оценка серьезности' оцени общую картину:\n"
        "- есть ли значимые отклонения\n"
        "- требуют ли результаты внимания врача\n"
        "- выглядят ли изменения легкими, умеренными или потенциально серьезными\n"
        "- срочность дальнейших действий (если она видна из документов)\n\n"

        "Правила:\n"
        "- Используй только данные из документов\n"
        "- Не придумывай диагнозы\n"
        "- Если данных недостаточно, прямо укажи это\n"
    )

    user_prompt = f"Ниже текст медицинских документов:\n\n{text_pl}"

    try:

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None


# ---------------------------
# PDF PROCESSING
# ---------------------------

def process_pdf(index: int, total: int, pdf_path: Path, txt_dir: Path, mode: str) -> str:

    txt_path = txt_dir / (pdf_path.stem + ".txt")

    if txt_path.exists():

        try:
            return txt_path.read_text(encoding="utf-8")
        except Exception:
            pass

    print(f"[{index}/{total}] Processing → {pdf_path.name}")

    text = extract_text_from_pdf(pdf_path, mode)

    if not text.strip():

        print(f"⚠️ No text extracted from {pdf_path.name}")
        return ""

    try:
        txt_path.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"TXT write error: {e}")

    return text


# ---------------------------
# DIRECTORY PROCESSING
# ---------------------------

def process_directory(
    input_dir: Path,
    output_dir: Optional[Path],
    mode: str,
    use_llm: bool,
    llm_model: str,
):

    project_root = input_dir.parent

    txt_dir = Path(output_dir) if output_dir else project_root / "txt"
    txt_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = [p for p in input_dir.rglob("*.pdf") if p.is_file()]

    if not pdf_files:
        print("No PDF files found")
        return

    print(f"Found PDFs: {len(pdf_files)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        total = len(pdf_files)
        texts = list(
            executor.map(
                lambda args: process_pdf(*args),
                [(i + 1, total, p, txt_dir, mode) for i, p in enumerate(pdf_files)]
            )
        )

    texts = [t for t in texts if t.strip()]

    if not texts:
        print("No text extracted from any PDF")
        return

    combined_text = "\n\n".join(texts)

    openai_key = os.getenv("OPENAI_API_KEY")

    if use_llm and openai_key:

        summary = call_openai_doctor_summary(
            text_pl=combined_text,
            api_key=openai_key,
            model=llm_model,
        )

    else:
        summary = combined_text[:2000]

    summary_path = project_root / "summary.txt"

    with summary_path.open("w", encoding="utf-8") as f:

        f.write("ОБЩЕЕ САММАРИ МЕДИЦИНСКИХ ДОКУМЕНТОВ\n")
        f.write("=====================================\n\n")
        f.write(summary or "")

    print(f"\nSummary saved: {summary_path}")


# ---------------------------
# CLI
# ---------------------------

def main():

    configure_tesseract()

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", default="pdf")
    parser.add_argument("--output", default=None)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--mode", default="auto", choices=["ocr", "native", "auto"])

    args = parser.parse_args()

    input_dir = Path(os.path.abspath(args.input))
    output_dir = Path(os.path.abspath(args.output)) if args.output else None

    process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        mode=args.mode,
        use_llm=not args.no_llm,
        llm_model=args.llm_model,
    )


if __name__ == "__main__":
    main()