#!/bin/bash
cd /home/ubuntu/HHyeast-server
export FLASK_APP=hello.py
export FLASK_DEBUG=0

nohup gunicorn --bind 0.0.0.0:5000 wsgi &  2>&1
# Run as a service without gunicorn (just change the username):
# sudo -u ilektra -E -H -- flask run --host=0.0.0.0 &>/home/ilektra/server.out &
# Start from command line without gunicorn:
# nohup flask run --host=0.0.0.0 &  2>&1
