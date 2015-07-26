import os
import re
import posixpath
import md5
import urlparse
from collections import namedtuple, deque

from settings import pkg_dir, pkg_href_prefix, PYPI_SERVER_URL
from pypi_page import get_hrefs_from_html
import state

class Package(object):
    
    package_suffix  = ['.tar.gz']

    def __init__(self, path, include_fragment, is_local):
        self.is_local = is_local
        self.path = path
        self.is_local = is_local
        if include_fragment and '#' not in posixpath.basename(self.path):
            raise ValueError('%s has no fragment' % path)
        self.include_fragment =include_fragment

    @property
    def fragment(self):
        if self.include_fragment:
            return self.path.rsplit('#', 1)[-1]
        return ''

    @property
    def name(self):
        """
        Flask
        """
        return self.filename.rstrip(self.suffix).split('-')[0]

    @property
    def suffix(self):
        for suffix in self.package_suffix:
            if self.filename.endswith(suffix):
                return suffix

    @property
    def filename(self):
        """
        Flask-0.7.1.tar.gz
        """
        basename = posixpath.basename(self.path)
        if not self.is_local and '#' in basename:
            basename, _ = basename.rsplit('#', 1)
        return basename

    @property
    def version(self):
        """
        0.7.1
        """
        return self.filename.rstrip(self.suffix).split('-')[1]

    @property
    def url(self):
        if self.is_local:
            return pkg_href_prefix + posixpath.join(self.name.lower(), 
                            self.filename) + '#md5=' + self.md5
        else:
            return self.path

    @property
    def md5(self):
        if self.fragment:
            return self.fragment.split('=')[1]
        if self.is_local:
            return md5_cache[self.path]

    @property
    def is_downloading(self):
        return self.filename in state.download_packages

    @classmethod
    def from_local_path(cls, path):
        """
        package/flask/Flask-0.7.1.tar.gz
        """
        return cls(path, include_fragment=False, is_local=True)

    @classmethod
    def from_pypi_href(cls, path):
        """
        https://pypi.python.org/packages/source/F/Flask/Flask-0.7.1.tar.gz
        #md5=4705d31035839dec320a1fd76ac2fa30
        """
        return cls(path, include_fragment=True, is_local=False)

    @classmethod
    def from_filename(cls, path):
        """
        Flask-0.7.1.tar.gz
        """
        return cls(path, include_fragment=False, is_local=False)


class Md5Cache(dict):
    def __init__(self, size):
        super(Md5Cache, self).__init__()
        self.size = size
        self.queue = deque()

    def __missing__(self, key):
        with open(key) as f:
            self[key] = md5.new(f.read()).hexdigest()
        self.queue.append(key)
        if len(self.queue) > self.size:
            remove_key = self.queue.popleft()
            del self[remove_key]
        return self[key]
        
md5_cache = Md5Cache(100)


class PackageReadWriter(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, 'w+')
        self.write_size = 0
        self.write_done = False
        self.is_close = False

    def read(self, pos, size):
        '''
        return value:
            None, no more data
            '', more data not come
        '''
        if self.is_close:
            self.file = open(self.filepath, 'r+')
        self.file.seek(pos)
        data = self.file.read(size)
        if not data and pos >= self.total_size:
            return None
        return data

    def write(self, pos, data):
        self.file.seek(pos)
        self.file.write(data)
        self.write_size += len(data)

    def flush(self):
        self.file.flush()

    def close(self):
        self.is_close = True
        self.file.close()

    @property
    def total_size(self):
        if self.write_done:
            return self.write_size
        else:
            return float('inf')

    @property
    def current_size(self):
        return self.write_size


def find_package(pkg_name, version):
    specify_dir = os.path.join(pkg_dir, pkg_name.lower())
    paths = []
    if os.path.exists(specify_dir):
        paths = os.listdir(specify_dir)
    for path in paths:
        package = Package.from_local_path(os.path.join(specify_dir, path))
        if package.version == version:
            return package

def find_match_link(anchor_tags, dst_version):
    for anchor in anchor_tags:
        pkg = Package.from_pypi_href(anchor.href)
        if pkg.version == dst_version:
            return anchor.href


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
SUPPORTED_EXTENSIONS = ['.tar.gz']

def split_package_name(name):
    for ext in SUPPORTED_EXTENSIONS:
        if name.endswith(ext):
            return name[:-len(ext)], ext
    return name, None
    
def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

if __name__ == "__main__":
    url = u'https://pypi.python.org/../packages/source/F/Flask/Flask-0.8.tar.gz#md5=a5169306cfe49b3b369086f2a63816ab'
    url = 'https://pypi.python.org/packages/source/F/Flask/Flask-0.6.tar.gz#md5=55a5222123978c8c16dae385724c0f3a'
    package =  Package.from_pypi_href(url)
    print package.name
    print package.suffix
    print package.filename
    print package.fragment
    print package.version
    print package.url
    print package.md5
