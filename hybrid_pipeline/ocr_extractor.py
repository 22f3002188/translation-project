#ocr_extraction.py
from sarvamai import SarvamAI
import zipfile
import os


def run_sarvam_ocr(pdf_path, output_dir, api_key):

    print("Starting OCR job...")

    client = SarvamAI(api_subscription_key=api_key)

    job = client.document_intelligence.create_job(
        language="mr-IN",
        output_format="html"
    )

    print(f"Job created: {job.job_id}")

    job.upload_file(pdf_path)
    print("File uploaded")

    job.start()
    print("Job started")

    status = job.wait_until_complete()
    print(f"Job completed: {status.job_state}")

    base = os.path.basename(pdf_path)
    base = base.replace(".pdf", "").replace(" ", "_").replace(",", "")

    pdf_output_dir = os.path.join(output_dir, base)
    os.makedirs(pdf_output_dir, exist_ok=True)

    zip_path = os.path.join(pdf_output_dir, base + ".zip")

    job.download_output(zip_path)
    print(f"ZIP downloaded → {zip_path}")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(pdf_output_dir)

    html_file = None

    for root, dirs, files in os.walk(pdf_output_dir):
        for file in files:
            if file.endswith(".html"):
                html_file = os.path.join(root, file)
                break

    if not html_file:
        raise Exception("No HTML file found in OCR output")

    print(f"OCR HTML → {html_file}")

    return html_file