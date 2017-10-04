# HHyeast-server

To install package: `pip3 install -r requirements.txt`

To run the server locally: `bokeh serve --show lolliplotServerStandalone.py`
  (note this is an outdated version of the server)

To generate hello.py with the correct IP: `python3 populate_hello.py <yourIPhere>`
  To run locally, you can use `localhost` for the IP. Otherwise, give the IP of the (virtual) machine you're running on.

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