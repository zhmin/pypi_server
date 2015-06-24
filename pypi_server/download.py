import requests
import urlparse
import html5lib

PYPI_SERVER = 'https://pypi.python.org/simple/' 

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


if __name__ == "__main__":
    url = urlparse.urljoin(PYPI_SERVER, 'flask')
    page = HTMLPage(url)
    for l in page.links:
        print l
