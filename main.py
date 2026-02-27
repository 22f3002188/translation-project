# #main.py
import os
import sys
import shutil
import logging
import json

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
# Multi-stage language detection
# ----------------------------------------
def detect_pdf_language(pdf_path):

    print(" Detecting language...")

    try:

        text = extract_text(pdf_path)

        if text and len(text.strip()) > 200:

            sample = text[:2000]
            indic_ratio = indic_character_ratio(sample)
            lang = detect(sample)

            print(f"Detected (text-based): {lang}")

            if lang == "en" and indic_ratio < 0.10:
                return "english_text"

            if indic_ratio > 0.30:
                return "indic_text"

            return "mixed_text"

        else:
            print("Low extractable text → likely image PDF")
            return "image"

    except Exception:
        return "image"


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
    # 1️⃣ METADATA
    # ========================================
    metadata = extract_metadata(pdf_path)

    print("\n Metadata Summary:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")

    # ========================================
    # 2️⃣ LANGUAGE CHECK (TEXT LAYER)
    # ========================================
    lang_type = detect_pdf_language(pdf_path)

    metadata["detected_language_type"] = lang_type

    # ========================================
    # 3️⃣ IF ENGLISH TEXT → SKIP
    # ========================================
    if lang_type == "english_text":

        print("\n English TEXT PDF detected → Skipping pipeline")

        shutil.copy(pdf_path, output_pdf_path)
        save_metadata_json(metadata, output_pdf_path)
        return

    # ========================================
    # 4️⃣ IMAGE OR NON-ENGLISH → RUN OCR
    # ========================================
    print("\n Running OCR...")

    html_path = run_sarvam_ocr(
        pdf_path,
        OUTPUT_HTML,
        SARVAM_API_KEY
    )

    # ----------------------------------------
    # Detect language from OCR result
    # ----------------------------------------
    from bs4 import BeautifulSoup

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    ocr_text = soup.get_text(" ", strip=True)

    try:
        detected_lang = detect(ocr_text[:2000])
    except:
        detected_lang = "unknown"

    print(f"OCR detected language: {detected_lang}")

    # ========================================
    # 5️⃣ IF ENGLISH IMAGE → SKIP
    # ========================================
    if detected_lang == "en":

        print("\n English IMAGE PDF detected → Returning original")

        shutil.copy(pdf_path, output_pdf_path)
        save_metadata_json(metadata, output_pdf_path)
        return

    # ========================================
    # 6️⃣ TRANSLATE + REBUILD
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

# main.py

# import os
# import sys
# import shutil
# import logging
# import json
# import re

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
# # English detection (SAFE ADDITION)
# # ----------------------------------------
# def is_english_text(text):

#     if not text or len(text) < 100:
#         return False

#     indic_ratio = indic_character_ratio(text)

#     try:
#         lang = detect(text)
#     except:
#         return False

#     return lang == "en" and indic_ratio < 0.05


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
#     # 1️⃣ METADATA EXTRACTION
#     # ========================================
#     metadata = extract_metadata(pdf_path)

#     print("\n Metadata Summary:")
#     for key, value in metadata.items():
#         print(f"   {key}: {value}")

#     # ========================================
#     # 2️⃣ LANGUAGE DETECTION
#     # ========================================
#     print(" Detecting language...")

#     try:
#         text_sample = extract_text(pdf_path)[:2000]
#     except:
#         text_sample = ""

#     # ========================================
#     # 3️⃣ SKIP ENGLISH PDFs (SAFE)
#     # ========================================
#     if is_english_text(text_sample):

#         print("\n English PDF detected")
#         print("⏭ Skipping translation pipeline")

#         shutil.copy(pdf_path, output_pdf_path)

#         save_metadata_json(metadata, output_pdf_path)

#         print(f" Original PDF copied → {output_pdf_path}")
#         return

#     # ========================================
#     # 4️⃣ RUN OCR + TRANSLATION
#     # ========================================
#     print("\n Running OCR + Translation pipeline")

#     html_path = run_sarvam_ocr(
#         pdf_path,
#         OUTPUT_HTML,
#         SARVAM_API_KEY
#     )

#     soup = rebuild_layout(html_path)

#     render_pdf(soup, output_pdf_path)

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

# import os
# import sys
# import shutil
# import logging
# import json
# import re

# from langdetect import detect
# from pdfminer.high_level import extract_text

# logging.getLogger("pdfminer").setLevel(logging.ERROR)

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
# # Detect English safely
# # ----------------------------------------
# def is_english_text(text):

#     if not text:
#         return False

#     text_clean = re.sub(
#         r"[^A-Za-z0-9\s.,%-]",
#         " ",
#         text
#     )

#     text_clean = re.sub(r"\s+", " ", text_clean)

#     if len(text_clean) < 300:
#         return False

#     try:
#         lang = detect(text_clean)
#     except:
#         return False

#     words = text_clean.split()

#     english_words = [
#         w for w in words
#         if re.match(r"^[A-Za-z]+$", w)
#     ]

#     ratio = len(english_words) / max(len(words), 1)

#     return lang == "en" and ratio > 0.65


# # ----------------------------------------
# # Save metadata
# # ----------------------------------------
# def save_metadata_json(metadata, output_pdf_path):

#     base_name = os.path.basename(output_pdf_path)

#     json_path = os.path.join(
#         os.path.dirname(output_pdf_path),
#         base_name.replace(".pdf", "_metadata.json")
#     )

#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(metadata, f, indent=4, ensure_ascii=False)


# # ----------------------------------------
# # Process PDF
# # ----------------------------------------
# def process_pdf(pdf_path):

#     print(f"\n Processing: {pdf_path}")

#     base_name = os.path.basename(pdf_path)

#     output_pdf_path = os.path.join(
#         OUTPUT_PDF,
#         base_name
#     )

#     os.makedirs(OUTPUT_PDF, exist_ok=True)

#     metadata = extract_metadata(pdf_path)

#     # Extract text sample
#     try:
#         text_sample = extract_text(pdf_path)[:4000]
#     except:
#         text_sample = ""

#     # ===============================
#     # SKIP ENGLISH DIGITAL PDF
#     # ===============================
#     if len(text_sample.strip()) > 800:

#         if is_english_text(text_sample):

#             print(" English digital PDF detected → Skipping pipeline")

#             shutil.copy(pdf_path, output_pdf_path)

#             save_metadata_json(metadata, output_pdf_path)

#             return

#     # ===============================
#     # RUN OCR + TRANSLATION
#     # ===============================
#     print(" Running OCR + Translation pipeline")

#     html_path = run_sarvam_ocr(
#         pdf_path,
#         OUTPUT_HTML,
#         SARVAM_API_KEY
#     )

#     soup = rebuild_layout(html_path)

#     render_pdf(soup, output_pdf_path)

#     save_metadata_json(metadata, output_pdf_path)

#     print(f" Completed: {base_name}")


# # ----------------------------------------
# # Run all
# # ----------------------------------------
# def run():

#     pdf_files = [
#         f for f in os.listdir(INPUT_DIR)
#         if f.lower().endswith(".pdf")
#     ]

#     print(f"\n Found {len(pdf_files)} PDFs\n")

#     for file in pdf_files:

#         pdf_path = os.path.join(INPUT_DIR, file)

#         try:
#             process_pdf(pdf_path)
#         except Exception as e:
#             print(f" Failed: {file} → {e}")


# if __name__ == "__main__":
#     run()
