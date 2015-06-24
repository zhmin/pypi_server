import os
import posixpath
import collections
import md5
import urlparse
from settings import pkg_dir, pkg_href_prefix


def find_package(pkg_name):
    specify_dir = os.path.join(pkg_dir, pkg_name.lower())
    paths = []
    if os.path.exists(specify_dir):
        paths = os.listdir(specify_dir)
    return [Package(pkg_name, p) for p in paths] 
    
    
class Package(object):
    
    def __init__(self, pkg_name, filename):
        self.filename = filename
        self.pkg_name = pkg_name

    @property
    def path(self):
        return os.path.join(pkg_dir, self.pkg_name, self.filename)

    @property
    def version(self):
        return parse_pkg_version(self.link)

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
    name, _ = split_package_name(posixpath.basename(path.rstrip('/')))
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
SUPPORTED_EXTENSIONS = ['tar.gz']

def split_package_name(name):
    for ext in SUPPORTED_EXTENSIONS:
        if name.endswith(ext):
            return name[:len(ext)], ext
    return name, None
    
