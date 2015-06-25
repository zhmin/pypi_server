import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application
import tornado.options

from settings import pkg_dir, Template
from utils import find_package
from download import HTMLPage, download_package

tornado.options.parse_command_line()

class MainPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        names = os.listdir(pkg_dir)
        html = Template('index.html').render(packages=names)
        self.write(html)


class PackageHandler(RequestHandler):
    def get(self, pkg_name, *args, **kwargs):
        links = []
        pkgs = find_package(pkg_name)
        context = {'package_name': pkg_name, 'links': pkgs}
        html = Template('package.html').render(**context)
        self.write(html)

class Downloadhandler(RequestHandler):

    def get(self, *args, **kwargs):
        pkg_name = self.get_argument('package')
        version = self.get_argument('version')
        packages = find_package(pkg_name, version)

        if not packages:
            page = HTMLPage.from_package_name(pkg_name)
            link = page.find_link(version)
            if link:
                download_package(link)
                self.write({'download': link.basename})
            else:
                self.write({'version': page.versions})
        else:
            self.write({'status': 'find'})


def main():
    app = Application([
        (r"/simple/?", MainPageHandler),
        (r"/simple/([^/\s]+)/?", PackageHandler),
        (r"/package/(.*)", StaticFileHandler, {'path': pkg_dir}), 
        (r"/download/?", Downloadhandler),
        ],
        {'debug': True,
        'log_file_prefix': './log/',
        }
    )
    server = HTTPServer(app)
    server.listen(8000)
    IOLoop.current().start()


if __name__ == "__main__":
    main()

