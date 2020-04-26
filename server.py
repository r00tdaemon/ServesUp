import conf
import tornado.ioloop
import tornado.web
import tornado.log

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, conf):
        self.conf = conf

    def get(self):
        self.write(self.conf["body"])


def make_app(config_file="./conf.json"):
    config = conf.Config(config_file)
    tornado.log.access_log.setLevel("DEBUG")
    return tornado.web.Application(config.handlers)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
