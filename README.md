# Simserve
Simserve is a server simulator which can be used to simulate server interactions of a program (malware).

## Files
* `config_parse.py` - Parse the config.json file using the Config class. Also,
                      creates the request handlers to be used by the server. 
* `handler.py` - Defines a custom request handler which can be configured to send 
                 different responses based on the options given to it and logs each 
                 request-response pair.
* `server.py` - Main file to start the server.

## Installation and Usage
*This tool is written in python 3.6*  
To install dependencies run -  
`pip install -r requirements.txt`

To configure the tool copy `config.json.example` to `config.json`.
- `port` - Specifies the port on which to run the server.
- `routes` - List of paths for which server responds.
  - `path` - Each route has a path string to define the URL path.
  - `responses` - List of responses for each route for different methods. If no
                  response is defined for a method server returns 405 status.
    - `headers` - Dictionary of headers to send with the response.
    - `body` - The response body for given route.
    - `methods` - Methods for which this response should be sent.

To run - 
`python3 server.py`              

## Future Improvements

