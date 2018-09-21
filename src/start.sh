#!/bin/sh

python initDB.py

/usr/local/bin/gunicorn -b :$1 server:app