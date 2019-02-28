# HHyeast-server

To install package: `pip3 install -r requirements.txt`

To generate hello.py and other files from the templates, with the correct IP and other parameters: 
```
python3 populate_templates.py <yourIPhere> <timeoutForTests>
```
For example, to run locally with a timeout of 30s for the tests:
```
python3 populate_templates.py localhost 30
```
If you're not running locally, give the IP of the (virtual) machine you're running on.
For example, on Azure:
```
python3 populate_templates.py hhyeast.ucl.ac.uk 30
```

To run the flask application: 
```
export FLASK_APP=hello.py
export FLASK_DEBUG=1
flask run
```
For production run, `FLASK_DEBUG=0`.

To run on azure, you need to specify the host:
```
flask run --host=0.0.0.0
```
and, if starting form an ssh session, you should tell the application to run in the background
and to not hang up when you log out. The output will automatically be saved in `nohup.out`:
```
nohup flask run --host=0.0.0.0 &  2>&1
```

Note that the application expects to find the data files in `~/data`.
