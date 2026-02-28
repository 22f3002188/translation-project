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
        margin: 0;
        padding: 0;
        line-height: 1.5 !important;
    }

    body {
        font-family: "NotoSansDevanagari", serif;
        background-color: #fff9db;   /* Light yellow background */
        color: #222222;
        padding: 12px;
        font-size: 15px;
        text-align: justify;
    }

    /* ===============================
       MAIN HEADINGS
    ================================ */

    h1 {
        font-size: 30px !important;
        font-weight: bold;
        font-style: italic;
        color: #b71c1c;
        margin: 14px 0 8px 0;
        border-bottom: 3px solid #b71c1c;
        padding-bottom: 6px;
    }

    h2 {
        font-size: 24px !important;
        font-weight: bold;
        font-style: italic;
        color: #0d47a1;
        margin: 12px 0 6px 0;
        border-left: 6px solid #0d47a1;
        padding-left: 10px;
    }

    h3 {
        font-size: 20px !important;
        font-weight: bold;
        font-style: italic;
        color: #1b5e20;
        margin: 10px 0 4px 0;
    }

    /* ===============================
       PARAGRAPHS
    ================================ */

    p {
        margin: 6px 0;
        text-align: justify;
        line-height: 1.6;
    }

    div {
        margin: 2px 0;
        text-align: justify;
    }

    div:empty,
    p:empty {
        display: none;
    }

    br {
        display: none;
    }

    /* ===============================
       BULLET LIST
    ================================ */

    ul {
        margin: 6px 0 6px 22px;
    }

    li {
        margin-bottom: 4px;
        line-height: 1.6;
    }

    /* ===============================
       TABLE STYLING
    ================================ */

    table {
        width: 92%;
        margin-left: auto;
        margin-right: auto;
        border-collapse: collapse;
        margin-top: 18px;
        margin-bottom: 18px;
        background-color: #ffffff;
        table-layout: fixed;
    }

    thead {
        display: table-header-group;
        background-color: #ffe082;
    }

    tr {
        page-break-inside: avoid;
    }

    td, th {
        border: 1px solid #444;
        padding: 8px;
        vertical-align: top;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        font-size: 14px !important;
    }

    th {
        background-color: #ffca28;
        font-weight: bold;
        text-align: center;
    }

    /* ===============================
       IMAGE STYLE
    ================================ */

    img {
        max-width: 65%;
        display: block;
        margin: 18px auto;
        border: 2px solid #999;
        padding: 4px;
        background-color: white;
    }

    /* ===============================
       PAGE SETTINGS + PAGE NUMBER
    ================================ */

    @page {
        size: A3 landscape;
        margin: 18mm;
        background: #fff9db;

        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 12px;
            font-weight: bold;
            color: #444;
        }
    }

    """)

    HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=[publication_css]
    )

    print(f"Publication PDF saved → {output_pdf}")
