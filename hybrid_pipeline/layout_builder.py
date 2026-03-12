# from bs4 import BeautifulSoup, NavigableString
# from hybrid_pipeline.translator import translate_text
# import re

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
# # ----------------------------------------
# # Clean OCR text
# # ----------------------------------------
# def clean_ocr_text(text):

#     if not text:
#         return text

#     text = re.sub(r"[•▪●◆■]", " ", text)

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

#     #  NEW: Repair glued words
#     text = repair_word_boundaries(text)

#     return text.strip()
# # ----------------------------------------
# # Normalize layout (REMOVE OCR DIRTY STYLES SAFELY)
# # ----------------------------------------
# def normalize_layout(soup):

#     print(" Normalizing layout...")

#     for tag in soup.find_all(True):

#         if tag.has_attr("style"):

#             style = tag["style"]

#             # Remove ALL problematic OCR layout styles
#             style = re.sub(r"height\s*:[^;]+;?", "", style)
#             style = re.sub(r"width\s*:[^;]+;?", "", style)
#             style = re.sub(r"font-size\s*:[^;]+;?", "", style)
#             style = re.sub(r"position\s*:[^;]+;?", "", style)
#             style = re.sub(r"top\s*:[^;]+;?", "", style)
#             style = re.sub(r"left\s*:[^;]+;?", "", style)
#             style = re.sub(r"line-height\s*:[^;]+;?", "", style)

#             # Force clean block flow
#             style += """
#                 display:block;
#                 white-space:normal;
#                 word-wrap:break-word;
#             """

#             tag["style"] = style

#     print(" Layout normalized\n")
#     return soup


# # ----------------------------------------
# # SAFE TEXT NODE TRANSLATION
# # ----------------------------------------
# def translate_text_nodes(tag):

#     for child in list(tag.children):

#         if isinstance(child, NavigableString):

#             original_text = str(child)

#             if not original_text.strip():
#                 continue

#             cleaned = clean_ocr_text(original_text)

#             if cleaned:
#                 translated = translate_text(cleaned)
#                 child.replace_with(translated)

#         else:
#             translate_text_nodes(child)

# # ----------------------------------------
# # Translate headings + paragraphs
# # ----------------------------------------
# def translate_headings_and_paragraphs(soup):

#     print(" Translating headings + paragraphs...")

#     tags = soup.find_all(["h1", "h2", "h3", "h4", "p"])

#     print(f"   Total text blocks: {len(tags)}")

#     for tag in tags:
#         translate_text_nodes(tag)

#     print(" Paragraph translation completed\n")
#     return soup

# # ----------------------------------------
# # Translate bullet lists
# # ----------------------------------------
# def translate_bullets(soup):

#     print(" Translating bullet lists...")

#     bullets = soup.find_all("li")

#     print(f"   Bullets found: {len(bullets)}")

#     for li in bullets:
#         translate_text_nodes(li)

#     print(" Bullet translation completed\n")
#     return soup

# def remove_standalone_page_numbers(soup):

#     for tag in soup.find_all(["p", "div"]):

#         text = tag.get_text(strip=True)

#         # Remove standalone numbers (1-3 digits only)
#         if text.isdigit() and 1 <= len(text) <= 3:
#             tag.decompose()

#     return soup

# # ----------------------------------------
# # Translate + Fix tables (Structure Safe)
# # ----------------------------------------
# def translate_tables(soup):

#     print(" Translating tables...")

#     tables = soup.find_all("table")

#     print(f"   Tables detected: {len(tables)}")

#     for table in tables:

#         # Clean table style (keep your original layout intention)
#         table["style"] = """
#             width:85%;
#             margin-left:auto;
#             margin-right:auto;
#             border-collapse:collapse;
#             table-layout:fixed;
#             margin-top:25px;
#             margin-bottom:25px;
#             font-size:12px;
#         """

#         rows = table.find_all("tr")

#         if not rows:
#             continue

