from jinja2 import Environment, FileSystemLoader

pkg_dir = 'packages'

template_dir = 'templates'
env = Environment(loader=FileSystemLoader(template_dir))
Template = lambda name: env.get_template(name)
