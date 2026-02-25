# layout_builder.py
# from bs4 import BeautifulSoup
# from hybrid_pipeline.translator import translate_text
# import re


# # ----------------------------------------
# # Clean OCR text
# # ----------------------------------------
# def clean_ocr_text(text):

#     if not text:
#         return text

#     text = re.sub(r"\s+", " ", text)
#     return text.strip()


# # ----------------------------------------
# # Normalize layout (remove overlaps)
# # ----------------------------------------
# def normalize_layout(soup):

#     print(" Normalizing layout...")

#     for tag in soup.find_all(["div", "p", "span"]):

#         if tag.has_attr("style"):

#             style = tag["style"]

#             # Remove fixed height/width
#             style = re.sub(r"height\s*:[^;]+;?", "", style)
#             style = re.sub(r"width\s*:[^;]+;?", "", style)

#             style += """
#                 display:block;
#                 white-space:normal;
#                 word-wrap:break-word;
#             """

#             tag["style"] = style

#     print(" Layout normalized\n")

#     return soup


# # ----------------------------------------
# # Translate headings + paragraphs
# # ----------------------------------------
# def translate_headings_and_paragraphs(soup):

#     print(" Translating headings + paragraphs...")

#     tags = soup.find_all(
#         ["h1", "h2", "h3", "h4", "p", "strong", "b"]
#     )

#     print(f"   Total text blocks: {len(tags)}")

#     for tag in tags:

#         text = tag.get_text(" ", strip=True)

#         if not text:
#             continue

#         text = clean_ocr_text(text)

#         translated = translate_text(text)

#         tag.clear()
#         tag.append(translated)

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

#         text = li.get_text(" ", strip=True)

#         if not text:
#             continue

#         text = clean_ocr_text(text)

#         translated = translate_text(text)

#         li.clear()
#         li.append(translated)

#     print(" Bullet translation completed\n")

#     return soup


# # ----------------------------------------
# # Translate + Fix tables (UPDATED ONLY HERE)
# # ----------------------------------------
# def translate_tables(soup):

#     print(" Translating tables...")

#     tables = soup.find_all("table")

#     print(f"   Tables detected: {len(tables)}")

#     for table in tables:

#         # Keep table centered + same size
#         table["style"] = """
#             width:85%;
#             margin-left:auto;
#             margin-right:auto;
#             border-collapse:collapse;
#             table-layout:fixed;
#             margin-top:25px;
#             margin-bottom:25px;
#             font-size:11px;
#         """

#         rows = table.find_all("tr")

#         if not rows:
#             continue

#         columns = len(rows[0].find_all(["td", "th"]))

#         col_lengths = [0] * columns

#         # Measure text length per column
#         for row in rows:

#             cells = row.find_all(["td", "th"])

#             for i, cell in enumerate(cells):

#                 text = cell.get_text(" ", strip=True)

#                 if len(text) > col_lengths[i]:
#                     col_lengths[i] = len(text)

#         total = sum(col_lengths) or 1

#         # Apply width proportionally
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

#         # ------------------------------
#         # UPDATED TRANSLATION SECTION
#         # ------------------------------
#         for cell in table.find_all(["td", "th"]):

#             text = cell.get_text(" ", strip=True)

#             if not text:
#                 continue

#             text = clean_ocr_text(text)

#             # Force Marathi source for table cells
#             translated = translate_text(
#                 text,
#                 force_src="mar_Deva"
#             )

#             cell.clear()
#             cell.append(translated)

#     print(" Table translation completed\n")

#     return soup


# # ----------------------------------------
# # Fix images
# # ----------------------------------------
# def fix_images(soup):

#     print(" Fixing images...")

#     for img in soup.find_all("img"):

#         img["style"] = """
#             max-width:55%;
#             height:auto;
#             display:block;
#             margin:20px auto;
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

#     # Step-wise processing
#     soup = normalize_layout(soup)

#     soup = translate_headings_and_paragraphs(soup)