#         # ------------------------------
#         # 🔹 Clean fragmented header text
#         # ------------------------------
#         for th in table.find_all("th"):
#             header_text = th.get_text(" ", strip=True)
#             header_text = re.sub(r'\s+', ' ', header_text)
#             th.clear()
#             th.append(header_text)

#         # ------------------------------
#         # 🔹 Measure column width based on content length
#         # ------------------------------
#         first_row_cells = rows[0].find_all(["td", "th"])
#         columns = len(first_row_cells)
#         col_lengths = [0] * columns

#         for row in rows:
#             cells = row.find_all(["td", "th"])
#             for i, cell in enumerate(cells):
#                 text = cell.get_text(" ", strip=True)
#                 text = re.sub(r'\s+', ' ', text)
#                 if len(text) > col_lengths[i]:
#                     col_lengths[i] = len(text)

#         total = sum(col_lengths) or 1

#         # ------------------------------
#         # 🔹 Apply proportional width + clean text
#         # ------------------------------
#         for row in rows:
#             cells = row.find_all(["td", "th"])

#             for i, cell in enumerate(cells):

#                 width = (col_lengths[i] / total) * 100

#                 if width < 8:
#                     width = 8
#                 if width > 50:
#                     width = 50

#                 cell["style"] = f"""
#                     width:{width}%;
#                     border:1px solid black;
#                     padding:8px;
#                     text-align:center;
#                     vertical-align:middle;
#                     word-wrap:break-word;
#                     overflow-wrap:break-word;
#                     white-space:normal;
#                 """

#                 # Clean OCR noise before translation
#                 full_text = cell.get_text(" ", strip=True)
#                 full_text = clean_ocr_text(full_text)

#                 cell.clear()
#                 cell.append(full_text)

#                 # Translate content safely
#                 translate_text_nodes(cell)

#     print(" Table translation completed\n")
#     return soup

# # ----------------------------------------
# # Translate remaining div blocks safely
# # ----------------------------------------
# def translate_div_blocks(soup):

#     divs = soup.find_all("div")

#     for div in divs:
#         translate_text_nodes(div)

#     return soup

# # ----------------------------------------
# # Merge small consecutive div blocks into proper paragraphs
# # ----------------------------------------
# def merge_small_div_blocks(soup):

#     body = soup.body
#     if not body:
#         return soup

#     new_elements = []
#     buffer = ""

#     for element in body.find_all(["div", "p"], recursive=False):

#         text = element.get_text(" ", strip=True)

#         if not text:
#             continue

#         # Only merge very small fragments (less aggressive)
#         if len(text) < 120:
#             buffer += " " + text
#         else:
#             if buffer:
#                 new_p = soup.new_tag("p")
#                 new_p.string = buffer.strip()
#                 new_elements.append(new_p)
#                 buffer = ""

#             new_elements.append(element)

#     if buffer:
#         new_p = soup.new_tag("p")
#         new_p.string = buffer.strip()
#         new_elements.append(new_p)

#     body.clear()

#     for el in new_elements:
#         body.append(el)

#     return soup
# # ----------------------------------------
# # Fix images
# # ----------------------------------------
# def fix_images(soup):

#     print(" Fixing images...")

#     for img in soup.find_all("img"):

#         img["style"] = """
#             max-width:60%;
#             height:auto;
#             display:block;
#             margin:15px auto;
#         """

#     print(" Images fixed\n")
#     return soup



# # ----------------------------------------
# # MAIN LAYOUT REBUILDER
# # ----------------------------------------
# def rebuild_layout(html_path):

#     print(f"\n Rebuilding layout: {html_path}\n")

#     with open(html_path, "r", encoding="utf-8") as f:
#         soup = BeautifulSoup(f, "html.parser")

#     soup = normalize_layout(soup)

#     soup = remove_standalone_page_numbers(soup)

#     soup = merge_small_div_blocks(soup)

#     soup = translate_headings_and_paragraphs(soup)

#     soup = translate_bullets(soup)

#     soup = translate_tables(soup)

#     soup = translate_div_blocks(soup)

#     soup = fix_images(soup)

