#!/bin/bash
cd /home/ilektra/HHyeast-server
export FLASK_APP=hello.py
export FLASK_DEBUG=0

sudo -u ilektra -E -H -- flask run --host=0.0.0.0 &>/home/ilektra/server.out &
