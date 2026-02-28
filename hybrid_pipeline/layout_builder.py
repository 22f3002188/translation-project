from bs4 import BeautifulSoup, NavigableString
from hybrid_pipeline.translator import translate_text
import re

# Common agricultural and structural words
SAFE_WORDS = {
    "the", "and", "with", "from", "that", "this", "should",
    "will", "are", "was", "for", "per", "crop", "soil",
    "seed", "water", "variety", "plants", "plant",
    "growth", "yield", "disease", "pigeon", "pea",
    "hectare", "kg", "gm", "field", "land", "storage",
    "fungus", "moisture", "flowering", "harvest"
}

def repair_word_boundaries(text):

    if not text:
        return text

    words = text.split()
    repaired_words = []

    for token in words:

        lower_token = token.lower()

        # Skip short words
        if len(token) < 7:
            repaired_words.append(token)
            continue

        split_done = False

        # Try safe split positions
        for i in range(3, len(token) - 3):

            left = lower_token[:i]
            right = lower_token[i:]

            if left in SAFE_WORDS and right in SAFE_WORDS:
                repaired_words.append(token[:i] + " " + token[i:])
                split_done = True
                break

        if not split_done:
            repaired_words.append(token)

    text = " ".join(repaired_words)

    # Specific safe fixes
    text = re.sub(r'pigeonpea', 'pigeon pea', text, flags=re.IGNORECASE)

    # Fix uppercase merges
    text = re.sub(r'([A-Z]{3,})([A-Z][a-z])', r'\1 \2', text)

    # Normalize spacing
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
# ----------------------------------------
# Clean OCR text
# ----------------------------------------
def clean_ocr_text(text):

    if not text:
        return text

    text = re.sub(r"[•▪●◆■]", " ", text)

    text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1\2", text)

    text = re.sub(r'(?<=[a-z0-9])\.(?=[A-Za-z])', '. ', text)
    text = re.sub(r'(?<=[a-z0-9]):(?=[A-Za-z])', ': ', text)
    text = re.sub(r'(?<=[a-z0-9]),(?=[A-Za-z])', ', ', text)

    text = re.sub(r'\b(\w+)\.\s*\1\b', r'\1', text, flags=re.IGNORECASE)

    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

    text = re.sub(r'\s*/\s*', ' / ', text)

    text = re.sub(r'\.{2,}', '.', text)

    text = re.sub(r'\s+', ' ', text)

    #  NEW: Repair glued words
    text = repair_word_boundaries(text)

    return text.strip()
# ----------------------------------------
# Normalize layout (REMOVE OCR DIRTY STYLES SAFELY)
# ----------------------------------------
def normalize_layout(soup):

    print(" Normalizing layout...")

    for tag in soup.find_all(True):

        if tag.has_attr("style"):

            style = tag["style"]

            # Remove ALL problematic OCR layout styles
            style = re.sub(r"height\s*:[^;]+;?", "", style)
            style = re.sub(r"width\s*:[^;]+;?", "", style)
            style = re.sub(r"font-size\s*:[^;]+;?", "", style)
            style = re.sub(r"position\s*:[^;]+;?", "", style)
            style = re.sub(r"top\s*:[^;]+;?", "", style)
            style = re.sub(r"left\s*:[^;]+;?", "", style)
            style = re.sub(r"line-height\s*:[^;]+;?", "", style)

            # Force clean block flow
            style += """
                display:block;
                white-space:normal;
                word-wrap:break-word;
            """

            tag["style"] = style

    print(" Layout normalized\n")
    return soup


# ----------------------------------------
# SAFE TEXT NODE TRANSLATION
# ----------------------------------------
def translate_text_nodes(tag):

    for child in list(tag.children):

        if isinstance(child, NavigableString):

            original_text = str(child)

            if not original_text.strip():
                continue

            cleaned = clean_ocr_text(original_text)

            if cleaned:
                translated = translate_text(cleaned)
                child.replace_with(translated)

        else:
            translate_text_nodes(child)

# ----------------------------------------
# Translate headings + paragraphs
# ----------------------------------------
def translate_headings_and_paragraphs(soup):

    print(" Translating headings + paragraphs...")

    tags = soup.find_all(["h1", "h2", "h3", "h4", "p"])

    print(f"   Total text blocks: {len(tags)}")

    for tag in tags:
        translate_text_nodes(tag)

    print(" Paragraph translation completed\n")
    return soup

