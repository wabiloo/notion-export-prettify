from os import path, listdir
import logging
import tempfile
import zipfile

from args import parse_args
from html_manipulator import HtmlManipulator
from pdf_maker import PdfMaker
from resource_loader import ResourceLoader
from html_templator import HtmlTemplator

logging.basicConfig(level=logging.DEBUG)

args = parse_args()

resources = ResourceLoader(args.template_dir)


# Create a temporary directory to extract the zip file to
with tempfile.TemporaryDirectory() as temp_dir:
    logging.debug("Temporary directory: %s", temp_dir)

    with zipfile.ZipFile(args.zip_file, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

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
    manipulator = HtmlManipulator(html_file)

    # Prepare metadata
    metadata = {
        "title": args.title or manipulator.get_title(),
        "subtitle": args.subtitle or "",
        "project": args.project or "",
        "author": args.author or "",
        "date": args.date or "",
    }

    # 1.a. - Overwrite CSS
    if css_file := resources.get_resource_path("overwrites.css"):
        manipulator.add_css(css_file)

    # 1.b. - Remove internal info
    if args.strip_internal_info:
        manipulator.remove_internal_info()
        manipulator.remove_database_properties()

    # 1.c. - Number headings
    if args.heading_numbers:
        manipulator.number_headings()

    # 1.d. - Reset TOC
    manipulator.move_toc(keep=args.table_of_contents)

    # 1.e. - handle Notion's header (title)
    if with_cover_page:
        manipulator.remove_header()
    else:
        if title_template := resources.get_resource_content("title.html"):
            title_block = HtmlTemplator.render(title_template, metadata)
            manipulator.inject_title_block(title_block)

        # else we keep the title as it is in the Notion doc

    # 1.x. - Save to file
    updated_html_path = path.join(temp_dir, "updated_doc.html")
    with open(updated_html_path, "w") as f:
        f.write(manipulator.get_html())
        logging.debug("Updated HTML saved to %s", updated_html_path)

    # 3. - Convert to PDF

    # 3.a. - Get header template
    header_html = None
    header_template = resources.get_resource_content("header.html")
    if header_template:
        header_html = HtmlTemplator.render(header_template, metadata)

    # 3.b. - Get footer template
    footer_html = None
    footer_template = resources.get_resource_content("footer.html")
    if footer_template:
        footer_html = HtmlTemplator.render(footer_template, metadata)

    # 3.c. - Generate PDF
    pdf_maker = PdfMaker(temp_dir=temp_dir)
    pdf_maker.from_html_file(updated_html_path, header_html, footer_html)

    # 3.d. - Merge branding
    if background_file := resources.get_resource_path("background.pdf"):
        pdf_maker.merge_background_pdf(background_file)

    # 3.e. - Add title page
    if with_cover_page:
        title_html = "<html></html>"
        title_template = resources.get_resource_content("cover.html")
        if title_template:
            title_html = HtmlTemplator.render(title_template, metadata)

        title_page_file = resources.get_resource_path("cover.pdf")

        pdf_maker.inject_title_page_pdf(title_page_file, title_html)

    # 4. - Save to file
    output_file = args.output
    if not output_file:
        # Save in the same directory as the input with the title as filename
        output_file = path.join(path.dirname(args.zip_file), metadata["title"] + ".pdf")

    pdf_maker.save(output_file)

    logging.info("PDF generated at %s" % output_file)
