import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application
import tornado.options

from settings import pkg_dir, Template

tornado.options.parse_command_line()

class MainPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        names = os.listdir(pkg_dir)
        html = Template('index.html').render(packages=names)
        self.write(html)


class PackageHandler(RequestHandler):
    def get(self, pkg_name, *args, **kwargs):
        links = []
        for filename in os.listdir(pkg_dir):
            print pkg_name, filename
            if pkg_name.lower() in filename.lower():
                links.append(filename)
        html = Template('package.html').render(links=links)
        self.write(html)


def main():
    app = Application([
        (r"/simple/?", MainPageHandler),
        (r"/simple/([^/\s]+)/?", PackageHandler),
        (r"/package/([^/\s]+)/?", StaticFileHandler, {'path': pkg_dir}), 
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

