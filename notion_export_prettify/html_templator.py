from jinja2 import Template
from bs4 import BeautifulSoup


class HtmlTemplator:
    def __init__(self, template):
        self.html = template

    def inject(self, context, **kwargs):
        template = Template(self.html)
        self.html = template.render(context, **kwargs)
        return self

    def add_css(self, css):
        soup = BeautifulSoup(self.html, "html.parser")
        new_style_tag = soup.new_tag("style", type="text/css")
        new_style_tag.string = css

        # Append the new <style> tag to the <head>
        soup.head.insert(0, new_style_tag)
        self.html = str(soup)
        return self
