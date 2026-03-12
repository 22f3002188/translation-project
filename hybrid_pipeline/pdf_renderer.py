# from weasyprint import HTML, CSS
# import os


# def render_pdf(soup, output_pdf):

#     html_string = str(soup)

#     os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

#     publication_css = CSS(string="""

#     /* ===============================
#        GLOBAL RESET
#     ================================ */

#     * {
#         margin: 0;
#         padding: 0;
#         line-height: 1.5 !important;
#     }

#     body {
#         font-family: "NotoSansDevanagari", serif;
#         background-color: #fff9db;   /* Light yellow background */
#         color: #222222;
#         padding: 12px;
#         font-size: 15px;
#         text-align: justify;
#     }

#     /* ===============================
#        MAIN HEADINGS
#     ================================ */

#     h1 {
#         font-size: 30px !important;
#         font-weight: bold;
#         font-style: italic;
#         color: #b71c1c;
#         margin: 14px 0 8px 0;
#         border-bottom: 3px solid #b71c1c;
#         padding-bottom: 6px;
#     }

#     h2 {
#         font-size: 24px !important;
#         font-weight: bold;
#         font-style: italic;
#         color: #0d47a1;
#         margin: 12px 0 6px 0;
#         border-left: 6px solid #0d47a1;
#         padding-left: 10px;
#     }

#     h3 {
#         font-size: 20px !important;
#         font-weight: bold;
#         font-style: italic;
#         color: #1b5e20;
#         margin: 10px 0 4px 0;
#     }

#     /* ===============================
#        PARAGRAPHS
#     ================================ */

#     p {
#         margin: 6px 0;
#         text-align: justify;
#         line-height: 1.6;
#     }

#     div {
#         margin: 2px 0;
#         text-align: justify;
#     }

#     div:empty,
#     p:empty {
#         display: none;
#     }

#     br {
#         display: none;
#     }

#     /* ===============================
#        BULLET LIST
#     ================================ */

#     ul {
#         margin: 6px 0 6px 22px;
#     }

#     li {
#         margin-bottom: 4px;
#         line-height: 1.6;
#     }

#     /* ===============================
#        TABLE STYLING
#     ================================ */

#     table {
#         width: 92%;
#         margin-left: auto;
#         margin-right: auto;
#         border-collapse: collapse;
#         margin-top: 18px;
#         margin-bottom: 18px;
#         background-color: #ffffff;
#         table-layout: fixed;
#     }

#     thead {
#         display: table-header-group;
#         background-color: #ffe082;
#     }

#     tr {
#         page-break-inside: avoid;
#     }

#     td, th {
#         border: 1px solid #444;
#         padding: 8px;
#         vertical-align: top;
#         word-wrap: break-word;
#         overflow-wrap: break-word;
#         white-space: normal;
#         font-size: 14px !important;
#     }

#     th {
#         background-color: #ffca28;
#         font-weight: bold;
#         text-align: center;
#     }

#     /* ===============================
#        IMAGE STYLE
#     ================================ */

#     img {
#         max-width: 65%;
#         display: block;
#         margin: 18px auto;
#         border: 2px solid #999;
#         padding: 4px;
#         background-color: white;
#     }

#     /* ===============================
#        PAGE SETTINGS + PAGE NUMBER
#     ================================ */

#     @page {
#         size: A3 landscape;
#         margin: 18mm;
#         background: #fff9db;

#         @bottom-center {
#             content: "Page " counter(page) " of " counter(pages);
#             font-size: 12px;
#             font-weight: bold;
#             color: #444;
#         }
#     }

#     """)

#     HTML(string=html_string).write_pdf(
#         output_pdf,
#         stylesheets=[publication_css]
#     )

#     print(f"Publication PDF saved → {output_pdf}")

from weasyprint import HTML, CSS
import os
import re


def clean_heading_colons(html_string):
    """
    Remove trailing colon from headings like:
    'Land and climate :' → 'Land and climate'
    """

    html_string = re.sub(r'(<h[1-3][^>]*>)(.*?)(:)\s*(</h[1-3]>)',
                         r'\1\2\4',
                         html_string,
                         flags=re.IGNORECASE)

    return html_string


def render_pdf(soup, output_pdf):

    html_string = str(soup)

    # remove colon from headings
    html_string = clean_heading_colons(html_string)

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    css = CSS(string="""

    /* --------------------------------
       GLOBAL TEXT FIX
    -------------------------------- */

    * {
        box-sizing: border-box;
        hyphens: auto;
        max-width: 100%;
    }

    /* --------------------------------
       BODY
    -------------------------------- */

    body {
        font-family: "Noto Serif Devanagari", "Noto Sans", serif;
        font-size: 14px;
        line-height: 1.6;
        margin: 15mm;
        color: #222;

        border: 4px solid #4CAF50;
        padding: 20px;
    }

    /* --------------------------------
       HEADINGS
    -------------------------------- */
    
    h1 {
        font-size: 26px;
        color: #1B5E20;
        border-bottom: 3px solid #4CAF50;
        padding-bottom: 5px;
        margin-top: 20px;
        text-align: left !important;
    }
    
    h2 {
        font-size: 20px;
        color: #2E7D32;
        margin-top: 18px;
        font-weight:700;
        text-align: left !important;
    }
    
    h3 {
        font-size: 17px;
        margin-top: 15px;
        text-align: left !important;
    }
    /* --------------------------------
       PARAGRAPHS
    -------------------------------- */

    p {
        text-align: justify;
        margin-bottom: 8px;
        margin-top: 0;
    }

    /* --------------------------------
       LISTS
    -------------------------------- */

    ul {
        margin-left: 25px;
        margin-bottom: 10px;
    }

    li {
        margin-bottom: 6px;
    }

    /* --------------------------------
       TABLES (IMPROVED)
    -------------------------------- */

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        table-layout: auto;
        font-size: 12px;
    }

    th {
        background: #2E7D32;
        color: white;
        font-weight: bold;
        padding: 10px;
        border: 1px solid #999;
        text-align: center;
        white-space: normal;
    }

    td {
        padding: 10px;
        border: 1px solid #bbb;
        text-align: center;
        vertical-align: middle;
        white-space: normal;
        word-break: normal;
        overflow-wrap: break-word;
        min-width: 60px;
    }

    tr:nth-child(even) {
        background: #f7f7f7;
    }

    table tr {
        page-break-inside: avoid;
    }

    /* --------------------------------
       IMAGES
    -------------------------------- */

    img {
        max-width: 65%;
        height: auto;
        display: block;
        margin: 20px auto;
        page-break-inside: avoid;
    }

    /* --------------------------------
       PAGE SETTINGS
    -------------------------------- */

    @page {
        size: A4;
        margin: 18mm;

        @bottom-center {
            content: "Page " counter(page);
            font-size: 10px;
            color: #444;
        }
    }

    """)

    HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=[css]
    )
