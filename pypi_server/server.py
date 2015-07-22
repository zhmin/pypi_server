import os
import urlparse

import requests
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application, asynchronous
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import tornado.options
from tornado.httpclient import AsyncHTTPClient

from settings import pkg_dir, Template, PYPI_SERVER_URL
from utils import find_package, parse_pkg_name
from pypi_page import html_cache, get_hrefs_from_html, get_package_url

tornado.options.parse_command_line()

class MainPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        names = os.listdir(pkg_dir)
        html = Template('index.html').render(packages=names)
        
        self.write(html)

class SimplePackageHandler(RequestHandler):
    @gen.coroutine
    def get(self, pkg_name):
        html = yield html_cache.get(pkg_name)
        anchor_tags = get_hrefs_from_html(html, exp='*.tar.gz', match_type='fnmatch')
        links = []
        for anchor in anchor_tags:
            href = "/package/" + os.path.basename(anchor.href)
            links.append({'href': href, 'name': anchor.name})
        
        content = Template('package.html').render(links=links, package_name=pkg_name)
        self.write(content)
        self.finish()

class DownloadPakcageHandler(RequestHandler):
    @gen.coroutine
    def get(self, pkg_path):
        # get pypi server package url
        dst_pkg_info = parse_pkg_name(pkg_path.strip())
        pkg_url = get_package_url(dst_pkg_info.name)

        html = yield html_cache.get(dst_pkg_info.name)
        anchor_tags =  get_hrefs_from_html(html, exp='*.tar.gz',
                                    match_type='fnmatch')
        path = find_match_link(anchor_tags, dst_pkg_info.version)
        url = urlparse.urljoin(pkg_url, path)

        f = open('flask-0.9.tar.gz', 'wb')
        
        def data_received(chunk):
            self.request.connection.write(chunk)
            f.write(chunk)

        def header_received(header_line):
            self.request.connection.write(header_line)

        client = AsyncHTTPClient()
        yield client.fetch(url, connect_timeout=200 * 1000, request_timeout= 200 * 1000, header_callback=header_received, streaming_callback=data_received)
        self.request.finish()
        f.close()

def find_match_link(anchor_tags, dst_version):
    for anchor in anchor_tags:
        pkg_info = parse_pkg_name(anchor.name)
        if pkg_info.version == dst_version:
            return anchor.href

def main():
    app = Application([
        (r"/simple/?", MainPageHandler),
        (r"/simple/([^/\s]+)/?", SimplePackageHandler),
        # (r"/package/(.*)", StaticFileHandler, {'path': pkg_dir}), 
        (r"/package/(.*)", DownloadPakcageHandler), 
        ],
        {'debug': True,
        'log_file_prefix': './log/',
        }
    )
    server = HTTPServer(app)
    server.listen(5000)
    IOLoop.current().start()


if __name__ == "__main__":
    main()

