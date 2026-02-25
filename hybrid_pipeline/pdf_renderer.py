# # PDF_RENDER.PY
# from weasyprint import HTML, CSS
# import os


# def render_pdf(soup, output_pdf):

#     html_string = str(soup)

#     os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

#     publication_css = CSS(string="""

#         /* =========================
#            DEVANAGARI FONT SUPPORT
#            (Fix □□□ boxes issue)
#         ========================== */

#         @font-face {
#             font-family: "NotoSansDevanagari";
#             src: local("Noto Sans Devanagari"),
#                  local("NotoSansDevanagari"),
#                  url("/usr/share/fonts/truetype/NotoSansDevanagari.ttf") format("truetype");
#         }

#         body {
#             font-family: "NotoSansDevanagari", "Noto Sans", "Times New Roman", serif;
#             font-size: 12px;
#             line-height: 1.6;
#             text-align: justify;
#         }

#         /* =========================
#            PAGE SETTINGS
#         ========================== */

#         @page {
#             size: A3 landscape;
#             margin: 15mm;
#         }

#         h1, h2, h3 {
#             text-align: center;
#             font-weight: bold;
#             margin: 20px 0 10px 0;
#         }

#         /* =========================
#            TABLE FIX START
#         ========================== */

#         table {
#             width: 85%;
#             margin-left: auto;
#             margin-right: auto;
#             border-collapse: collapse;
#             table-layout: fixed;
#             page-break-inside: auto;
#         }

#         thead {
#             display: table-header-group;
#         }

#         tfoot {
#             display: table-footer-group;
#         }

#         tr {
#             page-break-inside: avoid;
#             page-break-after: auto;
#         }

#         td, th {
#             border: 1px solid black;
#             padding: 8px;
#             text-align: center;
#             vertical-align: middle;
#             word-wrap: break-word;
#             overflow-wrap: break-word;
#             white-space: normal;
#             page-break-inside: avoid;
#         }

#         table.large-table {
#             page-break-inside: auto;
#         }

#         /* =========================
#            TABLE FIX END
#         ========================== */

#         img {
#             max-width: 55%;
#             height: auto;
#             display: block;
#             margin: 20px auto;
#         }

#     """)

#     HTML(string=html_string).write_pdf(
#         output_pdf,
#         stylesheets=[publication_css]
#     )

#     print(f"Publication PDF saved → {output_pdf}")


# pdf_render.py  (FINAL PAGINATION SAFE)

# pdf_render.py  (COLUMN SAFE FINAL)


# pdf_render.py

from weasyprint import HTML, CSS
import os


def render_pdf(soup, output_pdf):

    html_string = str(soup)

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    publication_css = CSS(string="""

        @page {
            size: A3 landscape;
            margin: 15mm;
        }

        body {
            font-family:
                "Noto Sans Devanagari",
                Arial,
                sans-serif;
            font-size: 12px;
            line-height: 1.6;
        }

        table {
            width:100%;
            border-collapse:collapse;
            table-layout:auto;
            page-break-inside:auto;
        }

        tr {
            page-break-inside:avoid;
        }

        th, td {
            border:1px solid black;
            padding:18px;
            vertical-align:top;
            word-wrap:break-word;
            overflow-wrap:break-word;
            white-space:normal;
        }
        /* =========================
        FINAL TABLE PAGINATION
        ========================= */

        table {
            page-break-inside:auto;
            break-inside:auto;
            margin-top:30px;
            margin-bottom:30px;
            display:block;
        }

        thead {
            display:table-header-group;
        }

        tfoot {
            display:table-footer-group;
        }

        /* Prevent text overlap */
        p, div, section {
            page-break-inside:auto;
        }

        /* Space around tables */
        table + p,
        table + div {
            margin-top:20px;
        }
    """)

    HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=[publication_css]
    )
