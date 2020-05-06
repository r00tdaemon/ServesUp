# Simserve
Simserve is a server simulator which can be used to simulate server interactions of a program (malware). It is highly configurable as users can configure it to produce valid http responses for given set of requests.

## Files
* `config_parse.py` - Parse the config.json file using the Config class. Also,
                      creates the request handlers to be used by the server. 
* `handler.py` - Defines a custom request handler which can be configured to send 
                 different responses based on the options given to it and logs each 
                 request-response pair.
* `server.py` - Main file to start the server.

* `plugins.base` - The base plugin class used to for dynamic responses. For on this below.

## Installation and Usage
*This tool is written in **python 3.6***  
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
    - `response_type` - How to generate the response. Can be "static" or "script"
    - `script` - Name of python module from which to generate the response. Used if `"response_type` is "script". User can provide either a default plugin(`customresp`), a relative path to python script or an absolute path to the script.
    
To run - `python3 server.py`
     
### Plugins
Users can create their own plugins which will allow them to generate dynamic responses based on the requests received.

To create a plugin you need to import the base plugin class and override its abstract method.  
```python
from simserve.plugins.base import Plugin

class MyResponse(Plugin):
    def response(self, request):
        return f"Hello from plugin"
```         
The `customresp.py` serves as a simple example of a plugin.

## Future Improvements
* Allow specifying file path for config file.
* Option to log request and responses to a file.
* Create a GUI for the tool.
