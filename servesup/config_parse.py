import sys
import json
from servesup import handler


class ConfigValidationError(Exception):
    """Exception raised for config validation errors."""
    pass


class Config:
    # Valid response types
    VALID_RESPONSE_TYPES = ["file", "script", "static"]

    def __init__(self, file_path):
        self.config_file = file_path
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, "r") as file:
                self._conf = json.load(file)
        except FileNotFoundError:
            print(f"Can not find the config file {self.config_file}.")
            sys.exit(-1)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file {self.config_file}: {e}")
            sys.exit(-1)

        # Validate the config
        self._validate_config()

        self._port = self._conf.get("port")
        self._routes = self._conf.get("routes")
        self._handlers = [
            (
                route.get("path"),
                handler.CustomHandler,
                dict(handler_opts=route.get("handler_opts"))
            ) for route in self._routes
        ]

    def _validate_config(self):
        """Validate the configuration JSON."""
        # Check if required top-level keys exist
        if "port" not in self._conf:
            raise ConfigValidationError("Missing required key 'port' in config")
        if "routes" not in self._conf:
            raise ConfigValidationError("Missing required key 'routes' in config")

        # Validate port is a positive integer
        port = self._conf.get("port")
        if not isinstance(port, int) or port <= 0:
            raise ConfigValidationError("'port' must be a positive integer")

        # Validate routes is a list
        routes = self._conf.get("routes")
        if not isinstance(routes, list):
            raise ConfigValidationError("'routes' must be a list")

        # Check for unique paths
        paths = []
        for route in routes:
            if "path" not in route:
                raise ConfigValidationError("Each route must have a 'path' key")

            path = route.get("path")
            if path in paths:
                raise ConfigValidationError(f"Duplicate path found: '{path}'")
            paths.append(path)

            # Validate handler_opts
            if "handler_opts" not in route:
                raise ConfigValidationError(f"Route '{path}' is missing 'handler_opts'")

            handler_opts = route.get("handler_opts")
            if "responses" not in handler_opts:
                raise ConfigValidationError(f"Route '{path}' is missing 'responses' in handler_opts")

            # Validate responses
            responses = handler_opts.get("responses")
            if not isinstance(responses, list):
                raise ConfigValidationError(f"Route '{path}' has 'responses' that is not a list")

            for i, response in enumerate(responses):
                # Check response_type
                if "response_type" not in response:
                    raise ConfigValidationError(f"Route '{path}', response {i} is missing 'response_type'")

                response_type = response.get("response_type")
                if response_type not in self.VALID_RESPONSE_TYPES:
                    raise ConfigValidationError(
                        f"Route '{path}', response {i} has invalid 'response_type': '{response_type}'. "
                        f"Must be one of: {', '.join(self.VALID_RESPONSE_TYPES)}"
                    )

                # Validate based on response_type
                if response_type == "file":
                    if "file_path" not in response:
                        raise ConfigValidationError(f"Route '{path}', response {i} is missing 'file_path' for file response type")
                elif response_type == "script":
                    if "script" not in response:
                        raise ConfigValidationError(f"Route '{path}', response {i} is missing 'script' for script response type")
                elif response_type == "static":
                    if "body" not in response:
                        raise ConfigValidationError(f"Route '{path}', response {i} is missing 'body' for static response type")

                # Check methods
                if "methods" not in response:
                    raise ConfigValidationError(f"Route '{path}', response {i} is missing 'methods'")

                methods = response.get("methods")
                if not isinstance(methods, list) or not methods:
                    raise ConfigValidationError(f"Route '{path}', response {i} has 'methods' that is not a non-empty list")

    def reload(self):
        """Reload the configuration from the config file."""
        self._load_config()

    @property
    def port(self):
        return self._port

    @property
    def routes(self):
        return self._routes

    @property
    def handlers(self):
        return self._handlers
