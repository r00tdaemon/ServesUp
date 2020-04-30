import config_parse
import handler
import tornado.ioloop
import tornado.web
import tornado.log


def make_app(handlers):
    tornado.log.access_log.setLevel("DEBUG")
    return tornado.web.Application(handlers, default_handler_class=handler.Custom404Handler)


def start_server(config):
    app = make_app(config.handlers)
    app.listen(config.port)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()


def main(config_file="./conf.json"):
    config = config_parse.Config(config_file)
    start_server(config)


if __name__ == "__main__":
    main()
