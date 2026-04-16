# 📄 Hybrid Document Translation Pipeline (PDF → OCR → Translation → Structured PDF)

## 🚀 Overview

This project is a **Hybrid Document AI Pipeline** that processes multilingual PDFs (including scanned documents) and converts them into **clean, structured, translated PDFs**.

It intelligently decides:

* Whether a PDF needs **OCR**
* Whether translation is required
* How to preserve layout (tables, headings, images)

---

## 🧠 Key Idea

> Convert **noisy, real-world PDFs** into **clean, readable, translated documents** using a combination of:

* OCR (Document AI)
* NLP preprocessing
* Transformer-based translation
* Layout reconstruction
* HTML → PDF rendering

---

## 🏗️ System Architecture

```
Input PDF
   ↓
Metadata Extraction
   ↓
Language Detection
   ↓
If Text PDF → Direct Copy
If Image PDF → OCR
   ↓
Text Cleaning + Layout Reconstruction
   ↓
Translation (Transformer Model)
   ↓
HTML → Styled PDF
   ↓
Final Output + Metadata JSON
```

---

## 📂 Project Structure

```
.
├── main.py                      # Pipeline controller
├── config.py                   # Configurations (paths, API keys)
├── requirements.txt
│
├── hybrid_pipeline/
│   ├── ocr_extractor.py        # OCR using Sarvam API
│   ├── layout_builder.py       # Layout reconstruction + cleaning
│   ├── translator.py           # ML-based translation
│   ├── pdf_renderer.py         # HTML → PDF rendering
│   ├── metadata_extractor.py   # Extract PDF metadata
│
├── input/                      # Input PDFs
├── output/
│   ├── html/
│   ├── pdf/
```

---

## ⚙️ How It Works (Step-by-Step)

### 1️⃣ Metadata Extraction

* Extracts:

  * Title, Author, Pages
  * Creation & modification date
* Helps in tracking and debugging

---

### 2️⃣ Language Detection

* Uses:

  * Unicode heuristics (Indic detection)
  * Statistical detection (`langdetect`)
* Decides:

  * English → Skip processing
  * Non-English → Process further

---

### 3️⃣ OCR (If Needed)

* Uses **SarvamAI Document Intelligence API**
* Converts:

  ```
  PDF → Structured HTML
  ```
* Preserves:

  * Tables
  * Paragraphs
  * Layout

---

### 4️⃣ Layout Reconstruction

Fixes common OCR issues:

* Broken sentences
* Incorrect ordering (multi-column PDFs)
* Merged words (e.g., `pigeonpea → pigeon pea`)
* Removes noise (symbols, page numbers)

Also:

* Reorders blocks using spatial coordinates (`top`, `left`)
* Normalizes HTML structure

---

### 5️⃣ Translation (Core AI Component)

* Uses **IndicTrans2 (Transformer Model)**
* Supports multiple Indian languages

#### Features:

* Pre-translation glossary (domain-specific)
* Post-translation correction
* Grammar polishing
* Duplicate removal

Example:

```
तूर → pigeon pea
```

---

### 6️⃣ Table & Content Handling

* Tables handled separately:

  * Numbers are preserved
  * Text is translated
* Images:

  * Resized and centered
* Headings:

  * Cleaned and formatted

---

### 7️⃣ PDF Rendering

* Uses **WeasyPrint**
* Converts:

  ```
  HTML + CSS → PDF
  ```

#### Styling includes:

* Typography
* Tables
* Page numbers
* Margins and layout

---

### 8️⃣ Output

* Final translated PDF
* Metadata JSON file

---

## 🧠 Core Concepts Used

### 🔥 1. Document AI

* OCR + layout understanding

### 🔥 2. Hybrid Pipeline

* Rule-based + ML + API

### 🔥 3. NLP Preprocessing

* Tokenization
* Cleaning
* Normalization

### 🔥 4. Transformer Models

* Seq2Seq translation
* Beam search decoding

### 🔥 5. Layout Reconstruction

* Spatial reasoning using coordinates

### 🔥 6. HTML DOM Manipulation

* Using BeautifulSoup

### 🔥 7. CSS-based PDF Rendering

* Professional formatting

### 🔥 8. Heuristic Optimization

* Avoid unnecessary OCR/translation

---

## ⚡ Key Features

✅ Handles scanned & text PDFs
✅ Multilingual support (Indic languages)
✅ Layout preservation (tables, images)
✅ Domain-aware translation (agriculture glossary)
✅ Robust error handling
✅ Modular architecture

---

## 🛠️ Tech Stack

* Python
* PyTorch
* Hugging Face Transformers
* BeautifulSoup
* WeasyPrint
* PyPDF2 / PDFMiner
* SarvamAI OCR API

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
```

Update `config.py` with your API key.

```bash
python main.py
```

---

## 💡 Design Decisions

* Used **OCR API instead of Tesseract** → better layout preservation
* Used **HTML as intermediate format** → easier transformation
* Combined **heuristics + ML** → optimized performance

---

## 🚀 Future Improvements

* Fine-tune translation model on domain data
* Add RAG for context-aware translation
* Parallel processing for faster pipeline
* Use LayoutLM for better document understanding

---

## 📌 Summary

This project demonstrates a **real-world AI system** that integrates:

* OCR
* NLP
* Transformer models
* Backend pipeline design

👉 It is designed to handle **noisy, real-world documents**, not just clean datasets.

---

## 👤 Author

**Harsh Jayswal**