#     print(" Layout rebuild + translation completed\n")

#     return soup


from bs4 import BeautifulSoup, NavigableString
from hybrid_pipeline.translator import translate_text
import re


# ======================================================
# FIX GLUED WORDS
# ======================================================

SAFE_WORDS = {
    "the","and","with","from","that","this","should","will","are","was",
    "for","per","crop","soil","seed","water","variety","plants","plant",
    "growth","yield","disease","pigeon","pea","hectare","kg","gm",
    "field","land","storage","fungus","moisture","flowering","harvest"
}

def repair_word_boundaries(text):

    if not text:
        return text

    words = text.split()
    repaired_words = []

    for token in words:

        lower = token.lower()

        if len(token) < 7:
            repaired_words.append(token)
            continue

        split_done = False

        for i in range(3, len(token) - 3):

            left = lower[:i]
            right = lower[i:]

            if left in SAFE_WORDS and right in SAFE_WORDS:
                repaired_words.append(token[:i] + " " + token[i:])
                split_done = True
                break

        if not split_done:
            repaired_words.append(token)

    text = " ".join(repaired_words)

    text = re.sub(r'pigeonpea', 'pigeon pea', text, flags=re.IGNORECASE)

    return text.strip()

def reorder_blocks(soup):

    positioned = []

    for tag in soup.find_all(["span","p","div"]):

        style = tag.get("style","")

        top = re.search(r'top\s*:\s*([\d.]+)', style)
        left = re.search(r'left\s*:\s*([\d.]+)', style)

        if not top or not left:
            continue

        try:
            t = float(top.group(1))
            l = float(left.group(1))
        except:
            continue

        text = tag.get_text(strip=True)

        if not text:
            continue

        positioned.append({
            "top": t,
            "left": l,
            "node": tag
        })

    if not positioned:
        return soup

    # detect page midpoint
    max_left = max(b["left"] for b in positioned)
    mid = max_left / 2

    left_col = [b for b in positioned if b["left"] < mid]
    right_col = [b for b in positioned if b["left"] >= mid]

    # sort vertically
    left_col.sort(key=lambda b: b["top"])
    right_col.sort(key=lambda b: b["top"])

    # choose reading order
    # if right column starts higher → booklet layout
    if right_col and left_col and right_col[0]["top"] < left_col[0]["top"]:
        ordered = right_col + left_col
    else:
        ordered = left_col + right_col

    body = soup.body

    # clear body
    for node in list(body.children):
        node.extract()

    # append in correct order
    for b in ordered:
        body.append(b["node"])

    return soup

def reflow_paragraphs(soup):

    for p in soup.find_all("p"):

        text = p.get_text(" ", strip=True)

        if not text:
            continue

        # remove excessive line breaks
        text = re.sub(r'\s+', ' ', text)

        # fix broken sentences
        text = re.sub(r'\.\s+', '. ', text)

        p.clear()
        p.append(text)

    return soup
# ======================================================
# NUMERAL NORMALIZATION
# ======================================================

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


# ======================================================
# CLEAN OCR TEXT
# ======================================================

def clean_ocr_text(text):

    if not text:
        return text
        

    text = normalize_numerals(text)

    text = text.replace("￾","") 

    text = text.replace("�", "")

    text = re.sub(r"[|•▪●◆■]", " ", text)

    # merge newline after punctuation
    text = re.sub(r'\.\s*\n\s*', '. ', text)

    # fix hyphen line breaks
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # join lines with space
    text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1 \2", text)

    # punctuation spacing
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([,:])([A-Za-z])', r'\1 \2', text)

    # camelCase fix
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # number-letter merge
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

    text = re.sub(r'\s*/\s*', ' / ', text)

    text = re.sub(r'\.{2,}', '.', text)

    text = re.sub(r'\s+', ' ', text)

    text = text.replace(" X ", " × ")
    text = text.replace(" x ", " × ")

    text = repair_word_boundaries(text)

    return text.strip()

    
