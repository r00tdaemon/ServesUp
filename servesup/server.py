import os
import argparse
import tornado.ioloop
import tornado.web
import tornado.log
from servesup import handler, config_parse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys


class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_file, app, config):
        self.config_file = config_file
        self.app = app
        self.config = config

    def on_modified(self, event):
        if event.src_path == self.config_file:
            tornado.log.access_log.info(f"Config file {self.config_file} changed. Restarting server...")
            # Stop the current server
            tornado.ioloop.IOLoop.current().stop()
            # Reload the config
            self.config.reload()
            # Restart the server
            tornado.ioloop.IOLoop.current().start()


def make_app(handlers):
    tornado.log.access_log.setLevel("DEBUG")
    return tornado.web.Application(handlers, default_handler_class=handler.Custom404Handler)


def start_server(config):
    app = make_app(config.handlers)
    app.listen(config.port)

    # Set up config file monitoring
    observer = Observer()
    event_handler = ConfigFileHandler(config.config_file, app, config)
    observer.schedule(event_handler, path=os.path.dirname(config.config_file), recursive=False)
    observer.start()

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        observer.stop()
        tornado.ioloop.IOLoop.current().stop()
    observer.join()


def main():
    default_conf = f"{os.getcwd()}/conf.json"
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", metavar="FILE_PATH", type=str, default=default_conf)
    args = parser.parse_args()
    config = config_parse.Config(args.config_file)
    start_server(config)


if __name__ == "__main__":
    main()
