from os import path, getcwd
import sys
import configargparse
import argparse
import logging
from importlib.metadata import version


# Function to manually find and modify the --config argument to make it a full path
def modify_config_path(args):

    config_index = None
    for i, arg in enumerate(args):
        if arg in ("-t", "--template"):
            config_index = i + 1
            break

    if config_index is not None and config_index < len(args):
        template_arg = args[config_index]
        logging.debug(f"Template argument: {template_arg}")

        if path.exists(template_arg):
            if path.isfile(template_arg):
                logging.debug(f"Template file at '{template_arg}'")
                return args
            if path.isdir(template_arg):
                template_file = path.join(template_arg, "template.cfg")
                args[config_index] = template_file
                return args

        if not path.exists(template_arg):
            logging.debug(f"No template file at '{template_arg}'")
            # If the template argument is not a full path, try to find it in the current directory
            candidate_template_dir = path.realpath(path.join(getcwd(), template_arg))
            logging.debug(f"Checking for template in '{candidate_template_dir}")
            if path.exists(candidate_template_dir) and path.isdir(
                candidate_template_dir
            ):
                candidate_template_file = path.join(
                    candidate_template_dir, "template.cfg"
                )
                args[config_index] = candidate_template_file
            else:
                # Try the built-in templates
                builtin_template_dir = path.realpath(
                    path.join(path.dirname(__file__), "../templates", template_arg)
                )
                logging.debug(f"Checking for template in '{builtin_template_dir}")
                if path.exists(builtin_template_dir) and path.isdir(
                    builtin_template_dir
                ):
                    builtin_template_file = path.join(
                        builtin_template_dir, "template.cfg"
                    )
                    args[config_index] = builtin_template_file

    return args


def parse_args():
    # Preprocess the command line arguments
    sanitized_args = modify_config_path(sys.argv[1:])

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

    parser.add_argument(
        "-v", "--version", action="version", version=version("notion-export-prettify")
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

    return parser.parse_args(sanitized_args)
