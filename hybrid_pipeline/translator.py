# import torch
# import re
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from langdetect import detect
# from hybrid_pipeline.transliteration import (
#     detect_punjabi_transliteration,
#     transliterate_to_gurmukhi
# )


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
# #  AGRICULTURAL GLOSSARY (LOCK TERMS)
# # ======================================================

# GLOSSARY_PRE = {
#     "तूर": "pigeon pea",
#     "आंतरपीक": "intercropping",
#     "वाण": "variety",
#     "तक्ता": "Table",
#     "महाराष्ट्र": "Maharashtra",
#     "बियाणे": "seed",
#     "लागवड": "cultivation",
#     "खत": "fertilizer",
#     "रोग": "disease",
#     "पूर्व मशागत": "land preparation",
#     "आंतर मशागत": "intercultural operations",
#     "मशागत": "cultivation operations",

#     # Agricultural disease fixes
#     "मर": "wilt disease",
#     "मर रोग": "wilt disease",
#     "मुरडा": "sterility mosaic disease",
#     "मुरडा रोग": "sterility mosaic disease",

#     # Agriculture terms
#     "पेरणी": "sowing",
#     "काढणी": "harvesting",
#     "साठवण": "storage"
# }
# GLOSSARY_POST = {
#     "turkey": "pigeon pea",
#     "turmeric": "pigeon pea",
#     "interpeak": "intercropping",
#     "interpicking": "intercropping",
#     "death disease": "wilt disease",
#     "coal": "weeding",
#     "in the past": "land preparation",
#     "interagency": "intercultural operations"
# }


# def apply_pre_glossary(text):
#     for marathi, english in GLOSSARY_PRE.items():
#         text = text.replace(marathi, english)
#     return text


# def apply_post_glossary(text):
#     for wrong, correct in GLOSSARY_POST.items():
#         text = text.replace(wrong, correct)
#     return text


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

# # Common agricultural and structural words
# SAFE_WORDS = {
#     "the", "and", "with", "from", "that", "this", "should",
#     "will", "are", "was", "for", "per", "crop", "soil",
#     "seed", "water", "variety", "plants", "plant",
#     "growth", "yield", "disease", "pigeon", "pea",
#     "hectare", "kg", "gm", "field", "land", "storage",
#     "fungus", "moisture", "flowering", "harvest"
# }

# def repair_word_boundaries(text):

#     if not text:
#         return text

#     words = text.split()
#     repaired_words = []

#     for token in words:

#         lower_token = token.lower()

#         # Skip short words
#         if len(token) < 7:
#             repaired_words.append(token)
#             continue

#         split_done = False

#         # Try safe split positions
#         for i in range(3, len(token) - 3):

#             left = lower_token[:i]
#             right = lower_token[i:]

#             if left in SAFE_WORDS and right in SAFE_WORDS:
#                 repaired_words.append(token[:i] + " " + token[i:])
#                 split_done = True
#                 break

#         if not split_done:
#             repaired_words.append(token)

#     text = " ".join(repaired_words)

#     # Specific safe fixes
#     text = re.sub(r'pigeonpea', 'pigeon pea', text, flags=re.IGNORECASE)

#     # Fix uppercase merges
#     text = re.sub(r'([A-Z]{3,})([A-Z][a-z])', r'\1 \2', text)

#     # Normalize spacing
#     text = re.sub(r'\s+', ' ', text)

#     return text.strip()
# # ======================================================
# # CLEAN OCR NOISE
# # ======================================================
# # ======================================================
# # CLEAN OCR NOISE
# # ======================================================
# def clean_text(text):

#     if not text:
#         return text

#     text = normalize_numerals(text)

#     text = re.sub(r"[|•▪●◆■]", " ", text)

#     # Merge newline after full stop
#     text = re.sub(r'\.\s*\n\s*', '. ', text)

#     # Merge broken words across lines
#     text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1\2", text)

#     text = re.sub(r'(?<=[a-z0-9])\.(?=[A-Za-z])', '. ', text)
#     text = re.sub(r'(?<=[a-z0-9]):(?=[A-Za-z])', ': ', text)
#     text = re.sub(r'(?<=[a-z0-9]),(?=[A-Za-z])', ', ', text)

#     text = re.sub(r'\b(\w+)\.\s*\1\b', r'\1', text, flags=re.IGNORECASE)

