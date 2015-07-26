import os
import urlparse
import md5
from functools import partial

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, StaticFileHandler, Application, asynchronous
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import tornado.options

from settings import pkg_dir, Template, PYPI_SERVER_URL
from utils import find_package, Package, ensure_dir, find_match_link
from pypi_page import html_cache, get_hrefs_from_html, get_package_url
from state import download_packages

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
            # pypi_url = get_package_url(pkg_name)
            package = Package.from_pypi_href(anchor.href)
    
            link = {'href': os.path.join('/package', package.name.lower(), 
                                package.filename + '#md5=' + package.md5),
                    'name': package.filename }
            local_pkg = find_package(package.name, package.version)
            link['is_local'] = True if local_pkg else False
            links.append(link)
        
        content = Template('package.html').render(links=links, package_name=pkg_name)
        self.write(content)
        self.finish()


class DownloadPakcageHandler(RequestHandler):

    @gen.coroutine
    @asynchronous
    def get(self, pkg_path):
        # get pypi server package url
        package = Package.from_filename(pkg_path.rstrip('/'))
        html = yield html_cache.get(package.name)

        if not package.is_downloading:
            local_pkg = find_package(package.name, package.version)
            if local_pkg:
                # if local server exsits, redirect
                redirect_url = os.path.join('/download/', local_pkg.name.lower(), package.filename)
                self.redirect(redirect_url)
                raise gen.Return()
            else:
                # not download yet
                pkg_url = get_package_url(package.name)
                anchor_tags =  get_hrefs_from_html(html, exp='*.tar.gz',
                                            match_type='fnmatch')
                href = find_match_link(anchor_tags, package.version)
                url = urlparse.urljoin(pkg_url, href)

                package = Package.from_pypi_href(url)
                readwriter = download_packages.get_file(package.filename)
                print id(readwriter)
                
                def data_received(readwriter, chunk):
                    self.request.connection.write(chunk)
                    readwriter.write(readwriter.current_size, chunk)

                def header_received(header_line):
                    self.request.connection.write(header_line)

                client = AsyncHTTPClient()
                print url
                yield client.fetch(url, connect_timeout=20 * 60, request_timeout= 20 * 60, 
                                    header_callback=header_received, 
                                    streaming_callback=partial(data_received, readwriter))
                
                readwriter.close()
                readwriter.write_done = True
                filepath = os.path.join('packages', package.name.lower(), package.filename)

                # md5 file check
                with open(filepath) as f:
                    file_md5 = md5.new(f.read()).hexdigest()
                if file_md5 == package.md5:
                    self.request.connection.close()
                    download_packages.remove_file(package.filename)
                else:
                    os.remove(filepath)
                    self.send_error(status_code=500, reason='downlaod file damaged')
        else:
            # package downloading
            self.set_status(200)
            self.set_header("Content-Type", "application/octet-stream")
            # self.set_header("Content-Length", content_length)
            readwriter = download_packages.get_file(package.filename)
            print id(readwriter)

            def read_chunk(readwriter, pos, chunk_size= 200*1024):
                chunk = readwriter.read(pos, chunk_size)
                if chunk is None:
                    print chunk
                    self.finish()
                    readwriter.close()
                else:
                    pos += len(chunk)
                    self.write(chunk)
                    IOLoop.current().call_later(0.5, read_chunk, readwriter, pos)

            IOLoop.current().call_later(0.5, read_chunk, readwriter, 0)


def main():
    app = Application([
        (r"/simple/?", MainPageHandler),
        (r"/simple/([^/\s]+)/?", SimplePackageHandler),
        (r"/download/(.*)", StaticFileHandler, {'path': pkg_dir}), 
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

