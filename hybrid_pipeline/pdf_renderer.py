from weasyprint import HTML, CSS
import os


def render_pdf(soup, output_pdf):

    html_string = str(soup)

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    publication_css = CSS(string="""

    /* ===============================
       GLOBAL RESET
    ================================ */

    * {
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    body {
        font-family: "NotoSansDevanagari", serif;
        margin: 0;
        padding: 0;
        background-color: #f4f8f2;
        color: #222222;
    }

    /* ===============================
       MAIN HEADINGS
    ================================ */

    h1 {
        font-size: 22px !important;
        color: #1b5e20;
        border-bottom: 3px solid #2e7d32;
        padding-bottom: 6px;
        margin: 20px 0 12px 0;
        font-weight: bold;
    }

    h2 {
        font-size: 18px !important;
        color: #2e7d32;
        border-left: 5px solid #66bb6a;
        padding-left: 10px;
        margin: 16px 0 10px 0;
        font-weight: bold;
    }

    h3 {
        font-size: 16px !important;
        color: #388e3c;
        margin: 14px 0 8px 0;
        font-weight: bold;
    }

    /* ===============================
       PARAGRAPH CLEAN FORMAT
    ================================ */

    p {
        margin: 10px 0;
        text-align: justify;
        text-indent: 25px;
        font-size: 14px !important;
        line-height: 1.7 !important;
    }

    div {
        margin: 6px 0;
        text-align: justify;
    }

    /* ===============================
       BULLET LIST FIX
    ================================ */

    ul {
        margin: 8px 0 8px 25px;
        padding-left: 10px;
    }

    li {
        margin-bottom: 6px;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* ===============================
       TABLE STYLING (CLEAN & CENTERED)
    ================================ */

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background-color: #ffffff;
        table-layout: fixed;
    }

    thead {
        display: table-header-group;
        background-color: #c8e6c9;
    }

    tr {
        page-break-inside: avoid;
    }

    td, th {
        border: 1px solid #2e7d32;
        padding: 8px;
        vertical-align: top;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        font-size: 13px !important;
    }

    th {
        background-color: #a5d6a7;
        color: #1b5e20;
        font-weight: bold;
        text-align: center;
    }

    /* ===============================
       IMAGE STYLE
    ================================ */

    img {
        max-width: 60%;
        display: block;
        margin: 15px auto;
        border: 2px solid #2e7d32;
        padding: 4px;
        background-color: white;
    }

    /* ===============================
       PAGE SETTINGS
    ================================ */

    @page {
        size: A3 landscape;
        margin: 18mm;
    }

    """)

    HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=[publication_css]
    )

    print(f"Publication PDF saved → {output_pdf}")
