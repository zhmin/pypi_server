import os
from settings import pkg_dir


def find_package(pkg_name):
    specify_dir = os.path.join(pkg_dir, pkg_name.lower())
    paths = []
    if os.path.exists(specify_dir):
        paths = [os.path.join(specify_dir, n) for n in os.listdir(specify_dir)]
    return paths
    
    
