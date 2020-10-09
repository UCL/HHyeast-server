#!/bin/bash
cd /home/ilektra/HHyeast-server
source /home/ubuntu/.virtualenvs/hhserver/bin/activate
export FLASK_APP=hello.py
export FLASK_DEBUG=0

nohup gunicorn --bind 0.0.0.0:5000 wsgi &  2>&1
