import os
import md5
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
        pass

    @property
    def link(self):
        return pkg_href_prefix + os.path.join(self.pkg_name, self.filename) + '#' + self.md5_value

    @property
    def md5_value(self):
        return md5_file(self.path)

    
def md5_file(filepath):
    with open(filepath) as f:
        return md5.new(f.read()).hexdigest()
