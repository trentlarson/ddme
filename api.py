import json
import signal
import sys

from tornado.httpserver import HTTPServer
from tornado.httputil import HTTPHeaders
import tornado.ioloop
from tornado.options import define, options
from  tornado.web import URLSpec

from orders import Book, Buy, Sell

define("port", default=3000, help="run on the given port", type=int)
Book()


class BookHandler(tornado.web.RequestHandler):
    """
    Handle GET requests to /book API endpoint.
    """
    def get(self):
        ret = Book().orders()
        self.write(ret)


class OrderHandler(tornado.web.RequestHandler):
    """
    Handle POST requests to /buy and /sell API endpoints.
    """
    def post(self, **kwargs):
        order = None
        body = json.loads(self.request.body)
        if self.request.uri == "/buy":
            order = Buy(**body)
        if self.request.uri == "/sell":
            order = Sell(**body)
        try:
            resp = Book().match(order)
            http_status_code = 201
        except Exception as e:
            resp = {"message": e.message}
            http_status_code = 500
        self.set_header("location", "{}://{}{}".format(self.request.protocol,
            self.request.host, self.reverse_url("book")))
        self.set_status(http_status_code)
        self.write(resp)


def stop():
    """
    Stop the IOLoop.
    """
    tornado.ioloop.IOLoop.current().stop()

def sigint_handler(signum, frame):
    """
    Add shutdown task in next IOLoop.
    """
    tornado.ioloop.IOLoop.current().add_callback(stop)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        URLSpec(r"/book", BookHandler, name="book"),
        URLSpec(r"/buy", OrderHandler, name="buy"),
        URLSpec(r"/sell", OrderHandler, name="sell"),
    ])
    http_server = HTTPServer(application)
    http_server.listen(options.port)
    signal.signal(signal.SIGINT, sigint_handler)
    tornado.ioloop.IOLoop.current().start()
    sys.exit(0)

if __name__ == "__main__":
    main()

