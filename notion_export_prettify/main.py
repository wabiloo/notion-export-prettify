from os import path, listdir
import logging
import shutil
import tempfile
import zipfile

from .args import parse_args
from .notion_html_manipulator import NotionHtmlManipulator
from .pdf_maker import PdfMaker
from .resource_loader import ResourceLoader
from .html_templator import HtmlTemplator
from .print_color import red, green, orange

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.WARNING)


def main():
    args = parse_args()
    resources = ResourceLoader()

    # Template dir is the one containing the template config file
    if args.template:
        template_dir = path.dirname(args.template)
        resources.set_folder(template_dir)

    # Create a temporary directory to extract the zip file to
    with tempfile.TemporaryDirectory() as temp_dir:
        logging.debug("Temporary directory: %s", temp_dir)

        if args.input_file.endswith(".zip"):
            with zipfile.ZipFile(args.input_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        elif args.input_file.endswith(".html"):
            # If the input file is an HTML file, just copy it to the temporary directory
            logging.debug("Copying HTML file to temporary directory")
            shutil.copy(args.input_file, temp_dir)
            # as well as the associated folder with the same name (if any)
            input_asset_folder = args.input_file.replace(".html", "")
            if path.exists(input_asset_folder):
                shutil.copytree(
                    input_asset_folder,
                    path.join(temp_dir, path.basename(input_asset_folder)),
                )
        else:
            red("[ERROR] Unsupported input file format")
            exit(1)

        # Find the single HTML file in that folder
        html_files = [f for f in listdir(temp_dir) if f.endswith(".html")]
        if len(html_files) != 1:
            raise ValueError("Expected one HTML file in the zip file")
        html_file = path.join(temp_dir, html_files[0])

        # 0. Determine if there will be a title page
        with_cover_page = args.cover_page and (
            resources.get_resource_path("cover.html")
            or resources.get_resource_path("cover.pdf")
        )

        # 1. - Manipulate the HTML
        manipulator = NotionHtmlManipulator(html_file)

        # Prepare metadata
        metadata = {
            "title": args.title or manipulator.get_title(),
            "subtitle": args.subtitle or "",
            "project": args.project or "",
            "author": args.author or "",
            "date": args.date or "",
        }

        # Get page.css
        page_css = resources.get_resource_content("page.css")

        # 1.a. - Overwrite CSS
        if page_css:
            green("[PROC] Injecting page.css")
            manipulator.add_css_overwrites(page_css)
        else:
            orange("[SKIP] No page.css found")

        if css_overwrites := resources.get_resource_content("overwrites.css"):
            green("[PROC] Injecting overwrites.css")
            manipulator.add_css_overwrites(css_overwrites)
        else:
            orange("[SKIP] No overwrites.css found")

        # 1.b. - Remove internal info
        if args.strip_internal_info:
            green("[PROC] Removing internal info")
            manipulator.remove_internal_info()
            manipulator.remove_database_properties()
        else:
            orange("[SKIP] Keeping internal info (if any)")

        # 1.c. - Number headings
        if args.heading_numbers:
            green("[PROC] Numbering headings")
            manipulator.number_headings()
        else:
            orange("[SKIP] Headings kept as original")

        # 1.d. - Reset TOC
        if args.table_of_contents:
            green("[PROC] Processing TOC (if any in source)")
            manipulator.move_toc(keep=True)
        else:
            green("[PROC] Removing TOC (if any)")
            manipulator.move_toc(keep=False)

        # 1.e. - handle Notion's header (title)
        if with_cover_page:
            green("[PROC] Removing header from source (in favour of cover page)")
            manipulator.remove_header()
        else:
            if header_template := resources.get_resource_content("header.html"):
                green("[PROC] Rendering and injecting new header block")
                title_block = HtmlTemplator(header_template).inject(metadata).html
                manipulator.inject_title_block(title_block)
            else:
                orange("[SKIP] No HTML title template found. Keeping original header")

        # 1.x. - Save to file
        updated_html_path = path.join(temp_dir, "updated_doc.html")
        with open(updated_html_path, "w") as f:
            f.write(manipulator.get_html())
            logging.debug("Updated HTML saved to %s", updated_html_path)

        # 3. - Convert to PDF
        pdf_maker = PdfMaker(temp_dir=temp_dir)
        green("[PROC] Generating main PDF document")
        pdf_maker.from_html_file(updated_html_path)

        # 3.a. - Add header/footer underlay
        # NOTE: this cannot be done as an overlay, due to a bug in PyMuPDF
        if underlay_template := resources.get_resource_content("background.html"):
            green("[PROC] Rendering underlay templates for each page")
            underlay_html = (
                HtmlTemplator(underlay_template)
                .inject(
                    metadata,
                    pageNumber="__PAGENUMBER__",
                    hasCoverPage="hasCoverPage" if with_cover_page else "",
                )
                .add_css(page_css)
                .html
            )
            pdf_maker.merge_underlay_html(underlay_html)
        else:
            orange(
                "[SKIP] No HTML overlay template found. No headers and footers will be added"
            )

        # 3.b. - Merge branding background
        if background_file := resources.get_resource_path("background.pdf"):
            pdf_maker.merge_background_pdf(background_file)
            green("[PROC] Merging background PDF")
        else:
            orange("[SKIP] No PDF background file found")

        # 3.c. - Add cover page
        if with_cover_page:
            cover_html = "<html></html>"
            cover_template = resources.get_resource_content("cover.html")
            if cover_template:
                green("[PROC] Rendering cover template")
                cover_html = (
                    HtmlTemplator(cover_template)
                    .inject(metadata)
                    .add_css(page_css)
                    .html
                )
            else:
                orange("[SKIP] No HTML cover template found")

            cover_page_file = resources.get_resource_path("cover.pdf")
            if not cover_page_file:
                orange("[SKIP] No PDF cover page file found")

            green("[PROC] Prefixing with cover page")
            pdf_maker.prepend_cover_page(cover_page_file, cover_html)
        else:
            orange("[SKIP] Skipping cover page")

        # 4. - Save to file
        output_file = args.output
        if not output_file:
            filename = metadata["title"] + ".pdf"
            if "project" in metadata:
                filename = metadata["project"] + " - " + filename

            # Save in the same directory as the input with the title as filename
            output_file = path.join(path.dirname(args.input_file), filename)

        pdf_maker.save(output_file)

        green("PDF generated at %s" % output_file)


if __name__ == "__main__":
    main()