def clean_headings(soup):

    for tag in soup.find_all(["h1","h2","h3"]):

        text = tag.get_text(strip=True)

        text = text.rstrip(":").strip()

        # convert fake headings to paragraphs
        if len(text.split()) > 6:
            tag.name = "p"

        # remove very small headings
        if len(text) < 2:
            tag.name = "p"

        tag.clear()
        tag.append(text)

    return soup

# ======================================================
# REMOVE OCR ARTIFACTS
# ======================================================
def remove_artifacts(soup):

    for node in soup.find_all(string=True):

        txt = node.strip().lower()

        if not txt:
            continue

        # remove OCR garbage like html/body/head
        if txt in ["html", "body", "head"]:
            node.extract()
            continue

        # remove table labels
        if "table no" in txt or "तक्ता" in txt:

            parent = node.parent

            if parent:
                parent.decompose()
            else:
                node.extract()

    return soup


# ======================================================
# NORMALIZE OCR LAYOUT
# ======================================================

def normalize_layout(soup):

    for tag in soup.find_all(True):

        if tag.has_attr("style"):

            style = tag["style"]

            style = re.sub(r"position\s*:[^;]+;?", "", style)
            style = re.sub(r"top\s*:[^;]+;?", "", style)
            style = re.sub(r"left\s*:[^;]+;?", "", style)
            style = re.sub(r"width\s*:[^;]+;?", "", style)
            style = re.sub(r"height\s*:[^;]+;?", "", style)

            style += """
            display:block;
            white-space:normal;
            word-wrap:break-word;
            """

            tag["style"] = style

    return soup


# ======================================================
# MERGE SPAN FRAGMENTS
# ======================================================

def merge_spans(soup):

    for p in soup.find_all("p"):

        texts = []

        for elem in p.descendants:

            if isinstance(elem, NavigableString):

                txt = str(elem).strip()

                if txt:
                    texts.append(txt)

        if texts:

            merged = " ".join(texts)

            merged = re.sub(r'\s+', ' ', merged)

            p.clear()
            p.append(merged)

    return soup



# ======================================================
# TRANSLATE MAIN BLOCKS
# ======================================================

def translate_blocks(soup):

    # Only translate structural text blocks
    blocks = soup.find_all(["h1", "h2", "h3", "p", "li"])

    for block in blocks:

        # Skip blocks inside tables
        if block.find_parent("table"):
            continue

        text = clean_ocr_text(block.get_text(" ", strip=True))

        if not text:
            continue

        # Avoid translating very small fragments
        if len(text) < 3:
            continue

        try:

            translated = translate_text(text)

            block.clear()
            block.append(translated)

        except Exception as e:
            print("Block translation failed:", e)

    return soup


# ======================================================
# TRANSLATE REMAINING TEXT
# ======================================================
def translate_remaining_text(soup):

    for node in soup.find_all(string=True):

        text = str(node).strip()

        if not text:
            continue

        parent = node.parent.name

        # Skip main translated blocks
        if parent in ["p", "h1", "h2", "h3", "li"]:
            continue

        # Skip tables (already translated)
        if parent in ["td", "th", "table"]:
            continue

        # Skip scripts/styles
        if parent in ["script", "style"]:
            continue

        # Skip very small fragments
        if len(text) < 3:
            continue

        try:
            translated = translate_text(text)
            node.replace_with(translated)
        except:
            continue

    return soup

# ======================================================
# FIX TABLE STRUCTURE
# ======================================================

def fix_table_year_column(soup):

    tables = soup.find_all("table")

    for table in tables:

        for row in table.find_all("tr"):

            cells = row.find_all(["td","th"])

            if len(cells) == 5:

                year_cell = soup.new_tag("td")

                next_node = row.find_next(string=True)

                year_match = None

                if next_node:
                    year_match = re.search(r"\b(19|20)\d{2}\b", next_node)

                if year_match:
                    year_cell.string = year_match.group()
                    next_node.extract()
                else:
                    year_cell.string = ""

                cells[0].insert_after(year_cell)

    return soup


