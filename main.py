# #main.py
# import os
# import sys
# import shutil
# import logging
# import json

# from langdetect import detect
# from pdfminer.high_level import extract_text

# # Silence pdfminer warnings
# logging.getLogger("pdfminer").setLevel(logging.ERROR)


# # ----------------------------------------
# # Project imports
# # ----------------------------------------
# sys.path.append(
#     os.path.abspath(
#         os.path.join(os.path.dirname(__file__), "..")
#     )
# )

# from config import (
#     SARVAM_API_KEY,
#     INPUT_DIR,
#     OUTPUT_HTML,
#     OUTPUT_PDF
# )

# from hybrid_pipeline.ocr_extractor import run_sarvam_ocr
# from hybrid_pipeline.layout_builder import rebuild_layout
# from hybrid_pipeline.pdf_renderer import render_pdf
# from hybrid_pipeline.metadata_extractor import extract_metadata

# # ----------------------------------------
# # Indic script detection
# # ----------------------------------------
# def indic_character_ratio(text):

#     indic_chars = len(
#         [c for c in text if ord(c) > 2304]
#     )

#     total_chars = len(text)

#     if total_chars == 0:
#         return 0

#     return indic_chars / total_chars


# # ----------------------------------------
# # Multi-stage language detection
# # ----------------------------------------
# def detect_pdf_language(pdf_path):

#     print(" Detecting language...")

#     try:

#         text = extract_text(pdf_path)

#         if not text or len(text) < 100:
#             print("Low text detected — treating as image PDF")
#             return "image"

#         sample = text[:2000]

#         indic_ratio = indic_character_ratio(sample)

#         print(f"Indic ratio: {indic_ratio:.2f}")

#         lang = detect(sample)

#         print(f"Detected language: {lang}")

#         if indic_ratio > 0.30:
#             return "indic"

#         if lang == "en" and indic_ratio < 0.10:
#             return "english"

#         return "mixed"

#     except Exception as e:

#         print("Language detection failed — using OCR fallback")

#         return "unknown"


# # ----------------------------------------
# # Save metadata JSON
# # ----------------------------------------
# def save_metadata_json(metadata, output_pdf_path):

#     base_name = os.path.basename(output_pdf_path)
#     base_name = base_name.replace(".pdf", "")

#     json_path = os.path.join(
#         os.path.dirname(output_pdf_path),
#         base_name + "_metadata.json"
#     )

#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(metadata, f, indent=4, ensure_ascii=False)

#     print(f" Metadata JSON saved → {json_path}")


# # ----------------------------------------
# # Process single PDF
# # ----------------------------------------
# def process_pdf(pdf_path):

#     print(f"\n Processing: {pdf_path}")

#     base_name = os.path.basename(pdf_path)

#     output_pdf_path = os.path.join(
#         OUTPUT_PDF,
#         base_name
#     )

#     os.makedirs(OUTPUT_PDF, exist_ok=True)

#     # ========================================
#     # 1️ METADATA EXTRACTION
#     # ========================================
#     metadata = extract_metadata(pdf_path)

#     print("\n Metadata Summary:")
#     for key, value in metadata.items():
#         print(f"   {key}: {value}")

#     # ========================================
#     # 2️ LANGUAGE DETECTION
#     # ========================================
#     lang_type = detect_pdf_language(pdf_path)

#     metadata["detected_language_type"] = lang_type

#     # ========================================
#     # 3️ SKIP ENGLISH PDFs
#     # ========================================
#     if lang_type == "english":

#         print("\n English PDF detected")
#         print("⏭ Skipping translation pipeline")

#         shutil.copy(pdf_path, output_pdf_path)

#         print(
#             f" Original PDF copied → {output_pdf_path}"
#         )

#         # Save metadata JSON
#         save_metadata_json(metadata, output_pdf_path)

#         return

#     # ========================================
#     # 4️ RUN OCR + TRANSLATION
#     # ========================================
#     print("\n Running OCR + Translation pipeline")

#     html_path = run_sarvam_ocr(
#         pdf_path,
#         OUTPUT_HTML,
#         SARVAM_API_KEY
#     )

#     soup = rebuild_layout(html_path)

#     render_pdf(soup, output_pdf_path)

#     # Save metadata JSON
#     save_metadata_json(metadata, output_pdf_path)

#     print(f" Completed: {base_name}")

# # ----------------------------------------
# # Run for all PDFs
# # ----------------------------------------
# def run():

#     print("\n Starting POP Translation Pipeline...\n")

#     pdf_files = [
#         f for f in os.listdir(INPUT_DIR)
#         if f.lower().endswith(".pdf")
#     ]

#     print(f"Found {len(pdf_files)} PDF(s)\n")

#     for file in pdf_files:

#         pdf_path = os.path.join(INPUT_DIR, file)

#         try:
#             process_pdf(pdf_path)

#         except Exception as e:

#             print(f" Failed processing {file}")
#             print("Error:", str(e))

#     print("\n All PDFs processed!\n")


# # ----------------------------------------
# # Entry point
# # ----------------------------------------
# if __name__ == "__main__":
#     run()

# main.py

import os
import sys
import shutil
import logging
import json
import re

from langdetect import detect
from pdfminer.high_level import extract_text

# Silence pdfminer warnings
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
# Indic script detection
# ----------------------------------------
def indic_character_ratio(text):

    indic_chars = len(
        [c for c in text if ord(c) > 2304]
    )

    total_chars = len(text)

    if total_chars == 0:
        return 0

    return indic_chars / total_chars


# ----------------------------------------
# English detection (SAFE ADDITION)
# ----------------------------------------
def is_english_text(text):

    if not text or len(text) < 100:
        return False

    indic_ratio = indic_character_ratio(text)

    try:
        lang = detect(text)
    except:
        return False

    return lang == "en" and indic_ratio < 0.05


# ----------------------------------------
# Save metadata JSON
# ----------------------------------------
def save_metadata_json(metadata, output_pdf_path):

    base_name = os.path.basename(output_pdf_path)
    base_name = base_name.replace(".pdf", "")

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

    output_pdf_path = os.path.join(
        OUTPUT_PDF,
        base_name
    )

    os.makedirs(OUTPUT_PDF, exist_ok=True)

    # ========================================
    # 1️⃣ METADATA EXTRACTION
    # ========================================
    metadata = extract_metadata(pdf_path)

    print("\n Metadata Summary:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")

    # ========================================
    # 2️⃣ LANGUAGE DETECTION
    # ========================================
    print(" Detecting language...")

    try:
        text_sample = extract_text(pdf_path)[:2000]
    except:
        text_sample = ""

    # ========================================
    # 3️⃣ SKIP ENGLISH PDFs (SAFE)
    # ========================================
    if is_english_text(text_sample):

        print("\n English PDF detected")
        print("⏭ Skipping translation pipeline")

        shutil.copy(pdf_path, output_pdf_path)

        save_metadata_json(metadata, output_pdf_path)

        print(f" Original PDF copied → {output_pdf_path}")
        return

    # ========================================
    # 4️⃣ RUN OCR + TRANSLATION
    # ========================================
    print("\n Running OCR + Translation pipeline")

    html_path = run_sarvam_ocr(
        pdf_path,
        OUTPUT_HTML,
        SARVAM_API_KEY
    )

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