from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


class HtmlTemplator:
    def __init__(self, template_path):
        self.env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_from_file(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    @staticmethod
    def render(html_template, context):
        template = Template(html_template)
        return template.render(context)