#     text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

#     text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
#     text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

#     text = re.sub(r'\s*/\s*', ' / ', text)

#     text = re.sub(r'\.{2,}', '.', text)

#     text = re.sub(r'\s+', ' ', text)

#     text = repair_word_boundaries(text)

#     return text.strip()


# # ======================================================
# # LANGUAGE DETECTION
# # ======================================================

# def detect_language(text):

#     try:
#         lang = detect(text)

#         # If detected language exists in supported LANG_MAP
#         if lang in LANG_MAP:
#             return LANG_MAP[lang]

#         # If detection says English
#         if lang == "en":
#             return "eng_Latn"

#         # If something unexpected, fallback to Hindi Devanagari
#         return "hin_Deva"

#     except Exception:
#         return "hin_Deva"


# # ======================================================
# # SKIP RULES
# # ======================================================

# def should_translate(text):

#     text = text.strip()

#     if not text:
#         return False

#     # Skip pure numbers
#     if re.fullmatch(r"[0-9./-]+", text):
#         return False

#     return True

# def fix_joined_words(text):

#     if not text:
#         return text

#     # split common joined words
#     text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

#     # split words joined with numbers
#     text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
#     text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

#     # fix known agricultural joins
#     text = re.sub(r'pigeonpea', 'pigeon pea', text, flags=re.IGNORECASE)
#     text = re.sub(r'seedrate', 'seed rate', text, flags=re.IGNORECASE)
#     text = re.sub(r'wheatcrop', 'wheat crop', text, flags=re.IGNORECASE)
#     text = re.sub(r'plantgrowth', 'plant growth', text, flags=re.IGNORECASE)

#     # normalize spaces
#     text = re.sub(r'\s+', ' ', text)

#     return text.strip()

# def fix_sentence_spacing(text):

#     if not text:
#         return text

#     # Add space after . ? !
#     text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)

#     # Fix comma spacing
#     text = re.sub(r',([A-Za-z])', r', \1', text)

#     # Normalize spaces
#     text = re.sub(r'\s+', ' ', text)

#     return text.strip()
# # ======================================================
# # MAIN TRANSLATION FUNCTION
# # ======================================================

# def translate_text(text, force_src=None):

#     try:

#         text = clean_text(text)

#         if not should_translate(text):
#             return text

#         text = apply_pre_glossary(text)

#         # FORCE MARATHI if Devanagari script detected
#         if re.search(r'[\u0900-\u097F]', text):
#             src_lang = "mar_Deva"
#         elif force_src:
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
#             num_beams=5,
#             no_repeat_ngram_size=4,
#             repetition_penalty=1.4,
#             length_penalty=1.1,
#             early_stopping=True
#         )
                   

#         translated = tokenizer.decode(
#             outputs[0],
#             skip_special_tokens=True
#         ).strip()

#         translated = apply_post_glossary(translated)
#         translated = fix_sentence_spacing(translated)
#         translated = fix_joined_words(translated)

#         return translated

#     except Exception as e:
#         print(" Translation error:", e)
#         return text

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
# AGRICULTURAL GLOSSARY
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
    "रोग": "disease",

    "मर": "wilt disease",
    "मर रोग": "wilt disease",

    "मुरडा": "sterility mosaic disease",
    "मुरडा रोग": "sterility mosaic disease",

    "पेरणी": "sowing",
    "काढणी": "harvesting",
    "साठवण": "storage"
}


