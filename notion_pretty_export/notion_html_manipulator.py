from bs4 import BeautifulSoup


class NotionHtmlManipulator:
    def __init__(self, html_path):
        with open(html_path, "r") as file:
            html_content = file.read()
            self.soup = BeautifulSoup(html_content, "html.parser")
            self.page_body = self.soup.find("div", class_="page-body")
            self.toc = self.soup.find("nav")
            self.title = str(self.get_title())

            if not self.page_body:
                raise Exception(
                    "Page body not found. This does not appear to be a valid Notion document"
                )

    def get_title(self):
        if hasattr(self, "title"):
            return self.title

        # Get the first heading (document title)
        for header in self.soup.find_all("header"):
            page_title = header.find("h1")
            return page_title.text

    def add_css_overwrites(self, css_content):
        # Create a new <style> tag
        new_style_tag = self.soup.new_tag("style", type="text/css")
        new_style_tag.string = css_content

        # Append the new <style> tag to the <head>
        self.soup.head.append(new_style_tag)

    def remove_header(self):
        for header in self.soup.find_all("header"):
            header.extract()

    def inject_title_block(self, title_block):
        for header in self.soup.find_all("header"):
            header.clear()
            title_block = BeautifulSoup(title_block, "html.parser")
            header.append(title_block)

    def remove_internal_info(self):
        # Remove all Internal callouts
        for callout in self.page_body.find_all("figure", class_="callout"):
            # But only if it contains a div with the string "Internal"
            for div in callout.find_all("div"):
                if any(
                    child
                    for child in div.children
                    if child.string and child.string.lower().startswith("internal")
                ):
                    callout.extract()

    def remove_database_properties(self):
        for header in self.soup.find_all("header"):
            for table in header.find_all("table"):
                table.extract()

    def number_headings(self):
        counters = [0, 0, 0]  # h1, h2, h3
        # Process all headings
        for heading in self.page_body.find_all(["h1", "h2", "h3"]):
            level = int(heading.name[1]) - 1
            counters[level] += 1
            # Reset lower level counters
            for i in range(level + 1, 3):
                counters[i] = 0

            # Create the numbering string
            numbering = ".".join(str(counters[i]) for i in range(level + 1)) + ". "

            # Add into a new span
            heading_text = heading.text
            heading.clear()

            span_number = self.soup.new_tag("span")
            span_number["class"] = "heading-number"
            span_number.string = numbering

            span_text = self.soup.new_tag("span")
            span_text["class"] = "heading-text"
            span_text.string = heading_text

            heading.append(span_number)
            heading.append(span_text)

            # Update TOC links if necessary
            # Assuming TOC anchors use the heading's id attribute
            toc_link = self.soup.find("a", href=f'#{heading.get("id")}')
            if toc_link:
                toc_link.string = numbering + toc_link.text

    def move_toc(self, keep=True):
        # Move the TOC to the body
        if self.toc:
            # Find its ancestor that is a child of the body
            parent_to_remove = None
            for parent in self.toc.parents:
                if parent == self.page_body:
                    break
                parent_to_remove = parent

            if keep:
                # replace the parent with the nav
                parent_to_remove.replace_with(self.toc)

                # Prefix it with a new H1
                new_h1 = self.soup.new_tag("h1")
                new_h1.string = "Table of Contents"
                self.toc.insert_before(new_h1)
            else:
                parent_to_remove.extract()

    def get_html(self):
        return str(self.soup)