#     soup = translate_bullets(soup)

#     soup = translate_tables(soup)

#     soup = fix_images(soup)

#     print(" Layout rebuild + translation completed\n")

#     return soup


# # layout_builder.py
# # FINAL STABLE — TRANSLATION + LAYOUT SAFE


# layout_builder.py
# FINAL STABLE — TABLE + PAGINATION + SPEED SAFE

from bs4 import BeautifulSoup
from hybrid_pipeline.translator import translate_text
import re


# ----------------------------------------
# Clean OCR text
# ----------------------------------------
def clean_ocr_text(text):

    if not text:
        return text

    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ----------------------------------------
# Normalize layout
# ----------------------------------------
def normalize_layout(soup):

    print(" Normalizing layout...")

    for tag in soup.find_all(True):

        if tag.has_attr("style"):

            style = tag["style"]

            style = re.sub(r"position\s*:\s*absolute;?", "", style)
            style = re.sub(r"top\s*:[^;]+;?", "", style)
            style = re.sub(r"left\s*:[^;]+;?", "", style)
            style = re.sub(r"float\s*:[^;]+;?", "", style)
            style = re.sub(r"height\s*:[^;]+;?", "", style)

            tag["style"] = style

    return soup


# ----------------------------------------
# Translate ALL visible text
# (Captions + headings + numerals covered)
# ----------------------------------------
def translate_all_text(soup):

    print(" Translating text...")

    for element in soup.find_all(string=True):

        parent = element.parent.name

        if parent in ["script", "style"]:
            continue

        text = element.strip()

        if not text:
            continue

        cleaned = clean_ocr_text(text)

        translated = translate_text(
            cleaned,
            force_src="mar_Deva"
        )

        element.replace_with(translated)

    return soup


# ----------------------------------------
# FIX TABLES — FINAL PAGINATION SAFE
# ----------------------------------------
def fix_tables(soup):

    print(" Fixing tables...")

    for table in soup.find_all("table"):

        # --------------------------------
        # SAFE WRAPPER (NO BIG MARGINS)
        # --------------------------------
        wrapper = soup.new_tag("div")

        wrapper["style"] = """
            width:100%;
            clear:both;
            margin-top:10px;
            margin-bottom:10px;
            page-break-inside:auto;
        """

        table.wrap(wrapper)

        # --------------------------------
        # TABLE STYLE
        # --------------------------------
        table["style"] = """
            width:100%;
            border-collapse:collapse;
            table-layout:auto;
            page-break-inside:auto;
        """

        # --------------------------------
        # HEADER SAFE (No repeat overlap)
        # --------------------------------
        thead = table.find("thead")
        if thead:
            thead["style"] = "display:table-header-group;"

        # --------------------------------
        # ROW SAFETY (No vanish)
        # --------------------------------
        for row in table.find_all("tr"):

            row["style"] = """
                page-break-inside:avoid;
                page-break-after:auto;
            """

        # --------------------------------
        # CELL SAFETY
        # --------------------------------
        for cell in table.find_all(["td", "th"]):

            cell["style"] = """
                border:1px solid black;
                padding:14px;
                text-align:left;
                vertical-align:top;
                word-wrap:break-word;
                overflow-wrap:break-word;
                white-space:normal;
                min-height:40px;
            """

    return soup


# ----------------------------------------
# FIX IMAGES
# ----------------------------------------
def fix_images(soup):

    for img in soup.find_all("img"):

        img["style"] = """
            display:block;
            margin:20px auto;
            max-width:60%;
            height:auto;
            clear:both;
            page-break-inside:avoid;
        """

    return soup


# ----------------------------------------
# MAIN
# ----------------------------------------
def rebuild_layout(html_path):

    print(f"\n Rebuilding layout: {html_path}\n")

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    soup = normalize_layout(soup)
    soup = translate_all_text(soup)
    soup = fix_tables(soup)
    soup = fix_images(soup)

    print(" Layout rebuild completed\n")

    return soup