GLOSSARY_POST = {

    "turkey": "pigeon pea",
    "turmeric": "pigeon pea",
    "interpeak": "intercropping",
    "interpicking": "intercropping",
    "death disease": "wilt disease",
    "coal": "weeding",

    "In the past": "land preparation",
    "Interagency": "intercultural operations",
    "Income (ki / He.)":"Yield (kg/ha)"
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
# TERMINOLOGY NORMALIZATION
# ======================================================

TERM_MAP = {
    "tur": "pigeon pea",
    "turi": "pigeon pea",
    "tur dal": "pigeon pea lentils",
    "ki / he": "kg / ha",
    "lavagadi": "cultivation region"
}


def normalize_terms(text):

    for k, v in TERM_MAP.items():
        text = re.sub(rf"\b{k}\b", v, text, flags=re.IGNORECASE)

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
# CLEAN OCR TEXT
# ======================================================

def clean_text(text):

    if not text:
        return ""

    text = normalize_numerals(text)

    text = text.replace("￾", "")
    text = text.replace("�", "")

    text = re.sub(r"[|•▪●◆■]", " ", text)

    # fix encoding artifacts
    text = text.replace("â € \"", "-")
    text = text.replace("â € œ", "-")
    text = text.replace("â €", "-")

    text = re.sub(r'\.\s*\n\s*', '. ', text)

    text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1 \2", text)

    text = re.sub(r'(?<=[a-z0-9])\.(?=[A-Za-z])', '. ', text)
    text = re.sub(r'(?<=[a-z0-9]):(?=[A-Za-z])', ': ', text)
    text = re.sub(r'(?<=[a-z0-9]),(?=[A-Za-z])', ', ', text)

    text = re.sub(r'\s*/\s*', ' / ', text)

    text = re.sub(r'\.{2,}', '.', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def grammar_cleanup(text):

    fixes = {
        "forewarned": "",
        "The management of fertilizer": "Fertilizer management",
        "intercommunal": "Intercropping",
        "Correcting the number of plants per hectare": "Plant population management"
    }

    for k,v in fixes.items():
        text = text.replace(k,v)

    return text
# ======================================================
# LANGUAGE DETECTION
# ======================================================

def detect_language(text):

    try:

        lang = detect(text)

        if lang in LANG_MAP:
            return LANG_MAP[lang]

        if lang == "en":
            return "eng_Latn"

        return "hin_Deva"

    except Exception:
        return "hin_Deva"


# ======================================================
# TRANSLATION SKIP RULES
# ======================================================

def should_translate(text):

    text = text.strip()

    if not text:
        return False

    if re.fullmatch(r"[0-9./-]+", text):
        return False

    return True


# ======================================================
# POST TRANSLATION CLEANUPS
# ======================================================

def fix_sentence_spacing(text):

    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)

    text = re.sub(r',([A-Za-z])', r', \1', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def remove_duplicate_words(text):
    return re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)
    return text


def fix_joined_words(text):

    text = re.sub(r'pigeonpea', 'pigeon pea', text, flags=re.IGNORECASE)
    text = re.sub(r'seedrate', 'seed rate', text, flags=re.IGNORECASE)
    text = re.sub(r'wheatcrop', 'wheat crop', text, flags=re.IGNORECASE)
    text = re.sub(r'plantgrowth', 'plant growth', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ======================================================
# ENGLISH POLISHING (QUALITY IMPROVEMENT)
# ======================================================

def polish_english_text(text):

    if not text:
        return text

    # fix common grammar issues
    replacements = {

        "one of the important pulses crops": "an important pulse crop",

        "grown in season": "grown during the season",

        "grows on": "grows well in",

        "does not grow well": "does not perform well",

        "600 to 750 mm thick": "600 to 750 mm rainfall",

        "mainly in Kharif": "mainly during the Kharif season",

        "It is grown in season": "It is grown during the cropping season",

        "pigeon pea crop crop": "pigeon pea crop",

        "in hectare": "per hectare",

        "kg during sowing": "kg applied during sowing",

        "should be spread in the field": "should be applied to the field",

        "Eggs of the parasite Trichoderma": "Seeds should be treated with Trichoderma",

        "straws should be swept with the help of a stick": "the crop should be threshed",
        
        "processed at 5 grams per kg of seed": "applied at 5 g per kg of seed",
        
        "should be sprayed as per requirement": "should be sprayed when necessary",

        "should be treated with trichoderma should be applied": "seeds should be treated with Trichoderma"
                
            }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    # remove duplicate spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ======================================================
# MAIN TRANSLATION FUNCTION
# ======================================================

def translate_text(text, force_src=None):

    try:

        text = clean_text(text)

        if not should_translate(text):
            return text

        text = apply_pre_glossary(text)

        if re.search(r'[\u0900-\u097F]', text):
            src_lang = "mar_Deva"
        elif force_src:
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

        translated = normalize_terms(translated)

        translated = apply_post_glossary(translated)
        
        translated = remove_duplicate_words(translated)
        
        translated = fix_sentence_spacing(translated)
        
        translated = fix_joined_words(translated)
        
        translated = polish_english_text(translated)
        
        translated = grammar_cleanup(translated)

        return translated

    except Exception as e:

        print("Translation error:", e)

        return text
