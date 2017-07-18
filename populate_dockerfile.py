import sys
from jinja2 import Template, TemplateNotFound, Environment, FileSystemLoader


j2_env = Environment(loader=FileSystemLoader('.'))
rendered_template = j2_env.get_template(
                            'Dockerfile.template').render(dnprefix=sys.argv[1])
print(rendered_template)
with open("Dockerfile", "w") as f:
        f.write(rendered_template)
