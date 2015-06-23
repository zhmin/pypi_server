import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

from settings import pkg_dir, Template

class MainPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        names = os.listdir(pkg_dir)
        href = '<a href="/"> {} </a><br>'
        content = '\n'.join(href.format(name) for name in names)
        html = Template('index.html').render(content=content)
        self.write(html)



def main():
    app = Application([
        (r"/", MainPageHandler),
    ])
    server = HTTPServer(app)
    server.listen(8000)
    IOLoop.current().start()


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    main()

