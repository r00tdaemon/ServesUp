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
    def __init__(self, config_file, app, config, io_loop, server):
        self.config_file = config_file
        self.app = app
        self.config = config
        self.server = server
        self.io_loop = io_loop
        self.last_mtime = os.path.getmtime(config_file)

    def on_modified(self, event):
        if event.src_path == self.config_file:
            current_mtime = os.path.getmtime(self.config_file)
            if current_mtime == self.last_mtime:
                return
            self.last_mtime = current_mtime

            tornado.log.access_log.info(f"Config file {self.config_file} changed. Restarting server...")
            self.io_loop.add_callback(self._restart_server)

    def _restart_server(self):
        if self.server:
            self.server.stop()

        self.config.reload()

        self.app = make_app(self.config.handlers)
        self.server = self.app.listen(self.config.port)


def make_app(handlers):
    tornado.log.access_log.setLevel("DEBUG")
    return tornado.web.Application(handlers, default_handler_class=handler.Custom404Handler)


def start_server(config):
    app = make_app(config.handlers)
    server = app.listen(config.port)
    io_loop = tornado.ioloop.IOLoop.instance()

    # Set up config file monitoring
    observer = Observer()
    event_handler = ConfigFileHandler(config.config_file, app, config, io_loop, server)
    observer.schedule(event_handler, path=os.path.dirname(config.config_file), recursive=False)
    observer.start()

    try:
        io_loop.start()
    finally:
        observer.stop()
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
