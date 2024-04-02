import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Turn a Notion page into a styled PDF document."
    )

    parser.add_argument(
        "zip_file",
        type=str,
        help="Path to the zip file exported from Notion",
    )

    parser.add_argument(
        "template_dir",
        type=str,
        help="Path to the template directory",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output.pdf",
        help="Path to the output PDF file",
    )

    # metadata
    metadata = parser.add_argument_group(
        "Metadata",
        description="Available to be injected into header/footer/cover page templates",
    )
    metadata.add_argument("-t", "--title", type=str, help="Title of the document")
    metadata.add_argument("-s", "--subtitle", type=str, help="Subtitle of the document")
    metadata.add_argument("-p", "--project", type=str, help="project of the document")
    metadata.add_argument("-a", "--author", type=str, help="Author of the document")
    metadata.add_argument("-d", "--date", type=str, help="Date of the document")

    # options
    options = parser.add_argument_group(
        "Options", description="Options to control the output"
    )

    options.add_argument(
        "--cover-page",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Add a cover page (if defined in the template)",
    )
    options.add_argument(
        "--heading-numbers",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Add heading numbers",
    )
    options.add_argument(
        "--strip-internal-info",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove internal information, such as callouts and database properties",
    )

    return parser.parse_args()
