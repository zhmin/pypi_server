import os
import posixpath
import urlparse
import requests
import html5lib
from operator import attrgetter
from tornado.web import HTTPError

from utils import parse_pkg_version, ensure_dir
from settings import pkg_dir

PYPI_SERVER = 'https://pypi.python.org/simple/' 

class HTMLPage(object):
    def __init__(self, pkg_name, url, content=None):
        self.pkg_name = pkg_name
        self.url = url
        if content is None:
            content = requests.get(url).content
        self.content = content
        self.parser = html5lib.parse(self.content, 
            namespaceHTMLElements=False)

    @property
    def links(self):
        for anchor in self.parser.findall('.//a'):
            href = anchor.get('href')
            if href:
                url = urlparse.urljoin(self.url, href)
                yield Link(url, self.pkg_name)

    @property
    def versions(self):
        return [l.version for l in self.links if l.version]

    def find_link(self, version):
        for l in self.links:
            if l.version == version:
                return l
        return None
        
    @classmethod
    def from_package_name(cls, pkg_name):
        url = urlparse.urljoin(PYPI_SERVER, pkg_name)
        resp = requests.get(url)
        # url may redirect, so we should use response.url
        # or urljoin get wrong url
        return cls(pkg_name, resp.url, resp.content)

class Link(object):
    def __init__(self, url, pkg_name):
        self.url = url
        self.pkg_name = pkg_name

    @property
    def version(self):
        return parse_pkg_version(self.url, self.pkg_name)

    @property
    def basename(self):
        return posixpath.basename(self.path)

    @property
    def path(self):
        return urlparse.urlparse(self.url).path
        
def download_package(link):
    response = requests.get(link.url)
    if response.status_code == 404:
        raise HTTPError(404)
    dirpath = os.path.join(pkg_dir, link.pkg_name)
    ensure_dir(dirpath)
    filepath = os.path.join(dirpath, link.basename)
    with open(filepath, 'wb') as f:
        f.write(response.content)

def download_stream(url):
    resp = requests.get(url, stream=True)
    total_length = int(resp.headers['content-length'])
    recv_length = 0
    chunk_size = total_length / 1000
    for chunk in resp.raw.stream(chunk_size):
        recv_length +=  len(chunk)
        process = float(recv_length) / total_length
        print "%2f" % process
    

if __name__ == "__main1__":
    url = urlparse.urljoin(PYPI_SERVER, 'flask')
    page = HTMLPage.from_package_name('flask')
    for l in page.links:
        print l.url, l.version

if __name__ == "__main2__":
    url = urlparse.urljoin(PYPI_SERVER, 'flask')
    page = HTMLPage.from_package_name('flask')
    link = page.find_link('0.7')
    resp = requests.get(link.url)
    print resp.content


if __name__ == "__main__":
    url = 'https://pypi.python.org/packages/source/D/Django/Django-1.7.tar.gz#md5=03edab6828119aa9b32b2252d25eb38d'
    url = 'http://localhost:8000/package/flask/Flask-0.11.dev0.tar.gz#md5=02bd6fd75596cd591b15d9c55a47d987'
    download_stream(url)
