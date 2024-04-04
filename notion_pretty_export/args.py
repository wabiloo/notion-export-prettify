import configargparse
import argparse


def parse_args():
    parser = configargparse.ArgumentParser(
        description="Turn a Notion page into a styled PDF document."
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input file exported from Notion. Can be either the ZIP file, or the HTML file",
    )

    parser.add_argument(
        "-t",
        "--template",
        is_config_file=True,
        type=str,
        help="Path to the template file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to the output PDF file. "
        "Defaults to using the document title as filename, stored in the same folder as the input.",
    )

    # metadata
    metadata = parser.add_argument_group(
        "Metadata",
        description="Available to be injected into header/footer/cover page templates",
    )
    metadata.add_argument("--title", type=str, help="Title of the document")
    metadata.add_argument("--subtitle", type=str, help="Subtitle of the document")
    metadata.add_argument("--project", type=str, help="project of the document")
    metadata.add_argument("--author", type=str, help="Author of the document")
    metadata.add_argument("--date", type=str, help="Date of the document")

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
    options.add_argument(
        "--table-of-contents",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Add a table of contents (if existing in the Notion document)",
    )

    return parser.parse_args()
