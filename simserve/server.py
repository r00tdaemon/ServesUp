import os
import argparse
import tornado.ioloop
import tornado.web
import tornado.log
from simserve import handler, config_parse


def make_app(handlers):
    tornado.log.access_log.setLevel("INFO")
    return tornado.web.Application(handlers, default_handler_class=handler.Custom404Handler)


def start_server(config):
    app = make_app(config.handlers)
    app.listen(config.port)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()


def main():
    default_conf = f"{os.getcwd()}/conf.json"
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", metavar="FILE_PATH", type=str, default=default_conf)
    args = parser.parse_args()
    config = config_parse.Config(args.config_file)
    start_server(config)


if __name__ == "__main__":
    main()
