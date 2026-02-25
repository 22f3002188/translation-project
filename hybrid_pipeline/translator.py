# import torch
# import re
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from langdetect import detect


# # ======================================================
# # MODEL LOAD
# # ======================================================

# MODEL_NAME = "ai4bharat/indictrans2-indic-en-1B"

# print("🔹 Loading IndicTrans2 Universal Model...")

# tokenizer = AutoTokenizer.from_pretrained(
#     MODEL_NAME,
#     trust_remote_code=True
# )

# model = AutoModelForSeq2SeqLM.from_pretrained(
#     MODEL_NAME,
#     trust_remote_code=True,
#     torch_dtype=torch.float32
# )

# device = "cuda" if torch.cuda.is_available() else "cpu"
# model.to(device)

# print(" IndicTrans2 Ready")


# # ======================================================
# # LANGUAGE MAP
# # ======================================================

# LANG_MAP = {
#     "mr": "mar_Deva",
#     "hi": "hin_Deva",
#     "gu": "guj_Gujr",
#     "ta": "tam_Taml",
#     "te": "tel_Telu",
#     "kn": "kan_Knda",
#     "ml": "mal_Mlym",
#     "bn": "ben_Beng",
#     "pa": "pan_Guru",
#     "or": "ory_Orya",
#     "as": "asm_Beng",
#     "ur": "urd_Arab",
#     "en": "eng_Latn"
# }


# # ======================================================
# # NUMERAL NORMALIZATION
# # ======================================================

# INDIC_NUM_MAP = {
#     "०": "0","१": "1","२": "2","३": "3","४": "4",
#     "५": "5","६": "6","७": "7","८": "8","९": "9",
#     "૦": "0","૧": "1","૨": "2","૩": "3","૪": "4",
#     "૫": "5","૬": "6","૭": "7","૮": "8","૯": "9"
# }

# def normalize_numerals(text):
#     for k, v in INDIC_NUM_MAP.items():
#         text = text.replace(k, v)
#     return text


# # ======================================================
# # CLEAN OCR NOISE
# # ======================================================

# def clean_text(text):

#     text = normalize_numerals(text)

#     # Remove extra symbols breaking model
#     text = re.sub(r"[|•▪●◆■]", " ", text)

#     # Remove multiple spaces
#     text = re.sub(r"\s+", " ", text)

#     return text.strip()


# # ======================================================
# # LANGUAGE DETECTION
# # ======================================================

# def detect_language(text):

#     try:
#         lang = detect(text)

#         if lang in LANG_MAP:
#             return LANG_MAP[lang]

#         return "mar_Deva"

#     except:
#         return "mar_Deva"


# # ======================================================
# # SKIP RULES
# # ======================================================

# def should_translate(text):

#     text = text.strip()

#     if not text:
#         return False

#     if len(text) < 2:
#         return False

#     # Numbers only
#     if text.replace(".", "").replace("/", "").replace("-", "").isdigit():
#         return False

#     return True


# # ======================================================
# # MAIN TRANSLATION
# # ======================================================

# def translate_text(text, force_src=None):

#     try:

#         text = clean_text(text)

#         if not should_translate(text):
#             return text

#         # Force language (for tables)
#         if force_src:
#             src_lang = force_src
#         else:
#             src_lang = detect_language(text)

#         tgt_lang = "eng_Latn"

#         tagged_text = f"{src_lang} {tgt_lang} {text}"

#         inputs = tokenizer(
#             tagged_text,
#             return_tensors="pt",
#             truncation=True,
#             max_length=512
#         ).to(device)

#         with torch.no_grad():
#             outputs = model.generate(
#             **inputs,
#             max_length=512,
#             num_beams=4,

#             #  Anti-repetition controls
#             no_repeat_ngram_size=3,
#             repetition_penalty=1.5,
#             length_penalty=1.0,
#             early_stopping=True
#         )
#         translated = tokenizer.decode(
#             outputs[0],
#             skip_special_tokens=True
#         )

#         return translated.strip()

#     except Exception as e:

#         print(" Translation error:", e)

#         # Fallback → return original text
#         return text


# ======================================================
# INDIC TRANS2 TRANSLATOR — SPEED OPTIMIZED
# ======================================================


import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect

MODEL_NAME = "ai4bharat/indictrans2-indic-en-1B"

print("🔹 Loading IndicTrans2 Universal Model...")

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)

model.to(device)
model.eval()
torch.set_grad_enabled(False)

print(f" IndicTrans2 Ready on {device}")


# -------------------------------
# Language map
# -------------------------------
LANG_MAP = {
    "mr": "mar_Deva",
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
    "bn": "ben_Beng",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "pa": "pan_Guru",
    "ur": "urd_Arab",
    "en": "eng_Latn"
}


# -------------------------------
# Numeral normalization
# -------------------------------
INDIC_NUM_MAP = {
    "०":"0","१":"1","२":"2","३":"3","४":"4",
    "५":"5","६":"6","७":"7","८":"8","९":"9",
    "૦":"0","૧":"1","૨":"2","૩":"3","૪":"4",
    "૫":"5","૬":"6","૭":"7","૮":"8","૯":"9"
}

def normalize_numerals(text):
    for k,v in INDIC_NUM_MAP.items():
        text = text.replace(k,v)
    return text


# -------------------------------
# Clean OCR noise
# -------------------------------
def clean_text(text):

    text = normalize_numerals(text)
    text = re.sub(r"[|•▪●◆■]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -------------------------------
# Detect language
# -------------------------------
def detect_language(text):

    try:
        lang = detect(text)
        return LANG_MAP.get(lang, "mar_Deva")
    except:
        return "mar_Deva"


# -------------------------------
# Skip rules (improved)
# -------------------------------
def should_translate(text):

    text = text.strip()

    if not text:
        return False

    # Allow small captions
    if len(text) <= 1:
        return False

    return True


# -------------------------------
# MAIN TRANSLATION
# -------------------------------
def translate_text(text, force_src=None):

    try:

        text = clean_text(text)

        if not should_translate(text):
            return text

        src_lang = force_src if force_src else detect_language(text)
        tgt_lang = "eng_Latn"

        tagged = f"{src_lang} {tgt_lang} {text}"

        inputs = tokenizer(
            tagged,
            return_tensors="pt",
            truncation=True,
            max_length=256
        ).to(device)

        with torch.inference_mode():

            outputs = model.generate(
                **inputs,
                max_length=256,
                num_beams=2,
                no_repeat_ngram_size=3,
                repetition_penalty=1.3,
                early_stopping=True
            )

        translated = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return translated.strip()

    except Exception as e:
        print(" Translation error:", e)
        return text