from collections import namedtuple
import re
import fnmatch
import html5lib
import urlparse
import time
import collections

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from settings import PYPI_SERVER_URL

AnchorTag = namedtuple('HrefTag', ['href', 'name'])

def get_hrefs_from_html(html, exp=None, match_type=None):
    """
    exp is None: return all hrefs
    match_type: 
            'reg_exp': regular expresion match,
            'fnmatch': unix path match
    """
    parser = html5lib.parse(html, namespaceHTMLElements=False)
    if isinstance(exp, basestring) and match_type == 'reg_exp':
    	reg_exp =  re.compile(exp)
    for anchor in parser.findall('.//a[@href]'):
        href = anchor.get('href')
        name = anchor.text
        if exp is None:
            yield AnchorTag(href, name)
            continue
        if match_type == 'reg_exp' and reg_exp.match(name):
           yield AnchorTag(href, name)
        if match_type == 'fnmatch' and fnmatch.fnmatch(name, exp):
            yield AnchorTag(href, name)

class HtmlPageCache(object):

    def __init__(self, size=50):
        self.size = size
        self.cache = collections.OrderedDict()
    
    @property
    def expired_pages(self, deadline=time.time()):
        for name, infor in self.cache.items():
            if infor.deadline <= deadline:
                yield name

    @gen.coroutine
    def update(self, deadline=time.time()):
        for name in self.expired_pages(deadline):
            yield self.fetch_impl(name)

    @gen.coroutine
    def get(self, name):
        if name not in self.cache:
            html = yield self.fetch_impl(name)
            self.cache[name] = {'html': html, 'deadline': time.time() + 1*60*60}
        else:
            value = self.cache[name]
            del self.cache[name]
            self.cache[name] = value
        
        if len(self.cache) > self.size:
            self.cache.popitem(last=False)

        raise gen.Return(self.cache[name]['html'])
    
    @gen.coroutine
    def fetch_impl(self, name):
        pkg_url = get_package_url(name)
        client = AsyncHTTPClient()
        response = yield client.fetch(pkg_url)
        if response.code == 200:
            raise gen.Return(response.body)


html_cache = HtmlPageCache()
            

def get_package_url(name):
    url = urlparse.urljoin(PYPI_SERVER_URL, name)
    if not url.endswith('/'):
        url += '/'
    return url
    
