import utils
# PackageReadWriter
import os



class DownloadSates(object):
    def __init__(self):
        self.packages = {}

    def __contains__(self, key):
        return key in self.packages

    def __getitem__(self, key):
        return self.packages[key]

    def get_file(self, filename):
        pkg = utils.Package.from_filename(filename)
        if pkg.filename in self.packages:
            return self.packages[pkg.filename]
        directory = os.path.join('packages', pkg.name.lower())
        utils.ensure_dir(directory)
        filepath = os.path.join(directory, pkg.filename)
        self.packages[pkg.filename] = utils.PackageReadWriter(filepath)
        return  self.packages[pkg.filename]

    def remove_file(self, filename):
        del self.packages[filename]


download_packages = DownloadSates()



