# ServesUp
ServesUp is a powerful HTTP server simulator designed for developers, testers, and security researchers. It allows you to create a fully configurable HTTP server that can simulate various API endpoints, web services, and server behaviors without modifying your client applications.

## Key Features
- **Configurable HTTP Responses**: Define custom responses for any HTTP method (GET, POST, PUT, DELETE, etc.)
- **Dynamic Response Generation**: Create responses using Python scripts
- **File Serving**: Serve static files with automatic content-type detection
- **Custom Headers**: Set any HTTP headers for your responses
- **Hot Reloading**: Server automatically reloads when configuration changes
- **Request Logging**: Detailed logging of all requests and responses

## Use Cases
- **API Testing**: Simulate backend services for frontend development
- **Security Testing**: Quickly creating a server to send exploit payload
- **Development**: Develop against mock APIs before the real backend is ready
- **Debugging**: Isolate and reproduce specific server behaviors

## Files
* `config_parse.py` - Parse the config.json file using the Config class. Also,
                      creates the request handlers to be used by the server. 
* `handler.py` - Defines a custom request handler which can be configured to send 
                 different responses based on the options given to it and logs each 
                 request-response pair.
* `server.py` - Main file to start the server.

* `plugins.base` - The base plugin class used to for dynamic responses. More on this below.

## Installation and Usage
*This tool is written in **python 3.6***  
Clone the repository.  
```
git clone https://github.com/r00tdaemon/ServesUp.git
cd servesup
```

To install dependencies run -  
`pip install -r requirements.txt`

To configure the tool copy `conf.json.example` to `conf.json`.
- `port` - Specifies the port on which to run the server.
- `routes` - List of paths for which server responds.
  - `path` - Each route has a path string to define the URL path.
  - `responses` - List of responses for each route for different methods. If no
                  response is defined for a method server returns 405 status.
    - `headers` - Dictionary of headers to send with the response.
    - `body` - The response body for given route. Used if `"response_type` is "static"
    - `methods` - HTTP methods for which this response should be sent.
    - `response_type` - How to generate the response. Can be "static", "script", or "file"
    - `script` - Name of python module from which to generate the response. Used if `"response_type` is "script". User can provide either a default plugin(`customresp`), a relative path to python script or an absolute path to the script.
    - `file_path` - Path to the file to serve. Used if `"response_type` is "file". Can be an absolute path or a path relative to the current working directory.

### Response Types

#### Static Response
The simplest response type that returns a static string as the response body:
```json
{
  "response_type": "static",
  "body": "This is a static response",
  "methods": ["GET"],
  "headers": {
    "Content-Type": "text/plain"
  }
}
```

#### Script Response
Generates a dynamic response using a Python script:
```json
{
  "response_type": "script",
  "script": "customresp",
  "methods": ["GET"],
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### File Response
Serves the contents of a file as the response body:
```json
{
  "response_type": "file",
  "file_path": "/path/to/your/file.txt",
  "methods": ["GET"],
  "headers": {
    "Content-Type": "text/plain"
  }
}
```

    
To run - `servesup`  
By default it looks for config file in current working dir.
To specify path to config file pass `-c` flag.  
`servesup -c <path to conf.json>`
     
### Plugins
Users can create their own plugins which will allow them to generate dynamic responses based on the requests received.

To create a plugin you need to import the base plugin class and override its abstract method.  
```python
from servesup.plugins.base import Plugin

class MyResponse(Plugin):
    def response(self, request):
        return f"Hello from plugin"
```         
The `customresp.py` serves as a simple example of a plugin.

## Future Improvements
* Option to log request and responses to a file.
* Create a GUI for the tool.
