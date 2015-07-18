import os
import urlparse

import requests
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application
from tornado.httpclient import AsyncHTTPClient
import tornado.options

from settings import pkg_dir, Template, PYPI_SERVER_URL
from utils import find_package
from pypi_page import get_hrefs

tornado.options.parse_command_line()

class MainPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        names = os.listdir(pkg_dir)
        html = Template('index.html').render(packages=names)
        
        self.write(html)

class SimplePackageHandler(RequestHandler):
    def get(self, pkg_name):
        pkg_url = urlparse.urljoin(PYPI_SERVER_URL, pkg_name)
        response = requests.get(pkg_url)
        anchor_tags = get_hrefs(response.content)
        content = Template('package.html').render(anchor_tags)

class PackageHandler(RequestHandler):
    def get(self, pkg_name, *args, **kwargs):
        links = []
        pkgs = find_package(pkg_name)
        context = {'package_name': pkg_name, 'links': pkgs}
        html = Template('package.html').render(**context)
        self.write(html)

class DownloadPakcageHandler(RequestHandler):
    def get(self):
        package = Package.from_url(self.request.path)
        if package.isexists:
            self.redirct('/package/%s' % self.request.path)
        else:
            def data_recived(chunk):
                self.write(chunk)
            package_url = urlparse.urljoin(PYPI_SERVER_URL, self.request.path)
            http_client = AsyncHTTPClient(package_url, streaming_callback=data_recived)


def main():
    app = Application([
        (r"/simple/?", MainPageHandler),
        (r"/simple/([^/\s]+)/?", SimplePackageHandler),
        (r"/package/(.*)", StaticFileHandler, {'path': pkg_dir}), 
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

