#!/bin/sh

echo "sleep 30s"
sleep 30s
python initDB.py

/usr/local/bin/gunicorn -b :$1 server:app