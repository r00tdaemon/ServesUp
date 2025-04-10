import sys
import json
from servesup import handler
from jsonschema import validate, ValidationError


class ConfigValidationError(Exception):
    """Exception raised for config validation errors."""
    pass


class Config:
    # Valid response types
    VALID_RESPONSE_TYPES = ["file", "script", "static"]

    # Valid HTTP methods
    VALID_HTTP_METHODS = ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTIONS"]

    # JSON Schema for config validation
    CONFIG_SCHEMA = {
        "type": "object",
        "required": ["port", "routes"],
        "properties": {
            "port": {
                "type": "integer",
                "minimum": 1
            },
            "routes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["path", "handler_opts"],
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "handler_opts": {
                            "type": "object",
                            "required": ["responses"],
                            "properties": {
                                "responses": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["response_type", "methods"],
                                        "properties": {
                                            "response_type": {
                                                "type": "string",
                                                "enum": ["file", "script", "static"]
                                            },
                                            "methods": {
                                                "type": "array",
                                                "minItems": 1,
                                                "items": {
                                                    "type": "string",
                                                    "enum": ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD", "OPTIONS"]
                                                }
                                            },
                                            "file_path": {
                                                "type": "string"
                                            },
                                            "script": {
                                                "type": "string"
                                            },
                                            "body": {
                                                "type": "string"
                                            },
                                            "headers": {
                                                "type": "object",
                                                "additionalProperties": {
                                                    "type": "string"
                                                }
                                            }
                                        },
                                        "oneOf": [
                                            {
                                                "properties": {
                                                    "response_type": {"const": "file"}
                                                },
                                                "required": ["file_path"]
                                            },
                                            {
                                                "properties": {
                                                    "response_type": {"const": "script"}
                                                },
                                                "required": ["script"]
                                            },
                                            {
                                                "properties": {
                                                    "response_type": {"const": "static"}
                                                },
                                                "required": ["body"]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

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
        """Validate the configuration JSON using JSONSchema and additional checks."""
        try:
            # Basic schema validation
            validate(instance=self._conf, schema=self.CONFIG_SCHEMA)

            # Additional validation for unique paths
            paths = [route.get("path") for route in self._conf.get("routes", [])]
            duplicates = {path for path in paths if paths.count(path) > 1}
            if duplicates:
                raise ConfigValidationError(f"Duplicate paths found: {', '.join(duplicates)}")

            # Validate that each HTTP method appears only once per path
            for route in self._conf.get("routes", []):
                path = route.get("path")
                used_methods = set()

                for response in route.get("handler_opts", {}).get("responses", []):
                    methods = response.get("methods", [])
                    for method in methods:
                        if method in used_methods:
                            raise ConfigValidationError(
                                f"Duplicate HTTP method '{method}' found in path '{path}'. "
                                f"Each HTTP method can only be used once per path."
                            )
                        used_methods.add(method)

        except ValidationError as e:
            raise ConfigValidationError(f"Config validation failed: {e.message}")

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