# ----------------------------------------
# Translate bullet lists
# ----------------------------------------
def translate_bullets(soup):

    print(" Translating bullet lists...")

    bullets = soup.find_all("li")

    print(f"   Bullets found: {len(bullets)}")

    for li in bullets:
        translate_text_nodes(li)

    print(" Bullet translation completed\n")
    return soup


# ----------------------------------------
# Translate + Fix tables (Structure Safe)
# ----------------------------------------
def translate_tables(soup):

    print(" Translating tables...")

    tables = soup.find_all("table")

    print(f"   Tables detected: {len(tables)}")

    for table in tables:

        # Clean table style (keep your original layout intention)
        table["style"] = """
            width:85%;
            margin-left:auto;
            margin-right:auto;
            border-collapse:collapse;
            table-layout:fixed;
            margin-top:25px;
            margin-bottom:25px;
            font-size:12px;
        """

        rows = table.find_all("tr")

        if not rows:
            continue

        # ------------------------------
        # 🔹 Clean fragmented header text
        # ------------------------------
        for th in table.find_all("th"):
            header_text = th.get_text(" ", strip=True)
            header_text = re.sub(r'\s+', ' ', header_text)
            th.clear()
            th.append(header_text)

        # ------------------------------
        # 🔹 Measure column width based on content length
        # ------------------------------
        first_row_cells = rows[0].find_all(["td", "th"])
        columns = len(first_row_cells)
        col_lengths = [0] * columns

        for row in rows:
            cells = row.find_all(["td", "th"])
            for i, cell in enumerate(cells):
                text = cell.get_text(" ", strip=True)
                text = re.sub(r'\s+', ' ', text)
                if len(text) > col_lengths[i]:
                    col_lengths[i] = len(text)

        total = sum(col_lengths) or 1

        # ------------------------------
        # 🔹 Apply proportional width + clean text
        # ------------------------------
        for row in rows:
            cells = row.find_all(["td", "th"])

            for i, cell in enumerate(cells):

                width = (col_lengths[i] / total) * 100

                if width < 8:
                    width = 8
                if width > 50:
                    width = 50

                cell["style"] = f"""
                    width:{width}%;
                    border:1px solid black;
                    padding:8px;
                    text-align:center;
                    vertical-align:middle;
                    word-wrap:break-word;
                    overflow-wrap:break-word;
                    white-space:normal;
                """

                # Clean OCR noise before translation
                full_text = cell.get_text(" ", strip=True)
                full_text = clean_ocr_text(full_text)

                cell.clear()
                cell.append(full_text)

                # Translate content safely
                translate_text_nodes(cell)

    print(" Table translation completed\n")
    return soup

# ----------------------------------------
# Translate remaining div blocks safely
# ----------------------------------------
def translate_div_blocks(soup):

    divs = soup.find_all("div")

    for div in divs:
        translate_text_nodes(div)

    return soup

# ----------------------------------------
# Merge small consecutive div blocks into proper paragraphs
# ----------------------------------------
def merge_small_div_blocks(soup):

    body = soup.body
    if not body:
        return soup

    new_elements = []
    buffer = ""

    for element in body.find_all(["div", "p"], recursive=False):

        text = element.get_text(" ", strip=True)

        if not text:
            continue

        # Only merge very small fragments (less aggressive)
        if len(text) < 120:
            buffer += " " + text
        else:
            if buffer:
                new_p = soup.new_tag("p")
                new_p.string = buffer.strip()
                new_elements.append(new_p)
                buffer = ""

            new_elements.append(element)

    if buffer:
        new_p = soup.new_tag("p")
        new_p.string = buffer.strip()
        new_elements.append(new_p)

    body.clear()

    for el in new_elements:
        body.append(el)

    return soup
# ----------------------------------------
# Fix images
# ----------------------------------------
def fix_images(soup):

    print(" Fixing images...")

    for img in soup.find_all("img"):

        img["style"] = """
            max-width:60%;
            height:auto;
            display:block;
            margin:15px auto;
        """

    print(" Images fixed\n")
    return soup


# ----------------------------------------
# MAIN LAYOUT REBUILDER
# ----------------------------------------
def rebuild_layout(html_path):

    print(f"\n Rebuilding layout: {html_path}\n")

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    soup = normalize_layout(soup)

    soup = merge_small_div_blocks(soup)

    soup = translate_headings_and_paragraphs(soup)

    soup = translate_bullets(soup)

    soup = translate_tables(soup)

    soup = translate_div_blocks(soup)

    soup = fix_images(soup)

    print(" Layout rebuild + translation completed\n")

    return soup
