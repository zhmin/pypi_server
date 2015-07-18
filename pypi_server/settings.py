from jinja2 import Environment, FileSystemLoader

pkg_dir = 'packages'
pkg_href_prefix = '/package/'

template_dir = 'templates'
env = Environment(loader=FileSystemLoader(template_dir))
Template = lambda name: env.get_template(name)

PYPI_SERVER_URL = 'https://pypi.python.org/simple/'

