from os import path, listdir
import logging
import tempfile
import zipfile

from args import parse_args
from html_manipulator import HtmlManipulator
from pdf_maker import PdfMaker
from resource_loader import ResourceLoader
from html_templator import HtmlTemplator
import print_color

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.WARNING)

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
        print_color.green("[PROC] Injecting overwrites.css")
        manipulator.add_css(css_file)
    else:
        print_color.orange("[SKIP] No overwrites.css found")

    # 1.b. - Remove internal info
    if args.strip_internal_info:
        print_color.green("[PROC] Removing internal info")
        manipulator.remove_internal_info()
        manipulator.remove_database_properties()
    else:
        print_color.orange("[SKIP] Keeping internal info (if any)")

    # 1.c. - Number headings
    if args.heading_numbers:
        print_color.green("[PROC] Numbering headings")
        manipulator.number_headings()
    else:
        print_color.orange("[SKIP] Headings kept as original")

    # 1.d. - Reset TOC
    if args.table_of_contents:
        print_color.green("[PROC] Processing TOC (if any in source)")
        manipulator.move_toc(keep=True)
    else:
        print_color.green("[PROC] Removing TOC (if any)")
        manipulator.move_toc(keep=False)

    # 1.e. - handle Notion's header (title)
    if with_cover_page:
        print_color.green(
            "[PROC] Removing header from source (in favour of cover page)"
        )
        manipulator.remove_header()
    else:
        if cover_template := resources.get_resource_content("title.html"):
            print_color.green("[PROC] Rendering and injecting new title block")
            title_block = HtmlTemplator.render(cover_template, metadata)
            manipulator.inject_title_block(title_block)
        else:
            print_color.orange(
                "[SKIP] No HTML title template found. Keeping original header"
            )

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
        print_color.green("[PROC] Rendering header template")
        header_html = HtmlTemplator.render(header_template, metadata)
    else:
        print_color.orange("[SKIP] No header template found")

    # 3.b. - Get footer template
    footer_html = None
    footer_template = resources.get_resource_content("footer.html")
    if footer_template:
        print_color.green("[PROC] Rendering footer template")
        footer_html = HtmlTemplator.render(footer_template, metadata)
    else:
        print_color.orange("[SKIP] No footer template found")

    # 3.c. - Generate PDF
    pdf_maker = PdfMaker(temp_dir=temp_dir)
    print_color.green("[PROC] Generating main PDF document")
    pdf_maker.from_html_file(updated_html_path, header_html, footer_html)

    # 3.d. - Merge branding
    if background_file := resources.get_resource_path("background.pdf"):
        pdf_maker.merge_background_pdf(background_file)
        print_color.green("[PROC] Merging background PDF")
    else:
        print_color.orange("[SKIP] No PDF background file found")

    # 3.e. - Add cover page
    if with_cover_page:
        cover_html = "<html></html>"
        cover_template = resources.get_resource_content("cover.html")
        if cover_template:
            print_color.green("[PROC] Rendering cover template")
            cover_html = HtmlTemplator.render(cover_template, metadata)
        else:
            print_color.orange("[SKIP] No HTML cover template found")

        title_page_file = resources.get_resource_path("cover.pdf")
        if not title_page_file:
            print_color.orange("[SKIP] No PDF cover page file found")

        print_color.green("[PROC] Prefixing with cover page")
        pdf_maker.inject_title_page_pdf(title_page_file, cover_html)
    else:
        print_color.orange("[SKIP] Skipping cover page")

    # 4. - Save to file
    output_file = args.output
    if not output_file:
        filename = metadata["title"] + ".pdf"
        if "project" in metadata:
            filename = metadata["project"] + " - " + filename

        # Save in the same directory as the input with the title as filename
        output_file = path.join(path.dirname(args.zip_file), filename)

    pdf_maker.save(output_file)

    print_color.green("PDF generated at %s" % output_file)
