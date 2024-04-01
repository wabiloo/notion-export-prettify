# notion-pretty-export
Turn your notion page into a styled and branded PDF

## Usage
```
usage: Notion2PDF [-h] [-o OUTPUT] [-t TITLE] [-s SUBTITLE] [-p PROJECT] [-a AUTHOR] [-d DATE] [--title-page | --no-title-page]
                  [--heading-numbers | --no-heading-numbers] [--strip-internal-info | --no-strip-internal-info]
                  zip_file template_dir

Turn a Notion page into a styled PDF document.

positional arguments:
  zip_file              Path to the zip file exported from Notion
  template_dir          Path to the template directory

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to the output PDF file
  -t TITLE, --title TITLE
                        Title of the document
  -s SUBTITLE, --subtitle SUBTITLE
                        Subtitle of the document
  -p PROJECT, --project PROJECT
                        project of the document
  -a AUTHOR, --author AUTHOR
                        Author of the document
  -d DATE, --date DATE  Date of the document
  --title-page, --no-title-page
                        Add a title page (if defined in the template)
  --heading-numbers, --no-heading-numbers
                        Add heading numbers
  --strip-internal-info, --no-strip-internal-info
                        Remove internal information, such as callouts and database properties
```