from playwright.sync_api import sync_playwright
import fitz  # PyMuPDF
from os import path

empty_template = """
<html><body></body></html>
"""


class PdfMaker:
    def __init__(self, temp_dir, output_name=None):
        self.pdf_doc = None
        self.temp_dir = temp_dir
        if output_name:
            self.output_path = path.join(temp_dir, output_name)
        else:
            self.output_path = path.join(temp_dir, "updated_doc.pdf")

    def from_html_file(self, html_input_path, header_html=None, footer_html=None):
        """PlayWright - modern replacement for pyppeteer"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Navigate to the page
            page.goto(f"file://{html_input_path}")

            # Add PDF-specific overwrites
            # page.add_style_tag(
            #     content="@page:first {margin-top: 0;} body {margin-top: 1cm;}"
            # )

            page.pdf(
                path=self.output_path,
                format="A4",
                display_header_footer=True,
                header_template=header_html or empty_template,
                footer_template=footer_html or empty_template,
                prefer_css_page_size=True,
                margin=dict(top="0", right="0", bottom="0", left="0"),
            )

            # This shit doesn't work. No matter how I try, hyperlinks break
            # page.pdf(
            #     path=self.output_path + ".other",
            #     format="A4",
            #     display_header_footer=True,
            #     header_template=empty_template,
            #     footer_template=footer_html or empty_template,
            #     prefer_css_page_size=True,
            #     margin=dict(top="0", right="0", bottom="0", left="0"),
            # )

            # doc1 = fitz.open(self.output_path)

            # # Check the link targes
            # for i, link in enumerate(doc1[0].get_links()):
            #     print(link)
            #     if i >= 1:
            #         break

            # doc2 = fitz.open(self.output_path + ".other")
            # for i, link in enumerate(doc2[0].get_links()):
            #     print(link)
            #     if i >= 1:
            #         break

            # pages_to_keep = 1
            # # Remove the pages from pdf2 that you want to replace, except the first page (TOC)
            # for page_num in range(len(doc2) - 1, pages_to_keep - 1, -1):
            #     doc2.delete_page(page_num)

            # # Insert the pages from pdf1 into pdf2, starting right after the TOC
            # doc2.insert_pdf(doc1, from_page=pages_to_keep)

            # self.pdf_doc = doc2

            # for i, link in enumerate(self.pdf_doc[0].get_links()):
            #     print(link)
            #     if i >= 1:
            #         break

            self.pdf_doc = fitz.open(self.output_path)

            browser.close()

    def from_html(self, html_content):
        file_path = path.join(self.temp_dir, "additional_html.html")
        with open(file_path, "w") as f:
            f.write(html_content)
        return self.from_html_file(file_path)

    def merge_background_pdf(
        self,
        background_pdf_path,
    ):
        background = fitz.open(background_pdf_path)

        for page in self.pdf_doc:
            page.show_pdf_page(page.rect, background, overlay=False)

    def inject_title_page_pdf(self, titlepage_pdf_path, additional_html):
        final_titlepage_pdf_path = titlepage_pdf_path
        if additional_html:
            title_pdf_make = PdfMaker(
                temp_dir=self.temp_dir, output_name="titlepage.pdf"
            )
            title_pdf_make.from_html(additional_html)
            if titlepage_pdf_path:
                title_pdf_make.merge_background_pdf(titlepage_pdf_path)

            final_titlepage_pdf_path = path.join(self.temp_dir, "final_title_page.pdf")
            title_pdf_make.save(final_titlepage_pdf_path)

        titlepage = fitz.open(final_titlepage_pdf_path)
        # Insert first page at the beginning of the document
        self.pdf_doc.insert_pdf(titlepage, start_at=0)

    def save(self, output_pdf_path):
        self.pdf_doc.save(output_pdf_path)
