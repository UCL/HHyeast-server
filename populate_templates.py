import sys
from jinja2 import Template, TemplateNotFound, Environment, FileSystemLoader


j2_env = Environment(loader=FileSystemLoader('.'))

rendered_template = j2_env.get_template(
        'hello.template').render(dnprefix=sys.argv[1])
with open("hello.py", "w") as f:
        f.write(rendered_template)

rendered_template = j2_env.get_template(
        'testing-script.template').render(dnprefix=sys.argv[1], tout=sys.argv[2])
with open("testing-script.py", "w") as f:
        f.write(rendered_template)

rendered_template = j2_env.get_template(
        'Dockerfile.template').render(dnprefix=sys.argv[1])
with open("Dockerfile", "w") as f:
        f.write(rendered_template)
