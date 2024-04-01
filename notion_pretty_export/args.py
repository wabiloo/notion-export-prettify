import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Notion2PDF", description="Turn a Notion page into a styled PDF document."
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
    parser.add_argument("-t", "--title", type=str, help="Title of the document")
    parser.add_argument("-s", "--subtitle", type=str, help="Subtitle of the document")
    parser.add_argument("-p", "--project", type=str, help="project of the document")
    parser.add_argument("-a", "--author", type=str, help="Author of the document")
    parser.add_argument("-d", "--date", type=str, help="Date of the document")

    # transformations
    parser.add_argument(
        "--title-page",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Add a title page (if defined in the template)",
    )
    parser.add_argument(
        "--heading-numbers",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Add heading numbers",
    )
    parser.add_argument(
        "--strip-internal-info",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove internal information, such as callouts and database properties",
    )

    return parser.parse_args()
