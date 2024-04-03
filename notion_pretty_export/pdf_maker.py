from playwright.sync_api import sync_playwright
import fitz  # PyMuPDF
from os import path
import logging

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

    def from_html_file(self, html_input_path):
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

            # NOTE: abandonned any attempt at making use of header_template and footer_template. Too inflexible
            page.pdf(
                path=self.output_path,
                # format="A4",
                display_header_footer=False,
                prefer_css_page_size=True,
                # margin=dict(top="0", right="0", bottom="0", left="0"),
            )

            self.pdf_doc = fitz.open(self.output_path)

            browser.close()

    def from_html(self, html_content):
        file_path = path.join(self.temp_dir, "additional_html.html")
        with open(file_path, "w") as f:
            f.write(html_content)
        return self.from_html_file(file_path)

    def merge_underlay_html(self, underlay_html):
        for i, page in enumerate(self.pdf_doc):
            logging.debug("Making underlay for page %s", i)

            # replace the page number in the html
            page_underlay_html = underlay_html
            page_underlay_html = page_underlay_html.replace(
                "__PAGENUMBER__", str(i + 1)
            )
            underlay_pdf = PdfMaker(
                temp_dir=self.temp_dir, output_name=f"underlay_{i}.pdf"
            )
            underlay_pdf.from_html(page_underlay_html)

            # NOTE: there's an apparent bug in PyMuPDF when using overlay=True:
            #  dimensions of the overlay are 4x reduced and it is mirrored in both directions
            page.show_pdf_page(page.rect, underlay_pdf.pdf_doc, pno=0, overlay=False)

    def merge_background_pdf(
        self,
        background_pdf_path,
    ):
        background = fitz.open(background_pdf_path)

        for page in self.pdf_doc:
            page.show_pdf_page(page.rect, background, overlay=False)

    def prepend_cover_page(self, cover_pdf_path, additional_html):
        final_cover_pdf_path = cover_pdf_path
        if additional_html:
            title_pdf_make = PdfMaker(
                temp_dir=self.temp_dir, output_name="titlepage.pdf"
            )
            title_pdf_make.from_html(additional_html)
            if cover_pdf_path:
                title_pdf_make.merge_background_pdf(cover_pdf_path)

            final_cover_pdf_path = path.join(self.temp_dir, "final_title_page.pdf")
            title_pdf_make.save(final_cover_pdf_path)

        titlepage = fitz.open(final_cover_pdf_path)
        # Insert first page at the beginning of the document
        self.pdf_doc.insert_pdf(titlepage, start_at=0)

    def save(self, output_pdf_path=None):
        if not output_pdf_path:
            output_pdf_path = self.output_path
        self.pdf_doc.save(output_pdf_path)
