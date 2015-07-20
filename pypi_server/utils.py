import os
import re
import posixpath
import collections
import md5
import urlparse

from settings import pkg_dir, pkg_href_prefix


def find_package(pkg_name, version=None):
    specify_dir = os.path.join(pkg_dir, pkg_name.lower())
    paths = []
    if os.path.exists(specify_dir):
        paths = os.listdir(specify_dir)
    packages =  [Package(pkg_name, p) for p in paths] 
    if version:
        packages = filter(lambda p: p.version == version, packages)
    return packages
    
    
class Package(object):
    
    def __init__(self, pkg_name, filename):
        self.filename = filename
        self.pkg_name = pkg_name

    @property
    def path(self):
        return os.path.join(pkg_dir, self.pkg_name, self.filename)

    @property
    def version(self):
        return parse_pkg_version(self.link, self.pkg_name)

    @property
    def link(self):
        return pkg_href_prefix + os.path.join(self.pkg_name, self.filename) + '#md5=' + self.md5_value

    @property
    def md5_value(self):
        return md5_cache[self.path]
    

class Md5Cache(dict):
    def __init__(self, size):
        super(Md5Cache, self).__init__()
        self.size = size
        self.queue = collections.deque()

    def __missing__(self, key):
        with open(key) as f:
            self[key] = md5.new(f.read()).hexdigest()
        self.queue.append(key)
        if len(self.queue) > self.size:
            remove_key = self.queue.popleft()
            del self[remove_key]
        return self[key]
        
md5_cache = Md5Cache(100)


egg_info_re = re.compile(r'([\w.]+)-([\w.!+-]+)')

def parse_pkg_version(url, search_name):
    path = urlparse.urlparse(url).path
    name, suffix = split_package_name(posixpath.basename(path.rstrip('/')))
    if suffix is None:
        return None
    match = egg_info_re.search(name)
    if not match:
        return None
    name = match.group(0).lower()
    name = name.replace('_', '-')
    look_for = search_name.lower() + '-'
    if name.startswith(look_for):
        return match.group(0)[len(look_for):]
    else:
        return None

#tar.gz must be below tar
SUPPORTED_EXTENSIONS = ['.tar.gz']

def split_package_name(name):
    for ext in SUPPORTED_EXTENSIONS:
        if name.endswith(ext):
            return name[:-len(ext)], ext
    return name, None
    
def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def format_size(bytes):
    if bytes > 1000 * 1000:
        return '%.1fMB' % (bytes / 1000.0 / 1000)
    elif bytes > 10 * 1000:
        return '%ikB' % (bytes / 1000)
    elif bytes > 1000:
        return '%.1fkB' % (bytes / 1000.0)
    else:
        return '%ibytes' % bytes

if __name__ == "__main__":
    url = u'https://pypi.python.org/../packages/source/F/Flask/Flask-0.8.tar.gz#md5=a5169306cfe49b3b369086f2a63816ab'
    print parse_pkg_version(url, 'flask')
