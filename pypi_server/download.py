import os
import posixpath
import urlparse
import requests
import html5lib

from utils import parse_pkg_version, ensure_dir
from settings import pkg_dir


class HTMLPage(object):
    def __init__(self, url, content=None):
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
                yield urlparse.urljoin(self.url, href)

def download_package(pkg_name, dst_version):
    url = urlparse.urljoin(PYPI_SERVER, pkg_name)
    print url
    page = HTMLPage(url)
    for link in page.links:
        version = parse_pkg_version(link, pkg_name)
        if version == dst_version:
            resp = requests.get(link)
            dirpath = os.path.join(pkg_dir, pkg_name)
            ensure_dir(dirpath)
            filename = posixpath.basename(urlparse.urlparse(link).path)
            with open(os.path.join(dirpath, filename), 'wb') as f:
                f.write(resp.content)
            return


if __name__ == "__main1__":
    url = urlparse.urljoin(PYPI_SERVER, 'flask')
    page = HTMLPage(url)
    for l in page.links:
        print l

if __name__ == "__main__":
    download_package('flask', '0.8')
