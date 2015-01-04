#!/bin/sh
env/bin/uwsgi --socket 127.0.0.1:5000 -w WSGI:app
