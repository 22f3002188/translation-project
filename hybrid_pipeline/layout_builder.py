from bs4 import BeautifulSoup, NavigableString
from hybrid_pipeline.translator import translate_text
import re


# ----------------------------------------
# Clean OCR text
# ----------------------------------------
def clean_ocr_text(text):

    if not text:
        return text

    # Remove bullet characters
    text = re.sub(r"[•▪●◆■]", " ", text)

    # Merge broken line words
    text = re.sub(r"(\w)\s*\n\s*(\w)", r"\1\2", text)

    # Remove line breaks
    text = text.replace("\n", " ")

    # Normalize spacing
    text = re.sub(r"\s+", " ", text)

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

        columns = len(rows[0].find_all(["td", "th"]))
        col_lengths = [0] * columns

        # Measure column text length
        for row in rows:
            cells = row.find_all(["td", "th"])
            for i, cell in enumerate(cells):
                text = cell.get_text(" ", strip=True)
                if len(text) > col_lengths[i]:
                    col_lengths[i] = len(text)

        total = sum(col_lengths) or 1

        # Apply proportional width
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

    soup = translate_headings_and_paragraphs(soup)

    soup = translate_bullets(soup)

    soup = translate_tables(soup)

    soup = translate_div_blocks(soup)

    soup = fix_images(soup)

    print(" Layout rebuild + translation completed\n")

    return soup