# ======================================================
# TABLE HEADER CLEAN
# ======================================================

def refine_table_header(text):

    if not text:
        return text

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"^The\s+", "", text, flags=re.IGNORECASE)

    text = re.sub(r"\(\s*kg\s*\)", "(kg)", text, flags=re.IGNORECASE)
    text = re.sub(r"\(\s*cm\s*\)", "(cm)", text, flags=re.IGNORECASE)

    text = text.strip().capitalize()

    return text


# ======================================================
# TRANSLATE TABLES
# ======================================================
def translate_tables(soup):

    tables = soup.find_all("table")

    for table in tables:

        table["style"] = """
        width:100%;
        border-collapse:collapse;
        table-layout:auto;
        margin-top:20px;
        margin-bottom:20px;
        font-size:12px;
        """

        for row in table.find_all("tr"):

            cells = row.find_all(["td","th"])

            for cell in cells:

                text = clean_ocr_text(cell.get_text(" ", strip=True))

                if not text:
                    continue

                # If cell contains only numbers/measurements
                if re.fullmatch(r"[0-9xX./%\- ]+", text):

                    cell.clear()
                    cell.append(text)

                else:

                    translated = translate_text(text)

                    if cell.name == "th":
                        translated = refine_table_header(translated)

                    cell.clear()
                    cell.append(translated)

                cell["style"] = """
                border:1px solid #444;
                padding:8px;
                text-align:center;
                vertical-align:middle;
                white-space:normal;
                word-break:normal;
                overflow-wrap:break-word;
                font-size:12px;
                line-height:1.4;
                """

    return soup

# ======================================================
# FIX IMAGES
# ======================================================

def fix_images(soup):

    for img in soup.find_all("img"):

        if not img.get("src"):
            continue

        img["style"] = """
        max-width:70%;
        height:auto;
        display:block;
        margin:20px auto;
        """

    return soup

def extract_top(style):

    if not style:
        return None

    m = re.search(r'top\s*:\s*([0-9\.]+)', style)

    if m:
        try:
            return float(m.group(1))
        except:
            return None

    return None


def sort_blocks_by_top(soup):

    body = soup.body
    if not body:
        return soup

    blocks = []

    for div in soup.find_all("div"):

        style = div.get("style", "")

        if "top" not in style:
            continue

        m = re.search(r'top\s*:\s*([0-9\.]+)', style)

        if not m:
            continue

        try:
            top = float(m.group(1))
        except:
            continue

        blocks.append((top, div))

    if not blocks:
        return soup

    # sort by vertical position
    blocks.sort(key=lambda x: x[0])

    # remove from DOM
    for _, div in blocks:
        div.extract()

    # append in correct order
    for _, div in blocks:
        body.append(div)

    return soup
# ======================================================
# REMOVE PAGE NUMBERS
# ======================================================

def remove_page_numbers(soup):

    for tag in soup.find_all(["p","div","span"]):

        text = tag.get_text(strip=True)

        if re.fullmatch(r"page\s*\d+", text.lower()):
            tag.decompose()
            continue

        if re.fullmatch(r"[-() ]*\d{1,3}[-() ]*", text):
            tag.decompose()

    return soup


# ======================================================
# MAIN PIPELINE
# ======================================================
def rebuild_layout(html_path):

    print(f"Processing layout: {html_path}")

    with open(html_path,"r",encoding="utf-8") as f:
        soup = BeautifulSoup(f,"html.parser")

    soup = remove_artifacts(soup)

    soup = reorder_blocks(soup)
    
    soup = sort_blocks_by_top(soup)
    
    soup = normalize_layout(soup)
    
    soup = remove_page_numbers(soup)
    
    soup = merge_spans(soup)
    
    soup = reflow_paragraphs(soup)
    
    soup = clean_headings(soup)
    
    soup = fix_table_year_column(soup)
    
    soup = translate_blocks(soup)
    
    soup = translate_tables(soup)
    
    soup = translate_remaining_text(soup)
    
    soup = fix_images(soup)

    return soup
