import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect


# ======================================================
# MODEL LOAD
# ======================================================

MODEL_NAME = "ai4bharat/indictrans2-indic-en-1B"

print("🔹 Loading IndicTrans2 Universal Model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float32
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

print(" IndicTrans2 Ready")


# ======================================================
# LANGUAGE MAP
# ======================================================

LANG_MAP = {
    "mr": "mar_Deva",
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "bn": "ben_Beng",
    "pa": "pan_Guru",
    "or": "ory_Orya",
    "as": "asm_Beng",
    "ur": "urd_Arab",
    "en": "eng_Latn"
}


# ======================================================
#  AGRICULTURAL GLOSSARY (LOCK TERMS)
# ======================================================

GLOSSARY_PRE = {
    "तूर": "pigeon pea",
    "आंतरपीक": "intercropping",
    "वाण": "variety",
    "तक्ता": "Table",
    "महाराष्ट्र": "Maharashtra",
    "बियाणे": "seed",
    "लागवड": "cultivation",
    "खत": "fertilizer",
    "रोग": "disease"
}

GLOSSARY_POST = {
    "turkey": "pigeon pea",
    "turmeric": "pigeon pea",
    "interpeak": "intercropping",
    "interpicking": "intercropping",
    "death disease": "wilt disease",
    "coal": "weeding"
}


def apply_pre_glossary(text):
    for marathi, english in GLOSSARY_PRE.items():
        text = text.replace(marathi, english)
    return text


def apply_post_glossary(text):
    for wrong, correct in GLOSSARY_POST.items():
        text = text.replace(wrong, correct)
    return text


# ======================================================
# NUMERAL NORMALIZATION
# ======================================================

INDIC_NUM_MAP = {
    "०": "0","१": "1","२": "2","३": "3","४": "4",
    "५": "5","६": "6","७": "7","८": "8","९": "9",
    "૦": "0","૧": "1","૨": "2","૩": "3","૪": "4",
    "૫": "5","૬": "6","૭": "7","૮": "8","૯": "9"
}

def normalize_numerals(text):
    for k, v in INDIC_NUM_MAP.items():
        text = text.replace(k, v)
    return text


# ======================================================
# CLEAN OCR NOISE
# ======================================================

def clean_text(text):

    text = normalize_numerals(text)

    # Remove special bullets
    text = re.sub(r"[|•▪●◆■]", " ", text)

    #  Merge vertical broken words
    text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1\2", text)

    # Remove line breaks
    text = text.replace("\n", " ")

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ======================================================
# LANGUAGE DETECTION
# ======================================================

def detect_language(text):

    try:
        lang = detect(text)

        # If detected language exists in supported LANG_MAP
        if lang in LANG_MAP:
            return LANG_MAP[lang]

        # If detection says English
        if lang == "en":
            return "eng_Latn"

        # If something unexpected, fallback to Hindi Devanagari
        return "hin_Deva"

    except Exception:
        return "hin_Deva"


# ======================================================
# SKIP RULES
# ======================================================

def should_translate(text):

    text = text.strip()

    if not text:
        return False

    if len(text) < 2:
        return False

    if text.replace(".", "").replace("/", "").replace("-", "").isdigit():
        return False

    return True


# ======================================================
# MAIN TRANSLATION FUNCTION
# ======================================================

def translate_text(text, force_src=None):

    try:

        text = clean_text(text)

        if not should_translate(text):
            return text

        #  Apply glossary BEFORE translation
        text = apply_pre_glossary(text)

        if force_src:
            src_lang = force_src
        else:
            src_lang = detect_language(text)

        tgt_lang = "eng_Latn"

        tagged_text = f"{src_lang} {tgt_lang} {text}"

        inputs = tokenizer(
            tagged_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=512,
                num_beams=4,
                no_repeat_ngram_size=3,
                repetition_penalty=1.3,
                length_penalty=1.0,
                early_stopping=True
            )

        translated = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        ).strip()

        #  Apply glossary AFTER translation
        translated = apply_post_glossary(translated)

        return translated

    except Exception as e:

        print(" Translation error:", e)
        return text
