# HHyeast-server

To install package: `pip3 install -r requirements.txt`

To run the server locally: `bokeh serve --show lolliplotServerStandalone.py`
  (note this is a very outdated version of the server)

To generate hello.py and other files from the templates, with the correct IP and other parameters: 
`python3 populate_templates.py <yourIPhere> <timeoutForTests>`
For example, to run locally with a timeout of 30s for the tests:
`python3 populate_templates.py localhost 30` 
If you're not running locally, give the IP of the (virtual) machine you're running on.

To run the flask application: 
```
export FLASK_APP=hello.py
export FLASK_DEBUG=1
flask run
```

To run on azure, you need to specify the host:
```
flask run --host=0.0.0.0
```

Note that the application expects to find the data files in `~/data`.
