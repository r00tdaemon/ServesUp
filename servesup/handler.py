import os
import sys
import inspect
import importlib
import importlib.util
import mimetypes
from typing import (
    Dict,
    Union,
)

import tornado.web
from tornado import httputil
from tornado.log import access_log

from servesup.plugins.base import Plugin


class CustomHandler(tornado.web.RequestHandler):
    def initialize(self, handler_opts):
        self._opts = handler_opts

    def _get_resp(self, method: str) -> Union[Dict, None]:
        for resp in self._opts.get("responses"):
            if method in resp.get("methods"):
                return resp
        return None

    @staticmethod
    def _load_script(path: str):
        if importlib.util.find_spec(f"servesup.plugins.{os.path.splitext(os.path.basename(path))[0]}"):
            return importlib.import_module(f"servesup.plugins.{path}")
        elif os.path.isfile(f"{os.getcwd()}/{path}.py") or os.path.isfile(f"{os.getcwd()}/{path}"):
            path = f"{os.getcwd()}/{path}"
            path = f"{path}.py" if os.path.isfile(f"{path}.py") else f"{path}"
            module_name = f"__servesup_plugin__.{os.path.splitext(os.path.basename(path))[0]}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                access_log.error(f"Could not load plugin. {e}")
                raise tornado.web.HTTPError(500)
            return module
        elif os.path.isfile(path):
            module_name = f"__servesup_plugin__.{os.path.splitext(os.path.basename(path))[0]}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                access_log.error(f"Could not load plugin. {e}")
                raise tornado.web.HTTPError(500)
            return module
        else:
            access_log.error("Couldn't find plugin to load.")
            raise tornado.web.HTTPError(500)

    def _get_file_content_type(self, file_path: str) -> str:
        """Determine the content type of a file based on its extension."""
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            # Default to application/octet-stream if type cannot be determined
            content_type = 'application/octet-stream'
        return content_type

    def _read_file_content(self, file_path: str) -> bytes:
        """Read file content in binary mode."""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            access_log.error(f"Could not read file {file_path}. {e}")
            raise tornado.web.HTTPError(500)

    def _get_resp_body(self, resp: Dict):
        response_type = resp.get("response_type")
        if response_type == "script":
            plug_module = self._load_script(resp.get('script'))
            _, plug = inspect.getmembers(
                plug_module,
                lambda x: inspect.isclass(x) and not inspect.isabstract(x) and issubclass(x, Plugin)
            )[0]
            return plug().response(self.request)
        elif response_type == "static":
            return resp.get("body")
        elif response_type == "file":
            file_path = resp.get("file_path")
            if not file_path:
                access_log.error("No file_path specified for file response type")
                raise tornado.web.HTTPError(500)

            # Set content type based on file extension
            # content_type = self._get_file_content_type(file_path)
            # self.set_header("Content-Type", content_type)

            # Read and return file content
            return self._read_file_content(file_path)

    @staticmethod
    def _format_request(req: httputil.HTTPServerRequest) -> str:
        log = f"\n----- Request -----\n"
        log += f"{req.method} {req.uri} {req.version}\n"
        for k, v in sorted(req.headers.get_all()):
            log += f"{k}: {v}\n"
        if req.body:
            log += f"{req.body}\n\n"
        log += f"----- End -----\n"
        return log

    @staticmethod
    def _format_response(resp) -> str:
        log = f"\n----- Response -----\n"
        for k, v in sorted(resp.get("headers")):
            log += f"{k}: {v}\n"
        log += f"\n{resp.get('body')}\n"
        log += f"----- End -----\n"
        return log

    @staticmethod
    def log_req_resp(req: httputil.HTTPServerRequest, resp: Union[Dict, None]) -> None:
        access_log.info(CustomHandler._format_request(req))
        if resp:
            access_log.info(CustomHandler._format_response(resp))

    def _handle_req(self):
        resp = self._get_resp(self.request.method)
        if resp is None:
            self.log_req_resp(self.request, None)
            raise tornado.web.HTTPError(405)

        headers = resp.get("headers", {}).items()
        for k, v in headers:
            self.set_header(k, v)

        body = self._get_resp_body(resp)
        self.log_req_resp(self.request, dict(headers=headers, body=body))
        self.finish(body)

    def get(self):
        self._handle_req()

    def post(self):
        self._handle_req()

    def delete(self):
        self._handle_req()

    def put(self):
        self._handle_req()

    def patch(self):
        self._handle_req()

    def head(self):
        self._handle_req()

    def options(self):
        self._handle_req()


class Custom404Handler(tornado.web.RequestHandler):
    def prepare(self):
        CustomHandler.log_req_resp(self.request, None)
        raise tornado.web.HTTPError(status_code=404)
