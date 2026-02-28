# #main.py
import os
import sys
import shutil
import logging
import json

from langdetect import detect
from pdfminer.high_level import extract_text

logging.getLogger("pdfminer").setLevel(logging.ERROR)

# ----------------------------------------
# Project imports
# ----------------------------------------
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from config import (
    SARVAM_API_KEY,
    INPUT_DIR,
    OUTPUT_HTML,
    OUTPUT_PDF
)

from hybrid_pipeline.ocr_extractor import run_sarvam_ocr
from hybrid_pipeline.layout_builder import rebuild_layout
from hybrid_pipeline.pdf_renderer import render_pdf
from hybrid_pipeline.metadata_extractor import extract_metadata


# ----------------------------------------
# STRICT DEVANAGARI DETECTION
# ----------------------------------------
def indic_character_ratio(text):

    total_chars = len(text)

    indic_chars = sum(
        1 for c in text
        if 2304 <= ord(c) <= 2431   # Correct Unicode range
    )

    return (indic_chars / total_chars) if total_chars else 0


# ----------------------------------------
# TEXT LAYER LANGUAGE DETECTION
# ----------------------------------------
def detect_pdf_language(pdf_path):

    print(" Detecting language...")

    try:
        text = extract_text(pdf_path)

        if not text:
            print("No text layer → Image PDF")
            return "unknown"

        words = text.split()
        unique_words = set(words)

        print(f"Total words: {len(words)}")
        print(f"Unique words: {len(unique_words)}")

        # 🔥 Weak or repetitive text layer
        if len(unique_words) < 50:
            print("Weak text layer → Forcing OCR")
            return "unknown"

        sample = text[:5000]
        indic_ratio = indic_character_ratio(sample)

        print(f"Text-layer Devanagari ratio: {indic_ratio:.5f}")

        if indic_ratio > 0.05:
            print("Indic content in text layer → OCR required")
            return "indic"

        lang = detect(sample)
        print(f"Detected language: {lang}")

        if lang == "en":
            return "english"

        return "mixed"

    except Exception:
        print("Language detection failed → unknown")
        return "unknown"


# ----------------------------------------
# Save metadata JSON
# ----------------------------------------
def save_metadata_json(metadata, output_pdf_path):

    base_name = os.path.basename(output_pdf_path).replace(".pdf", "")

    json_path = os.path.join(
        os.path.dirname(output_pdf_path),
        base_name + "_metadata.json"
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f" Metadata JSON saved → {json_path}")


# ----------------------------------------
# Process single PDF
# ----------------------------------------
def process_pdf(pdf_path):

    print(f"\n Processing: {pdf_path}")

    base_name = os.path.basename(pdf_path)
    output_pdf_path = os.path.join(OUTPUT_PDF, base_name)
    os.makedirs(OUTPUT_PDF, exist_ok=True)

    # ========================================
    # 1️⃣ METADATA
    # ========================================
    metadata = extract_metadata(pdf_path)

    print("\n Metadata Summary:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")

    # ========================================
    # 2️⃣ TEXT-LAYER LANGUAGE CHECK
    # ========================================
    lang_type = detect_pdf_language(pdf_path)
    metadata["detected_language_type"] = lang_type

    if lang_type == "english":

        print("\n Pure English TEXT PDF detected")
        print("⏭ Skipping translation pipeline")

        shutil.copy(pdf_path, output_pdf_path)
        save_metadata_json(metadata, output_pdf_path)
        return

    # ========================================
    # 3️⃣ RUN OCR (Image-based or Mixed PDFs)
    # ========================================
    print("\n Running OCR...")

    html_path = run_sarvam_ocr(
        pdf_path,
        OUTPUT_HTML,
        SARVAM_API_KEY
    )

    from bs4 import BeautifulSoup
    import re

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    ocr_text = soup.get_text(" ", strip=True)

    # ========================================
    # 4️⃣ OCR LANGUAGE DENSITY ANALYSIS
    # ========================================

    words = re.findall(r'\b\w+\b', ocr_text)
    total_words = len(words)

    # English words (3+ letters)
    eng_words = re.findall(r'\b[A-Za-z]{3,}\b', ocr_text)
    eng_word_count = len(eng_words)

    # Devanagari words (3+ characters)
    dev_words = re.findall(r'[\u0900-\u097F]{3,}', ocr_text)
    dev_word_count = len(dev_words)

    eng_ratio = (eng_word_count / total_words) if total_words else 0
    dev_ratio = (dev_word_count / total_words) if total_words else 0

    print(f"\n OCR Analysis:")
    print(f"   Total words: {total_words}")
    print(f"   English words: {eng_word_count}")
    print(f"   Devanagari words: {dev_word_count}")
    print(f"   English ratio: {eng_ratio:.3f}")
    print(f"   Devanagari ratio: {dev_ratio:.3f}")

    # ========================================
    # 5️⃣ DECISION LOGIC
    # ========================================

    # If document is predominantly English → skip
    if eng_ratio > 0.60 and dev_ratio < 0.10:

        print("\n OCR is predominantly English → Skipping translation")
        shutil.copy(pdf_path, output_pdf_path)
        save_metadata_json(metadata, output_pdf_path)
        return

    # If almost no Indic content → skip
    if dev_word_count < 30:

        print("\n OCR contains insignificant Indic content → Skipping")
        shutil.copy(pdf_path, output_pdf_path)
        save_metadata_json(metadata, output_pdf_path)
        return

    # ========================================
    # 6️⃣ TRANSLATE + REBUILD + RENDER
    # ========================================
    print("\n Running Translation + Layout Rebuild")

    soup = rebuild_layout(html_path)

    render_pdf(soup, output_pdf_path)

    save_metadata_json(metadata, output_pdf_path)

    print(f" Completed: {base_name}")

# ----------------------------------------
# Run for all PDFs
# ----------------------------------------
def run():

    print("\n Starting POP Translation Pipeline...\n")

    pdf_files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".pdf")
    ]

    print(f"Found {len(pdf_files)} PDF(s)\n")

    for file in pdf_files:

        pdf_path = os.path.join(INPUT_DIR, file)

        try:
            process_pdf(pdf_path)
        except Exception as e:
            print(f" Failed processing {file}")
            print("Error:", str(e))

    print("\n All PDFs processed!\n")


# ----------------------------------------
# Entry point
# ----------------------------------------
if __name__ == "__main__":
    run()
