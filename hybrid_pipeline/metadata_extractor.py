#metadata_extraction.py
from PyPDF2 import PdfReader
import os


# ----------------------------------------
# Convert datetime safely
# ----------------------------------------
def safe_date(value):

    if value is None:
        return "Unknown"

    try:
        return str(value)
    except:
        return "Unknown"


# ----------------------------------------
# Extract metadata
# ----------------------------------------
def extract_metadata(pdf_path):

    print(f" Extracting metadata: {pdf_path}")

    metadata_dict = {}

    try:

        reader = PdfReader(pdf_path)

        meta = reader.metadata

        metadata_dict["file_name"] = os.path.basename(pdf_path)
        metadata_dict["file_path"] = pdf_path
        metadata_dict["total_pages"] = len(reader.pages)

        metadata_dict["title"] = meta.title or "Unknown"
        metadata_dict["author"] = meta.author or "Unknown"
        metadata_dict["subject"] = meta.subject or "Unknown"
        metadata_dict["creator"] = meta.creator or "Unknown"
        metadata_dict["producer"] = meta.producer or "Unknown"

        # SAFE DATE CONVERSION
        metadata_dict["creation_date"] = safe_date(
            meta.creation_date
        )

        metadata_dict["modification_date"] = safe_date(
            meta.modification_date
        )

        print(" Metadata extracted\n")

    except Exception as e:

        print("⚠ Metadata extraction failed:", str(e))

        metadata_dict = {
            "file_name": os.path.basename(pdf_path),
            "error": "Metadata not available"
        }

    return metadata_dict
